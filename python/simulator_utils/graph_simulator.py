import networkx as nx
import sys
sys.path.insert(0,"../")
from centrality_utils.base_computer import BaseComputer
import graph_extractor as ge
    
class OnlineGraphSimulator():
    def __init__(self,graph_array,time_type="epoch",verbose=False):
        """Graph simulator for calculating centrality scores in each snapshot. Use 'time_type'='epoch' if the elapsed time is measures in seconds, or 'time_type'='index' if the elapsed time is measures in the number of edges."""
        timestamps, edge_map, num_edges = ge.store_edges(graph_array)
        if time_type not in ["index","epoch"]:
            raise RuntimeError("Invalid time_type")
        self.verbose = verbose
        self.time_type = time_type
        self.timestamps = sorted(timestamps)
        self.edge_map = edge_map
        self.num_edges = num_edges
        
    def take_snapshot(self, interval_id, current_time, score_computers, experiment_folder, snapshot_graph, edge_simulators):
        """When a snapshot boundary is reached in the simulation, the simulator will export the current centrality scores to files if 'edge_simulators'=None. Otherwise it will simulate scores on the predicted links."""
        total_num_nodes, total_num_edges, snapshot_num_nodes, snapshot_num_edges = len(self.graph.nodes()), len(self.graph.edges()), len(snapshot_graph.nodes()), len(snapshot_graph.edges())
        if edge_simulators != None:
            # simulate the next interval with edge_simulators
            for e_sim in edge_simulators:
                e_sim.simulate(interval_id, current_time, score_computers, experiment_folder, self.graph)
        else:
            # export original centrality scores
            for comp in score_computers:
                comp.save_snapshot(experiment_folder+"/original", interval_id, time=current_time, graph=self.graph, snapshot_graph=snapshot_graph)
            print("Snapshot processed: interval_id=%i, boundary=%i" % (interval_id, current_time))
            if self.verbose:
                print("   Total graph: #nodes=%i, #edges=%i" % (total_num_nodes, total_num_edges))
                print("   Snapshot graph: #nodes=%i, #edges=%i" % (snapshot_num_nodes, snapshot_num_edges))
        snapshot_graph.clear()
        return [total_num_nodes, total_num_edges, snapshot_num_nodes, snapshot_num_edges]
        
    def update_for_epoch(self, score_computers, timestamp, snapshot_graph):
        """Update score computers with all links in the current epoch"""
        for link in self.edge_map[timestamp]:
            self.graph.add_edge(link[0],link[1])
            snapshot_graph.add_edge(link[0],link[1])
            # update scores
            for comp in score_computers:
                comp.update(link, time=timestamp, graph=self.graph, snapshot_graph=snapshot_graph)
        
    def _run_with_epoch_boundaries(self, score_computers, boundaries, experiment_folder, max_index=None, edge_simulators=None):
        """'boundaries' must contain integers, which represent epochs. These will be the score evaluation barriers."""
        print("'run_with_epoch_boundaries' will be executed!")
        num_epochs = len(self.timestamps)
        prev_epoch, current_epoch = -1, 0
        interval_id = 0
        terminate_loop = False
        self.graph = nx.DiGraph()
        snapshot_graph = nx.DiGraph()
        experiment_graph_stats = []
        for epoch_idx in range(num_epochs):
            current_epoch = self.timestamps[epoch_idx]
            is_updated = False
            if current_epoch <= boundaries[interval_id]:
                self.update_for_epoch(score_computers, current_epoch, snapshot_graph)
                is_updated = True
            # handle inactive intervals (when there is no edge in the interval)
            while (not terminate_loop) and current_epoch >= boundaries[interval_id]:
                # NOTE: the last incomplete interval snapshot will not be saved!!! We should inspect whether we are at the last epoch in data!!!
                if (max_index != None and interval_id >= max_index-1) or interval_id == len(boundaries)-1:
                    terminate_loop = True
                if terminate_loop or (current_epoch >= boundaries[interval_id] and prev_epoch < boundaries[interval_id]):
                    snapshot_graph_stats = self.take_snapshot(interval_id, boundaries[interval_id], score_computers, experiment_folder, snapshot_graph, edge_simulators)
                    experiment_graph_stats.append(snapshot_graph_stats)
                    if terminate_loop:
                        print("Termination: interval_id=%i" % interval_id)
                        return experiment_graph_stats
                    interval_id += 1
            if not is_updated:
                self.update_for_epoch(score_computers, current_epoch, snapshot_graph)         
                is_updated = True
            prev_epoch = current_epoch
        # save last snapshot if all links have been prosessed
        if interval_id > 1 and current_epoch > boundaries[interval_id-1] and current_epoch < boundaries[interval_id]:
            snapshot_graph_stats = self.take_snapshot(interval_id, boundaries[interval_id], score_computers, experiment_folder, snapshot_graph, edge_simulators)
            experiment_graph_stats.append(snapshot_graph_stats)
            print("Termination: idx=%i. All links have been prosessed!" % interval_id)
        return experiment_graph_stats
        
    def _run_with_edge_boundaries(self, score_computers, boundaries, experiment_folder, max_index=None, edge_simulators=None):
        """'boundaries' must contain integers, which represent edge indices. These will be the score evaluation barriers."""
        print("'run_with_edge_boundaries' will be executed!")
        num_epochs = len(self.timestamps)
        edge_idx = 1
        interval_id = 0
        terminate_loop = False
        self.graph = nx.DiGraph()
        snapshot_graph = nx.DiGraph()
        experiment_graph_stats = []
        for epoch_idx in range(num_epochs):
            timestamp = self.timestamps[epoch_idx]
            for link in self.edge_map[timestamp]:
                self.graph.add_edge(link[0],link[1])
                snapshot_graph.add_edge(link[0],link[1])
                # update scores
                for comp in score_computers:
                    comp.update(link,time=edge_idx,graph=self.graph,snapshot_graph=snapshot_graph)
                if (max_index != None and edge_idx >= max_index) or (interval_id == len(boundaries)-1 and edge_idx == boundaries[-1]) or edge_idx == self.num_edges:
                    terminate_loop = True
                # take snapshot
                if terminate_loop or edge_idx == boundaries[interval_id]:
                    snapshot_graph_stats = self.take_snapshot(interval_id, boundaries[interval_id], score_computers, experiment_folder, snapshot_graph, edge_simulators)
                    experiment_graph_stats.append(snapshot_graph_stats)
                    if terminate_loop:
                        print("Termination: interval_id=%i" % interval_id)
                        return experiment_graph_stats
                    interval_id += 1
                edge_idx += 1
        return experiment_graph_stats
                
    def run_with_boundaries(self,score_computers,boundaries,experiment_folder,max_index=None,edge_simulators=None):
        """'boundaries' must contain integers. Simulation is based on 'time_type' parameter of this object!!!"""
        for i in range(len(score_computers)):
            if not isinstance(score_computers[i],BaseComputer):
                raise RuntimeError("The %ith computer does NOT extend BaseComputer!" % (i+1))
        if self.time_type == "index":
            experiment_graph_stats = self._run_with_edge_boundaries(score_computers, boundaries, experiment_folder, max_index=max_index, edge_simulators=edge_simulators)
        else:
            experiment_graph_stats = self._run_with_epoch_boundaries(score_computers, boundaries, experiment_folder, max_index=max_index, edge_simulators=edge_simulators)
        return experiment_graph_stats
    
    """
    def run(self,score_computers,experiment_folder,delta,max_index=None,edge_simulators=None):
        for i in range(len(score_computers)):
            if not isinstance(score_computers[i],BaseComputer):
                raise RuntimeError("The %ith computer does NOT extend BaseComputer!" % (i+1))
        edge_idx = 0
        interval_id = 0
        terminate_loop = False  
        num_epochs = len(self.timestamps)
        last_snapshot_epoch = self.timestamps[0]
        self.graph = nx.DiGraph()
        snapshot_graph = nx.DiGraph()
        
        for epoch_idx in range(num_epochs):
            timestamp = self.timestamps[epoch_idx]
            for link in self.edge_map[timestamp]:
                self.graph.add_edge(link[0],link[1])
                snapshot_graph.add_edge(link[0],link[1])
                # update scores
                current_time = edge_idx if self.time_type == "index" else timestamp
                for comp in score_computers:
                    comp.update(link,time=current_time,graph=self.graph,snapshot_graph=snapshot_graph)
                # define index and termination
                if self.time_type == "index":
                    idx = edge_idx
                    export_snapshot = True if (idx % delta == 0 and idx > 0) else False
                if self.time_type == "epoch":
                    idx = (timestamp-self.timestamps[0]) // delta
                    export_snapshot = timestamp - last_snapshot_epoch > delta
                    if export_snapshot:
                        last_snapshot_epoch = timestamp
                
                if max_index != None and idx >= max_index-1:
                    terminate_loop = True
                    
                # export snapshot
                if export_snapshot or terminate_loop:
                    if edge_simulators != None:
                        # simulate the next interval with edge_simulators
                        last_index = edge_idx if self.time_type == "index" else timestamp
                        for e_sim in edge_simulators:
                            e_sim.simulate(interval_id,last_index,score_computers,experiment_folder,self.graph)
                    else:
                        # export original centrality scores
                        for comp in score_computers:
                            comp.save_snapshot(experiment_folder+"/original", interval_id,time=current_time,graph=self.graph,snapshot_graph=snapshot_graph)
                    print("Snapshot processed: idx=%i" % interval_id)
                    if self.verbose:
                        print("   Total graph: #nodes=%i, #edges=%i" % (len(self.graph.nodes()),len(self.graph.edges())))
                        print("   Snapshot graph: #nodes=%i, #edges=%i" % (len(snapshot_graph.nodes()),len(snapshot_graph.edges())))
                    if terminate_loop:
                        print("Termination: idx=%i" % interval_id)
                        return
                    snapshot_graph.clear()
                    interval_id += 1
                edge_idx += 1
    """
