from collections import deque

def find_path(adj, coordinates, start, goal):
    visited = set()
    prev = {start: None}
    queue = deque([start])
    visited.add(start)

    while queue:
        u = queue.popleft()
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
            return path, len(visited), dist/1000 if dist else None
        for v, _ in adj.get(u, []):
            if v not in visited:
                visited.add(v)
                prev[v] = u
                queue.append(v)
    return None, len(visited), None