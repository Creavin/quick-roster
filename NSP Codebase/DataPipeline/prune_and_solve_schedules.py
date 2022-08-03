import os
import re
import json

from sklearn.metrics import confusion_matrix

import pipeline_constants as const
import NspUtils.RosterLabeler as Labeler
import numpy as np
import pandas as pd

from time import perf_counter
from NspUtils.ScheduleJsonDecoder import ScheduleJsonDecoder
from sklearn import preprocessing
from joblib import load
from NspSolver.Scheduler import Scheduler


def prune_solve_schedules(model_name, input_dir, output_dir, threshold=0.9):
    data = []
    for file in os.listdir(input_dir):
        #if re.match('.*-0-mip.*', file):  # only solve one of the mips
        if re.match('.*json', file):  # only solve one of the mips
             data += prune_solve(model_name, input_dir + '/' + file, output_dir, threshold)
            # prune_solve(model_name, input_dir + '/' + file, output_dir, threshold)  todo tmp delete
            #data.append(prune_solve(model_name, input_dir + '/' + file, output_dir, threshold))
    print(data)
    #df = pd.DataFrame.from_records(data)
    #print(df)
    #df.to_csv(f"{const.RESULTS_DIR}/eval_solve_results.csv")

def prune_solve(model_name, input_file, output_dir, threshold=0.90):
    print("[INFO] parsing file: ", input_file)
    with open(input_file) as schedule_data:
        schedule_json_str = schedule_data.read()
        schedule_json = json.loads(schedule_json_str)
        schedule = ScheduleJsonDecoder.decode_schedule(schedule_json)

    print("[INFO] scheduling file: ", input_file)

    lpr_roster = Scheduler().schedule(schedule, lpr=True)[0]
    assert lpr_roster != None

    df = Labeler.label(lpr_roster, is_training_data=False)
    # todo put back old ml comps
    #scaler: preprocessing.StandardScaler = load(f'{const.ML_COMP}/scaler.joblib')
    #model = load(f'{const.ML_COMP}/{model_name}.joblib')

    # todo remove these comp is no good
    scaler: preprocessing.StandardScaler = load(f'{const.ML_COMP}/scaler_v2.joblib')
    model = load(f'{const.ML_COMP}/{model_name}_v2.joblib')

    X = preprocess_data(df)
    X = scaler.transform(X)

    worker_assignment_shape = (schedule.worker_data.number_workers,
                               schedule.shift_data.number_days,
                               schedule.shift_data.number_tracks,
                               schedule.shift_data.number_shifts,
                               schedule.skill_data.number_skills)

    y_pred_p = model.predict_proba(X)
    #threshold = calc_threshold(y_pred_p, worker_assignment_shape, schedule)

    y_pred_0 = np.where(y_pred_p[:,0] < threshold, 0, y_pred_p[:,0])
    y_pred_1 = y_pred_p[:,1]
    y_pred = np.where(y_pred_0 > y_pred_1, 0, 1)

    worker_assignment = np.reshape(y_pred, worker_assignment_shape)

    prune = calc_prune(worker_assignment_shape, y_pred)
    max_pruning = calc_max_prune(worker_assignment_shape, schedule)

    print("Prune:", prune)
    print("Max prune:", max_pruning)

    if threshold == 1.0:
        worker_assignment = np.ones(worker_assignment_shape)
    mip_rosters = Scheduler().schedule(schedule=schedule, lpr=False, pruned_assignment=worker_assignment,
                                       node_limit=None)

    for index, roster in enumerate(mip_rosters):
        file_name = os.path.basename(input_file).split('.')[0] + f"-{index}-pmip.json"
        with open(f"{output_dir}/{file_name}", 'w', encoding='utf-8') as output_file:
            json.dump(roster.to_dict(), output_file, sort_keys=True, indent=4)

    data = []
    for roster in mip_rosters:
        y = np.round(roster.worker_assignment.flatten(order='C'))
        slack = roster.grb_vars['total_slack']
        skill = roster.grb_vars['total_skill_penalty']
        obj = skill + 5 * slack
        data.append({"uuid": schedule.uuid, "q": threshold, "prune": prune, "fnr": calc_fnr(y, y_pred),
                 "max_prune": max_pruning, "obj": obj})
    return data

def calc_fnr(y, y_pred):
    cm = confusion_matrix(y, y_pred)
    print(cm)
    return false_negative_rate(cm)

def false_negative_rate(cm):
    return round(cm[1][0] / (cm[1][0] + cm[1][1]), 3)

def calc_prune(worker_assignment_shape, y_pred):
    size = np.product(worker_assignment_shape)
    sum = np.sum(y_pred)
    prune_pc = (size - sum) / size
    return prune_pc


