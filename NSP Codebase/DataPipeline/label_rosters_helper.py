import os
import re
from NspUtils.CsvJoiner import CsvJoiner
from NspUtils.RosterLabeler import label_file


def label_files(input_dir, output_dir, output_file):
    completed_files = set(os.listdir(output_dir))

    for file in os.listdir(input_dir):
        if file not in completed_files:
            if re.match(f'.*mip.*', file):
                print("FILE is ", file)
                try:
                    label_file(input_dir + '/' + file, output_dir)
                except:
                    print(f"ERROR: Fault with file {file}")

    CsvJoiner.join_csvs(output_dir, output_file)


def join_pre_labeled_rosters(input_dir, output_file):
    CsvJoiner.join_csvs(input_dir, output_file)
