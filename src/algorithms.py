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

class PathFinder:
    """Handles pathfinding algorithms"""
    def __init__(self, visualizer, maze_state):
        self.viz = visualizer
        self.maze_state = maze_state
    
    def compute_path(self, algo_name):
        """Compute shortest path using specified algorithm"""
        if self.maze_state.start is None:
            raise ValueError("Start cell not set!")
        if self.maze_state.end is None:
            raise ValueError("End cell not set!")
        
        # Update visualizer references
        self.viz.start = self.maze_state.start
        self.viz.goal = self.maze_state.end
        self.viz.maze = self.maze_state.maze
        
        # Create graph from current maze
        graph = self.viz.maze_to_graph()
        graph.start = self.maze_state.start
        graph.goal = self.maze_state.end
        
        # Convert graph to edges
        edges = []
        for (r, c) in graph.nodes:
            u = self.viz.id_from_coord(r, c)
            for (nr, nc) in graph.neighbors((r, c)):
                v = self.viz.id_from_coord(nr, nc)
                edges.append((u, v, 1))
        
        src_id = self.viz.id_from_coord(*self.maze_state.start)
        dst_id = self.viz.id_from_coord(*self.maze_state.end)
        n = self.maze_state.rows * self.maze_state.cols
        
        # Run selected algorithm
        path_ids = self._run_algorithm(algo_name, n, edges, src_id, dst_id)
        
        if path_ids:
            self.maze_state.shortest_path = [self.viz.coord_from_id(pid) for pid in path_ids]
            print(f"Found path length: {len(self.maze_state.shortest_path)}")
        else:
            self.maze_state.shortest_path = []
            raise ValueError("No path found!")
    
    def _run_algorithm(self, algo_name, n, edges, src_id, dst_id):
        """Execute the specified pathfinding algorithm"""
        if algo_name == "Dijkstra":
            return SPFA_Algorithms.dijkstras(n=n, edges=edges, src=src_id, dst=dst_id)
        elif algo_name == "A*":
            return SPFA_Algorithms.a_star(
                n=n, edges=edges, src=src_id, dst=dst_id,
                heuristic=self._manhattan_heuristic
            )
        elif algo_name == "Bellman-Ford":
            return SPFA_Algorithms.bellman_ford(n=n, edges=edges, src=src_id, dst=dst_id)
        else:
            raise ValueError(f"Unknown algorithm: {algo_name}")
    
    def _manhattan_heuristic(self, node_id):
        """Calculate Manhattan distance heuristic"""
        r, c = self.viz.coord_from_id(node_id)
        er, ec = self.maze_state.end
        return abs(r - er) + abs(c - ec)
