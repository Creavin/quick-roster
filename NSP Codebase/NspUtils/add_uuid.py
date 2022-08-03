import uuid
import os
import json
import re
import NspUtils.ScheduleJsonDecoder


#solved_dir = "/home/thomas/Desktop/All Datafiles/Custom Rosters/output-35a,b/"
DRY_RUN = False

def inject_uuid(full_path, schedule_uuid = None):
    with open(full_path) as json_file:
        if not schedule_uuid:
            schedule_uuid = str(uuid.uuid4())

        schedule = json.load(json_file)
        schedule['uuid'] = schedule_uuid

    with open(full_path, 'w', encoding='utf-8') as output_file:
        json.dump(schedule, output_file, sort_keys=True, indent=4)

def add_uuid_to_schedule_and_rosters(dir, solved_dir):
    for file in os.listdir(dir):
        print(file)
        full_path = dir + '/' + file
        file_name = os.path.basename(file).split('.')[0]
        file_uuid = str(uuid.uuid4())
        if not DRY_RUN:
            inject_uuid(full_path, file_uuid)

        if solved_dir:
            for solved_file in os.listdir(solved_dir):
                if re.match(f'^{file_name}*', solved_file):
                    print(solved_file)
                    solved_file_path = solved_dir + '/' + solved_file
                    if not DRY_RUN:
                        inject_uuid(solved_file_path, file_uuid)

def add_uuid_to_rosters(dir):
    basename_to_uuid = {}

    for file in os.listdir(dir):
        schedule_basename = re.sub(r"(((-[\d*])*-mip)|((-[\d*])*-lpr))\.json", "", file)
        if schedule_basename in basename_to_uuid:
            inject_uuid(dir + f'/{file}', basename_to_uuid[schedule_basename])
        else:
            id = str(uuid.uuid4())
            basename_to_uuid[schedule_basename] = id
            inject_uuid(dir + f'/{file}', id)

    print(basename_to_uuid)


dir = "/home/thomas/Desktop/All Datafiles/Scheduling Benchmarks/rest-skill"
add_uuid_to_rosters(dir)