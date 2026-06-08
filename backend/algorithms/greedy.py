import heapq
from backend.algorithms.astar import haversine

def find_path(adj, coordinates, start, goal):
    if start not in coordinates or goal not in coordinates:
        return None, 0, None
    lat_goal, lon_goal = coordinates[goal]
    prev = {start: None}
    open_set = []
    visited = set()
    h_start = haversine(*coordinates[start], lat_goal, lon_goal)
    heapq.heappush(open_set, (h_start, start))

    while open_set:
        _, u = heapq.heappop(open_set)
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
            dist = 0
            for i in range(len(path)-1):
                for v, w in adj.get(path[i], []):
                    if v == path[i+1]:
                        dist += w
                        break
            return path, len(visited), dist/1000 if dist > 0 else None
        for v, w in adj.get(u, []):
            if v in visited:
                continue
            if v not in [item[1] for item in open_set]:
                h = haversine(*coordinates[v], lat_goal, lon_goal)
                heapq.heappush(open_set, (h, v))
                prev[v] = u
    return None, len(visited), None