import os, multiprocessing, functools
import numpy as np
from .base_computer import *
from .weight_funtions import *

def link2str(link):
    return str((int(link[0]),int(link[1])))

class OnlineRankParams():
    def __init__(self,alpha=0.05,beta=1.0,weight_function=ConstantWeighter()):
        if alpha > 0 and alpha < 1:
            self.alpha = alpha
        else:
            raise RuntimeError("'alpha' must be from interval (0,1)!")
        if beta >= 0 and beta <= 1:
            self.beta = beta
        else:
            raise RuntimeError("'beta' must be from interval [0,1]!")
        self.weight_func = weight_function
        
    def __str__(self):
        return "olr_a%0.2f_b%0.2f_%s" % (self.alpha,self.beta,str(self.weight_func))

class OnlineRankComputer(BaseComputer):
    """Implementation of Andras"s idea with multiple parameters: version 4.0"""
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
        
    def copy(self):
        params_copy = list(self.param_list)
        obj_copy = OnlineRankComputer([],[],params_copy)
        obj_copy.num_of_nodes = self.num_of_nodes
        obj_copy.node_indexes = self.node_indexes.copy()
        obj_copy.edge_indexes = self.edge_indexes.copy()
        obj_copy.online_ranks = np.copy(self.online_ranks)
        obj_copy.max_edge_index = self.max_edge_index
        obj_copy.edge_weights = np.copy(self.edge_weights)
        obj_copy.edge_last_activation = np.copy(self.edge_last_activation)
        obj_copy.node_last_activation = self.node_last_activation.copy()
        return obj_copy
    
    def clear(self):
        self.param_list = None
        self.node_indexes = None
        self.edge_indexes = None
        self.online_ranks = None
        self.max_edge_index = None
        self.edge_weights = None
        self.edge_last_activation = None
        self.node_last_activation = None
        
    def get_updated_node_rank(self,time,graph,node_id,rating=None):
        node_index = self.node_indexes[node_id]
        hashed_in_edges = [link2str(link) for link in graph.in_edges(nbunch=[node_id])]
        olr_values = [param.alpha for param in self.param_list]
        for h_in_edge in hashed_in_edges:
            edge_index = self.edge_indexes[h_in_edge]  
            time_last_activation = self.edge_last_activation[edge_index]
            delta_time = time - time_last_activation
            time_decaying_weights = [param.beta * param.weight_func.weight(delta_time) for param in self.param_list]
            olr_values += self.edge_weights[edge_index,:] * time_decaying_weights
        if rating != None: # combine updated value with old value based on rating
            olr_values = rating * np.array(olr_values) + (1.0-rating) * self.online_ranks[node_index,:]
        return node_index, olr_values # return updated ranks for scource node
    
    def get_all_updated_node_ranks(self,time,graph):
        updated_scores = []
        for node in self.node_last_activation:
            node_index = self.node_indexes[node]
            node_index, node_rank = self.get_updated_node_rank(time,graph,node)
            row = [node] + list(node_rank)
            updated_scores.append(row)
        return np.array(updated_scores)
    
    def update(self,edge,time,graph,snapshot_graph=None,rating=None):
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
        src_node_index, src_updated_ranks = self.get_updated_node_rank(time,graph,src,rating=rating)
        self.online_ranks[src_node_index,:] = src_updated_ranks
        self.edge_weights[edge_index,:] = src_updated_ranks
        self.edge_last_activation[edge_index] = time
        
    def save_snapshot(self,experiment_folder,snapshot_index,time,graph,snapshot_graph=None):
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        all_nodes_updated = self.get_all_updated_node_ranks(time,graph)
        for j in range(len(self.param_list)):
            tpr = self.param_list[j]
            output_folder = "%s/%s" % (experiment_folder,tpr)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            active_arr = all_nodes_updated[:,[0,j+1]]
            scores2file(active_arr,"%s/olr_%i.csv" % (output_folder,snapshot_index))
        
