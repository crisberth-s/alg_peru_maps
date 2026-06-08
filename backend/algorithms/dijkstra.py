import heapq

def find_path(adj, coordinates, start, goal):
    dist = {start: 0}
    prev = {start: None}
    visited = set()
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        if u == goal:
            path = []
            curr = goal
            while curr is not None:
                path.append(curr)
                curr = prev[curr]
            path.reverse()
            return path, len(visited), dist[goal] / 1000
        for v, w in adj.get(u, []):
            if v in visited:
                continue
            new_dist = d + w
            if v not in dist or new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))
    return None, len(visited), None