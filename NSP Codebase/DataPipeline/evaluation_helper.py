import os
import re
import json
import pandas as pd

from sklearn.metrics import confusion_matrix

import NspUtils.RosterLabeler as Labeler
import numpy as np
import pipeline_constants as const

from time import perf_counter
from NspUtils.ScheduleJsonDecoder import ScheduleJsonDecoder
from NspUtils.RosterJsonDecoder import RosterJsonDecoder
from sklearn import preprocessing
from joblib import load
from NspSolver.Scheduler import Scheduler


def evaluate_rosters(model_name, input_dir, threshold_range):
    data = []
    for file in os.listdir(input_dir):
        if re.match('.*-mip.*', file):  # only solve one of the mips
            data += prune_schedule(model_name, input_dir + '/' + file, threshold_range)
    df = pd.DataFrame.from_records(data)
    print(df)
    df.to_csv(f"{const.RESULTS_DIR}/eval_results.csv")


def prune_schedule(model_name, input_file, threshold_range):
    print("[INFO] parsing file: ", input_file)
    with open(input_file) as roster_data:
        roster_json_str = roster_data.read()
        roster_json = json.loads(roster_json_str)
        roster = RosterJsonDecoder.decode_roster(roster_json)
        schedule = roster.get_schedule()


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


    y_pred_p = model.predict_proba(X)
    #threshold = calc_threshold(y_pred_p, worker_assignment_shape, schedule)

    data = []
    for threshold in threshold_range:
        y_pred_0 = np.where(y_pred_p[:,0] < threshold, 0, y_pred_p[:,0])
        y_pred_1 = y_pred_p[:,1]

        y_pred = np.where(y_pred_0 > y_pred_1, 0, 1)
        worker_assignment = np.reshape(y_pred, worker_assignment_shape)
        y = np.round(np.array(roster.worker_assignment).flatten(order='C'))

        fnr = calc_fnr(y, y_pred)
        prune = calc_prune(y, y_pred)
        max_pruning = max_prune(y)
        print("FNR:", fnr)
        print("Prune:", prune)
        print("Max prune:", max_pruning)

        data.append({"uuid": schedule.uuid, "q": threshold, "prune": prune, "fnr": fnr, "max_prune": max_pruning})
    return data

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


def pop_features(df, features):
    for feat in features:
        df.pop(feat)

def preprocess_data(df):
    print(df.shape)
    remove_features = ['index',
                   "med_num_skills_of_each_worker", "avg_num_skills_of_each_worker",
                   "chi_num_skills_of_each_worker",
                   "diff_avg_skill_penalty_and_worker_penalty",
                   "local_skill_demand",
                   "deviations_skill_staffing_from_mean",
                   "num_days", 'num_workers', "staff_req_sparcity", "skill_scarcity"
                   ]
    pop_features(df, remove_features)
    X = df.values
    return X


def calc_fnr(y, y_pred):
    cm = confusion_matrix(y, y_pred)
    print(cm)
    return false_negative_rate(cm)

def calc_prune(y, y_pred):
    cm = confusion_matrix(y, y_pred)
    return prune_percentage(cm)

def prune_percentage(cm):
    return round( (cm[0][0] + cm[1][0]) / (np.sum(cm[:])), 3)

def false_negative_rate(cm):
    return round(cm[1][0] / (cm[1][0] + cm[1][1]), 3)

def max_prune(y):
    size = len(y)
    total_required = np.sum(y)
    max_prune = size - total_required
    return max_prune/size

#evaluate_rosters("sgd", f"{const.ROOT}/tmp", np.arange(0.5,1.0,.05))
evaluate_rosters("sgd", f"{const.SOLVED_ROSTERS}", np.arange(0.5,1.0,.05))
