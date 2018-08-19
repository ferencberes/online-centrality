import pandas as pd
import networkx as nx

def link2str(link):
    return str((int(link[0]),int(link[1])))

def scores2file(score_map,output_file):
    """Export scores to .csv files"""
    score_df = pd.DataFrame(score_map,columns=["node_id","score"])
    score_df.to_csv(output_file,sep=" ",header=False,index=False)

def get_graph_from_snapshots(comp, new_snapshot_graph, param, idx):
    """Aggregate multiple graph snapshots. Needed for static PageRank and Indegree."""
    comp.graph_snapshots[idx].append(list(new_snapshot_graph.edges()))
    while len(comp.graph_snapshots[idx]) > param.lookback_cnt:
        comp.graph_snapshots[idx].popleft()
    #print(len(new_snapshot_graph.edges()), len(comp.graph_snapshots[idx]))
    U = nx.DiGraph()
    for e_list in comp.graph_snapshots[idx]:
        #print(len(e_list))
        U.add_edges_from(e_list)
    #print(param.lookback_cnt, len(U.edges()))
    return U    
    
class BaseComputer():
    
    def update(self,edge,time=None,graph=None,snapshot_graph=None):
        pass
    
    def save_snapshot(self,experiment_folder,snapshot_index,time=None,graph=None,snapshot_graph=None):
        pass
    