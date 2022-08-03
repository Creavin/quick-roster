import os
import re
import glob

import numpy as np
import pandas as pd

from scipy.stats import chisquare
from NspObjects.Penalties import Penalties
from NspObjects.ShiftData import ShiftData
from NspObjects.SkillData import SkillData
from NspObjects.WorkerData import WorkerData
from NspUtils.RosterJsonDecoder import RosterJsonDecoder

decoder = RosterJsonDecoder()


def label_file(input_file, output_dir=None, is_training_data=True):
    dict = decoder.json_to_dict(input_file)
    roster = decoder.decode_roster(dict)

    lpr_values = get_lpr_target_values(input_file)
    df = label(roster, lpr_values, is_training_data)

    if output_dir:
        df.to_csv(f'{output_dir}/{os.path.basename(input_file).split(".")[0]}.csv')
    else:
        return df


def label(roster, lpr_values=None, is_training_data=True):
    if is_training_data:
        y = roster.worker_assignment
        y = np.array(y)

    if lpr_values is None:
        lpr_values = roster.worker_assignment

    # Keys: 'num_lpr_assignments','avg_lpr_assignment_value', 'median_lpr_assignment_value'
    # lpr_statistics_map = calc_lpr_values(input_file_path)
    # lpr_values = get_lpr_target_values(input_file)

    wd: WorkerData = roster.worker_data
    shiftd: ShiftData = roster.shift_data
    skilld = roster.skill_data

    num_workers = wd.number_workers
    num_days = shiftd.number_days
    num_shifts = shiftd.number_shifts
    num_tracks = shiftd.number_tracks
    num_skills = skilld.number_skills
    roster_shape = (num_workers, num_days, num_tracks, num_shifts, num_skills)

    num_skills_of_each_worker = [len(value) for value in wd.worker_id_to_skill_map.values()]
    avg_num_skills_of_each_worker = np.mean(num_skills_of_each_worker)
    med_num_skills_of_each_worker = np.median(num_skills_of_each_worker)
    chi_num_skills_of_each_worker, _ = chisquare(num_skills_of_each_worker)

    # array[d][s] which contains sets of workers with availability for d,s
    available_workers = calc_available_workers(wd, shiftd)
    # float which represents avg available workers
    avg_available_workers = np.mean(len(available_workers[:][:]))

    staff_req_sparcity = np.sum(shiftd.shift_staffing_level_requirements) / np.product(roster_shape)
    staff_avail_sparcity = np.sum(wd.worker_availability) / np.product(roster_shape)

    # array[d][s]
    deviations_current_avail_workers_from_avg = calc_dev_availability_from_mean(available_workers,
                                                                                avg_available_workers)

    # array[d][s] which contains total num workers required to fully staff shift (incl track and skills)
    staffing_required_across_shifts = calc_staffing_requirement_across_shift(shiftd)
    # array[d][s][skill] which contains total num workers required to fully staff a skill
    skill_staffing_required_across_shifts = calc_skill_staffing_requirement_across_shift(shiftd, skilld)
    # float representing avg staff required for that skill
    avg_skill_staffing_required_across_shifts = np.mean(skill_staffing_required_across_shifts[:][:][:])
    # dev between skill staffing and avg
    deviations_skill_staffing_from_mean = calc_dev_skill_staffing_from_mean(skill_staffing_required_across_shifts,
                                                                            avg_skill_staffing_required_across_shifts)

    # array[s] which yields the chi^2 of that shift across each day
    shift_req_chi_square = calc_chi_square_shift_req(shiftd.shift_staffing_level_requirements, True)
    # array[d] which yields the chi^2 of each shift across a day
    day_req_chi_square = calc_chi_square_shift_req(shiftd.shift_staffing_level_requirements)

    workers_max_avail = wd.worker_max_shifts  # array[w] of each workers max amount of shifts they do
    # array[w][skill] of each workers skill penalty for a given skill
    workers_skill_penalties = calc_each_workers_skill_penalties(wd, skilld)

    # array[skill] of the average skill penalty for a given skill. < 0 indicates other workers incur less skill
    # penalties
    avg_skill_penalty = np.round(np.average(workers_skill_penalties, axis=0), 3)

    # array[d][s][skill]
    avg_skill_penalty_of_available_workers = calc_avg_skill_penalty_of_available_workers(available_workers,
                                                                                         workers_skill_penalties)
    # array[d][s][skill]
    min_skill_penalty_of_available_workers = calc_min_skill_penalty_of_available_workers(available_workers,
                                                                                         workers_skill_penalties)

    # array[d][s][skill]
    std_skill_penalty_of_available_workers = calc_std_skill_penalty_of_available_workers(available_workers,
                                                                                         workers_skill_penalties)
    # array[w][d][s][skill]
    dev_from_mean_worker_penalty = calc_dev_from_mean(avg_skill_penalty_of_available_workers, workers_skill_penalties,
                                                      std_skill_penalty_of_available_workers)

    # array[w] of each workers total amount of shifts they are available to work
    workers_total_available_shifts = calc_stat_worker_avail(np.sum, wd, shiftd.number_days)

    # array[w] of ratios. if <= 1, worker can be assigned to any amount of their available shifts
    available_shifts_less_than_max = np.where(workers_total_available_shifts <= workers_max_avail, True, False)
    #workers_available_shifts_to_max_shifts_ratio = np.divide(workers_total_available_shifts, workers_max_avail)
    #workers_available_shifts_to_max_shifts_ratio[np.isinf(workers_available_shifts_to_max_shifts_ratio)] = 0
    # workers_available_shifts_to_max_shifts_ratio = np.divide(workers_total_available_shifts, workers_max_avail,
    #                                                         out=np.zeros_like(workers_total_available_shifts),
    #                                                         where=workers_max_avail!=0)

    # int of total workers required to 100% fill all positions
    total_shifts_required_to_fill_roster = calc_stat_day_staffing_requirement(np.sum, shiftd, total_requirement=True)

    # int of avg shifts each worker needs to fill to 100% cover the schedule
    avg_shifts_required_per_worker = total_shifts_required_to_fill_roster / num_workers

    # array[w] of ratios. if <= 1, worker can be assigned to any amount of their available shifts
    avg_shifts_required_less_than_max = np.where(avg_shifts_required_per_worker <= workers_max_avail, True, False)
    #avg_shifts_required_per_worker_to_max_shifts_ratio = np.round(avg_shifts_required_per_worker / workers_max_avail)
    #avg_shifts_required_per_worker_to_max_shifts_ratio[np.isinf(avg_shifts_required_per_worker_to_max_shifts_ratio)] = 0
    # avg_shifts_required_per_worker_to_max_shifts_ratio = np.round(
    #    np.divide(avg_shifts_required_per_worker, workers_max_avail,
    #              out=np.zeros_like(avg_shifts_required_per_worker, dtype=float),
    #              where=workers_max_avail!=0), 3)

    # percentage representing max possible coverage that could be achieved
    max_possible_coverage = calc_total_possible_coverage(wd) / total_shifts_required_to_fill_roster

    # array[skill] represents num workers with skill
    overall_skill_rarity = calc_skill_rarity(wd, skilld) / num_workers

    total_worker_assignments = np.sum(shiftd.shift_staffing_level_requirements[:][:][:][:])

    # array[skill] represents number of worker-assignments required for a skill
    skill_staffing_demand = calc_skill_demand(shiftd, skilld)
    overall_skill_demand = skill_staffing_demand / total_worker_assignments

    # array[skill] with number of shifts workers with that skill are avail to do
    skill_availability = calc_skill_availability(wd, shiftd, skilld, available_workers)
    skill_scarcity = skill_availability / skill_staffing_demand

    # Add features
    rows = []
    for w, d, t, s, skill in np.ndindex((num_workers, num_days, num_tracks, num_shifts, num_skills)):
        data = {}
        data['index'] = str([w, d, t, s, skill])

        data['num_workers'] = num_workers
        data['num_days'] = num_days
        data['num_shifts'] = num_shifts
        data['num_tracks'] = num_tracks
        data['num_skills'] = num_skills

        data['staff_req_sparcity'] = staff_req_sparcity
        data['staff_avail_sparcity'] = staff_avail_sparcity

        data['avg_num_skills_of_each_worker'] = avg_num_skills_of_each_worker
        data['med_num_skills_of_each_worker'] = med_num_skills_of_each_worker
        data['chi_num_skills_of_each_worker'] = chi_num_skills_of_each_worker

        #data['num_available_workers'] = len(available_workers[d][s])
        #data['avg_num_available_workers'] = avg_available_workers
        #data['med_num_available_workers'] = np.median(len(available_workers[:][:]))
        #data['chi_num_available_workers'], _ = chisquare(len(available_workers[:][:]))


        data['worker_is_available'] = wd.worker_availability[w][d][s]
        data['worker_skill_penalty'] = workers_skill_penalties[w][skill]
        data['worker_max_avail'] = workers_max_avail[w]

        data['day_req_chi_value'] = day_req_chi_square[d]
        data['shift_req_chi_value'] = shift_req_chi_square[s]

        # diff my penalty vs the avg worker's penalty
        data['diff_avg_skill_penalty_and_worker_penalty'] = avg_skill_penalty[skill] - workers_skill_penalties[w][skill]
        # diff my penalty vs the avg available worker's penalty
        data['diff_avg_avail_w_skill_penalty_and_worker_penalty'] = avg_skill_penalty_of_available_workers[d][s][skill] \
                                                                    - workers_skill_penalties[w][skill]
        # is my penalty the min penalty
        data['worker_penalty_equals_min_penalty'] = min_skill_penalty_of_available_workers[d][s][skill] == \
                                                    workers_skill_penalties[w][skill]

        # num deviations of my skill penalty from the avg avail skill penalty
        data['worker_skill_penalty_num_dev_from_mean'] = dev_from_mean_worker_penalty[w][d][s][skill]

        data['local_skill_rarity'] = overall_skill_rarity[skill]  # todo make relative to avg rarity
        data['local_skill_demand'] = overall_skill_demand[skill]  # todo make relative to avg demand
        data['skill_scarcity'] = skill_scarcity[skill]

        # local_skill_scarcity

        data['staffing_req'] = shiftd.shift_staffing_level_requirements[d][t][s][
            skill]  # todo add comp to other skills in shift and shifts global demand
        data['diff_skill_staffing_and_avg_skill_staffing'] = skill_staffing_required_across_shifts[d][s][skill] - \
                                                             avg_skill_staffing_required_across_shifts
        data['deviations_skill_staffing_from_mean'] = deviations_skill_staffing_from_mean[d][s][skill]

        # data['staffing_req_across_shift'] = staffing_required_across_shifts[d][s]
        data['diff_available_workers_and_staffing_req_across_shifts'] = len(available_workers[d][s]) - \
                                                                        staffing_required_across_shifts[d][s]

        # avg shift avail vs. current shift avail
        data['diff_average_avail_workers_and_current_avail_workers'] = len(available_workers[d][s]) - \
                                                                       avg_available_workers
        data['deviations_current_avail_workers_from_avg'] = deviations_current_avail_workers_from_avg[d][s]

        data['max_possible_coverage'] = max_possible_coverage

        data['available_shifts_less_than_max'] = available_shifts_less_than_max[w]
        data['total_workers_required_to_fill_roster'] = total_shifts_required_to_fill_roster
        data['avg_shifts_required_less_than_max'] = avg_shifts_required_less_than_max[w]

        data['lpr_val'] = lpr_values[w][d][t][s][skill]

        if is_training_data:
            data['target'] = int(y[w][d][t][s][skill])

        rows.append(data)
    df = pd.DataFrame(rows)
    df = df.fillna(-1)
    pd.set_option('display.max_columns', None)
    return df


