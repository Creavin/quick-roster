import os
import json
import re
import shutil
from time import perf_counter
import extract_meta_data_helper
from gurobipy import GRB

from NspSolver.Scheduler import Scheduler
from NspUtils.ScheduleJsonDecoder import ScheduleJsonDecoder


def solve_schedules(input_dir, output_dir, node_limit=None):
    previously_solved_schedules = get_previously_solved_schedules(output_dir)
    for file in os.listdir(output_dir):
        schedule_name = re.sub(r"(-[\d*]-mip)|(-[\d*]-lpr)", "", file)
        if file != schedule_name:  # i.e don't include raw schedule in solved schedules
            previously_solved_schedules.add(schedule_name)

    print(previously_solved_schedules)

    for file in os.listdir(input_dir):
        if file not in previously_solved_schedules:
            solve(input_dir + '/' + file, output_dir, node_limit=node_limit, lpr=False)
            solve(input_dir + '/' + file, output_dir, node_limit=node_limit, lpr=True)


def solve_hard_schedules(input_dir, output_dir):
    previously_solved_schedules = get_previously_solved_schedules(output_dir)
    hard_schedules = {}

    for file in os.listdir(input_dir):
        status = extract_meta_data_helper.extract_gurobi_status(input_dir + '/' + file)
        if str(status) == str(GRB.NODE_LIMIT):  # todo change to int
            schedule_name = re.sub(r"(-[\d*]-mip)|(-[\d*]-lpr)", "", file)
            hard_schedules[schedule_name] = file
        # get schedule and write to file

    print(hard_schedules)
    print("Num hard schedules:", len(hard_schedules))

    for schedule_name, file in hard_schedules.items():
        print("File: ", file)
        if schedule_name not in previously_solved_schedules:
            solve(input_dir + '/' + file, output_dir, node_limit=None, lpr=False, is_roster=True)
            solve(input_dir + '/' + file, output_dir, node_limit=None, lpr=True, is_roster=True)
        else:
            print("Already solved", file)


def solve(input_file, output_dir, node_limit=None, lpr=False, is_roster=False):
    print("[INFO] parsing file: ", input_file)
    print("[INFO] lpr: ", lpr)
    with open(input_file) as schedule_data:
        schedule_json_str = schedule_data.read()
        schedule_json = json.loads(schedule_json_str)
        schedule = ScheduleJsonDecoder.decode_schedule(schedule_json)
        if is_roster:
            input_file = re.sub(r"(-[\d*]-mip)|(-[\d*]-lpr)", "", input_file)  # todo / warning: Dangerous mutation


    process_start_time = perf_counter()
    print("[INFO] scheduling file: ", input_file)
    rosters = Scheduler().schedule(schedule, lpr=lpr, node_limit=node_limit)
    print(f"[INFO] {len(rosters)} rosters created: ")

    for index, roster in enumerate(rosters):
        if lpr:
            file_name = os.path.basename(input_file).split('.')[0] + f"-{index}-lpr.json"
        else:
            file_name = os.path.basename(input_file).split('.')[0] + f"-{index}-mip.json"

        with open(f"{output_dir}/{file_name}", 'w', encoding='utf-8') as output_file:
            json.dump(roster.to_dict(), output_file, sort_keys=True, indent=4)


    process_end_time = perf_counter()
    gurobi_run_time = process_end_time - process_start_time
    print("[INFO] Elapsed time: ", gurobi_run_time)

def get_previously_solved_schedules(output_dir):
    previously_solved_schedules_lpr = set()
    previously_solved_schedules_mip = set()
    for file in os.listdir(output_dir):
        schedule_name = re.sub(r"(-[\d*]-mip)", "", file)
        if file != schedule_name:  # i.e don't include raw schedule in solved schedules
            previously_solved_schedules_mip.add(schedule_name)

        schedule_name = re.sub(r"(-[\d*]-lpr)", "", file)
        if file != schedule_name:  # i.e don't include raw schedule in solved schedules
            previously_solved_schedules_lpr.add(schedule_name)

    return previously_solved_schedules_lpr.intersection(previously_solved_schedules_mip)

