import json

def parse_costs_data(costs_json: str) -> dict:
    """
    Parsea un JSON con la forma:
    {
      "A": {"B": 2, "C": 2, ...},
      "B": {"A": 2, "C": 6, ...},
      ...
    }
    y devuelve un diccionario de costos: dict[node][neighbor] = weight.
    """
    raw = json.loads(costs_json)
    costs = {}
    for node, nbrs in raw.items():
        if not isinstance(nbrs, dict):
            raise ValueError(f"Los valores de '{node}' deben ser un diccionario de vecinos y pesos")
        costs[node] = {nbr: float(w) for nbr, w in nbrs.items()}
    return costs


def solve_diligencia(costs: dict, start: str, dest: str, stages: int):
    """
    Resuelve el problema de la diligencia en exactamente `stages` saltos:
      - costs: dict[node] = dict[neighbor] = cost
      - start: nodo inicial
      - dest: nodo destino fijo en la etapa final
      - stages: número de aristas a recorrer
    Retorna:
      (min_cost, path) donde path es la lista de nodos desde start hasta dest.
    """
    # Inicializar DP para etapa stages+1
    f_next = {node: float('inf') for node in costs}
    f_next[dest] = 0

    # choice[n][s] = mejor siguiente nodo desde s en etapa n
    choice = [dict() for _ in range(stages+1)]

    # Recurrencia hacia atrás
    for n in range(stages, 0, -1):
        f_cur = {}
        for s in costs:
            best_cost = float('inf')
            best_x = None
            for x, w in costs[s].items():
                val = w + f_next.get(x, float('inf'))
                if val < best_cost:
                    best_cost = val
                    best_x = x
            f_cur[s] = best_cost
            choice[n][s] = best_x
        f_next = f_cur

    # Reconstrucción de la ruta
    path = [start]
    curr = start
    for n in range(1, stages+1):
        curr = choice[n].get(curr)
        if curr is None:
            break
        path.append(curr)
    return f_next[start], path