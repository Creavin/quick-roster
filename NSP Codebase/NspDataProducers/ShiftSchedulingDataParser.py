import re
import random
import numpy as np
from NspDataProducers.TimePeriod import TimePeriod
from NspObjects.ShiftData import ShiftData
from NspObjects.SkillData import SkillData
from NspObjects.WorkerData import WorkerData

SHIFT_DURATION = 15
DAY_NAMES = ["mon", "tue", "wed", "thur", "fri", "sat", "sun"]


class ShiftSchedulingBenchmarkParser:
    def __init__(self, file_path, rest_period=False):
        self.file_path = file_path
        self.num_days = self.parse_num_days()
        self.num_tasks = self.parse_num_tasks()
        self.num_shifts = int(24 * (60 / SHIFT_DURATION))
        self.shift_info_map = self.parse_shift_info()
        self.worker_info = self.parse_staff_info()
        self.num_workers = len(self.worker_info.items())
        self.rest_period = rest_period

    def create_shift_data(self):
        day_names = []
        shift_times = []
        task_names = []

        for day_id in range(self.num_days):
            day_names.append(f"{DAY_NAMES[day_id % 7]}_{day_id}")

        for shift_time in range(self.num_shifts):
            time = self.minutes_to_hh_mm(shift_time * 15)
            shift_times.append(time)

        for task_id in range(self.num_tasks):
            task_names.append(task_id)

        shift_staffing_level_requirements = np.zeros((self.num_days, self.num_tasks, self.num_shifts, 1), dtype=int)
        for day_id, shift_info in self.shift_info_map.items():
            for entry in shift_info:
                shift_index = entry["time_period"].periods_since_midnight
                required_avail = (entry["max_staff"] - entry["min_staff"]) / 2 + entry["min_staff"]
                shift_staffing_level_requirements[day_id][entry["task_id"]][shift_index][0] = required_avail

        return ShiftData(day_names, shift_times, task_names, shift_staffing_level_requirements)

    def minutes_to_hh_mm(self, minutes):
        hours = int(minutes / 60)
        remaining_minutes = minutes - hours * 60

        hours_str = str(hours).zfill(2)
        remaining_minutes_str = str(remaining_minutes).zfill(2)
        return f"{hours_str}:{remaining_minutes_str}"

    def create_worker_data(self):
        worker_names = []
        worker_max_shifts = []
        worker_id_to_skill_map = {}

        for id, info in self.worker_info.items():
            worker_names.append(f"worker_{id}")
            worker_max_shifts.append(int(info["max_total_minutes"] / SHIFT_DURATION))

        # init same avail and skills for everyone
        if not self.rest_period:
            worker_availability = np.full((self.num_workers, self.num_days, self.num_shifts), 1)
        else:
            worker_availability = np.zeros((self.num_workers, self.num_days, self.num_shifts))
            worker_shift_start_ids = np.zeros((self.num_workers, self.num_days), dtype=int)

            # Set each worker's start shift id
            worker_spacing = round(self.num_shifts / self.num_workers)
            for w in range(self.num_workers):
                starting_shift_id = random.randint(0, self.num_shifts - 1)
                for d in range(self.num_days):
                    worker_shift_start_ids[w][d] = w * worker_spacing

            work_period = int(self.num_shifts * (13 / 24))

            # Mark workers available for 13 hrs after their start shift
            for w in range(self.num_workers):
                for d in range(self.num_days):
                    if worker_shift_start_ids[w][d] + (work_period - 1) < self.num_shifts:
                        for s in range(work_period):
                            worker_availability[w][d][worker_shift_start_ids[w][d] + s] = 1
                    else:
                        shift_counter = 0
                        while worker_shift_start_ids[w][d] + shift_counter < self.num_shifts:
                            worker_availability[w][d][worker_shift_start_ids[w][d] + shift_counter] = 1
                            shift_counter += 1

                        if d < self.num_days - 2:
                            remaining_shifts = work_period - shift_counter
                            for shift_id in range(remaining_shifts):
                                worker_availability[w][d + 1][shift_id] = 1

        for worker_id in range(self.num_workers):
            worker_id_to_skill_map[worker_id] = [0]

        return WorkerData(worker_names, worker_availability, worker_max_shifts, worker_id_to_skill_map)

    def create_skill_data(self):
        skill_id_to_name_map = {0: "Standard"}
        skill_hierarchy = {0: []}
        return SkillData(skill_id_to_name_map, skill_hierarchy)

    def parse_num_days(self):
        with open(self.file_path, "r") as file:
            days_pattern = "days"
            days_on_next_line = False

            for line in file:
                if days_on_next_line:
                    days_on_next_line = False
                    number_days = int(line)

                if re.search(days_pattern, line):
                    days_on_next_line = True

        return number_days + 1

    def parse_num_tasks(self):
        with open(self.file_path, "r") as file:
            tasks_pattern = "tasks$"
            tasks_on_next_line = False

            for line in file:
                if tasks_on_next_line:
                    tasks_on_next_line = False
                    number_tasks = int(line)

                if re.search(tasks_pattern, line):
                    tasks_on_next_line = True

        return number_tasks

    def parse_staff_info(self):
        with open(self.file_path, "r") as file:
            staff_pattern = "# ID, MinTotalMinutes, MaxTotalMinutes"
            staff_on_next_line = False
            staff_info = {}

            for line in file:
                if re.search(staff_pattern, line):
                    staff_on_next_line = True
                    break

            if staff_on_next_line:
                for line in file:
                    if not re.search("^\s", line):
                        split_line = line.split(",")
                        staff_info[int(split_line[0]) - 1] = {"min_total_minutes": int(split_line[1]),
                                                              "max_total_minutes": int(split_line[2])}
                    else:
                        break

        return staff_info

    def parse_shift_info(self):
        with open(self.file_path, "r") as file:
            shift_pattern = "# Day, Time, TaskID, Min, Max"
            shift_on_next_line = False
            shift_info = {}

            for line in file:
                if re.search(shift_pattern, line):
                    shift_on_next_line = True
                    break

            if shift_on_next_line:
                for line in file:
                    if not re.search("^\s", line):
                        split_line = line.split(",")
                        day_id = int(split_line[0]) - 1
                        start_end_time = split_line[1].split("-")
                        time_period = TimePeriod(start_end_time[0], start_end_time[1])

                        if day_id not in shift_info:
                            shift_info[day_id] = []
                        shift_info[day_id].append({"time_period": time_period,
                                                   "task_id": int(split_line[2]) - 1,
                                                   "min_staff": int(split_line[3]),
                                                   "max_staff": int(split_line[4])})
                    else:
                        break

        return shift_info
