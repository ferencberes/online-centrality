import os
import numpy as np
import pandas as pd
import networkx as nx
from collections import deque
from .base_computer import *

class StaticNegativeBetaMeasureParams():
    def __init__(self,lookback_cnt=0):
        self.lookback_cnt = lookback_cnt
        if lookback_cnt > 0:
            self.graph_type = "snapshot_%i" % lookback_cnt
        else:
            self.graph_type = "total"
        
    def __str__(self):
        return "nbm_%s" % (self.graph_type)

class StaticNegativeBetaMeasureComputer(BaseComputer):
    def __init__(self,param_list):
        """Input: list of StaticNegativeBetaMeasureParams objects"""
        self.param_list = param_list
        self.graph_snapshots = [deque([]) for i in range(len(self.param_list))]
        self.stat_nbmes = None

    def copy(self):
        params_copy = list(self.param_list)
        snapshots_copy = list(self.graph_snapshots)
        obj_copy = StaticNegativeBetaMeasureComputer(params_copy)
        obj_copy.graph_snapshots = snapshots_copy
        obj_copy.stat_nbmes = np.copy(self.stat_nbmes)
        return obj_copy

    def clear(self):
        self.param_list = None
        self.graph_snapshots = None
        self.stat_nbmes = None

    def update(self,edge,graph,snapshot_graph,time=None,rating=None):
        """edge=(src,trg)"""
        # This is a static measure. It only needs to be updated at snapshot update
        pass

    def calculate_neg_beta_measures(self,graph,snapshot_graph,epsilon=0.001):
        nbmes_df = pd.DataFrame()
        for i in range(len(self.param_list)):
            param = self.param_list[i]
            G = graph if param.lookback_cnt == 0 else get_graph_from_snapshots(self, snapshot_graph, param, i)
            out_deg = G.out_degree()
            # calculate weights for in edges
            rec_out_deg = dict([(n,1.0/out_deg[n] if out_deg[n] > 0 else 1.0) for n in out_deg])
            edges_with_weights = [(link[0],link[1],rec_out_deg[link[0]]) for link in G.edges()]
            # re-initialize the snapshot graph with 'in_weights'
            G.clear()
            G.add_weighted_edges_from(edges_with_weights,weight="in_weight")
            nbmes = G.in_degree(weight="in_weight") # due to the 'in_weight' values on the edges the result is the negative beta measure
            # we want to included zero neg. beta measure nodes in output files as well, that is why we add epsilon!
            nbmes_with_epsilon = pd.Series(nbmes) + epsilon
            new_col_df = pd.DataFrame({str(i):nbmes_with_epsilon})
            nbmes_df = nbmes_df.join(new_col_df, how='outer')
        nbmes_df.insert(0,"node_id",nbmes_df.index)
        return nbmes_df.fillna(0.0).as_matrix()


    def save_snapshot(self,experiment_folder,snapshot_index,graph,snapshot_graph,time=None):
        self.stat_nbmes = self.calculate_neg_beta_measures(graph,snapshot_graph)
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        for j in range(len(self.param_list)):
            neg_beta_mes = self.param_list[j]
            output_folder = "%s/%s" % (experiment_folder,neg_beta_mes)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            pos_idx = self.stat_nbmes[:,j+1] > 0 
            active_arr = self.stat_nbmes[pos_idx][:,[0,j+1]]
            scores2file(active_arr,"%s/ndm_%i.csv" % (output_folder,snapshot_index))