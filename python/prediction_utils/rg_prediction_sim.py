import sys, os
import numpy as np

sys.path.append('../')
import evaluation_utils.eval_utils as eu

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

### calculate statistics ###

def calculate_bigger_than_const_ratio(stat_map, measure_id, score_folders, intervals, original_experiment_path, const, filter_keys=None, n_threads=1):
    """Calculate the ratio of scores that is not 'const'."""
    stat_map[measure_id] = {}
    for score in score_folders:
        score_file_path = "%s/%s/" % (original_experiment_path,score)
        if "%s_" % measure_id in score:
            if not is_enabled_by_filter(score, filter_keys):
                continue
            stat_map[measure_id][score] = eu.get_bigger_than_const_ratio_for_days("%s/%s" % (score_file_path,measure_id), const, intervals, n_threads=n_threads)

### calculate player prediction similarities

def load_or_calculate_prediction_result(input_path_prefixes, score, met, intervals, similarity_result_folder, excluded_indices, restricted_indices, n_threads):
    if not os.path.exists(similarity_result_folder):
        os.makedirs(similarity_result_folder)
    similarity_result_file = "%s/%s.txt" % (similarity_result_folder,met)
    if os.path.exists(similarity_result_file):
        res = list(np.loadtxt(similarity_result_file))
        print("Results were loaded from file: %s" % similarity_result_file)
    else:
        res = eu.calculate_measure_for_days(input_path_prefixes, measure_type=met, days=intervals, is_sequential=False, excluded_indices=excluded_indices, restricted_indices=restricted_indices, n_threads=n_threads)
        np.savetxt(similarity_result_file,res)
        print("%s: '%s' was calculated." % (score, met))
    return res

def calculate_metrics_for_prediction(similarity_map, measure_id, metric_id, score_folders, interval_bounds, experiment_paths, similarity_result_folder, excluded_indices=None, restricted_indices=None, filter_keys=None, n_threads=1):
    similarity_map[measure_id] = {}
    for day_idx, _ in interval_bounds:
        similarity_map[measure_id][day_idx] = {}
    for score in score_folders:
        if "%s_" % measure_id in score:
            if not is_enabled_by_filter(score, filter_keys):
                continue
            if not os.path.exists(similarity_result_folder):
                os.makedirs(similarity_result_folder)
            for day_idx, bound in interval_bounds:
                input_path_prefixes = []
                input_path_prefixes.append("%s/%i/players" %  (experiment_paths[0],day_idx)) # label prefix
                input_path_prefixes.append("%s/%s/%s" % (experiment_paths[1], score, measure_id if measure_id != "nbm" else "ndm")) # prediction file prefix
                similarity_res_dir = "%s/%i/%s" % (similarity_result_folder, day_idx, score)
                similarity_map[measure_id][day_idx][score] = load_or_calculate_prediction_result(input_path_prefixes, score, metric_id, range(bound[0],bound[1]), similarity_res_dir, excluded_indices, restricted_indices, n_threads)
    print("prediction analysis was FINISHED")
