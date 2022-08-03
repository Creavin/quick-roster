from NspUtils.ScheduleJsonDecoder import ScheduleJsonDecoder
import json
import random
import csv
import uuid
import numpy as np
from scipy.stats import norm
from scipy.stats import bernoulli
from numpy.random import lognormal


DEFAULT_OUTPUT_FILE = "./output"
days = ["mon", "tue", "wed", "thur", "fri", "sat", "sun"]
skill_names = ["Trainee Nurse", "Nurse", "Surgeon", "Supervisor", "Assistant to the Manager", "Manager"]
names_file_path = '/home/thomas/Dropbox/FYP/FypCodebase/NspDataProducers/datasets/names.csv'

def generate_data(num_workers, num_days, num_shifts, num_tracks, num_skills, mean_availability=.9, 
                    mean_staffing_requirement=0.5, output_dir=DEFAULT_OUTPUT_FILE):
    num_skills = max(1, num_skills)

    worker_dict = generate_worker_data(num_workers, num_days, num_shifts, num_skills, mean_availability)
    shift_dict = generate_shift_data(num_workers, num_days, num_tracks, num_shifts, num_skills, mean_staffing_requirement)
    skill_dict = generate_skill_data(num_skills)
    id = str(uuid.uuid4())

    schedule_type = f"{num_workers}-{num_days}-{num_shifts}-{num_tracks}-{num_skills}-{mean_availability}"
    meta_data = {"schedule_type": schedule_type}
    data = {"uuid": id, "worker_data": worker_dict, "shift_data": shift_dict, "skill_data": skill_dict,
            "meta_data": meta_data}

    output_file = f"{output_dir}/{id}.json"
    with open(output_file, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, sort_keys=True, indent=4)

    return data


def generate_worker_data(num_workers, num_days, num_shifts, num_skills, worker_shift_availability_bernoulli_mean):
    worker_data_dict = {"__worker_data__": True}

    # set worker names
    with open('/home/thomas/Dropbox/FYP/FypCodebase/NspDataProducers/datasets/names.csv') as namesfile:
        reader = csv.reader(namesfile)
        names = [r[0] for r in reader]

    worker_names = []
    for w in range(num_workers):
        n = random.randint(0, 500)
        worker_names.append(names[n])
    worker_data_dict["worker_names"] = worker_names

    # set max hours for each worker
    total_shifts = num_days * num_shifts
    worker_max_hours_float = np.full((w+1), total_shifts) - (lognormal(0.1*num_shifts, 0.5, w+1))

    worker_max_hours = [int(abs(i)) for i in worker_max_hours_float]
    worker_data_dict["worker_max_shifts"] = worker_max_hours

    # set worker skills
    worker_skills = {}
    for w in range(num_workers):
        #skills = random.randint(0, num_skills-1)
        skills = w % num_skills
        worker_skills[str(w)] = [skills]
    worker_data_dict["worker_id_to_skill_map"] = worker_skills

    # worker availability
    availability = np.zeros((num_workers, num_days, num_shifts), dtype=int)
    for w in range(num_workers):
        for d in range(num_days):
            availability[w][d] = bernoulli(worker_shift_availability_bernoulli_mean).rvs(num_shifts)

    # set worker availability
    worker_data_dict["worker_availability"] = availability.tolist()

    return worker_data_dict


def generate_shift_data(num_workers, num_days, num_tracks, num_shifts, num_skills, mean_staffing_requirement):
    shift_data_dict = {"__shift_data__": True}
    day_names = []
    for day in range(num_days):
        day_names.append(days[day % 7] + "." + str(day))
    shift_data_dict['day_names'] = day_names

    shift_names = []
    for shift in range(num_shifts):
        shift_names.append("shift." + str(shift))
    shift_data_dict['shift_names'] = shift_names

    track_names = []
    for track in range(num_tracks):
        track_names.append("track." + str(track))
    shift_data_dict['track_names'] = track_names

    # Set shift staffing requirements
    req_shape = (num_days, num_tracks, num_shifts, num_skills)
    shift_requirements = np.zeros((num_days, num_tracks, num_shifts, num_skills), dtype=int)
    total_shifts_per_day = num_tracks * num_shifts
    mean = (num_workers * mean_staffing_requirement) / (num_skills * num_tracks)
    req = np.round(norm(mean).rvs(size=np.product(req_shape)))  # req per skill
    req = req.reshape(req_shape)
    #for d in range(num_days):
    #    for t in range(num_tracks):
    #        for s in range(num_shifts):
    #             
    #            #requirements_float = (norm(total_shifts_per_day/(num_skills*num_tracks*num_workers)).rvs(size=num_skills))
    #            #requirements_float = (norm(num_workers/(num_skills*num_tracks)/4).rvs(size=num_skills))
    #            
    #            requirements = [int(abs(i)) for i in requirements_float]
    #            shift_requirements[d][t][s] = requirements
    shift_data_dict["shift_staffing_level_requirements"] = req.tolist()

    return shift_data_dict


def generate_skill_data(num_skills):
    skill_data_dict = {"__skill_data__": True}

    skill_id_to_name_map = {}
    for skills in range(num_skills):
        skill_id_to_name_map[str(skills + 1)] = skill_names[skills % len(skill_names)] + "." + str(skills + 1)
    skill_data_dict['skill_id_to_name_map'] = skill_id_to_name_map

    # todo un-hardcode this
    skill_hierarchy = {
      "0": [["1", "MINOR_PENALTY"]],
      "1": [["2", "MAJOR_PENALTY"]],
      "2": [["3", "MINOR_PENALTY"], ["4", "MAJOR_PENALTY"]],
      "3": [["4", "MINOR_PENALTY"]]
    }
    skill_data_dict['skill_hierarchy'] = skill_hierarchy

    return skill_data_dict


if __name__ == '__main__':
    num_workers = 5
    num_days = 5
    num_shifts = 10
    num_tracks = 2
    num_skills = 4

    generate_data(num_workers, num_days, num_shifts, num_tracks, num_skills)
    decoder = ScheduleJsonDecoder

    with open(DEFAULT_OUTPUT_FILE) as mixed_data:
        schedule_json_str = mixed_data.read()
        schedule_json = json.loads(schedule_json_str)
        worker_data, shift_data, skill_data = decoder.decode_schedule_data(schedule_json)
        id = decoder.get_uuid(schedule_json)
        print(id)
        print(type(worker_data))
        print(type(shift_data))
        print(type(skill_data))

#    "__shift_data__": true,
#    "day_names": ["Monday", "Tuesday"],
#    "shift_names": ["9", "10", "11", "12", "13", "14", "15", "16"],
#    "track_names": ["RoomA", "RoomB"],
#    "shift_staffing_level_requirements": [
#      [[1, 1, 0, 2, 1, 0, 0, 1], [1, 1, 0, 0, 0, 0, 2, 0]],
#      [[1, 1, 0, 2, 1, 0, 0, 1], [1, 1, 0, 0, 0, 0, 2, 0]]],
#    "shift_skill_requirements": [
#
