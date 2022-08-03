class WorkerData:

    def __init__(self, worker_names, worker_availability, worker_max_shifts, worker_id_to_skill_map):
        self.worker_names = worker_names
        self.worker_max_shifts = worker_max_shifts
        self.worker_id_to_skill_map = worker_id_to_skill_map
        self.number_workers = len(worker_names)

        if type(worker_availability[0][0][0]) == list:
            worker_availability = [[[s[0] for s in d]
                                    for d in w]
                                   for w in worker_availability]
            assert type(worker_availability[0][0][0]) != list

        self.worker_availability = worker_availability

    def to_dict(self):
        worker_id_to_skill_map = {}
        for k, v in self.worker_id_to_skill_map.items():
            worker_id_to_skill_map[k] = list(v)

        worker_avail = self.worker_availability
        if not isinstance(worker_avail, list):
            worker_avail = worker_avail.tolist()

        return {
            "__worker_data__": True,
            'worker_names': self.worker_names,
            'worker_availability': worker_avail,
            'worker_max_shifts': self.worker_max_shifts,
            'worker_id_to_skill_map': worker_id_to_skill_map,
            'number_workers': self.number_workers
        }
