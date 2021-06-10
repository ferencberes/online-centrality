import sys, os
import numpy as np
from .base_computer import *
from .weight_funtions import *
from temporalkatz.evaluation_utils.eval_utils import load_score_map

class DecayedIndegreeParams():
    def __init__(self,weight_function=ConstantWeighter(),batch_score_part=""):
        self.batch_score_part = batch_score_part
        self.weight_func = weight_function
        
    def __str__(self):
        if self.batch_score_part != "":
            return "did_%s_%s" % (self.batch_score_part.split("/")[0],str(self.weight_func))
        else:
            return "did_%s" % str(self.weight_func)
        
class DecayedIndegreeComputer(BaseComputer):
    """Indegree with time decay function"""
    def __init__(self,nodes,edges,param_list,min_time=0,storage_ratio=1.8):
        self.param_list = param_list
        self.num_of_nodes, self.num_of_edges = len(nodes), len(edges)
        self.node_indexes, self.edge_indexes = dict(zip(nodes,range(self.num_of_nodes))), dict(zip(edges,range(self.num_of_edges)))
        self.online_ranks = np.zeros((self.num_of_nodes,len(self.param_list)))
        self.node_last_activation = {}
        stored_num_of_edges = int(np.ceil(self.num_of_edges * storage_ratio))
        self.max_edge_index = len(edges)
        self.edge_weights = np.zeros((stored_num_of_edges,len(self.param_list)))
        self.edge_last_activation = np.ones(stored_num_of_edges) * min_time
        self.batch_score_maps = [None for i in range(len(self.param_list))]
        self.batch_score_mins = [0.0 for i in range(len(self.param_list))]
        
    def get_updated_node_rank(self,time,graph,node_id):
        node_index = self.node_indexes[node_id]
        # drop multi-edge instances
        hashed_in_edges = [link2str(link) for link in set(graph.in_edges(nbunch=[node_id]))]
        olr_values = np.zeros(len(self.param_list))
        #num_found = 0
        for h_in_edge in hashed_in_edges:
            edge_index = self.edge_indexes[h_in_edge]  
            time_last_activation = self.edge_last_activation[edge_index]
            delta_time = time - time_last_activation
            time_decaying_weights, batch_scores = [], []
            for idx, param in enumerate(self.param_list):
                time_decaying_weights.append(param.weight_func.weight(delta_time))
                if self.batch_score_maps[idx] is not None:
                    src, _ = str2link(h_in_edge)
                    if float(src) in self.batch_score_maps[idx]:
                        batch_scores.append(self.batch_score_maps[idx][float(src)])
                        #num_found += 1
                    else:
                        batch_scores.append(self.batch_score_mins[idx])
                else:
                    batch_scores.append(1.0)
            olr_values += np.array(batch_scores) * time_decaying_weights
        #print("Num found: %i" % num_found)
        return node_index, olr_values # return updated ranks for scource node

    def get_all_updated_node_ranks(self,time,graph):
        updated_scores = []
        for node in self.node_last_activation:
            node_index = self.node_indexes[node]
            node_index, node_rank = self.get_updated_node_rank(time,graph,node)
            row = [node] + list(node_rank)
            updated_scores.append(row)
        return np.array(updated_scores)

    def update(self,edge,time,graph,snapshot_graph=None):
        src, trg = int(edge[0]), int(edge[1])
        self.node_last_activation[src] = time
        self.node_last_activation[trg] = time
        hashed_edge = link2str(edge)
        try:
            edge_index = self.edge_indexes[hashed_edge]
        except:
            if self.max_edge_index > len(self.edge_weights):
                raise RuntimeError("Cannot store more edge!!!")
            edge_index = self.max_edge_index
            self.edge_indexes[hashed_edge] = edge_index
            self.max_edge_index += 1
        src_node_index, src_updated_ranks = self.get_updated_node_rank(time,graph,src)
        self.online_ranks[src_node_index,:] = src_updated_ranks
        self.edge_weights[edge_index,:] = src_updated_ranks
        self.edge_last_activation[edge_index] = time
        
    def save_snapshot(self,experiment_folder,snapshot_index,time,graph,snapshot_graph=None):
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        all_nodes_updated = self.get_all_updated_node_ranks(time,graph)
        for j, param in enumerate(self.param_list):
            output_folder = "%s/%s" % (experiment_folder, param)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            active_arr = all_nodes_updated[:,[0,j+1]]
            scores2file(active_arr,"%s/did_%i.csv" % (output_folder,snapshot_index))
            self.load_centrality_for_next_interval(j, param, snapshot_index, experiment_folder)
            
    def load_centrality_for_next_interval(self, param_idx, param, snapshot_index, score_root_dir):
        if param.batch_score_part != "":
            file_prefix = "%s/%s" % (score_root_dir, param.batch_score_part)
            scores_df = load_score_map(file_prefix, snapshot_index).reset_index()
            score_dict = dict(zip(scores_df["id"],scores_df["score"]))
            self.batch_score_maps[param_idx] = score_dict
            self.batch_score_mins[param_idx] = min(score_dict.values())
