import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from scipy.stats import pearsonr, spearmanr, kendalltau
import sys, multiprocessing, functools
import temporalkatz.evaluation_utils.eval_utils as eu
from temporalkatz.evaluation_utils.correlation_computer import fast_weighted_kendall
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

def get_top_k_centrality(centrality_item, k=None):
    c_nodes, c_vals = centrality_item
    c_scores = list(zip(c_nodes, c_vals))
    c_df = pd.DataFrame(c_scores, columns=["node_id","score"]).sort_values("score", ascending=False)
    if k != None:
        c_df = c_df.head(k)
    return list(c_df["node_id"]), list(c_df["score"])

def get_sample_index(eval_snapshots, snapshot_id):
    if eval_snapshots.index(snapshot_id) < len(eval_snapshots) / 3:
        sample_index = 0
    elif eval_snapshots.index(snapshot_id) < 2 * len(eval_snapshots) / 3:
        sample_index = 1
    else:
        sample_index = 2
    return sample_index

def get_snapshot_correlations(eval_snapshots, score_prefix, static_c_item, k, snapshot_id):
    """Compare centrality measure to ground truth static centrality"""
    # select proper sample
    sample_index = get_sample_index(eval_snapshots, snapshot_id)
    ordered_keys, ordered_scores = get_top_k_centrality(static_c_item[sample_index],k)
    # load score
    score_df = eu.load_score_map(score_prefix, snapshot_id, epsilon=0.0).reset_index()
    score_df["id"] = score_df.astype("i")
    # normalization
    w = score_df["score"].sum()
    score_df["score"] = score_df["score"] / w
    score_map = dict(zip(score_df["id"],score_df["score"]))
    augmented_score_values = np.array([score_map.get(x,0.0) for x in ordered_keys])
    # calculate correlations
    pearson_val = pearsonr(augmented_score_values, ordered_scores)[0]
    spearman_val = spearmanr(augmented_score_values, ordered_scores)[0]
    kendall_val = kendalltau(augmented_score_values, ordered_scores)[0]
    # custom code
    w_kendall_val = fast_weighted_kendall(augmented_score_values, ordered_scores)[1]
    snapshot_vector = [snapshot_id, pearson_val, spearman_val, kendall_val, w_kendall_val]
    return snapshot_vector

def get_correlations(score_prefix, snapshots, static_c_item, k=None, n_threads=1):
    if n_threads > 1:
        f_partial = functools.partial(get_snapshot_correlations, snapshots, score_prefix, static_c_item, k)
        pool = multiprocessing.Pool(processes=n_threads)
        corrs = np.array(pool.map(f_partial, snapshots))
        pool.close()
        pool.join()
    else:
        corrs = np.array([get_snapshot_correlations(snapshots, score_prefix, static_c_item, k, i) for i in snapshots])
    score_name = score_prefix.split("/")[-2]
    print(score_name,"pearson:",np.mean(corrs[:,1]),"spearman:",np.mean(corrs[:,2]),"kendall:",np.mean(corrs[:,3]),"w_kendall:",np.mean(corrs[:,4]))
    return corrs
