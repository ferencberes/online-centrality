import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
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

def custom_katz(G,alpha,max_iter=100,eps=None, use_weights=True):
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
        if eps != None and mean_diff < eps:
            print("Ending at iteration: %i" % i)
            break
    if np.max(katz) == np.inf:
        raise RuntimeError("Katz-index diverged!")
    return dict(zip(G.nodes(),list(katz[0,:])))

def get_graph_with_multiplicity(edge_stream):
    edge_counter = Counter(edge_stream)
    link_with_count = [(u, v, edge_counter[(u,v)] / len(edge_stream)) for u, v in edge_counter]
    M = nx.DiGraph()
    M.add_weighted_edges_from(link_with_count)
    return M

def get_stream(G, iters, pr_alpha=0.85, katz_alphas=[0.05], katz_max_iter=2000, is_custom_katz=True, norm_outdegree=True,  weight='weight', node_sample=None):
    if node_sample == None:
        H = G
    else:
        H = G.subgraph(node_sample)
    print(H.number_of_nodes(),H.number_of_edges())
    # weight normalization only for pagerank
    if norm_outdegree:
        norm = sum(dict(H.out_degree(weight='weight')).values())
    else:
        norm = sum(dict(H.in_degree(weight='weight')).values())
    sampling_edges = {e[:-1]: e[-1]['weight']/norm for e in H.edges(data=True)}
    # sampling
    stream = [list(sampling_edges.keys())[i] for i in np.random.choice(range(len(sampling_edges)), size=iters, p=list(sampling_edges.values()))]
    M = get_graph_with_multiplicity(stream)
    # pagerank for stream
    if norm_outdegree:
        personalization = {k: v / norm for k, v in dict(M.out_degree(weight='weight')).items()}
    else:
        personalization = {k: v / norm for k, v in dict(M.in_degree(weight='weight')).items()}
    pr_basic = nx.pagerank(M, alpha=pr_alpha, personalization=personalization, weight=weight)
    # katz for stream
    katz_basic_list = []
    for katz_alpha in katz_alphas:
        try:
            if is_custom_katz:
                katz_dict = custom_katz(M, alpha=katz_alpha, max_iter=katz_max_iter, use_weights=(weight == 'weight'))
            else:
                katz_dict = nx.katz_centrality(M, alpha=katz_alpha, tol=0.001, max_iter=katz_max_iter, weight=weight)
            katz_basic_list.append(katz_dict)
        except nx.PowerIterationFailedConvergence:
            print("Convergence failed for beta=%.3f" % katz_alpha)
            continue
        except:
            raise
    return (stream, pr_basic, katz_basic_list)

def calculate_self_correlation(c_prefix, idx_order, snapshots, visu=True):
    values = []
    for snapshot_idx in snapshots:
        score_df_x = eu.load_score_map(c_prefix, snapshot_idx, epsilon=0.0)#.reset_index()
        x = [score_df_x.loc[k]["score"] for k in idx_order]
        values.append(x)
    pe_corrs = [pearsonr(values[i], values[i+1])[0] for i in range(len(snapshots)-1)]
    sp_corrs = [spearmanr(values[i], values[i+1])[0] for i in range(len(snapshots)-1)]
    if visu:
        plt.figure(figsize=(20,5))
        plt.plot(snapshots[:-1],pe_corrs, c='b',label="pearson")
        plt.plot(snapshots[:-1],sp_corrs, c='g',label="spearman")
        plt.legend(loc=8)
        plt.title(c_prefix.split("/")[-2])
    return [pe_corrs, sp_corrs]

def get_snapshot_correlations(score_prefix, snapshot_id, delta, iters, static_c_items):
    """Compare centrality measure to ground truth static centrality"""
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
