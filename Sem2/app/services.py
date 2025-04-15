from app.schemas import GraphRequest, PathResult
def branch_and_bound_tsp(distance_matrix):
    n = len(distance_matrix)
    min_distance = float('inf')
    best_route = None
    def tsp(node, visited, cost, path):
        nonlocal min_distance, best_route
        if len(path) == n:
            cost += distance_matrix[node][0]
            if cost < min_distance:
                min_distance = cost
                best_route = path
            return
        for next_node in range(n):
            if next_node not in visited:
                tsp(next_node, visited | {next_node}, cost + distance_matrix[node][next_node], path + [next_node])
    tsp(0, {0}, 0, [0])
    return best_route, min_distance

def findShortestPath(graphR: GraphRequest):
    graph = graphR.graph
    distance_matrix = [[float('inf')] * len(graph.nodes) for _ in range(len(graph.nodes))]
    for row in graph.edges:
        distance_matrix[row[0] - 1][row[1] - 1] = 1
        distance_matrix[row[1] - 1][row[0] - 1] = 1
    for i in range(len(graph.nodes)):
        distance_matrix[i][i] = 0
    ans = branch_and_bound_tsp(distance_matrix)
    if ans[1] >= float('inf'): return ("No answer")
    return PathResult(path = list(map(lambda x: x+1, ans[0])), total_distance = float(ans[1]))