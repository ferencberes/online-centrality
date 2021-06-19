import os
import numpy as np
import pandas as pd
import networkx as nx
from collections import deque
from .base_computer import *

class StaticHarmonicCentralityParams():
    def __init__(self,lookback_cnt=0):
        self.lookback_cnt = lookback_cnt
        if lookback_cnt > 0:
            self.graph_type = "snapshot_%i" % lookback_cnt
        else:
            self.graph_type = "total"
        
    def __str__(self):
        return "hc_%s" % (self.graph_type)

class StaticHarmonicCentralityComputer(BaseComputer):
    def __init__(self,param_list):
        """Input: list of StaticHarmonicCentralityParams objects"""
        self.param_list = param_list
        self.graph_snapshots = [deque([]) for i in range(len(self.param_list))]
        self.stat_hc = None
        
    def update(self,edge,graph,snapshot_graph,time=None):
        """edge=(src,trg)"""
        # This is a static measure. It only needs to be updated at snapshot update
        pass

    def calculate_harmonic_centralities(self,graph,snapshot_graph,epsilon=0.001):
        hc_df = pd.DataFrame()
        for i in range(len(self.param_list)):
            param = self.param_list[i]
            G = nx.DiGraph(graph) if param.lookback_cnt == 0 else get_graph_from_snapshots(self, snapshot_graph, param, i)
            hc_values = nx.harmonic_centrality(G)
            # we want to included zero hc value nodes in output files as well, that is why we add epsilon!
            hc_with_epsilon = pd.Series(hc_values) + epsilon
            new_col_df = pd.DataFrame({str(i):hc_with_epsilon})
            hc_df = hc_df.join(new_col_df, how='outer')
        hc_df.insert(0,"node_id",hc_df.index)
        return hc_df.fillna(0.0).values
        
    def save_snapshot(self,experiment_folder,snapshot_index,graph,snapshot_graph,time=None):
        self.stat_hc = self.calculate_harmonic_centralities(graph,snapshot_graph)
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        for j, param in enumerate(self.param_list):
            output_folder = "%s/%s" % (experiment_folder,param)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            pos_idx = self.stat_hc[:,j+1] > 0 
            active_arr = self.stat_hc[pos_idx][:,[0,j+1]]
            scores2file(active_arr,"%s/hc_%i.csv" % (output_folder,snapshot_index))