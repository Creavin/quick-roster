import os
import numpy as np
import random

from scipy.stats import lognorm
from scipy.stats import norm
from scipy.stats import expon
import random as rand

from NspDataProducers.DataGenerator import generate_data


def generate_schedules(number_schedules, output_dir):
    for n in range(number_schedules):
        # num_workers = random.randrange(25, 35, 1)  # range 5-35
        #num_workers = int(round(min(lognorm.rvs(.6, loc=5, scale=10), 40)))
        num_workers = rand.randrange(7, 40, 1) # int(round(min(lognorm.rvs(.6, loc=5, scale=10), 40)))

        # num_days = random.randrange(1, 11, 1)
        num_days = int(round(min(lognorm.rvs(1, loc=1, scale=3), 10)))

        # num_shifts = random.randrange(4, 13, 4)
        num_shifts = round(norm.rvs(loc=7, scale=1.5))
        num_shifts = int(min(max(4, num_shifts), 12))

        # num_tracks = random.randrange(1, 7, 2)
        num_tracks = int(round(1 + lognorm.rvs(1, scale=1)))

        num_skills = random.randrange(1, 4, 1)

        # mean_availability = random.randrange(7, 11, 1)/10
        mean_availability = round(max(.7, 1 - expon.rvs(scale=.1)), 3)

        #mean_staffing_req = norm.rvs(loc=0.5, scale=0.15)  # todo revert back
        mean_staffing_req = norm.rvs(loc=0.8, scale=0.05)
        mean_staffing_req = np.where(mean_staffing_req > 1, 1, mean_staffing_req)
        mean_staffing_req = np.where(mean_staffing_req <= 0, 0, mean_staffing_req)

        generate_data(num_workers, num_days, num_shifts, num_tracks, num_skills,
                      mean_availability=mean_availability, mean_staffing_requirement=mean_staffing_req, output_dir=output_dir)


def generate_schedules_v1():
    worker_range = range(5, 36, 10)
    days_range = range(3, 10, 3)
    shifts_range = range(4, 13, 4)
    tracks_range = range(1, 7, 2)
    skills_range = range(1, 4, 1)
    mean_availability_range = np.arange(0.7, 1, .1)

    for num_workers in worker_range:
        os.mkdir(f'../output/workers-{num_workers}')
        for num_days in days_range:
            for num_shifts in shifts_range:
                for num_tracks in tracks_range:
                    for num_skills in skills_range:
                        for mean_availability in mean_availability_range:
                            rounded_mean = round(mean_availability, 2)
                            name = f"{num_workers}-{num_days}-{num_shifts}-{num_tracks}-{num_skills}-{rounded_mean}"
                            generate_data(num_workers, num_days, num_shifts, num_tracks, num_skills,
                                          mean_availability=rounded_mean, output_file=f"../output/workers-{num_workers}/{name}.json")


if __name__ == '__main__':
    generate_schedules(1)
