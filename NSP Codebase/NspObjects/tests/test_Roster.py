import numpy as np
from unittest import TestCase
from NspObjects.ShiftData import ShiftData
from NspObjects.SkillData import SkillData
from NspObjects.WorkerData import WorkerData
from NspObjects.Roster import Roster


class TestRoster(TestCase):
    def setUp(self):
        worker_data = WorkerData(
            worker_names=["peter", "jane"],
            worker_availability=[[[1, 1, 0]], [[0, 0, 1]]],
            worker_max_shifts=[3, 3],
            worker_id_to_skill_map={0: [0], 1: [0]}
        )

        skill_data = SkillData(
            skill_id_to_name_map={0: "default"},
            skill_hierarchy={0: []}
        )

        shift_data = ShiftData(
            day_names=["Monday"],
            track_names=["Main Hall"],
            shift_names=["9", "10", "11"],
            shift_staffing_level_requirements=[[[[1], [1], [1]]]]
        )

        self.roster = Roster(
            uuid="123e4567-e89b-12d3-a456-426614174000",
            worker_data=worker_data,
            shift_data=shift_data,
            skill_data=skill_data,
            worker_assignment=np.array([
                [[[[1], [1], [0]]]],
                [[[[0], [0], [1]]]]
            ]),
            total_shifts_per_worker=[2, 1],
            grb_vars_dict={"total_slack_penalty": 0, "total_skill_penalty": 0}
        )

        pass


class TestEachFunction(TestRoster):
    def test_to_dict(self):
        roster_dict = self.roster.to_dict()
        print(roster_dict)
        assert str(roster_dict) == "{'__roster_data__': True, 'uuid': '123e4567-e89b-12d3-a456-426614174000', " \
                                   "'worker_data': {'__worker_data__': True, 'worker_names': ['peter', 'jane'], " \
                                   "'worker_availability': [[[1, 1, 0]], [[0, 0, 1]]], 'worker_max_shifts': [3, 3], " \
                                   "'worker_id_to_skill_map': {0: [0], 1: [0]}, 'number_workers': 2}, 'shift_data': {" \
                                   "'__shift_data__': True, 'day_names': ['Monday'], 'shift_names': ['9', '10', " \
                                   "'11'], 'track_names': ['Main Hall'], 'shift_staffing_level_requirements': [[[[1], " \
                                   "[1], [1]]]], 'number_days': 1, 'number_shifts': 3, 'number_tracks': 1}, " \
                                   "'skill_data': {'__skill_data__': True, 'number_skills': 1, " \
                                   "'skill_id_to_name_map': {0: 'default'}, 'skill_hierarchy': {0: []}}, 'grb_vars': " \
                                   "{'total_slack_penalty': 0, 'total_skill_penalty': 0}, 'worker_assignment': [[[[[" \
                                   "1], [1], [0]]]], [[[[0], [0], [1]]]]], 'total_shifts_per_worker': [2, 1]}"



        pass
