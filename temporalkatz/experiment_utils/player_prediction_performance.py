import os, shutil
import numpy as np
import temporalkatz.evaluation_utils.eval_utils as eu

def get_interval_bounds(num_of_days, lookback_size=2*24):
    interval_bounds = []
    for day_idx in range(0,num_of_days):
        upper_bound = (day_idx+1)*24
        lower_bound = upper_bound - lookback_size
        interval_subset = [max(0,lower_bound),upper_bound]
        interval_bounds += [(day_idx,interval_subset)]
    return interval_bounds

def duplicate_label_files(original_experiment_path, tennis_players_source_path, interval_bounds):
    if not os.path.exists(tennis_players_source_path):
        raise RuntimeError("Node labels haven't been generated yet! First, you have to run 'ScheduleScoreUpdater.ipynb' notebook for the same 'dataset_id'.")
    for day_idx, bounds in interval_bounds:
        target_folder = "%s/%i" % (original_experiment_path, day_idx)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        full_src_file = "%s/players_%i.csv" % (tennis_players_source_path, day_idx)
        for i in range(bounds[0],bounds[1]):
            dest = "%s/players_%i.csv" % (target_folder, i)
            shutil.copy(full_src_file, dest)
        print("Labels for the %ith day were duplicated!" % day_idx)

def is_enabled_by_filter(score, filter_keys):
    if filter_keys != None:
        is_enabled = False
        for f_key in filter_keys:
            if f_key in score:
                is_enabled = True
                break
    else:
        is_enabled = True
    return is_enabled

def load_or_calculate_prediction_result(input_path_prefixes, score, met, intervals, similarity_result_folder, excluded_indices, restricted_indices, always_recompute, n_threads):
    if not os.path.exists(similarity_result_folder):
        os.makedirs(similarity_result_folder)
    similarity_result_file = "%s/%s.txt" % (similarity_result_folder,met)
    if not always_recompute and os.path.exists(similarity_result_file):
        res = list(np.loadtxt(similarity_result_file))
        print("Results were loaded from file: %s" % similarity_result_file)
    else:
        res = eu.calculate_measure_for_days(input_path_prefixes, measure_type=met, days=intervals, is_sequential=False, excluded_indices=excluded_indices, restricted_indices=restricted_indices, n_threads=n_threads)
        np.savetxt(similarity_result_file,res)
        print("%s: '%s' was calculated." % (score, met))
    return res

def calculate_metrics_for_prediction(result_map, measure_id, metric_id, score_folders, interval_bounds, experiment_paths, similarity_result_folder, excluded_indices=None, restricted_indices=None, filter_keys=None, always_recompute=True, n_threads=1):
    result_map[measure_id] = {}
    for day_idx, _ in interval_bounds:
        result_map[measure_id][day_idx] = {}
    for score in score_folders:
        if measure_id == score.split("_")[0]:
            if not is_enabled_by_filter(score, filter_keys):
                continue
            if not os.path.exists(similarity_result_folder):
                os.makedirs(similarity_result_folder)
            for day_idx, bound in interval_bounds:
                input_path_prefixes = []
                input_path_prefixes.append("%s/%i/players" %  (experiment_paths[0],day_idx)) # label prefix
                input_path_prefixes.append("%s/%s/%s" % (experiment_paths[1], score, measure_id)) # prediction file prefix
                similarity_res_dir = "%s/%i/%s" % (similarity_result_folder, day_idx, score)
                result_map[measure_id][day_idx][score] = load_or_calculate_prediction_result(input_path_prefixes, score, metric_id, range(bound[0],bound[1]), similarity_res_dir, excluded_indices, restricted_indices, always_recompute, n_threads)
    print("prediction analysis was FINISHED")