def calc_threshold(y_pred_p, worker_assignment_shape, schedule):
    y_pred_0 = y_pred_p[:,0]
    size = np.product(worker_assignment_shape)
    total_required = min(np.sum(schedule.worker_data.worker_availability),
                         np.sum(schedule.shift_data.shift_staffing_level_requirements[:][:][:][:]))
    max_prune = size - total_required
    prune_after = int(max_prune - 1.5*total_required)
    if prune_after < 0:
        prune_after = int(size*((max_prune/size)*(max_prune/size)))
    sorted_prob_assignments = sorted(y_pred_0, reverse=True)
    threshold = sorted_prob_assignments[prune_after]
    return threshold

def calc_max_prune(worker_assignment_shape, schedule):
    size = np.product(worker_assignment_shape)
    total_required = min(np.sum(schedule.worker_data.worker_availability),
                         np.sum(schedule.shift_data.shift_staffing_level_requirements[:][:][:][:]))
    max_prune = size - total_required
    return max_prune/size

def pop_features(df, features):
    for feat in features:
        df.pop(feat)

def preprocess_data(df):
    print(df.shape)
    # todo put this back
    #remove_features = ['index',
    #                   "med_num_skills_of_each_worker", "avg_num_skills_of_each_worker",
    #                   "chi_num_skills_of_each_worker",
    #                   "diff_avg_skill_penalty_and_worker_penalty",
    #                   "local_skill_demand",
    #                   "deviations_skill_staffing_from_mean",
    #                   "num_days", 'num_workers', "staff_req_sparcity", "skill_scarcity"
    #                   ]

    # todo tmp feature removal
    remove_features = ['index',
                   "med_num_skills_of_each_worker", "avg_num_skills_of_each_worker",
                   "chi_num_skills_of_each_worker",
                   "diff_avg_skill_penalty_and_worker_penalty",
                   "local_skill_demand",
                   "deviations_skill_staffing_from_mean",
                   "num_days", 'num_workers', "staff_req_sparcity", "skill_scarcity"
                   ]
    remove_features += ["max_possible_coverage",
                    "local_skill_rarity",
                    "total_workers_required_to_fill_roster",
                    "num_skills",
                    "num_shifts",
                    "avg_shifts_required_less_than_max",
                    "worker_is_available"]

    remove_features += [
        "num_tracks",
        "diff_skill_staffing_and_avg_skill_staffing",
        "worker_skill_penalty_num_dev_from_mean",
        "staffing_req",
        "diff_available_workers_and_staffing_req_across_shifts"]

    pop_features(df, remove_features)
    X = df.values
    return X



def prune_schedules(model_name, input_dir):
    prune_rates = []
    for file in os.listdir(input_dir):
        if re.match('.*-0-mip.*', file):  # only solve one of the mips
            try:
                prune_rates.append(prune_schedule(model_name, input_dir + '/' + file))
            except:
                print(f"An error occured when prune solving {file}")
    print(prune_rates)
    print(np.average(np.array(prune_rates)))


def prune_schedule(model_name, input_file, threshold=0.99):
    print("[INFO] parsing file: ", input_file)
    with open(input_file) as schedule_data:
        schedule_json_str = schedule_data.read()
        schedule_json = json.loads(schedule_json_str)
        schedule = ScheduleJsonDecoder.decode_schedule(schedule_json)


    lpr_roster = Scheduler().schedule(schedule, lpr=True)[0]
    assert lpr_roster != None

    df = Labeler.label(lpr_roster, is_training_data=False)
    scaler: preprocessing.StandardScaler = load(f'{const.ML_COMP}/scaler.joblib')
    model = load(f'{const.ML_COMP}/{model_name}.joblib')

    X = preprocess_data(df)
    X = scaler.transform(X)

    worker_assignment_shape = (schedule.worker_data.number_workers,
                               schedule.shift_data.number_days,
                               schedule.shift_data.number_tracks,
                               schedule.shift_data.number_shifts,
                               schedule.skill_data.number_skills)

    size = np.product(worker_assignment_shape)
    #total_required = np.sum(schedule.shift_data.shift_staffing_level_requirements[:][:][:][:])
    total_required = min(np.sum(schedule.worker_data.worker_availability),
                         np.sum(schedule.shift_data.shift_staffing_level_requirements[:][:][:][:]))
    max_prune = size - total_required
    prune_after = int(max_prune - 1.5*total_required)
    if prune_after < 0:
        prune_after = int(size*((max_prune/size)*(max_prune/size)))

    y_pred_p = model.predict_proba(X)
    y_pred_0 = y_pred_p[:,0]
    sorted_prob_assignments = sorted(y_pred_0, reverse=True)
    prob_cut_off = sorted_prob_assignments[prune_after]
    print(prob_cut_off)

    y_pred_0 = np.where(y_pred_p[:,0] < prob_cut_off, 0, y_pred_p[:,0])
    y_pred_1 = y_pred_p[:,1]

    y_pred = np.where(y_pred_0 > y_pred_1, 0, 1)

    worker_assignment = np.reshape(y_pred, worker_assignment_shape)

    size = np.product(worker_assignment.shape)
    sum = np.sum(y_pred)
    prune_pc = (size - sum) / size

    print("\n\nPrune percentage:", prune_pc)
    return prune_pc

