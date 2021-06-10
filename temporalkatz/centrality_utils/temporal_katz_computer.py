import os
import numpy as np
from .base_computer import *
from .weight_funtions import *

class TemporalKatzParams():
    def __init__(self,beta,weight_function):
        if beta >= 0 and beta <= 1:
            self.beta = beta
        else:
            raise RuntimeError("'beta' must be from interval [0,1]!")
        self.weight_func = weight_function
        
    def __str__(self):
        return "tk_b%0.2f_%s" % (self.beta,str(self.weight_func))

class TemporalKatzComputer(BaseComputer):
    """General temporal Katz centrality implementation"""
    def __init__(self,nodes,param_list):
        self.param_list = param_list
        self.num_of_nodes = len(nodes)
        self.node_indexes = dict(zip(nodes,range(self.num_of_nodes)))
        self.ranks = np.zeros((self.num_of_nodes,len(self.param_list)))
        self.node_last_activation = {}
        
    def get_updated_node_rank(self,time,node_id):
        node_index = self.node_indexes[node_id]
        updated_ranks = self.ranks[node_index,:] # zero vector if node did not appear before
        if node_id in self.node_last_activation:
            delta_time = time - self.node_last_activation[node_id]
            time_decaying_weights = [param.weight_func.weight(delta_time) for param in self.param_list]
            updated_ranks *= time_decaying_weights
        return node_index, updated_ranks
    
    def get_all_updated_node_ranks(self,time):
        updated_scores = []
        for node in self.node_last_activation:
            node_index, node_rank = self.get_updated_node_rank(time,node)
            row = [node] + list(node_rank)
            updated_scores.append(row)
        return np.array(updated_scores)
    
    def update(self,edge,time,graph=None,snapshot_graph=None):
        src, trg = int(edge[0]), int(edge[1])
        beta_vector = [param.beta for param in self.param_list]
        src_index, src_rank = self.get_updated_node_rank(time,src)
        trg_index, trg_rank = self.get_updated_node_rank(time,trg)
        self.ranks[src_index,:] = src_rank
        self.ranks[trg_index,:] = trg_rank + beta_vector * (src_rank + 1) # +1 is for 1 length path
        self.node_last_activation[src] = time
        self.node_last_activation[trg] = time
        
    def save_snapshot(self,experiment_folder,snapshot_index,time,graph=None,snapshot_graph=None):
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        all_nodes_updated = self.get_all_updated_node_ranks(time)
        for j, param in enumerate(self.param_list):
            output_folder = "%s/%s" % (experiment_folder,param)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            active_arr = all_nodes_updated[:,[0,j+1]]
            scores2file(active_arr,"%s/tk_%i.csv" % (output_folder,snapshot_index))
        

class TruncatedTemporalKatzParams():
    def __init__(self,beta,weight_function):
        if beta >= 0 and beta <= 1:
            self.beta = beta
        else:
            raise RuntimeError("'beta' must be from interval [0,1]!")
        self.weight_func = weight_function
        
    def __str__(self):
        return "ttk_b%0.2f_%s" % (self.beta,str(self.weight_func))

class TruncatedTemporalKatzComputer(BaseComputer):
    """Truncated temporal Katz centrality implementation"""
    def __init__(self,nodes,param_list,k=5):
        self.k = k
        self.param_list = param_list
        self.num_of_nodes = len(nodes)
        self.node_indexes = dict(zip(nodes,range(self.num_of_nodes)))
        self.ranks = [np.zeros((self.num_of_nodes,len(self.param_list))) for i in range(k)]
        self.beta_vector = [param.beta for param in self.param_list]
        self.node_last_activation = {}
        
    def get_updated_node_rank(self,layer_idx,time,node_id):
        node_index = self.node_indexes[node_id]
        updated_ranks = self.ranks[layer_idx][node_index,:] # zero vector if node did not appear before
        if node_id in self.node_last_activation:
            delta_time = time - self.node_last_activation[node_id]
            time_decaying_weights = [param.weight_func.weight(delta_time) for param in self.param_list]
            updated_ranks *= time_decaying_weights
        return node_index, updated_ranks
    
    def get_all_updated_node_ranks(self,layer_idx,time):
        updated_scores = []
        for node in self.node_last_activation:
            node_index, node_rank = self.get_updated_node_rank(layer_idx,time,node)
            row = [node] + list(node_rank)
            updated_scores.append(row)
        return np.array(updated_scores)
    
    def update(self,edge,time,graph=None,snapshot_graph=None):
        src, trg = int(edge[0]), int(edge[1])
        # update each layer
        for layer_idx in list(reversed(range(0,self.k))):
            if layer_idx == 0:
                src_rank_shorter = np.zeros(len(self.param_list))
            else:
                _, src_rank_shorter = self.get_updated_node_rank(layer_idx-1,time,src)
            src_index, src_rank = self.get_updated_node_rank(layer_idx,time,src)
            trg_index, trg_rank = self.get_updated_node_rank(layer_idx,time,trg)
            self.ranks[layer_idx][src_index,:] = src_rank
            self.ranks[layer_idx][trg_index,:] = trg_rank + self.beta_vector * (src_rank_shorter + 1) # +1 is for 1 length path
        self.node_last_activation[src] = time
        self.node_last_activation[trg] = time
        
    def save_snapshot(self,experiment_folder,snapshot_index,time,graph,snapshot_graph=None):
        """Exports every truncated score with maximum length from 1 to k"""
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        for layer_idx in list(reversed(range(0,self.k))):
            all_nodes_updated = self.get_all_updated_node_ranks(layer_idx,time)
            for j, param in enumerate(self.param_list):
                output_folder = "%s/%s_length_limit_%i" % (experiment_folder,param,layer_idx+1)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                active_arr = all_nodes_updated[:,[0,j+1]]
                scores2file(active_arr,"%s/ttk_%i.csv" % (output_folder,snapshot_index))