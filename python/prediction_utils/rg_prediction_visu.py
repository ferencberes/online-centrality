import re
import matplotlib.pyplot as plt


def relabel(score,is_detailed):
    label = score
    if "olr" in score:
        label = label.replace("olr_a0.05_","online-")
        if "Const" in label:
            label = label.replace("(1.00)","")
        elif "Ray" in label:
            m = re.match(".+s([\d,\.]+),n:([\d,\.]+).*", score)
            sigma, norm = m.group(1), m.group(2)
            n_hour = int(norm.replace(".000","")) // 3600
            n_hour_str = str(n_hour) + (" hours" if n_hour > 1 else " hour")
            if is_detailed:
                label = "online-Ray(s:%s,%s)" % (sigma, n_hour_str)
            else:
                label = "online-Ray(%s)" % n_hour_str
        elif "Exp" in label:
            m = re.match(".+b:([\d,\.]+),n:([\d,\.]+).*", score)
            beta, norm = m.group(1), m.group(2)
            n_hour = int(norm.replace(".000","")) // 3600
            n_hour_str = str(n_hour) + (" hours" if n_hour > 1 else " hour")
            if is_detailed:
                label = "online-Exp(b:%s,%s)" % (beta, n_hour_str)
            else:
                label = "online-Exp(%s)" % n_hour_str
    elif "tpr" in score:
        m = re.match("tpr_a([\d,\.]+)_b([\d,\.]+).*", score)
        alpha, beta = m.group(1), m.group(2)
        if beta == "0.00":
            beta = "0.001"
        if is_detailed:
            label = "temp-PR(a%s,b%s)" % (alpha, beta)
        else:
            label = "temp-PR(b%s)" % beta
    else:
        score_id = ""
        if "spr" in score:
            score_id = "PR"
            m = re.match(".+a([\d,\.]+)_i([\d,\.]+).*", score)
            alpha, iters = m.group(1), m.group(2)
            if is_detailed:
                score_id = "PR(a%s,i%s)" % (alpha, iters)
            else:
                score_id = "PR"
        elif "indeg" in score:
            score_id = "indeg"
        elif "hc" in score:
            score_id = "HC"
        elif "nbm" in score:
            score_id = "NBM"
        else:
            raise RuntimeError("Invalid score: %s !!!")
            
        if "total" in score:
            label = "total-%s" % score_id
        else:
            snapshot_idx = score.split("_")[2]
            label = "snapshot-%s-%s" % (snapshot_idx, score_id)
    return label


def plot_non_const_ratio(intervals, dates, score_stat_results, other_data, col, ylabel, custom_palette):
    """Visualize the fraction of non-alpha scores with additional information 'other_data'"""
    num_of_intervals = len(intervals)
    fig, ax1 = plt.subplots(figsize=(20,20))
    if "olr" in score_stat_results:
        sub_dict = score_stat_results["olr"]
        for i, score in enumerate(sorted(sub_dict)):
            c = custom_palette[i % len(custom_palette)]
            ax1.plot(intervals,sub_dict[score],label=relabel(score,False), color=c)
        plt.xlim((0,num_of_intervals))
        plt.xticks(range(0,num_of_intervals,24),dates, rotation=40)
        plt.ylabel("Fraction")
        plt.xlabel("Time (UTC+2 midnight at date labels)")
        plt.legend()
        ax2 = ax1.twinx()
        ax2.plot(intervals, other_data, color=col)
        plt.ylabel(ylabel)