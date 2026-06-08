def find_path(adj, coordinates, start, goal):
    nodes = list(adj.keys())
    dist = {node: float('inf') for node in nodes}
    prev = {node: None for node in nodes}
    dist[start] = 0

    for _ in range(len(nodes)-1):
        updated = False
        for u, neighbors in adj.items():
            if dist[u] == float('inf'):
                continue
            for v, w in neighbors:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    updated = True
        if not updated:
            break

    # Verificar ciclos negativos (no debería haber)
    for u, neighbors in adj.items():
        if dist[u] == float('inf'):
            continue
        for v, w in neighbors:
            if dist[u] + w < dist[v]:
                return None, len(nodes), None

    if dist[goal] == float('inf'):
        return None, len(nodes), None

    path = []
    curr = goal
    while curr is not None:
        path.append(curr)
        curr = prev[curr]
    path.reverse()
    return path, len(nodes), dist[goal]/1000