def calc_dev_from_mean(avg, actual, std):
    workers = actual.shape[0]
    days, shifts, skills = avg.shape
    dev_from_mean = np.zeros((workers, days, shifts, skills))

    for w, d, s, skill in np.ndindex((workers, days, shifts, skills)):
        diff, dev = actual[w][skill] - avg[d][s][skill], std[d][s][skill]
        dev_from_mean[w][d][s][skill] = np.round(np.divide(diff, dev, out=np.zeros_like(diff), where=dev != 0), 3)

    return dev_from_mean


def calc_each_workers_skill_penalties(wd, skilld):
    skills_penalties = np.zeros((wd.number_workers, skilld.number_skills), dtype=int)
    for w, s in np.ndindex((wd.number_workers, skilld.number_skills)):
        skills_penalties[w][s] = Penalties.calculate_skill_penalty(wd.worker_id_to_skill_map[w], s,
                                                                   skilld.skill_hierarchy)
    return skills_penalties


# Calculate mean/sum/stat operation on worker availability
def calc_stat_worker_avail(func, wd: WorkerData, num_days, per_day=False):
    num_workers = wd.number_workers
    if per_day:
        avail = np.zeros((num_workers, num_days))
        for w, d in np.ndindex(num_workers, num_days):
            avail[w][d] = round(func(wd.worker_availability[w][d]), 3)
        return avail
    else:
        avail = np.zeros(num_workers)
        for w, d in np.ndindex(num_workers, num_days):
            avail[w] += round(func(wd.worker_availability[w][d]), 3)
        return avail


