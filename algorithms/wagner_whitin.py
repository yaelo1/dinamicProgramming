import json
from typing import List, Tuple

def parse_wagner_whitin_data(json_str: str) -> Tuple[List[int], float, float]:
    """
    Parsea un JSON con la forma:
    {
      "demand": [d1, d2, …, dT],
      "setup_cost": K,
      "holding_cost": h
    }
    donde:
      - demand[i] es la demanda del periodo i+1
      - K es el costo fijo de preparar un lote
      - h es el costo de mantener 1 unidad en inventario por periodo
    """
    raw = json.loads(json_str)
    demands = [int(x) for x in raw["demand"]]
    K = float(raw["setup_cost"])
    h = float(raw["holding_cost"])
    return demands, K, h

def solve_wagner_whitin(demands: List[int], K: float, h: float) -> Tuple[float, List[int]]:
    """
    Aplica DP de Wagner-Whitin:
      f[t] = costo mínimo para cubrir demanda hasta el periodo t
      f[t] = min_{1 ≤ j ≤ t} { f[j-1] + K 
                            + h * sum_{m=j..t} (m-j)*demand[m-1] }
    Reconstruye órdenes:
      se programa producción en j para cubrir j..t
    Retorna:
      - min_cost: f[T]
      - schedule: lista de longitudes (T) donde schedule[j-1] = cantidad a producir en j
    """
    T = len(demands)
    # f[0]=0, f[1..T] = ∞ inicialmente
    f = [0.0] + [float("inf")] * T
    prev_order = [0] * (T+1)

    # Precomputar costos de mantener inventario
    # holding_cost[j][t] = h * sum_{m=j..t} (m-j)*demand[m-1]
    holding_cost = [[0.0]*(T+1) for _ in range(T+1)]
    for j in range(1, T+1):
        for t in range(j, T+1):
            cost = 0.0
            for m in range(j, t+1):
                cost += (m-j) * demands[m-1] * h
            holding_cost[j][t] = cost

    # DP principal
    for t in range(1, T+1):
        for j in range(1, t+1):
            production_qty = sum(demands[j-1:t])
            cost = f[j-1] + K + holding_cost[j][t]
            if cost < f[t]:
                f[t] = cost
                prev_order[t] = j

    # Reconstruir schedule
    schedule = [0]*T
    t = T
    while t > 0:
        j = prev_order[t]
        schedule[j-1] = sum(demands[j-1:t])
        t = j-1

    return f[T], schedule
