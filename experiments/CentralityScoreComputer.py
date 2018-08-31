# coding: utf-8
import numpy as np

import sys
sys.path.insert(0,"../python/")
import centrality_utils.weight_funtions as wf 
import centrality_utils.temporal_katz_computer as tkc
import centrality_utils.decayed_indegree_computer as dic
import centrality_utils.temporal_pagerank as tprc
import centrality_utils.static_pagerank_computer as sprc
import centrality_utils.static_indegree_computer as sidc
import centrality_utils.static_negative_beta_measure_computer as snbmc
import centrality_utils.static_harmonic_centrality_computer as shcc
from centrality_utils.base_computer import link2str
import simulator_utils.graph_simulator as gsim
from data_processing.tennis_player_processing import load_dataset_parameters

# # 1. Load Parameters

# ### Works only after downloading the tennis player datasets!

#dataset_id = "uo17"
dataset_id = "rg17"

min_epoch, num_days, _, _, _, _ = load_dataset_parameters(dataset_id)

delta = 3600
index_threshold = int(num_days * 86400 / delta + 1)
print(delta, index_threshold)

# # 2. Load Graph Data 

data_path = '../data/%s_data/raw/%s_mentions.csv' % (dataset_id, dataset_id)
score_output_dir = '../data/%s_data/centrality_measures/' % dataset_id

data = np.loadtxt(data_path, delimiter=' ', dtype='i')
print('%s dataset were loaded.' % dataset_id)
print('Number of edges in data: %i.' % len(data))

print(data[:5])

# ## a.) exclude early information

selector = data[:,0] >= min_epoch
data = data[selector,:]
print('Number of edges in data after excluding edges below epoch %i: %i.' % (min_epoch,len(data)))

# ## b.) preprocessing nodes and edges

src_unique = np.unique(data[:,1])
trg_unique = np.unique(data[:,2])
nodes = np.unique(np.concatenate((src_unique,trg_unique)))
edges = [link2str(link) for link in data[:,1:3].tolist()] # element must be string to be hashable
print(len(nodes), len(edges))

print(edges[:3])

# # 3. Compute online centraliy measures

# ## a.) Setting parameters

tk_params, ttk_params, tpr_params, pr_params, indeg_params, nbm_params, hc_params = [], [], [], [], [], [], []
gsim_params = []

# ### Testing just a few parameters (fine parameter testing takes a lot of time)

norm_factors = []
norm_factors += [3600.0 * i for i in [1,2,3,4,6,8,10,12,24]]
print(norm_factors)

if delta == 3600:
    static_lookbacks = [1,2,3,4,6,8,10,12,24]
else:
    static_lookbacks = [0, 1, 2, 4, 7, 14, 21, 30]


# ### Select parameters for TemporalKatzComputer

tk_beta = 1.0 # choose beta for temporal Katz centrality

tk_params = []
tk_params += [tkc.TemporalKatzParams(tk_beta,wf.ExponentialWeighter(base=0.5,norm=n)) for n in norm_factors]

if len(tk_params) > 0:
    gsim_params.append(tkc.TemporalKatzComputer(nodes,tk_params))


# ### Select parameters for TruncatedTemporalKatzComputer

ttk_params = []
ttk_params += [tkc.TruncatedTemporalKatzParams(tk_beta,wf.ExponentialWeighter(base=0.5,norm=n)) for n in norm_factors]

if len(ttk_params) > 0:
    gsim_params.append(tkc.TruncatedTemporalKatzComputer(nodes,ttk_params,k=5))

# ### Select parameters for TemporalPageRankComputer

tpr_params += [tprc.TemporalPageRankParams(0.85,b) for b in [0.001,0.01,0.05,0.1,0.3,0.5,0.9]] 

if len(tpr_params) > 0:
    gsim_params.append(tprc.TemporalPageRankComputer(nodes,tpr_params))


# ### Select parameters for StaticPageRankComputer

pr_params += [sprc.StaticPageRankParams(lookback_cnt=l,alpha=0.85,max_iter=100) for l in static_lookbacks]

if len(pr_params) > 0:
    gsim_params.append(sprc.StaticPageRankComputer(pr_params))


# ### Select parameters for StaticIndegreeComputer

indeg_params += [sidc.StaticIndegreeParams(lookback_cnt=l) for l in static_lookbacks]

if len(indeg_params) > 0:
    gsim_params.append(sidc.StaticIndegreeComputer(indeg_params))

# ### Select parameters for StaticNegativeBetaMeasureComputer

nbm_params += [snbmc.StaticNegativeBetaMeasureParams(lookback_cnt=l) for l in static_lookbacks]

if len(nbm_params) > 0:
    gsim_params.append(snbmc.StaticNegativeBetaMeasureComputer(nbm_params))

# ### Select parameters for StaticHarmonicCentralityComputer

#exclude computation on the total graph
for l in static_lookbacks:
    if l == 0:
        continue
    else:
        hc_params.append(shcc.StaticHarmonicCentralityParams(lookback_cnt=l))

if len(hc_params) > 0:
    gsim_params.append(shcc.StaticHarmonicCentralityComputer(hc_params))

# ### Select parameters for OnlineIndegreeComputer

did_params = []
did_params += [dic.DecayedIndegreeParams(wf.ExponentialWeighter(base=0.5,norm=n)) for n in norm_factors]

gsim_params.append(dic.DecayedIndegreeComputer(nodes,edges,did_params,min_time=min_epoch))

# ## b.) Compute all online scores with one graph simulation

boundaries = min_epoch + np.array([delta*i for i in range(1,index_threshold+1)])

gsim_obj = gsim.OnlineGraphSimulator(data, time_type="epoch", verbose=True)
nexperiment_graph_stats = gsim_obj.run_with_boundaries(gsim_params,boundaries,score_output_dir,max_index=index_threshold)

print("Done")