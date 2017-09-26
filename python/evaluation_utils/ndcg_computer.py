import pandas as pd
import numpy as np

def dcg(relevance_map, pred_order, k=None):
    if k == None:
        k = len(pred_order)
    dcg_score = 0.0
    for i in xrange(k):
        pred_id = pred_order[i]
        if pred_id in relevance_map:
            dcg_score += float(relevance_map[pred_id]) / np.log(i+2)
    return dcg_score

def ndcg(relevance_col, prediction_col, k=None, use_random_shuffle=True):
    """Both map should be pandas dataframe column called 'score' with index 'node_id'!"""
    if use_random_shuffle:
        # do random shuffle due to ties in the predicted scores (prediction_order can change between ties)
        prediction_col = prediction_col.sample(frac=1)
    if k == None or (k > len(prediction_col) or k > len(relevance_col)):
        k = min(len(prediction_col),len(relevance_col))
    pred_order = list(prediction_col.sort_values("score",ascending=False).index[:k])
    relevance_order = list(relevance_col.sort_values("score",ascending=False).index[:k])
    relevance_map = dict(relevance_col["score"])
    dcg_val, idcg_val = dcg(relevance_map,pred_order,k=k), dcg(relevance_map,relevance_order,k=k)
    return float(dcg_val) / idcg_val  
