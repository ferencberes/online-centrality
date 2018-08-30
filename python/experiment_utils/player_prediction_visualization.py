import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os

### utils ###

def relabel(score):
    """Extract centrality measure type"""
    return score.split("_")[0]

def extract_time_window(score_name):
    if ",n:" in score_name:
        return float(score_name.split(",n:")[1].split("_")[0][:-1]) / 3600
    elif "_snapshot_" in score_name:
        return float(score_name.split("_snapshot_")[1].split("_")[0])
    else:
        return None
    
def extract_beta(score_name):
    if "0.05_b" in score_name:
        return float(score_name.split("0.05_b")[1].split("_")[0])
    else:
        return None

def extract_params(df):
    """Extract 'time_window' and 'beta' parameters of the centrality measures"""
    df["time_window"] = df["score"].apply(extract_time_window)
    df["beta"] = df["score"].apply(extract_beta)

### Plotters ###

markers = ["s","*","o","^","v",">","D",]

def pred_perf_plot(prediction_results, score_visu_list, interval_bounds, day_idx, offset=0):
    l_bound, u_bound = interval_bounds[day_idx-offset][1][0], interval_bounds[day_idx-offset][1][1]
    x = range(0,u_bound-l_bound)
    visu_args = []
    for i,score in enumerate(score_visu_list):
        score_pref = score.split("_")[0]
        m = markers[i % len(markers)]
        y = prediction_results[score_pref][day_idx][score]
        visu_args += [x,y,"%s-" % m]
    res = plt.plot(*visu_args)
    x_ticks = list(reversed(-np.array(range(0,len(y)+1,5))))
    plt.xticks(range(0,u_bound-l_bound,5),x_ticks)#,rotation="vertical")
    return res

def visu_pred_perf_per_day(prediction_results, score_visu_list, interval_bounds, day_indexes, dates, metric_id, img_dir):
    num_plots = len(day_indexes)
    n_rows, n_cols = num_plots // 2 + 1, 2
    print(n_rows, n_cols, num_plots)
    fig = plt.figure(figsize=(n_cols*10,n_rows*5))
    lines = None
    for i in range(num_plots):
        plt.subplot(n_rows,n_cols,i+1)
        lines = pred_perf_plot(prediction_results, score_visu_list, interval_bounds, day_indexes[i], offset=0)
        plt.ylim((0.0,1.0))
        plt.ylabel(metric_id)
        plt.title(dates[i])
    fig.legend(lines,score_visu_list,(0.55,0.065))
    plt.savefig(img_dir + "/daily_performance_%s.png" % metric_id)

def visu_mean_behaviour(prediction_results, visu_index_list, day_indexes, first_snapshot, last_snapshot, pref, metric_id, img_dir, palette):
    time_series = []
    dir_name = img_dir
    if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    for score in visu_index_list:
        if pref != "mixed" and pref not in score:
            continue
        score_pref = score.split("_")[0]
        for day_idx in range(len(prediction_results[score_pref])):
            perf_values = prediction_results[score_pref][day_idx][score]
            interval_idx = list(reversed(-np.array(range(1,len(perf_values)+1))))
            time_series += list(zip([score for i in interval_idx],[day_idx for i in interval_idx],interval_idx,perf_values))
    if len(time_series) > 0:
        time_series_df = pd.DataFrame(time_series,columns=["score","day","snapshot",metric_id])
        print(len(time_series_df))
        extract_params(time_series_df)
        time_series_df.to_csv("%s/full_table_%s_%s.csv" % (dir_name,pref,metric_id), sep=";", index=False)
        time_series_df = time_series_df[(time_series_df["snapshot"] >= first_snapshot) & (time_series_df["snapshot"] <= last_snapshot)]
        print(len(time_series_df))
        time_series_df = time_series_df[time_series_df["day"].isin(day_indexes)]
        print(len(time_series_df))
        plt.figure(figsize=(22,14))
        score_vals = time_series_df["score"].unique()
        for i,val in enumerate(score_vals):
            c, m = palette[i % len(palette)], markers[i % len(markers)]
            sns.tsplot(data=time_series_df[time_series_df["score"]==val], time="snapshot", unit="day", condition="score", value=metric_id, ci=0.95, color=c, marker=m)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.savefig("%s/mean_%s_%s.png" % (dir_name,pref,metric_id))
    else:
        print("No data to visualize!")