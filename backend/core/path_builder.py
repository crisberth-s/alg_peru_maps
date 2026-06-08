def path_to_coordinates(G, path):
    coords = []
    for node in path:
        lat = G.nodes[node]['y']
        lon = G.nodes[node]['x']
        coords.append((lat, lon))
    return coords

def route_distance(G, path):
    if len(path) < 2:
        return 0
    dist = 0
    for u, v in zip(path[:-1], path[1:]):
        edge_data = G.get_edge_data(u, v)
        if edge_data is None:
            continue
        dist += edge_data[0].get('length', 0)
    return dist / 1000