def calc_stat_day_staffing_requirement(func, sd: ShiftData, total_requirement=False):
    if total_requirement:
        return round(func(sd.shift_staffing_level_requirements[:][:][:][:]), 3)
    else:
        requirements = np.zeros(sd.number_days)
        for d in range(sd.number_days):
            requirements[d] = round(func(sd.shift_staffing_level_requirements[d][:][:][:]), 3)
        return requirements


def calc_available_workers(wd, sd: ShiftData):
    num_workers = wd.number_workers
    num_days = sd.number_days
    num_shifts = sd.number_shifts

    available_workers = np.array([set() for _ in range(num_days * num_shifts)]).reshape(num_days, num_shifts)
    for w in range(num_workers):
        for d, s in np.ndindex(num_days, num_shifts):
            if wd.worker_availability[w][d][s] == 1:
                available_workers[d][s].add(w)

    return available_workers


def calc_avg_skill_penalty_of_available_workers(available_workers, workers_skill_penalties):
    num_workers, num_skills = workers_skill_penalties.shape
    num_days, num_shifts = available_workers.shape

    skill_penalty_of_available_workers = np.empty((num_days, num_shifts, num_skills))
    for d, s in np.ndindex(num_days, num_shifts):
        avail_workers = available_workers[d][s]
        for skill in range(num_skills):
            penalties = [workers_skill_penalties[w][skill] for w in avail_workers]
            skill_penalty_of_available_workers[d][s][skill] = np.round(np.mean(penalties), 3)

    return skill_penalty_of_available_workers


