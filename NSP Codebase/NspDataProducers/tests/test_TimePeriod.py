from unittest import TestCase
from NspDataProducers.TimePeriod import TimePeriod


class TestTimePeriod(TestCase):
    def setUp(self) :
        self.time = TimePeriod("00:15", "00:30")
    pass


class TestInit(TestTimePeriod):
    def test_duration(self):
        self.assertEqual(self.time.period_duration_minutes, 15)

    def test_period_index(self):
        self.assertEqual(self.time.periods_since_midnight, 1)
