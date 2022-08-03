import pandas as pd
import os
import json
import re


def obj_function(slack, skill):
    return 5 * slack + skill


class RosterMetadataExtractor:

    @classmethod
    def extract_scores(self, solved_dir, pred_solved_dir):
        rows = {}
        for file in os.listdir(solved_dir):
            if re.match('.*-0-mip.*', file):
                print(file)
                full_path = solved_dir + '/' + file
                scores = self.get_meta_data(full_path)
                rows[scores['uuid']] = scores

        for file in os.listdir(pred_solved_dir):
            if solved_dir:  # todo is this needed
                if re.match('.*-0-mip.*', file):
                    print(file)
                    solved_full_path = pred_solved_dir + '/' + file
                    scores = self.get_meta_data(solved_full_path, "pred")
                    rows[scores['uuid']].update(scores)

        df = pd.DataFrame(rows.values()).set_index('uuid')
        df['obj_diff'] = df['pred_obj'] - df['true_obj']
        df['obj_diff_pc'] = (df['obj_diff'])/ df['true_obj']
        df['solve_time_diff'] = df['true_solve_time'] - df['pred_solve_time']
        df['solve_time_diff_pc'] = (df['solve_time_diff']) / df['true_solve_time']
        return df


    @classmethod
    def extract_score(self, rosters_dir):
        rows = {}
        for file in os.listdir(rosters_dir):
            if re.match('.*-0-pmip.*', file):
                print(file)
                full_path = rosters_dir + '/' + file
                scores = self.get_meta_data(full_path)
                rows[scores['uuid']] = scores

        df = pd.DataFrame(rows.values()).set_index('uuid')
        return df

    @classmethod
    def get_gurobi_status(self, file):
        with open(file) as json_file:
            file_data = json.load(json_file)
            if '__roster_data__' in file_data:
                return file_data['grb_vars']['gurobi_status']
            else:
                return None

    @classmethod
    def get_gurobi_data(self, file):
        with open(file) as json_file:
            file_data = json.load(json_file)
            if '__roster_data__' in file_data:
                return file_data['grb_vars']
            else:
                return None

    @classmethod
    def get_else_null(self, index, list):
        result = "Null"
        if index in list:
            result = list[index]
        return result

    @classmethod
    def get_meta_data(self, full_path, prefix="true"):
        with open(full_path) as json_file:
            file_data = json.load(json_file)
            slack_penalty = file_data['grb_vars']['total_slack']
            skill_penalty = file_data['grb_vars']['total_skill_penalty']
            solve_time = self.get_else_null('gurobi_run_time', file_data['grb_vars'])
            gurobi_status = self.get_else_null('gurobi_status', file_data['grb_vars'])
            node_count = self.get_else_null('node_count', file_data['grb_vars'])
            prune_pc = self.get_else_null('prune_percentage', file_data['grb_vars'])

            return {'uuid': file_data['uuid'],
                    f'{prefix}_skill': skill_penalty,
                    f'{prefix}_slack': slack_penalty,
                    f'{prefix}_solve_time': solve_time,
                    f'{prefix}_gurobi_status': gurobi_status,
                    f'{prefix}_node_count': node_count,
                    f'{prefix}_obj': obj_function(slack_penalty, skill_penalty),
                    f'{prefix}_prune_pc': prune_pc
                    }

    # def append_scores(self, ):
    # rows = [{'id': "alpha", 'true_slack': 0, 'true_skill': 0, 'true_obj': 0},
    #        {'id': "beta", 'true_slack': 1, 'true_skill': 1, 'true_obj': 2}]
    #
    # df = pd.DataFrame(rows).set_index('id')
    # pd.set_option('display.max_columns', None)
    # print(df)
    # df.to_csv('output/obj_scores.csv')
    #
    ### Add pred data
    # rows = []
    # df = pd.read_csv('output/obj_scores.csv').set_index('id')
    # print(df)
    #
    # data = {}
    # data['id'] = "alpha"
    # data['m1_slack'] = 2
    # data['m1_skill'] = 3
    # data['m1_obj'] = 5
    # rows.append(data)
    #
    ##print(df.loc['beta'])
    # df.loc['beta', ['m1_slack', 'm1_skill', 'm1_obj']] = [7, 8, 15]
    # df.loc['alpha', 'm1_slack'] = "4"
    # print(df)
