import heapq
import json

def parse_graph_data(graph_json: str):
    """
    Parsea una cadena JSON con la forma:
    {
      "A": [["B", 5], ["C", 2]],
      "B": [["A", 5], ["C", 1], ["D", 7]],
      ...
    }
    y devuelve un dict de listas de tuplas (vecino, peso).
    """
    raw = json.loads(graph_json)
    graph = {}
    for node, edges in raw.items():
        graph[node] = [(nbr, float(w)) for nbr, w in edges]
    return graph

def dijkstra(graph: dict, start: str):
    """
    graph: dict[node] = list of (neighbor, weight)
    start: nodo de origen
    Devuelve: (distancias, anteriores)
    - distancias[n] = costo mínimo desde start hasta n
    - anteriores[n] = nodo anterior en el camino óptimo
    """
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    previous  = {node: None for node in graph}
    heap = [(0, start)]

    while heap:
        curr_dist, u = heapq.heappop(heap)
        if curr_dist > distances[u]:
            continue
        for v, w in graph[u]:
            d = curr_dist + w
            if d < distances[v]:
                distances[v] = d
                previous[v] = u
                heapq.heappush(heap, (d, v))

    return distances, previous

def get_path(previous: dict, start: str, end: str):
    """
    Reconstruye la ruta desde `start` hasta `end`
    usando el diccionario `previous` retornado por dijkstra.
    """
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        if curr == start:
            break
        curr = previous[curr]
    path.reverse()
    return path
