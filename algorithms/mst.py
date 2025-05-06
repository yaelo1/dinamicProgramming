import json
from typing import List, Tuple, Optional, Dict
import heapq


def parse_mst_data(json_str: str) -> List[Tuple[str, str, float]]:
    """
    Espera un JSON con clave "edges" que sea una lista de tripletas [u, v, peso].
    Devuelve una lista de tuplas (u, v, peso=float).
    """
    data = json.loads(json_str)
    if "edges" not in data or not isinstance(data["edges"], list):
        raise ValueError("El JSON debe contener una clave 'edges' con una lista de aristas")
    edges: List[Tuple[str, str, float]] = []
    for idx, e in enumerate(data["edges"]):
        if (not isinstance(e, list) or len(e) != 3
                or not isinstance(e[0], str)
                or not isinstance(e[1], str)
                or not isinstance(e[2], (int, float))):
            raise ValueError(f"Arista inválida en posición {idx}: {e}")
        edges.append((e[0], e[1], float(e[2])))
    return edges


def solve_mst_undirected(edges: List[Tuple[str, str, float]]) -> Tuple[float, List[Tuple[str, str, float]]]:
    """
    Implementación optimizada de Prim usando heap y lista de adyacencia.
    Ideal para grafos dispersos.
    """
    # Mapeo de nodos a índices
    idx: Dict[str, int] = {}
    for u, v, _ in edges:
        if u not in idx:
            idx[u] = len(idx)
        if v not in idx:
            idx[v] = len(idx)
    n = len(idx)

    # Lista inversa de nombres
    names = [None] * n
    for name, i in idx.items():
        names[i] = name

    # Construir lista de adyacencia: lista de (peso, vecino)
    adj: List[List[Tuple[float, int]]] = [[] for _ in range(n)]
    for u, v, w in edges:
        ui, vi = idx[u], idx[v]
        adj[ui].append((w, vi))
        adj[vi].append((w, ui))

    visited = [False] * n
    total_cost = 0.0
    mst_edges: List[Tuple[str, str, float]] = []

    heap: List[Tuple[float, int, int]] = [(0.0, 0, -1)]  # (peso, nodo, padre)
    while heap and len(mst_edges) < n - 1:
        w, u, parent = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        if parent != -1:
            mst_edges.append((names[parent], names[u], w))
            total_cost += w
        for weight, v_idx in adj[u]:
            if not visited[v_idx]:
                heapq.heappush(heap, (weight, v_idx, u))

    return total_cost, mst_edges


def solve_arborescence(
    edges: List[Tuple[str, str, float]],
    root: Optional[str] = None
) -> Tuple[float, List[Tuple[str, str, float]]]:
    """
    Implementa el algoritmo de Chu-Liu/Edmonds para encontrar
    la arborescencia de coste mínimo en un grafo dirigido.
    """
    # Conjunto de nodos
    nodes = set(u for u, _, _ in edges) | set(v for _, v, _ in edges)
    if not nodes:
        return 0.0, []
    # Escoger root si no se define
    if root is None or root not in nodes:
        root = next(iter(nodes))

    # 1) Seleccionar la mejor arista entrante para cada nodo (excepto root)
    in_edge: Dict[str, Tuple[str, str, float]] = {}
    for v in nodes:
        if v == root:
            continue
        incoming = [(u, v, w) for u, v2, w in edges if v2 == v]
        if not incoming:
            raise ValueError(f"No hay arista entrante para el nodo '{v}'")
        best = min(incoming, key=lambda x: x[2])
        in_edge[v] = best

    # 2) Detectar ciclos
    cycles = []
    mark: Dict[str, int] = {}
    for v in nodes:
        if v == root or v in mark:
            continue
        path = []
        cur = v
        while cur not in path and cur != root:
            path.append(cur)
            cur = in_edge[cur][0]
        if cur in path:
            idx = path.index(cur)
            cycle = path[idx:]
            for node in cycle:
                mark[node] = 1
            cycles.append(cycle)

    # Si no hay ciclos, retorno directo
    if not cycles:
        arbo_edges = list(in_edge.values())
        total = sum(e[2] for e in arbo_edges)
        return total, arbo_edges

    # Contractar el primer ciclo
    cycle = cycles[0]
    cycle_set = set(cycle)
    supernode = "|".join(cycle)

    # Mapa de contracción
    def rep(x: str) -> str:
        return supernode if x in cycle_set else x

    contracted_edges: List[Tuple[str, str, float]] = []
    for u, v, w in edges:
        u2, v2 = rep(u), rep(v)
        if u2 == v2:
            continue
        w2 = w - (in_edge[v][2] if v in cycle_set else 0)
        contracted_edges.append((u2, v2, w2))

    # Nuevo root
    root2 = rep(root)
    # Recursión
    total_rec, edges_rec = solve_arborescence(contracted_edges, root2)

    # Reconstruir aristas finales
    result_edges: List[Tuple[str, str, float]] = []
    # 1) aristas fuera del ciclo
    for u, v, w in edges_rec:
        if v != supernode:
            result_edges.append((u, v, w))
        else:
            # elegir la arista entrante al ciclo correspondiente
            candidates = [(u0, v0, w0) for u0, v0, w0 in edges if rep(v0) == supernode]
            # coincide peso con w + offset
            for u0, v0, w0 in candidates:
                if abs((w0 - in_edge[v0][2]) - w) < 1e-9:
                    result_edges.append((u0, v0, w0))
                    break
    # 2) aristas internas del ciclo menos la reemplazada
    replaced = {v for _, v, _ in result_edges}
    for v in cycle:
        if v != root and v not in replaced:
            result_edges.append(in_edge[v])

    total = sum(e[2] for e in result_edges)
    return total, result_edges


def solve_mst(
    edges: List[Tuple[str, str, float]],
    directed: bool = False,
    root: Optional[str] = None,
) -> Tuple[float, List[Tuple[str, str, float]]]:
    """
    Si directed=False: retorna MST no dirigido.
    Si directed=True: retorna arborescencia dirigida de coste mínimo.
    """
    if directed:
        return solve_arborescence(edges, root)
    else:
        return solve_mst_undirected(edges)


if __name__ == "__main__":
    import sys
    data = sys.stdin.read()
    edges = parse_mst_data(data)
    total, tree = solve_mst(edges, directed=False)
    for u, v, w in tree:
        print(f"{u} -> {v} [{w}]")
    print(f"Costo total: {total}")