def calc_min_skill_penalty_of_available_workers(available_workers, workers_skill_penalties):
    num_workers, num_skills = workers_skill_penalties.shape
    num_days, num_shifts = available_workers.shape

    skill_penalty_of_available_workers = np.empty((num_days, num_shifts, num_skills))
    for d, s in np.ndindex(num_days, num_shifts):
        avail_workers = available_workers[d][s]
        for skill in range(num_skills):
            penalties = [workers_skill_penalties[w][skill] for w in avail_workers]
            skill_penalty_of_available_workers[d][s][skill] = np.round(np.min(penalties), 3)

    return skill_penalty_of_available_workers


def calc_std_skill_penalty_of_available_workers(available_workers, workers_skill_penalties):
    num_workers, num_skills = workers_skill_penalties.shape
    num_days, num_shifts = available_workers.shape

    skill_penalty_of_available_workers = np.empty((num_days, num_shifts, num_skills))
    for d, s in np.ndindex(num_days, num_shifts):
        avail_workers = available_workers[d][s]
        for skill in range(num_skills):
            penalties = [workers_skill_penalties[w][skill] for w in avail_workers]
            skill_penalty_of_available_workers[d][s][skill] = np.round(np.std(penalties), 3)

    return skill_penalty_of_available_workers


def calc_staffing_requirement_across_shift(sd: ShiftData):
    requirements = np.zeros((sd.number_days, sd.number_shifts), dtype=int)
    for d, s in np.ndindex(sd.number_days, sd.number_shifts):
        for t in range(sd.number_tracks):
            requirements[d][s] += sum(sd.shift_staffing_level_requirements[d][t][s][:])
    return requirements


