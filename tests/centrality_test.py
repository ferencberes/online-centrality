import os
import numpy as np
import temporalkatz.centrality_utils.weight_funtions as wf
import temporalkatz.centrality_utils.temporal_katz_computer as tkc
import temporalkatz.centrality_utils.temporal_pagerank as tprc
import temporalkatz.simulator_utils.graph_simulator as gsim
from temporalkatz.data_processing.tennis_player_processing import load_dataset_parameters

dirpath = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(dirpath, "..", "data")
test_dir = os.path.join(dirpath, "..", "test_results")

def prepare_data(dataset_id, delta, num_days=1):
    index_threshold = int(num_days * 86400 / delta + 1)
    min_epoch, _, _, _, _, _ = load_dataset_parameters(dataset_id)
    data_path = '%s/%s_data/raw/%s_mentions.csv' % (data_dir, dataset_id, dataset_id)
    score_output_dir = '%s/%s_data/centrality_measures/' % (test_dir, dataset_id)
    data = np.loadtxt(data_path, delimiter=' ', dtype='i')
    print('%s dataset were loaded.' % dataset_id)
    print('Number of edges in data: %i.' % len(data))
    selector = data[:,0] >= min_epoch
    data = data[selector,:]
    print('Number of edges in data after excluding edges below epoch %i: %i.' % (min_epoch,len(data)))
    src_unique = np.unique(data[:,1])
    trg_unique = np.unique(data[:,2])
    nodes = np.unique(np.concatenate((src_unique,trg_unique)))
    return data, nodes, index_threshold, min_epoch, score_output_dir

def test_temporal_katz():
    dataset_id, delta = "rg17", 43200
    data, nodes, index_threshold, min_epoch, score_output_dir = prepare_data(dataset_id, delta)
    params = [tkc.TemporalKatzParams(1.0, wf.RayleighWeighter())]
    gsim_params = [tkc.TemporalKatzComputer(nodes, params)]
    boundaries = min_epoch + np.array([delta*i for i in range(1, index_threshold+1)])
    gsim_obj = gsim.OnlineGraphSimulator(data, time_type="epoch", verbose=True)
    nexperiment_graph_stats = gsim_obj.run_with_boundaries(gsim_params, boundaries, score_output_dir, max_index=index_threshold)
    result_dir = "%s/%s_data/centrality_measures/original/tk_b1.00_Ray(s1.000,n:1.000)" % (test_dir, dataset_id)
    assert len(os.listdir(result_dir)) == 3
    
def test_truncated_temporal_katz():
    dataset_id, delta = "rg17", 4*3600
    data, nodes, index_threshold, min_epoch, score_output_dir = prepare_data(dataset_id, delta)
    params = [tkc.TruncatedTemporalKatzParams(1.0, wf.ExponentialWeighter(base=0.5, norm=7200))]
    gsim_params = [tkc.TruncatedTemporalKatzComputer(nodes, params, k=5)]
    boundaries = min_epoch + np.array([delta*i for i in range(1, index_threshold+1)])
    gsim_obj = gsim.OnlineGraphSimulator(data, time_type="epoch", verbose=True)
    nexperiment_graph_stats = gsim_obj.run_with_boundaries(gsim_params, boundaries, score_output_dir, max_index=index_threshold)
    result_dir = "%s/%s_data/centrality_measures/original/ttk_b1.00_Exp(b:0.500,n:7200.000)_length_limit_5" % (test_dir, dataset_id)
    assert len(os.listdir(result_dir)) == 7
    
def test_temporal_pagerank():
    dataset_id, delta = "rg17", 2*3600
    data, nodes, index_threshold, min_epoch, score_output_dir = prepare_data(dataset_id, delta)
    params = [tprc.TemporalPageRankParams(0.85, 0.05)]
    gsim_params = [tprc.TemporalPageRankComputer(nodes, params)]
    boundaries = min_epoch + np.array([delta*i for i in range(1, index_threshold+1)])
    gsim_obj = gsim.OnlineGraphSimulator(data, time_type="epoch", verbose=True)
    nexperiment_graph_stats = gsim_obj.run_with_boundaries(gsim_params, boundaries, score_output_dir, max_index=index_threshold)
    result_dir = "%s/%s_data/centrality_measures/original/tpr_a0.85_b0.05/" % (test_dir, dataset_id)
    assert len(os.listdir(result_dir)) == 13