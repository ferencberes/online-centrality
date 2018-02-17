import os
import numpy as np
import pandas as pd
import networkx as nx
from collections import deque
from .base_computer import *

class StaticIndegreeParams():
    def __init__(self,lookback_cnt=0):
        self.lookback_cnt = lookback_cnt
        if lookback_cnt > 0:
            self.graph_type = "snapshot_%i" % lookback_cnt
        else:
            self.graph_type = "total"
        
    def __str__(self):
        return "indeg_%s" % (self.graph_type)

    
class StaticIndegreeComputer(BaseComputer):
    def __init__(self,param_list):
        """Input: list of StaticIndegreeParams objects"""
        self.param_list = param_list
        self.graph_snapshots = [deque([]) for i in range(len(self.param_list))]
        self.stat_indeg = None
        
    def copy(self):
        params_copy = list(self.param_list)
        snapshots_copy = list(self.graph_snapshots)
        obj_copy = StaticIndegreeComputer(params_copy)
        obj_copy.graph_snapshots = snapshots_copy
        obj_copy.stat_indeg = np.copy(self.stat_indeg)
        return obj_copy
    
    def clear(self):
        self.param_list = None
        self.graph_snapshots = None
        self.stat_indeg = None
        
    def update(self,edge,graph,snapshot_graph,time=None,rating=None):
        """edge=(src,trg)"""
        # This is a static measure. It only needs to be updated at snapshot update
        pass
    
    def calculate_indegrees(self,graph,snapshot_graph,epsilon=0.001):
        indeg_df = pd.DataFrame()
        for i in range(len(self.param_list)):
            param = self.param_list[i]
            G = graph if param.lookback_cnt == 0 else get_graph_from_snapshots(self, snapshot_graph, param, i)
            in_degs = dict(G.in_degree())
            # we want to included zero indegree nodes in output files as well, that is why we add epsilon!
            indeg_with_epsilon = pd.Series(in_degs) + epsilon
            new_col_df = pd.DataFrame({str(i):indeg_with_epsilon})
            indeg_df = indeg_df.join(new_col_df, how='outer')
        indeg_df.insert(0,"node_id",indeg_df.index)
        return indeg_df.fillna(0.0).as_matrix()
        
    def save_snapshot(self,experiment_folder,snapshot_index,graph,snapshot_graph,time=None):
        self.stat_indeg = self.calculate_indegrees(graph,snapshot_graph)
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        for j in range(len(self.param_list)):
            indeg = self.param_list[j]
            output_folder = "%s/%s" % (experiment_folder,indeg)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            pos_idx = self.stat_indeg[:,j+1] > 0 
            active_arr = self.stat_indeg[pos_idx][:,[0,j+1]]
            scores2file(active_arr,"%s/indeg_%i.csv" % (output_folder,snapshot_index))
