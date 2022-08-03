from unittest import TestCase
from NspObjects.WorkerData import WorkerData


class TestWorkerData(TestCase):
    def setUp(self):
        self.worker_data = WorkerData(
            worker_names=["peter", "jane"],
            worker_availability=[[[1, 1, 0]], [[0, 0, 1]]],
            worker_max_shifts=[3, 3],
            worker_id_to_skill_map={0: {0}, 1: {0}}
        )
        pass


class TestEachFunction(TestWorkerData):
    def test_to_dict(self):
        worker_dict = self.worker_data.to_dict()
        assert str(worker_dict) == "{'__worker_data__': True, 'worker_names': ['peter', 'jane'], " \
                                   "'worker_availability': [[[1, 1, 0]], [[0, 0, 1]]], 'worker_max_shifts': [3, 3], " \
                                   "'worker_id_to_skill_map': {0: [0], 1: [0]}, 'number_workers': 2}"

        pass
