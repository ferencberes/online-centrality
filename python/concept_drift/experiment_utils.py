import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import sys

sys.path.insert(0,"../")
import evaluation_utils.eval_utils as eu

from numpy.linalg import eigvals

def get_1_per_lambda(A):
    max_eig = np.max(eigvals(A))
    if max_eig.imag == 0.0:
        return 1.0 / max_eig.real
    else:
        raise RuntimeError("Maximum eigenvalue is complex!")

def custom_katz(G,alpha,max_iter=1000,eps=0.0001, use_weights=True):
    N = G.number_of_nodes()
    A = nx.to_numpy_array(G)
    if not use_weights:
        A = np.ceil(A) # convert random weight to 1-s
    max_enabled_alpha = get_1_per_lambda(A)
    if alpha > max_enabled_alpha:
        print("Katz with aplha=%0.3f will diverge! The limit is %0.3f" % (alpha,max_enabled_alpha))
    katz = np.zeros((1,N))
    A_sp = alpha * A
    P_sp = np.eye(N)
    for i in range(0, max_iter):
        prev_katz = katz.copy()
        P_sp = np.matmul(P_sp,A_sp)
        col_sum = P_sp.sum(axis=0)
        katz += col_sum
        mean_diff = (katz-prev_katz).mean()
        if mean_diff < eps:
            print("Ending at iteration: %i" % i)
            break
    if np.max(katz) == np.inf:
        raise RuntimeError("Katz-index diverged!")
    return dict(zip(G.nodes(),list(katz[0,:])))

def get_stream(G, iters, pr_alpha=0.85, katz_alpha=0.05, is_custom_katz=True, norm_outdegree=True, random_sample=True, weight='weight'):
    if norm_outdegree:
        norm = sum(dict(G.out_degree(weight='weight')).values())
        sampling_edges = {e[:-1]: e[-1]['weight']/norm for e in G.edges(data=True)}
    else:
        norm = sum(dict(G.in_degree(weight='weight')).values())
        sampling_edges = {e[:-1]: e[-1]['weight']/norm for e in G.edges(data=True)}
    if random_sample:
        stream = [sampling_edges.keys()[i] for i in np.random.choice(range(len(sampling_edges)), size=iters, p=sampling_edges.values())]
    else:
        stream, small_stream = [], list(G.edges())
        ss = len(small_stream)
        for i in range(iters):
            stream.append(small_stream[i % ss])
    # personalized pagerank
    if norm_outdegree:
        personalization = {k: v / norm for k, v in dict(G.out_degree(weight='weight')).iteritems()}
    else:
        personalization = {k: v / norm for k, v in dict(G.in_degree(weight='weight')).iteritems()}
    pr_basic = nx.pagerank(G, alpha=pr_alpha, weight=weight)
    if is_custom_katz:
       katz_basic = custom_katz(G,alpha=katz_alpha,max_iter=1000, use_weights=(weight == 'weight'))
    else:
       katz_basic = nx.katz_centrality(G,alpha=katz_alpha,max_iter=5000, weight=weight)
    return (stream, pr_basic, katz_basic)

def get_snapshot_correlations(score_prefix, snapshot_id, delta, iters, static_c_items):
    """Compare centrality measure to ground truth static centrality for a single snapshot"""
    # load score
    score_df = eu.load_score_map(score_prefix, snapshot_id, epsilon=0.0).reset_index()
    score_df["id"] = score_df.astype("i")
    # normalization
    w = score_df["score"].sum()
    score_df["score"] = score_df["score"] / w
    score_map = dict(zip(score_df["id"],score_df["score"]))
    # select relevance
    if snapshot_id*delta < iters:
        ordered_keys, ordered_scores = static_c_items[0]
    elif snapshot_id*delta < 2*iters:
        ordered_keys, ordered_scores = static_c_items[1]
    else:
        ordered_keys, ordered_scores = static_c_items[2]
    
    # calculate correlations
    augmented_score_values = [score_map.get(x,0.0) for x in ordered_keys]
    res = []
    return [snapshot_id, pearsonr(augmented_score_values, ordered_scores)[0], spearmanr(augmented_score_values, ordered_scores)[0]]

def get_correlations(score_prefix, snapshots, delta, iters, static_c_items, visu=True):
    """Compare centrality measure to ground truth static centrality for multiple snapshots"""
    corrs = np.array([get_snapshot_correlations(score_prefix, i, delta, iters, static_c_items) for i in snapshots])
    score_name = score_prefix.split("/")[-2]
    if visu:
        plt.figure(figsize=(20,5))
        #plt.plot(corrs[:,0],corrs[:,1],label="pearson")
        plt.plot(corrs[:,0],corrs[:,2],label="spearman")
        plt.legend(loc=8)
        plt.xlabel("Snapshot: %i edges by each" % delta)
        plt.title(score_name)
    else:
        print(score_name,"pearson:",np.mean(corrs[:,1]),"spearman:",np.mean(corrs[:,2]))
    return corrs
