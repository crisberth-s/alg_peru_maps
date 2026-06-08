import heapq
from math import radians, sin, cos, sqrt, asin

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

def find_path(adj, coordinates, start, goal):
    if start not in coordinates or goal not in coordinates:
        return None, 0, None
    lat_goal, lon_goal = coordinates[goal]
    g_score = {start: 0}
    f_score = {start: haversine(*coordinates[start], lat_goal, lon_goal)}
    prev = {start: None}
    open_set = [(f_score[start], start)]
    visited = set()

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
            return path, len(visited), g_score[goal] / 1000
        for v, w in adj.get(u, []):
            if v in visited:
                continue
            tentative_g = g_score[u] + w
            if v not in g_score or tentative_g < g_score[v]:
                g_score[v] = tentative_g
                prev[v] = u
                lat_v, lon_v = coordinates[v]
                h = haversine(lat_v, lon_v, lat_goal, lon_goal)
                f_score[v] = tentative_g + h
                heapq.heappush(open_set, (f_score[v], v))
    return None, len(visited), None