import os
import numpy as np
import pandas as pd
import networkx as nx
from .base_computer import *

class HarmonicCentralityParams():
    def __init__(self, graph_type, distance=None):
        if graph_type in ["total", "snapshot"]:
            self.graph_type = graph_type
        else:
            raise RuntimeError("Choose 'graph_type' from 'total' or 'snapshot'!")
        self.distance = distance

    def __str__(self):
        return "hc_%s_d_%s" % (self.graph_type, self.distance)


class HarmonicCentralityComputer(BaseComputer):
    def __init__(self, param_list):
        """Input: list of HarmonicCentralityParams objects"""
        self.param_list = param_list
        self.hc = None

    def update(self, edge, graph, snapshot_graph, time=None):
        """edge=(src,trg)"""
        # This is a static measure. It only needs to be updated at snapshot update
        pass

    def calculate_harmonic_centrality(self, graph, snapshot_graph):
        hc_df = pd.DataFrame()
        for i in range(len(self.param_list)):
            param = self.param_list[i]
            G = graph if param.graph_type == "total" else snapshot_graph
            hc_scores = nx.harmonic_centrality(G, distance=param.distance)
            hc_df[str(i)] = pd.Series(hc_scores)
        hc_df.insert(0, "node_id", hc_df.index)
        return hc_df.fillna(0.0).as_matrix()

    def save_snapshot(self, experiment_folder, snapshot_index, graph, snapshot_graph, time=None):
        self.hc = self.calculate_harmonic_centrality(graph, snapshot_graph)
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)
        for j in range(len(self.param_list)):
            param = self.param_list[j]
            output_folder = "%s/%s" % (experiment_folder, param)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            pos_idx = self.hc[:, j+1] > 0
            active_arr = self.hc[pos_idx][:,[0,j+1]]
            scores2file(active_arr, "%s/hc_%i.csv" % (output_folder, snapshot_index))
