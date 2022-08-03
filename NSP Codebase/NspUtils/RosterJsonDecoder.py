from NspObjects.Roster import Roster
from NspObjects.Schedule import Schedule
from NspUtils.ScheduleJsonDecoder import ScheduleJsonDecoder
import json


class RosterJsonDecoder:
    @classmethod
    def decode_roster(self, dict):
        if 'meta_data' in dict:
            meta_data = dict['meta_data']
        else:
            meta_data = {}

        decoder = ScheduleJsonDecoder
        schedule = Schedule(
            uuid=decoder.get_uuid(dict),
            worker_data=decoder.decode_worker_data(dict['worker_data']),
            shift_data=decoder.decode_shift_data(dict['shift_data']),
            skill_data=decoder.decode_skill_data(dict['skill_data']),
            meta_data=meta_data
        )

        return Roster(schedule,
                      worker_assignment=dict['worker_assignment'],
                      total_shifts_per_worker=dict['total_shifts_per_worker'],
                      grb_vars_dict=dict['grb_vars']
                      )
        # todo remove
        #return Roster(
        #    uuid=decoder.get_uuid(dict),
        #    worker_data=decoder.decode_worker_data(dict['worker_data']),
        #    shift_data=decoder.decode_shift_data(dict['shift_data']),
        #    skill_data=decoder.decode_skill_data(dict['skill_data']),
        #    worker_assignment=dict['worker_assignment'],
        #    total_shifts_per_worker=dict['total_shifts_per_worker'],
        #    grb_vars_dict=dict['grb_vars'],
        #    meta_data=dict['meta_data']
        #)

    @classmethod
    def decode_from_json_file(self, input_file):
        return self.decode_roster(self.json_to_dict(input_file))

    @classmethod
    def json_to_dict(self, input_file):
        with open(input_file) as roster_json:
            roster_json_str = roster_json.read()
            return json.loads(roster_json_str)