def calc_skill_staffing_requirement_across_shift(sd: ShiftData, sk: SkillData):
    requirements = np.zeros((sd.number_days, sd.number_shifts, sk.number_skills), dtype=int)
    for d, s, t, skill in np.ndindex(sd.number_days, sd.number_shifts, sd.number_tracks, sk.number_skills):
        requirements[d][s][skill] += sd.shift_staffing_level_requirements[d][t][s][skill]
    return requirements


def calc_total_possible_coverage(wd):
    total_coverage = 0
    for w in range(wd.number_workers):
        total_coverage += min(np.sum(wd.worker_availability[w][:][:]), wd.worker_max_shifts[w])
    return total_coverage


def calc_lpr_values(input_file_path):
    input_file_name = os.path.basename(input_file_path)
    file_path = os.path.dirname(input_file_path)

    regex_pattern = re.sub(r'-[0-9]-mip.json', "-[0-9]-lpr.json", input_file_name)
    files = [f for f in os.listdir(file_path) if re.match(regex_pattern, f)]

    lpr_assignments = []
    for file in files:
        full_file_path = file_path + '/' + file
        lpr_dict = decoder.json_to_dict(full_file_path)
        lpr_roster = decoder.decode_roster(lpr_dict)
        lpr_y = np.array(lpr_roster.worker_assignment)
        lpr_assignments.append(lpr_y)

    num_lpr_assignments = len(lpr_assignments)
    avg_lpr_assignment_value = np.zeros(lpr_y.shape)
    median_lpr_assignment_value = np.zeros(lpr_y.shape)

    lpr_target_values = np.zeros(lpr_y.shape)

    for w, d, t, s, skill in np.ndindex(lpr_y.shape):
        tmp_assignment_values = [assignments[w][d][t][s][skill] for assignments in lpr_assignments]
        avg_lpr_assignment_value[w][d][t][s][skill] = np.mean(tmp_assignment_values)
        median_lpr_assignment_value[w][d][t][s][skill] = np.median(tmp_assignment_values)

    return {'num_lpr_assignments': num_lpr_assignments, 'avg_lpr_assignment_value': avg_lpr_assignment_value,
            'median_lpr_assignment_value': median_lpr_assignment_value}


def get_lpr_target_values(input_file_path):
    input_file_name = os.path.basename(input_file_path)
    file_path = os.path.dirname(input_file_path)

    regex_pattern = re.sub(r'-[0-9]-mip.json', "-0-lpr.json", input_file_name)
    #regex_pattern = re.sub(r'_[0-9]*-', r'\g<0>0-', regex_pattern)  # todo is this important?
    lpr_file_name = [f for f in os.listdir(file_path) if re.match(regex_pattern, f)]

    full_file_path = file_path + '/' + lpr_file_name[0]
    lpr_dict = decoder.json_to_dict(full_file_path)
    lpr_roster = decoder.decode_roster(lpr_dict)
    lpr_y = np.array(lpr_roster.worker_assignment)

    return lpr_y


