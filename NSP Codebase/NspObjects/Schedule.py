import json


class Schedule:

    def __init__(self, uuid, worker_data, shift_data, skill_data, meta_data=None):
        if meta_data is None:
            meta_data = {}
        self.uuid = uuid
        self.worker_data = worker_data
        self.shift_data = shift_data
        self.skill_data = skill_data

        self.worker_ids = range(worker_data.number_workers)
        self.day_ids = range(shift_data.number_days)
        self.shift_ids = range(shift_data.number_shifts)
        self.track_ids = range(shift_data.number_tracks)
        self.skill_ids = range(skill_data.number_skills)
        self.meta_data = meta_data

    def write_to_file(self, output_file):
        with open(output_file, 'w', encoding='utf-8') as output_file:
            json.dump(self.to_dict(), output_file, sort_keys=True, indent=4)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'worker_data':  self.worker_data.to_dict(),
            'shift_data':  self.shift_data.to_dict(),
            'skill_data':  self.skill_data.to_dict(),
            'meta_data': self.meta_data
        }


    def print_desired_schedule(self):
        print('Print Desired Schedule')
        for day_id in self.day_ids:
            for track_id in self.track_ids:
                print("day id: ", day_id, "\t track id: ", track_id, end="\t")

                for shift_id in self.shift_ids:
                    shift_staffing_str = "["
                    for skill_id in self.skill_ids:
                        shift_staffing_str += str(
                            int(self.shift_data.shift_staffing_level_requirements[day_id][track_id][shift_id][
                                    skill_id])) + ', '

                    print(shift_staffing_str + ']', end='\t')
                print()  # new line after printing all the shifts for a track
        print('')
