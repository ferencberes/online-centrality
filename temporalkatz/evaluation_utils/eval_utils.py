import sys, os, multiprocessing, functools
import pandas as pd
import numpy as np
from .correlation_computer import *
from .ndcg_computer import *
from .binary_eval_computer import *

### Utils ###

def load_score_map(input_prefix, day, epsilon=0.000000001, excluded_indices=None, restricted_indices=None):
    """TODO: The centrality maps were pre-sorted in decreasing order???"""
    score_file_path = input_prefix + '_%i.csv' % day
    if not os.path.exists(score_file_path):
        raise IOError("File is missing: %s" % score_file_path)
    else:
        scores = pd.read_csv(score_file_path, sep=" ", names=["id","score"])
        # filter for indices
        if restricted_indices != None:
            scores = scores[scores["id"].isin(restricted_indices)]
        else:
            if excluded_indices != None:
                scores = scores[~scores["id"].isin(excluded_indices)]
        # create dict like structure
        scores = scores.set_index("id")
        # all active nodes is set to have positive centrality scores
        if epsilon != None:
            scores["score"] = scores["score"] + epsilon
        return scores


def result2file(result_list,file_name):
    """Write correlation values to file for each snapshot."""
    with open(file_name, 'w') as f:
        if len(result_list) == 1:
            f.write('%f\n' % (result_list[0]))
        else:
            for i in range(len(result_list)):
                f.write('%i %f\n' % (i, result_list[i]))
    print('Done')

    
def get_bigger_than_const_ratio_for_a_day(input_prefix, const, day):
    """Calculate the ratio of scores that is not 'const' for a given day."""
    ratio_list = []
    scores = load_score_map(input_prefix, day, epsilon=0.0)
    return float(len(scores[scores["score"] > const])) / len(scores)


def get_bigger_than_const_ratio_for_days(input_prefix, const, days, n_threads=1):
    """Calculate the ratio of scores that is not 'const' for each day in 'days'."""
    f_partial = functools.partial(get_bigger_than_const_ratio_for_a_day, input_prefix, const)
    pool = multiprocessing.Pool(processes=n_threads)
    res = pool.map(f_partial, days)
    pool.close()
    pool.join()
    return res    
    
    
def calculate_measure_for_a_day(input_prefix, measure_type, is_sequential, excluded_indices, restricted_indices, day, output_prefix=None):
    """Calculate the selected correlation measure for the given snapshot."""
    if is_sequential:
        map_1 = load_score_map(input_prefix, day-1, excluded_indices=excluded_indices, restricted_indices=restricted_indices)
        map_2 = load_score_map(input_prefix, day, excluded_indices=excluded_indices, restricted_indices=restricted_indices)
    else: #pairwise
        if len(input_prefix) != 2:
            raise RuntimeError("Specify 2 input_prefix for pairwise correlations!")
        else:
            # relevance (ground truth)
            map_1 = load_score_map(input_prefix[0], day, excluded_indices=excluded_indices, restricted_indices=restricted_indices)
            # prediction
            map_2 = load_score_map(input_prefix[1], day, excluded_indices=excluded_indices, restricted_indices=restricted_indices)
    if "@" in measure_type:
        top_k = int(measure_type.split("@")[1])
    else:
        top_k = None
    m_val = None
    if "pearson" in measure_type:
        m_val = corr_pearson(map_1,map_2,k=top_k)[0]
    elif "spearman" in measure_type:
        m_val = corr_spearman(map_1,map_2,k=top_k)[0]
    elif "kendall" in measure_type:
        m_val = corr_kendalltau(map_1,map_2,k=top_k)[0]
    elif "w_kendall_fast" in measure_type:
        m_val = corr_weighted_kendalltau(map_1,map_2,use_fast=True)[0]
    elif "recall" in measure_type:
        m_val = recall(map_1,map_2,k=top_k)
    elif "precision" in measure_type:
        m_val = precision(map_1,map_2,k=top_k)
    elif "ndcg" in measure_type:
        if "lin" in measure_type:
            is_log_decay=False
        else:
            is_log_decay=True
        m_val = ndcg(map_1,map_2,k=top_k,is_log_decay=is_log_decay)
    else:
        raise RuntimeError("Invalid correlation type: %s!" % corr_type)
    if output_prefix == None or not is_sequential:
    	return m_val
    else:
        result2file([m_val], '_%i.%s' % (output_prefix, day-1, measure_type))
        

def calculate_measure_for_days(input_prefix, days, measure_type, is_sequential=True, excluded_indices=None, restricted_indices=None, n_threads=1):
    """Calculate the selected correlation measure for multiple snapshots.
    Choose from 'pearson', 'spearman', 'kendall' or 'w_kendall'."""
    if n_threads > 1:
        f_partial = functools.partial(calculate_measure_for_a_day, input_prefix, measure_type, is_sequential, excluded_indices, restricted_indices)
        pool = multiprocessing.Pool(processes=n_threads)
        res = pool.map(f_partial, days)
        pool.close()
        pool.join()
    else:
        res = [calculate_measure_for_a_day(input_prefix, measure_type, is_sequential, excluded_indices, restricted_indices, d) for d in days]
    return res


if __name__ == "__main__":
    if len(sys.argv) == 5:
        input_prefix = sys.argv[1]
        output_prefix = sys.argv[2]
        measure_type = sys.argv[3]
        excluded_indices = None
        day = int(sys.argv[4])
        
        calculate_measure_for_a_day(input_prefix, measure_type, excluded_indices, day, output_prefix)
    else:
        print("Usage: <input_prefix> <output_prefix> <measure_type> <second_day>")