def calc_skill_rarity(wd: WorkerData, skilld):
    skill_counter = np.zeros(skilld.number_skills)
    for w in range(wd.number_workers):
        for skill in wd.worker_id_to_skill_map[w]:
            skill_counter[skill] += 1

    return skill_counter


def calc_skill_demand(shiftd, skilld):
    skill_counter = np.zeros(skilld.number_skills)
    for d, t, s, in np.ndindex((shiftd.number_days, shiftd.number_tracks, shiftd.number_shifts)):
        for skill in range(skilld.number_skills):
            skill_counter[skill] += shiftd.shift_staffing_level_requirements[d][t][s][skill]

    return skill_counter


def build_skill_to_worker_set_map(wd: WorkerData, sk: SkillData):
    skill_to_worker_map = {skill: set() for skill in range(sk.number_skills)}
    for w in range(wd.number_workers):
        for skill in wd.worker_id_to_skill_map[w]:
            skill_to_worker_map[skill].add(w)

    return skill_to_worker_map


def calc_skill_availability(wd: WorkerData, sd: ShiftData, sk: SkillData, available_workers):
    skill_scarcity = np.zeros(sk.number_skills)
    skill_to_worker_map = build_skill_to_worker_set_map(wd, sk)
    # map skill to set of people
    # for avail workers; for skill
    #   count size of intersection

    for d, s in np.ndindex((sd.number_days, sd.number_shifts)):
        avail_workers_set = available_workers[d][s]
        for skill in range(sk.number_skills):
            workers_with_skill = skill_to_worker_map[skill]
            skill_scarcity[skill] += len(avail_workers_set.intersection(workers_with_skill))

    return skill_scarcity


def calc_dev_availability_from_mean(available_workers, avg_available_workers):
    days, shifts = available_workers.shape
    dev_from_mean = np.zeros((days, shifts))

    shift_availabilities = []
    for d, s in np.ndindex((days, shifts)):
        shift_availabilities.append(len(available_workers[d][s]))

    dev = np.std(shift_availabilities)
    for d, s in np.ndindex((days, shifts)):
        diff = len(available_workers[d][s]) - avg_available_workers
        dev_from_mean[d][s] = np.round(np.divide(diff, dev, out=np.zeros_like(diff), where=dev != 0), 3)

    return dev_from_mean


def calc_dev_skill_staffing_from_mean(skill_staffing_required_across_shifts, avg):
    dev_from_mean = np.zeros(skill_staffing_required_across_shifts.shape)

    shift_availabilities = []
    for d, s, skill in np.ndindex(skill_staffing_required_across_shifts.shape):
        shift_availabilities.append(skill_staffing_required_across_shifts[d][s][skill])

    dev_1 = np.std(shift_availabilities)
    dev = np.std(skill_staffing_required_across_shifts[:][:][:])

    for d, s, skill in np.ndindex(skill_staffing_required_across_shifts.shape):
        diff = skill_staffing_required_across_shifts[d][s][skill] - avg
        dev_from_mean[d][s][skill] = np.round(np.divide(diff, dev, out=np.zeros_like(diff), where=dev != 0), 3)

    return dev_from_mean


def calc_chi_square_shift_req(staffing_req, transpose=False):
    if type(staffing_req) != np.ndarray:
        staffing_req = np.array(staffing_req)

    d, t, s, skill = staffing_req.shape
    req_without_track = np.sum(staffing_req, axis=1)
    flat_req = req_without_track.flatten('C')

    shift_skill_req = flat_req.reshape((-1, skill))
    flat_shift_req = np.sum(shift_skill_req, axis=1)
    day_shift_req = flat_shift_req.reshape((-1, d))

    if transpose:
        chi_square_values, p = chisquare(day_shift_req.T)
    else:
        chi_square_values, p = chisquare(day_shift_req)
    return chi_square_values
