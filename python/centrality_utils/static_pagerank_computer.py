import os
import numpy as np
import pandas as pd
import networkx as nx
from collections import deque
from .base_computer import *

class StaticPageRankParams():
    def __init__(self,lookback_cnt=0,alpha=0.85,max_iter=100):
        self.max_iter = max_iter
        self.lookback_cnt = lookback_cnt
        if alpha > 0 and alpha < 1:
            self.alpha = alpha
        else:
            raise RuntimeError("'alpha' must be from interval (0,1)!")
        if lookback_cnt > 0:
            self.graph_type = "snapshot_%i" % lookback_cnt
        else:
            self.graph_type = "total"
        
    def __str__(self):
        return "spr_%s_a%0.2f_i%i" % (self.graph_type,self.alpha,self.max_iter)

    
class StaticPageRankComputer(BaseComputer):
    def __init__(self,param_list):
        """Input: list of StaticPageRankParams objects"""
        self.param_list = param_list
        self.graph_snapshots = [deque([]) for i in range(len(self.param_list))]
        self.stat_pr = None
        
    def update(self,edge,graph,snapshot_graph,time=None):
        """edge=(src,trg)"""
        # This is a static measure. It only needs to be updated at snapshot update
        pass
    
    def calculate_pageranks(self,graph,snapshot_graph):
        pr_df = pd.DataFrame()
        for i in range(len(self.param_list)):
            param = self.param_list[i]
            G = nx.DiGraph(graph) if param.lookback_cnt == 0 else get_graph_from_snapshots(self, snapshot_graph, param, i)
            pr_scores = nx.pagerank(G,alpha=param.alpha,max_iter=param.max_iter) 
            new_col_df = pd.DataFrame({str(i):pd.Series(pr_scores)})
            pr_df = pr_df.join(new_col_df, how='outer')
        pr_df.insert(0,"node_id",pr_df.index)
        return pr_df.fillna(0.0).as_matrix()
        
    def save_snapshot(self,experiment_folder,snapshot_index,graph,snapshot_graph,time=None):
        self.stat_pr = self.calculate_pageranks(graph,snapshot_graph)
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        for j, param in enumerate(self.param_list):
            output_folder = "%s/%s" % (experiment_folder,param)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            pos_idx = self.stat_pr[:,j+1] > 0 
            active_arr = self.stat_pr[pos_idx][:,[0,j+1]]
            scores2file(active_arr,"%s/spr_%i.csv" % (output_folder,snapshot_index))
