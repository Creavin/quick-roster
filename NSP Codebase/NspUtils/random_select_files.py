from DataPipeline import pipeline_constants as const
import os
import re
import random
import shutil

DRY_RUN = False
sampling_rate = {"worker-5": 40,
                "worker-15": 40,
                "worker-35": 0,
                "worker-25": 30}
def random_sample_schedules(base_dir, output_dir):
    for dir, rate in sampling_rate.items():
        schedule_name_to_rosters = {}

        for file in os.listdir(f"{base_dir}/{dir}"):
            schedule_name = re.sub(r"(-[\d*]-mip)|(-[\d*]-lpr)", "", file)
            if schedule_name not in schedule_name_to_rosters:
                schedule_name_to_rosters[schedule_name] = [file]
            else:
                schedule_name_to_rosters[schedule_name].append(file)
        print(schedule_name_to_rosters)

        sampled_schedules = random.sample(list(schedule_name_to_rosters.keys()), rate)
        print(sampled_schedules)

        for schedule in sampled_schedules:
            for roster_name in schedule_name_to_rosters[schedule]:
                if DRY_RUN:
                    print(f"{base_dir}/{dir}/{roster_name}", f"{output_dir}/{roster_name}")
                else:
                    shutil.copy(f"{base_dir}/{dir}/{roster_name}",
                                f"{output_dir}/{roster_name}")


random_sample_schedules(f"{const.ROOT}/data/generated_data",
                        f"{const.ROOT}/data/subset_generated_data")