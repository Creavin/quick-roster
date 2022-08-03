from unittest import TestCase
from NspDataProducers.ShiftSchedulingDataParser import ShiftSchedulingBenchmarkParser

class TestShiftSchedulingDataParser(TestCase):
    def setUp(self):
        self.parser = ShiftSchedulingBenchmarkParser("shift_scheduling_data_for_testing.txt")
        pass


class TestEachFunction(TestShiftSchedulingDataParser):
    def test_create_shift_data(self):
        shift_data = self.parser.create_shift_data()
        pass

    def test_create_skill_data(self):
        skill_data = self.parser.create_skill_data()
        pass

    def test_minutes_to_hh_mm(self):
        pass

    def test_create_worker_data(self):
        worker_data = self.parser.create_worker_data()
        pass

    def test_parse_num_days(self):
        assert self.parser.parse_num_days() == 5
        pass

    def test_parse_num_tasks(self):
        assert self.parser.parse_num_tasks() == 2
        pass

    def test_parse_staff_info(self):
        number_workers = len(self.parser.parse_staff_info().items())
        assert number_workers == 3
        pass

    def test_parse_shift_info(self):
        shift_info = self.parser.parse_shift_info()
        number_shifts = 0
        for day_id in range(len(shift_info.items())):
            number_shifts += len(shift_info[day_id])
        assert number_shifts == 20
        pass
