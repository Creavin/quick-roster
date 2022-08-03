# from WorkerData import WorkerData
# from ShiftData import ShiftData
# from SkillData import SkillData
from NspObjects.SkillData import SkillData
from NspObjects.WorkerData import WorkerData
from NspObjects.ShiftData import ShiftData
from NspObjects.Penalties import Penalties
from NspObjects.Schedule import Schedule

# improve by having function look up penalties
penalties = {"NO_PENALTY": Penalties.NO_PENALTY.value,
             "MINOR_PENALTY": Penalties.MINOR_PENALTY.value,
             "MAJOR_PENALTY": Penalties.MAJOR_PENALTY.value,
             "MAX_PENALTY": Penalties.MAX_PENALTY.value}


class ScheduleJsonDecoder:
    @classmethod
    def decode_schedule(self, dict):
        if 'meta_data' in dict:
            meta_data = dict['meta_data']
        else:
            meta_data = {}


        return Schedule(
            self.get_uuid(dict),
            self.decode_worker_data(dict['worker_data']),
            self.decode_shift_data(dict['shift_data']),
            self.decode_skill_data(dict['skill_data']),
            meta_data
        )

    @classmethod
    def decode_schedule_data(self, dict):
        return self.decode_worker_data(dict['worker_data']), \
               self.decode_shift_data(dict['shift_data']), \
               self.decode_skill_data(dict['skill_data'])

    @classmethod
    def get_uuid(self, dict):
        return self.decode_worker_data(dict['uuid'])

    @classmethod
    def decode_worker_data(self, dict):
        if "__worker_data__" in dict:
            raw_worker_skills_map = dict['worker_id_to_skill_map']
            worker_id_to_skills_map = {int(k): set(v) for k, v in raw_worker_skills_map.items()}
            return WorkerData(
                dict['worker_names'],
                dict['worker_availability'],
                dict['worker_max_shifts'],
                worker_id_to_skills_map)
        return dict

    @classmethod
    def decode_shift_data(self, dict):
        if "__shift_data__" in dict:
            return ShiftData(
                dict['day_names'],
                dict['shift_names'],
                dict['track_names'],
                dict['shift_staffing_level_requirements'],
            )

    @classmethod
    def decode_skill_data(self, dict):
        if "__skill_data__" in dict:
            raw_skill_id_map = dict['skill_id_to_name_map']
            skill_id_to_name_map = {int(k): v for k, v in raw_skill_id_map.items()}
            raw_skill_hierarchy = dict['skill_hierarchy']
            skill_hierarchy = {int(k): self.arrays_to_tuples(v) for k, v in raw_skill_hierarchy.items()}
            return SkillData(skill_id_to_name_map, skill_hierarchy)

    # todo make name more descriptive
    @classmethod
    def arrays_to_tuples(self, array_of_arrays):
        tuples = []
        for array in array_of_arrays:
            tuple = (int(array[0]), penalties[array[1]])
            tuples.append(tuple)
        return tuples
