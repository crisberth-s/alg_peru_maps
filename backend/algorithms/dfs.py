def find_path(adj, coordinates, start, goal):
    visited = set()
    prev = {start: None}
    stack = [start]

    while stack:
        u = stack.pop()
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
            return path, len(visited), dist/1000
        for v, _ in reversed(adj.get(u, [])):
            if v not in visited:
                prev[v] = u
                stack.append(v)
    return None, len(visited), None