import re

def handle_exp(label_first_part,score,is_detailed):
    m = re.match(".+b:([\d,\.]+),n:([\d,\.]+).*", score)
    beta, norm = m.group(1), m.group(2)
    n_hour = int(norm.replace(".000","")) // 3600
    n_hour_str = str(n_hour) + (" hours" if n_hour > 1 else " hour")
    if is_detailed:
        label = label_first_part + "-Exp(b:%s,%s)" % (beta, n_hour_str)
    else:
        label = label_first_part + "-Exp(b:%s,%s)" % (beta, n_hour_str)
    return label

def handle_ray(label_first_part,score,is_detailed):
    m = re.match(".+s([\d,\.]+),n:([\d,\.]+).*", score)
    sigma, norm = m.group(1), m.group(2)
    n_hour = int(norm.replace(".000","")) // 3600
    n_hour_str = str(n_hour) + (" hours" if n_hour > 1 else " hour")
    if is_detailed:
        label = label_first_part + "-Ray(s:%s,%s)" % (sigma, n_hour_str)
    else:
        label = label_first_part + "-Ray(%s)" % n_hour_str
    return label
                
def relabel(score,is_detailed):
    label = score
    if "olr" in score:
        label = label.replace("olr_a0.05_","online-")
        label_splits = label.split("_")
        label_first_part = label_splits[0] if len(label_splits) == 2 else "online"
        if "Const" in label:
            label = label.replace("(1.00)","")
        elif "Ray" in label:
            label = handle_ray(label_first_part,score,is_detailed)
        elif "Exp" in label:
            label = handle_exp(label_first_part,score,is_detailed)
    elif "olid" in score:
        if "hc" in score:
            label_first_part = "indeg" + "_" + "_".join(score.split("_")[1:4])
        else:
            label_first_part = "indeg"
        if "Ray" in label:
            label = handle_ray(label_first_part,score,is_detailed)
        elif "Exp" in label:
            label = handle_exp(label_first_part,score,is_detailed)
        else:
            raise RuntimeError("Invalid online indegree configuration!!!")
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

def extract_time_window(score_name):
    if ",n:" in score_name:
        return float(score_name.split(",n:")[1][:-1]) / 3600
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
    df["time_window"] = df["score"].apply(extract_time_window)
    df["olr_beta"] = df["score"].apply(extract_beta)
