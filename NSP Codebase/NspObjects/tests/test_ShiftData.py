from unittest import TestCase
from NspObjects.ShiftData import ShiftData


class TestShiftData(TestCase):
    def setUp(self):
        self.shift_data = ShiftData(
            day_names=["Monday"],
            track_names=["Main Hall"],
            shift_names=["9", "10", "11"],
            shift_staffing_level_requirements=[[[[1], [1], [1]]]]
        )
        pass


class TestEachFunction(TestShiftData):
    def test_to_dict(self):
        shift_dict = self.shift_data.to_dict()
        assert str(shift_dict) == "{'__shift_data__': True, 'day_names': ['Monday'], 'shift_names': ['9', '10', " \
                                  "'11'], 'track_names': ['Main Hall'], 'shift_staffing_level_requirements': [[[[1], " \
                                  "[1], [1]]]], 'number_days': 1, 'number_shifts': 3, 'number_tracks': 1} "
        pass
