import heapq

class SPFA_Algorithms:
    @staticmethod
    def dijkstras(n, edges, src, dst):
        adj = {i: [] for i in range(n)}

        # edges: (u,v,w)
        for u, v, w in edges:
            adj[u].append((v, w))

        dist = {i: float("inf") for i in range(n)}
        parent = {i: None for i in range(n)}

        dist[src] = 0
        pq = [(0, src)]

        while pq:
            cur_dist, node = heapq.heappop(pq)

            if node == dst:
                break  # we found the shortest path to the goal

            if cur_dist > dist[node]:
                continue

            for neigh, w in adj[node]:
                new_dist = cur_dist + w
                if new_dist < dist[neigh]:
                    dist[neigh] = new_dist
                    parent[neigh] = node
                    heapq.heappush(pq, (new_dist, neigh))

        # reconstruct path
        path = []
        cur = dst
        while cur is not None:
            path.append(cur)
            cur = parent[cur]

        path.reverse()
        return path    # list of node indices
    
    @staticmethod
    def bellman_ford(n, edges, src, dst):
    
        dist = {i: float("inf") for i in range(n)}
        parent = {i: None for i in range(n)}
        dist[src] = 0

       
        for _ in range(n - 1):
            for u, v, w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    parent[v] = u

        
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                print("Warning: Negative weight cycle detected!")
                return []

      
        if dist[dst] == float("inf"):
            return []  
        path = []
        cur = dst
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path
    
    @staticmethod
    def a_star(n, edges, src, dst, heuristic):

        adj = {i: [] for i in range(n)}
        for u, v, w in edges:
            adj[u].append((v, w))

        g_score = {i: float("inf") for i in range(n)}
        f_score = {i: float("inf") for i in range(n)}
        parent = {i: None for i in range(n)}

        g_score[src] = 0
        f_score[src] = heuristic(src)

        pq = [(f_score[src], src)]

        while pq:
            _, current = heapq.heappop(pq)

            if current == dst:
                break

            for neighbor, w in adj[current]:
                tentative_g = g_score[current] + w
                if tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor)
                    parent[neighbor] = current
                    heapq.heappush(pq, (f_score[neighbor], neighbor))

        if g_score[dst] == float("inf"):
            return []

        path = []
        cur = dst
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path
