import json

def parse_distribution_data(json_str: str) -> dict:
    """
    Parsea un JSON {"Centro1":[b0,b1,...], "Centro2":[...], ...}
    donde b[x] = beneficio si asignas x recursos a ese centro.
    Devuelve dict[centro] = lista de floats.
    """
    raw = json.loads(json_str)
    dist = {}
    for centro, beneficios in raw.items():
        if not isinstance(beneficios, list):
            raise ValueError(f"El valor de '{centro}' debe ser una lista de números")
        dist[centro] = [float(b) for b in beneficios]
    return dist

def solve_distribution(dist: dict, total: int):
    """
    DP de asignación escalonada:
      - dist: dict[centro] = [b0, b1, b2, ...]
      - total: recursos totales a repartir
    Retorna (max_beneficio, allocation) donde allocation es dict[centro]=x asignado.
    """
    centros = list(dist.keys())
    n = len(centros)

    # dp[i][k] = beneficio óptimo usando centros[i:] con k recursos restantes
    dp = [[0]*(total+1) for _ in range(n+1)]
    # choice[i][k] = cuántos recursos asigno a centros[i] en la solución óptima
    choice = [[0]*(total+1) for _ in range(n)]

    # Llenado bottom-up
    for i in range(n-1, -1, -1):
        beneficios = dist[centros[i]]
        for k in range(total+1):
            best = -float("inf")
            best_x = 0
            # x = recursos a poner en este centro
            max_x = min(k, len(beneficios)-1)
            for x in range(max_x+1):
                val = beneficios[x] + dp[i+1][k-x]
                if val > best:
                    best = val
                    best_x = x
            dp[i][k] = best
            choice[i][k] = best_x

    # Reconstrucción de la asignación
    allocation = {}
    k = total
    for i in range(n):
        x = choice[i][k]
        allocation[centros[i]] = x
        k -= x

    return dp[0][total], allocation
