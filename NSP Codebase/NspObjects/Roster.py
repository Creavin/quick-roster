from NspObjects.Schedule import Schedule


class Roster:

    def __init__(self, schedule, worker_assignment, total_shifts_per_worker, grb_vars_dict):
        self.uuid = schedule.uuid
        self.worker_data = schedule.worker_data
        self.shift_data = schedule.shift_data
        self.skill_data = schedule.skill_data
        self.meta_data = schedule.meta_data

        self.worker_ids = range(schedule.worker_data.number_workers)
        self.day_ids = range(schedule.shift_data.number_days)
        self.shift_ids = range(schedule.shift_data.number_shifts)
        self.track_ids = range(schedule.shift_data.number_tracks)
        self.skill_ids = range(schedule.skill_data.number_skills)

        self.grb_vars = grb_vars_dict
        self.worker_assignment = worker_assignment
        self.total_shifts_per_worker = total_shifts_per_worker

    def get_schedule(self):
        return Schedule(self.uuid, self.worker_data, self.shift_data, self.skill_data, self.meta_data)

    def to_dict(self):
        return {
            "__roster_data__": True,
            'uuid': self.uuid,
            'worker_data': self.worker_data.to_dict(),
            'shift_data': self.shift_data.to_dict(),
            'skill_data': self.skill_data.to_dict(),
            'grb_vars': self.grb_vars,
            'worker_assignment': self.worker_assignment.tolist(),
            'total_shifts_per_worker': self.total_shifts_per_worker,
            'meta_data': self.meta_data
        }

    def print_totals(self):
        # Print total slack and the number of shifts worked for each worker
        print('\nTotal slack required: ' + str(self.grb_vars['total_slack']))
        for w in range(self.worker_data.number_workers):
            print(self.worker_data.worker_names[w] + ' worked ' + str(self.total_shifts_per_worker[w]) + ' shifts')

        print("\n")
        print('Total penalty: ' + str(self.grb_vars['total_skill_penalty']))

    def print_worker_hours(self, print_in_order_of_worker=False):
        print("Each worker's hours")
        if print_in_order_of_worker:
            for worker_id in self.worker_ids:
                for day_id in range(self.shift_data.number_days):
                    self.print_worker_entry(worker_id, day_id)
        else:
            for day_id in range(self.shift_data.number_days):
                for worker_id in self.worker_ids:
                    self.print_worker_entry(worker_id, day_id)

    def print_worker_entry(self, worker_id, day_id):
        print("worker id: " + str(worker_id), "\t day id: " + str(day_id), end="\t")
        for track_id in self.track_ids:
            print(f"track: {track_id}", end=" ")

            is_assigned_to_shifts_str = "["
            for shift_id in self.shift_ids:

                is_assigned_to_position = '_'
                for skill_id in self.skill_ids:
                    if int(self.worker_assignment[worker_id][day_id][track_id][shift_id][skill_id]) == 1:
                        is_assigned_to_position = skill_id

                is_assigned_to_shifts_str += str(is_assigned_to_position) + ', '

            is_assigned_to_shifts_str = is_assigned_to_shifts_str.rstrip(", ") + "]\t"
            print(is_assigned_to_shifts_str, end='')
        print('')

    def print_schedule(self):
        print('Print Created Schedule Overview')
        for day_id in self.day_ids:
            for track_id in self.track_ids:
                print("day id: ", day_id, "\t track id: ", track_id, end="\t")

                for shift_id in self.shift_ids:
                    shift_staffing_str = "["
                    for skill_id in self.skill_ids:
                        num_workers = 0
                        for worker_id in self.worker_ids:
                            num_workers += int(
                                self.worker_assignment[worker_id][day_id][track_id][shift_id][skill_id])

                        shift_staffing_str += str(num_workers) + ', '
                    print(shift_staffing_str + ']', end='\t')
                print()  # new line after printing all the shifts for a track
        print()

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
