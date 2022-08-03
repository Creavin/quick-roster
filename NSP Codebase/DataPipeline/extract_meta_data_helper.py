import pandas as pd
from NspUtils.RosterMetadataExtractor import RosterMetadataExtractor
extractor = RosterMetadataExtractor()

def extract_meta_data_with_pred(solved_input_dir, pred_solved_input_dir, output_file):
    df = extractor.extract_scores(solved_input_dir, pred_solved_input_dir)

    pd.set_option('display.max_columns', None)
    print(df)
    df.to_csv(output_file)

def extract_meta_data(solved_input_dir, output_file):
    df = extractor.extract_score(solved_input_dir)
    pd.set_option('display.max_columns', None)
    print(df)
    df.to_csv(output_file)

def extract_gurobi_status(input_file):
    return extractor.get_gurobi_status(input_file)

def extract_solve_time(input_file):
    gurobi_data = extractor.get_gurobi_data(input_file)
    return gurobi_data['gurobi_run_time']
