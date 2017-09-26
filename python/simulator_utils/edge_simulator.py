import pandas as pd
import networkx as nx
import re

class EdgeSimulator():
    def __init__(self, predicted_edge_file_path, k=None):
        """Simulate predicted edges for centrality measures in the order of descending ratings."""
        self.init(predicted_edge_file_path, k)
        print(self.simulator_id)
        
    def init(self, predicted_edge_file_path, k):
        self.simulator_id = predicted_edge_file_path.split("/")[-2]
        if k != None:
            self.simulator_id = "%s_first_%i" % (self.simulator_id, k)
        self.delta = int(re.search('.+_d(\d+).*', predicted_edge_file_path.split("/")[-3]).group(1))
        self.score_computer_copies = []
        self.snapshot_graph = nx.DiGraph()
        self.total_graph = nx.DiGraph()
        self.preds = pd.read_csv(predicted_edge_file_path, sep=" ", names=["interval", "src", "trg", "rating"])
        self.top_k = k
        
    def copy_and_clean_score_computers(self, score_computers):
        if len(self.score_computer_copies) > 0:
            self.score_computer_copies = [comp.clear() for comp in self.score_computer_copies]
        self.score_computer_copies = [comp.copy() for comp in score_computers]
        
    def simulate(self, interval_id, last_index, score_computers, experiment_folder, graph):
        self.total_graph = graph.copy()
        self.snapshot_graph.clear()
        self.copy_and_clean_score_computers(score_computers)
        interval_edges = self.preds[self.preds["interval"]==interval_id+1]
        if self.top_k != None:
            interval_edges = interval_edges.head(self.top_k)
        if len(interval_edges) == 0:
            print("Last interval reached for predictions!")
        else:
            predicted_time = last_index + self.delta
            self.process_predicted_links(interval_edges, predicted_time)
            prediction_folder = "%s/predictions/%s" % (experiment_folder, self.simulator_id)
            for sc_copy in self.score_computer_copies:
                sc_copy.save_snapshot(prediction_folder, interval_id+1, time=predicted_time, graph=self.total_graph, snapshot_graph=self.snapshot_graph)
            print("Simulator for snapshot finished: %s" % self.simulator_id)
            
    def process_predicted_links(self, interval_edges, predicted_time):
        edge_tuple_list = interval_edges[["src", "trg"]].as_matrix()
        for link in edge_tuple_list:
            self.total_graph.add_edge(link[0], link[1])
            self.snapshot_graph.add_edge(link[0], link[1])
            for sc_copy in self.score_computer_copies:
                sc_copy.update(link, time=predicted_time, graph=self.total_graph, snapshot_graph=self.snapshot_graph)

                
class ReverseEdgeSimulator(EdgeSimulator):
    """Simulate predicted edges for centrality measures in the order of ascending ratings."""
    def __init__(self, predicted_edge_file_path, k=None):
        self.init(predicted_edge_file_path, k)
        self.simulator_id = "reverse_%s" % self.simulator_id
        print(self.simulator_id)
    
    def process_predicted_links(self, interval_edges, predicted_time):
        edge_tuple_list = interval_edges[["src","trg"]].as_matrix()
        for link in edge_tuple_list[::-1]: # iterate on edges in reverse order
            self.total_graph.add_edge(link[0], link[1])
            self.snapshot_graph.add_edge(link[0], link[1])
            for sc_copy in self.score_computer_copies:
                sc_copy.update(link,time=predicted_time, graph=self.total_graph, snapshot_graph=self.snapshot_graph)
    
    
class RankedEdgeSimulator(EdgeSimulator):
    """Simulate predicted edges for centrality measures in the order of descending ratings with convex combination based on the rating of the edges."""
    def __init__(self, predicted_edge_file_path, k=None):
        self.init(predicted_edge_file_path, k)
        self.simulator_id = "ranked_%s" % self.simulator_id
        print(self.simulator_id)
    
    def process_predicted_links(self, interval_edges, predicted_time):
        max_rating = interval_edges["rating"].max()
        edge_tuple_list = interval_edges[["src", "trg", "rating"]].as_matrix()
        for link in edge_tuple_list:
            self.total_graph.add_edge(link[0], link[1])
            self.snapshot_graph.add_edge(link[0], link[1])
            for sc_copy in self.score_computer_copies:
                sc_copy.update((link[0],link[1]), time=predicted_time, graph=self.total_graph, snapshot_graph=self.snapshot_graph, rating=float(link[2]) / max_rating)
            

class ReverseRankedEdgeSimulator(EdgeSimulator):
    """"""
    def __init__(self, predicted_edge_file_path, k=None):
        self.init(predicted_edge_file_path, k)
        self.simulator_id = "reverseranked_%s" % self.simulator_id
        print(self.simulator_id)
    
    def process_predicted_links(self, interval_edges, predicted_time):
        max_rating = interval_edges["rating"].max()
        edge_tuple_list = interval_edges[["src", "trg", "rating"]].as_matrix()
        for link in edge_tuple_list[::-1]:
            self.total_graph.add_edge(link[0], link[1])
            self.snapshot_graph.add_edge(link[0], link[1])
            for sc_copy in self.score_computer_copies:
                sc_copy.update((link[0], link[1]), time=predicted_time, graph=self.total_graph, snapshot_graph=self.snapshot_graph, rating=float(link[2])/max_rating)