import pandas as pd
import numpy as np

def recall(label_col, prediction_col, k=None, use_random_shuffle=True):
    """Both map should be pandas dataframe column called 'score' with index 'id'!"""
    if use_random_shuffle:
        # do random shuffle due to ties in the predicted scores (prediction_order can change between ties)
        prediction_col = prediction_col.sample(frac=1)
    if k == None:
        raise RuntimeError("You must define 'k' for recall!")
    predicted_items = set(prediction_col.sort_values("score",ascending=False).index[:k])
    relevant_items = set(label_col[label_col["score"] > 0.999].index)
    if len(relevant_items) > 0.0:
        intersection = predicted_items.intersection(relevant_items)
        return 1.0 * len(intersection) / len(relevant_items)
    else:
        return 0.0
    
def precision(label_col, prediction_col, k=None, use_random_shuffle=True):
    """Both map should be pandas dataframe column called 'score' with index 'id'!"""
    if use_random_shuffle:
        # do random shuffle due to ties in the predicted scores (prediction_order can change between ties)
        prediction_col = prediction_col.sample(frac=1)
    if k == None:
        raise RuntimeError("You must define 'k' for precision!")
    predicted_items = set(prediction_col.sort_values("score",ascending=False).index[:k])
    relevant_items = set(label_col[label_col["score"] > 0.999].index)
    if len(relevant_items) > 0.0:
        intersection = predicted_items.intersection(relevant_items)
        return 1.0 * len(intersection) / k
    else:
        return 0.0
