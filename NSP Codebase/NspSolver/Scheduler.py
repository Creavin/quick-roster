import sys
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from time import perf_counter

from NspObjects.WorkerData import WorkerData
from NspObjects.ShiftData import ShiftData
from NspObjects.SkillData import SkillData
from NspObjects.Roster import Roster
from NspObjects.Penalties import Penalties
from NspObjects.Schedule import Schedule

MINOR_PENALTY = 1
MAJOR_PENALTY = 3
MAX_PENALTY = 10

VERBOSE = True
DEBUG = False


class Scheduler:

    def init(self, schedule):
        self.orig_schedule = schedule
        self.uuid = schedule.uuid
        self.worker_data = schedule.worker_data
        self.shift_data = schedule.shift_data
        self.skill_data = schedule.skill_data
        self.model: gp.Model = gp.Model()

        self.worker_ids = range(self.worker_data.number_workers)
        self.day_ids = range(self.shift_data.number_days)
        self.shift_ids = range(self.shift_data.number_shifts)
        self.track_ids = range(self.shift_data.number_tracks)
        self.skill_ids = range(self.skill_data.number_skills)

    def schedule(self, schedule: Schedule, lpr=False, pruned_assignment=None, node_limit=None):
        self.init(schedule)
        self.pruned_assignment = pruned_assignment

        self.lpr = lpr
        if lpr:
            self.model = self.model.relax()  # Turn the MIP into a LIP

        if node_limit is not None:
            self.model.Params.NodeLimit = node_limit

        if self.pruned_assignment is not None:
            self.availability = np.array([[[[[min(self.worker_data.worker_availability[w][d][s],
                                                   self.pruned_assignment[w][d][t][s][skill])
                                                   for skill in self.skill_ids]
                                                  for s in self.shift_ids]
                                                 for t in self.track_ids]
                                                for d in self.day_ids]
                                               for w in self.worker_ids])
        else:
            self.availability = np.array([[[[[self.worker_data.worker_availability[w][d][s]
                                               for skill in self.skill_ids]
                                             for s in self.shift_ids]
                                            for t in self.track_ids]
                                           for d in self.day_ids]
                                          for w in self.worker_ids])

        # Create Gurobi Variables
        worker_assignment_vars = self.create_worker_assignment_vars()
        slack_per_shift_vars = self.create_slack_per_shift_vars()
        total_shifts_per_worker_vars = self.calculate_total_shifts_per_worker(worker_assignment_vars)
        skill_assignment_penalty_vars = self.add_skill_penalty_constraint(worker_assignment_vars)

        total_slack_var = self.model.addVar(name="TotalSlack", vtype=GRB.INTEGER, lb=0)
        total_skill_penalty_var = self.model.addVar(vtype=GRB.INTEGER, lb=0)

        # Constraints
        self.add_shift_slacking_constraint(worker_assignment_vars, slack_per_shift_vars)
        self.add_track_limit_constraint(worker_assignment_vars)

        self.model.addConstr(total_slack_var == np.sum(slack_per_shift_vars))
        self.model.addConstr(total_skill_penalty_var == np.sum(skill_assignment_penalty_vars))

        ## Unused -- should be re-implemented
        # add_max_daily_shifts_limit_constr(self.worker_data, worker_assignment_vars, self.shift_data, model)

        # Objectives
        self.model.ModelSense = GRB.MINIMIZE  # Set global sense for ALL objectives
        self.model.setObjective(5 * total_slack_var + total_skill_penalty_var)

        ## Unused -- model opts to relax all shifts to meet object
        # self.model.setObjectiveN(total_skill_penalty_var, index=2, priority=2, name='SkillPenalty')

        self.total_solve_time = 0
        self.total_node_count = 0
        self.status = None

        def solve():
            if lpr:
                for v in self.model.getVars():
                    if v.vType == GRB.INTEGER:
                        v.vType = GRB.CONTINUOUS


            gurobi_start_time = perf_counter()
            self.model.optimize()
            self.total_solve_time += perf_counter() - gurobi_start_time

            self.total_node_count += self.model.nodeCount

            status = self.model.Status
            if self.status is GRB.OPTIMAL or self.status is None:
                self.status = status

            if status in (GRB.INF_OR_UNBD, GRB.INFEASIBLE, GRB.UNBOUNDED):
                print('Model cannot be solved because it is infeasible or unbounded')
                sys.exit(0)

            if status != GRB.OPTIMAL:
                print('Optimization was stopped with status ' + str(status))
                if status != GRB.NODE_LIMIT:
                    sys.exit(0)

            num_solutions = self.model.SolCount
            rosters = []
            optimal_score = round(self.model.objVal)
            for solnum in range(num_solutions):
                self.model.setParam("SolutionNumber", solnum)
                score = round(self.model.objVal)

                if score != optimal_score:
                    continue

                if lpr:
                    print("Obj value", round(self.model.objVal))
                    print("Slack Penalty = ", total_slack_var.X)
                    print("Skill Penalty = ", total_skill_penalty_var.X)
                    grb_vars_set = {'total_slack': total_slack_var.X,
                                    'total_skill_penalty': total_skill_penalty_var.X,
                                    'gurobi_run_time': self.total_solve_time,
                                    'gurobi_status': int(self.status),
                                    'node_count': self.total_node_count}
                    total_shifts_per_worker_array = [total_shifts_per_worker_vars[w].X for w in self.worker_ids]
                    worker_assignment_array = np.array([[[[[worker_assignment_vars[w][d][t][s][skill].X
                                                            for skill in self.skill_ids]
                                                           for s in self.shift_ids]
                                                          for t in self.track_ids]
                                                         for d in self.day_ids]
                                                        for w in self.worker_ids])

                    print("Number of solutions", self.model.SolCount)
                    #rosters.append(Roster(self.uuid, self.worker_data, self.shift_data, self.skill_data, worker_assignment_array,
                    #                      total_shifts_per_worker_array, grb_vars_set))
                    rosters.append(Roster(self.orig_schedule, worker_assignment_array, total_shifts_per_worker_array, grb_vars_set))

                else:
                    print("Obj value", round(self.model.objVal))
                    print("Slack Penalty = ", total_slack_var.Xn)
                    print("Skill Penalty = ", total_skill_penalty_var.Xn)


                    grb_vars_set = {'total_slack': total_slack_var.Xn,
                                    'total_skill_penalty': total_skill_penalty_var.Xn,
                                    'gurobi_run_time': self.total_solve_time,
                                    'gurobi_status': int(self.status),
                                    'gurobi_obj_val': round(self.model.objVal),
                                    'node_count': self.total_node_count
                                    }

                    if self.pruned_assignment is not None:
                        size = np.product(self.pruned_assignment.shape)
                        sum = np.sum(self.pruned_assignment)
                        prune_pc = (size - sum) / size
                        grb_vars_set['prune_percentage'] = prune_pc


                    total_shifts_per_worker_array = [total_shifts_per_worker_vars[w].Xn for w in self.worker_ids]
                    worker_assignment_array = np.array([[[[[worker_assignment_vars[w][d][t][s][skill].Xn
                                                            for skill in self.skill_ids]
                                                           for s in self.shift_ids]
                                                          for t in self.track_ids]
                                                         for d in self.day_ids]
                                                        for w in self.worker_ids])

                    print("Number of solutions", self.model.SolCount)
                    #rosters.append(Roster(self.uuid, self.worker_data, self.shift_data, self.skill_data, worker_assignment_array,
                    #                      total_shifts_per_worker_array, grb_vars_set))
                    rosters.append(Roster(self.orig_schedule, worker_assignment_array, total_shifts_per_worker_array, grb_vars_set))
            return rosters

        solve()

        """
        Below is a secondary optimization which minimizes the difference between shifts.
        The total slack of the optimal solution is fixed and allows the skill penalty is allowed to be slightly
        degraded.
        """

        total_slack_var.ub = total_slack_var.X
        total_slack_var.lb = total_slack_var.X

        total_skill_penalty_var.ub = round(total_skill_penalty_var.X * 1.1, 0)

        avg_shifts = self.model.addVar(name="avg_shifts")
        diff_shifts = self.model.addVars(self.worker_ids, lb=-GRB.INFINITY, name="Diff")

        self.model.addConstr(self.worker_data.number_workers * avg_shifts == total_shifts_per_worker_vars.sum(),
                             "avgShifts")
        self.model.addConstrs((diff_shifts[w] == total_shifts_per_worker_vars[w] - avg_shifts for w in self.worker_ids),
                              "Diff")
        self.model.setObjective(gp.quicksum(diff_shifts[w] * diff_shifts[w] for w in self.worker_ids))
        self.model.Params.MIPGap = 0.05  # todo delete line. This is tmp
        self.model.Params.NodeLimit = 1500000  # todo delete line. This is tmp
        return solve()

    def create_worker_assignment_vars(self):
        vtype = GRB.BINARY
        if self.lpr:
            vtype = GRB.CONTINUOUS

        #if self.pruned_assignment is not None:
        #    worker_assignment_vars = np.array([[[[[self.model.addVar(vtype=vtype, lb=0,
        #                                                             ub=min(self.worker_data.worker_availability[w][d][s],
        #                                                                    self.pruned_assignment[w][d][t][s][skill]))
        #                                           for skill in self.skill_ids]
        #                                          for s in self.shift_ids]
        #                                         for t in self.track_ids]
        #                                        for d in self.day_ids]
        #                                       for w in self.worker_ids])
        #else:
        #    worker_assignment_vars = np.array([[[[[self.model.addVar(vtype=vtype, lb=0,
        #                                                             ub=self.worker_data.worker_availability[w][d][s])
        #                                           for skill in self.skill_ids]
        #                                          for s in self.shift_ids]
        #                                         for t in self.track_ids]
        #                                        for d in self.day_ids]
        #                                       for w in self.worker_ids])
        worker_assignment_vars = np.array([[[[[self.model.addVar(vtype=vtype, lb=0,
                                                                 ub=self.availability[w][d][t][s][skill])
                                               for skill in self.skill_ids]
                                              for s in self.shift_ids]
                                             for t in self.track_ids]
                                            for d in self.day_ids]
                                           for w in self.worker_ids])

        return worker_assignment_vars

    def create_slack_per_shift_vars(self):
        slack_per_shift = np.array([[[[self.model.addVar(lb=0, vtype=GRB.INTEGER)
                                       for skill in self.skill_ids]
                                      for t in self.track_ids]
                                     for s in self.shift_ids]
                                    for d in self.day_ids])
        return slack_per_shift

    def add_shift_slacking_constraint(self, worker_availability_vars, slack_per_shift_vars):
        total_assigned_work = np.array([[[[self.model.addVar(lb=0, vtype=GRB.INTEGER)
                                           for skill in self.skill_ids]
                                          for s in self.shift_ids]
                                         for t in self.track_ids]
                                        for d in self.day_ids])

        temp_total_work_var = self.model.addVar(lb=0, vtype=GRB.INTEGER)

        for day_id in self.day_ids:
            for track_id in self.track_ids:
                for shift_id in self.shift_ids:
                    for skill_id in self.skill_ids:
                        # total_assigned_work = np.sum(worker_availability_vars, axis=0)[day_id][shift_id][track_id][skill_id]
                        temp_total_work_var = np.sum(worker_availability_vars, axis=0)[day_id][track_id][shift_id][
                            skill_id]

                        self.model.addConstr(slack_per_shift_vars[day_id][shift_id][track_id][skill_id] ==
                                             self.shift_data.shift_staffing_level_requirements[day_id][track_id][
                                                 shift_id][skill_id]
                                             - temp_total_work_var)

    def add_track_limit_constraint(self, worker_availability_vars):
        for worker_id in self.worker_ids:
            for shift_id in self.shift_ids:
                for day_id in self.day_ids:
                    # todo fix sum
                    # workers_assignment_limit_per_shift = np.sum(worker_availability_vars[worker_id][day_id], axis=1)[shift_id]
                    # workers_assignment_limit_per_shift = np.sum(np.sum(worker_availability_vars[worker_id][day_id], axis=1)[shift_id])
                    workers_assignment_limit_per_shift = \
                        np.sum(worker_availability_vars[worker_id][day_id], axis=(2, 0))[shift_id]
                    # print(np.sum(l[0][1], axis=(2,0)))
                    self.model.addConstr(workers_assignment_limit_per_shift <= 1)

    def calculate_total_shifts_per_worker(self, worker_availability_vars):
        total_shifts_per_worker = np.array(
            [self.model.addVar(lb=0, vtype=GRB.INTEGER) for w in self.worker_ids])

        for w in self.worker_ids:
            self.model.addConstr(total_shifts_per_worker[w] == np.sum(np.sum(worker_availability_vars[w], axis=1)))

        return total_shifts_per_worker

    # unused -- should be re-implemented to prevent workers being assigned excess shifts per day
    def add_max_daily_shifts_limit_constr(self, worker_availability_vars):
        daily_shifts_per_worker_vars = np.array(
            [[self.model.addVar(lb=0, ub=self.worker_data.worker_max_shifts[w], vtype=GRB.INTEGER)
              for d in self.day_ids]
             for w in self.worker_ids])

        for w in self.worker_ids:
            for d in self.day_ids:
                # todo check sum
                self.model.addConstr(
                    daily_shifts_per_worker_vars[w][d] == np.sum(worker_availability_vars[w][d], axis=(1, 2, 0)))

    def add_skill_penalty_constraint(self, worker_assignment_vars):
        skill_assignment_penalty_vars = np.array([[[[[self.model.addVar(vtype=GRB.INTEGER)
                                                      for skill in self.skill_ids]
                                                     for s in self.shift_ids]
                                                    for t in self.track_ids]
                                                   for d in self.day_ids]
                                                  for w in self.worker_ids])

        self.assign_skill_penalties(worker_assignment_vars, skill_assignment_penalty_vars)

        return skill_assignment_penalty_vars

    def assign_skill_penalties(self, worker_assignment_vars, skill_assignment_penalty_vars):
        for w in self.worker_ids:
            if DEBUG:
                penalties = "["
            for d in self.day_ids:
                for s in self.shift_ids:
                    for t in self.track_ids:
                        for skill in self.skill_ids:
                            penalty = self.calculate_skill_penalty(
                                self.worker_data.worker_id_to_skill_map[w],
                                skill,
                                self.skill_data.skill_hierarchy
                            )
                            if DEBUG:
                                penalties += str(penalty) + ', '

                            self.model.addConstr(skill_assignment_penalty_vars[w][d][t][s][skill] == penalty *
                                                 worker_assignment_vars[w][d][t][s][skill])
            if DEBUG:
                penalties += ']'
                print(penalties)

    @staticmethod
    def calculate_skill_penalty(worker_skills, required_skill, skill_hierarchy):
        if required_skill in worker_skills:
            return 0

        skill_substitutes = skill_hierarchy.get(required_skill)
        if skill_substitutes:
            for skill_penalty_pair in skill_substitutes:
                if skill_penalty_pair[0] in worker_skills:
                    return skill_penalty_pair[1]

        return Penalties.MAX_PENALTY.value
