import os
import shutil
import generate_schedules
import pipeline_constants as const
import prune_and_solve_schedules
import solve_schedules_helper
import extract_meta_data_helper
from DataPipeline import label_rosters_helper

do_delete_files = False
do_generate_schedules = False
do_solve_schedules = True
do_label_rosters = False
do_prune_and_solve = False
do_extract_meta_data = True

do_separate_hard_instances = False

def main():
    if do_delete_files:
        if "delete" == input("Type 'delete' to remove previously created files: "):
            empty_pipeline_dir(const.GENERATED_SCHEDULES_DIR)
            empty_pipeline_dir(const.SOLVED_ROSTERS)
            empty_pipeline_dir(const.PRED_SOLVED_ROSTERS)
            empty_pipeline_dir(const.LABELED_ROSTERS)

    if do_generate_schedules:
        generate_schedules.generate_schedules(10, const.GENERATED_SCHEDULES_DIR)

    if do_solve_schedules:
        solve_schedules_helper.solve_schedules(const.GENERATED_SCHEDULES_DIR, const.SOLVED_ROSTERS)

    if do_separate_hard_instances:
        cp_hard_schedules(const.SOLVED_ROSTERS, f"{const.ROOT}/data/hard_rosters")


    if do_label_rosters:
        label_rosters_helper.label_files(const.SOLVED_ROSTERS, const.LABELED_ROSTERS, const.LABELED_FILE)
        #label_rosters_helper.join_pre_labeled_rosters(const.PRE_LABELED_ROSTERS_DIR, const.RESULTS_DIR + '/' + const.LABELED_FILE)

    if do_prune_and_solve:
        empty_pipeline_dir(const.PRED_SOLVED_ROSTERS)
        for clf in ["sgd"]:
            prune_and_solve_schedules.prune_solve_schedules(clf, const.GENERATED_SCHEDULES_DIR, const.PRED_SOLVED_ROSTERS, threshold=0.85)

    # todo test
    if do_extract_meta_data:
        extract_meta_data_helper.extract_meta_data(const.SOLVED_ROSTERS, const.RESULTS_DIR + '/meta_data.csv')
        extract_meta_data_helper.extract_meta_data_with_pred(const.SOLVED_ROSTERS, const.PRED_SOLVED_ROSTERS,
                                                          const.RESULTS_DIR + f'/obj_results_v2.csv')

def empty_pipeline_dir(dir):
    for file in os.listdir(dir):
        print("Deleting: ", file)
        os.remove(f"{dir}/{file}")


def cp_hard_schedules(input_dir, output_dir):
    for file in os.listdir(input_dir):
        time = extract_meta_data_helper.extract_solve_time(input_dir + '/' + file)
        if time >= 120:
            print(f"Copying file: {input_dir}/{file} to {output_dir}")
            shutil.copy(f"{input_dir}/{file}", output_dir)




if __name__ == '__main__':
    main()
