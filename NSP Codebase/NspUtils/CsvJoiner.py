import os
import glob
import pandas as pd


class CsvJoiner:

    @classmethod
    def join_csvs(self, input_directory, output_file="labeled_file.csv"):
        cwd = os.getcwd()
        os.chdir(input_directory)
        all_filenames = [i for i in glob.glob('*.csv')]
        print(all_filenames)
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
        combined_csv.to_csv(output_file, index=False, encoding='utf-8-sig')

        os.chdir(cwd)


    @classmethod
    def sample_csvs(self, input_directory, frac):
        os.chdir(input_directory)
        extension = 'csv'
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        print(all_filenames)

        output_files = os.listdir("output")
        print(output_files)

        for f in all_filenames:
            if f"{frac}-{f}" not in output_files:
                print(f)
                data = pd.read_csv(f)
                data_subset = data.sample(frac=frac, random_state=0)
                data_subset.to_csv(f"output/{frac}-{f}", index=False, encoding='utf-8-sig')

    @classmethod
    def sample_csv(self, file_path, frac):
        file_name = os.path.basename(file_path)
        os.chdir(os.path.dirname(file_path))

        output_files = os.listdir("output")
        print(output_files)

        if f"{frac}-{file_name}" not in output_files:
            data = pd.read_csv(file_path)
            data_subset = data.sample(frac=frac, random_state=0)
            data_subset.to_csv(f"output/{frac}-{file_name}", index=False, encoding='utf-8-sig')

