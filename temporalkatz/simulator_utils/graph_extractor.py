import numpy as np

def extract_vertices(edge_data):
    """Extract the nodes of the graph from its edges"""
    all_v_id = np.append(edge_data[:,1], edge_data[:,2], axis=0)
    return set(all_v_id)

def store_edges(edge_data):
    """Store edges in a dict where the keys are the edge times"""
    time_edge_map = {}
    for i in range(len(edge_data)):
        current_time = edge_data[i,0]
        if not current_time in time_edge_map:
            time_edge_map[current_time] = []
        time_edge_map[current_time].append(edge_data[i,1:3].tolist())
    
    sorted_times = sorted(time_edge_map.keys())
    print('Number of unique epochs: ' + str(len(sorted_times)))
    return sorted_times, time_edge_map, len(edge_data)

