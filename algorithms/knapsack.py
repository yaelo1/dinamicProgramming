def solve_knapsack(weights, values, capacity):
    """
    Solves the 0-1 Knapsack problem using dynamic programming.

    :param weights: List[int] pesos de los objetos
    :param values:  List[int] valores de los objetos
    :param capacity: int capacidad máxima de la mochila
    :return: (max_value, selected_indices)
             max_value: valor óptimo que cabe en la mochila
             selected_indices: lista de índices de objetos seleccionados
    """
    n = len(weights)
    # dp[i][c] = valor máximo usando primeros i objetos con capacidad c
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    # Llenado de la tabla
    for i in range(1, n + 1):
        w = weights[i-1]
        v = values[i-1]
        for c in range(capacity + 1):
            if w <= c:
                dp[i][c] = max(dp[i-1][c], dp[i-1][c-w] + v)
            else:
                dp[i][c] = dp[i-1][c]

    max_value = dp[n][capacity]

    # Retroceso para hallar los índices de los objetos seleccionados
    selected = []
    c = capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i-1][c]:
            # El objeto i-1 fue incluido
            selected.append(i-1)
            c -= weights[i-1]
    selected.reverse()

    return max_value, selected


def solve_multiple_knapsack(groups, capacity):
    """
    Solves the multiple-choice knapsack problem with dynamic programming.
    Each group can have only one item selected.

    :param groups: Dict[str, List[tuple]] Diccionario de grupos donde cada grupo tiene 
                   una lista de tuplas (peso, valor)
    :param capacity: int capacidad máxima
    :return: (max_value, selected_items)
             max_value: valor máximo óptimo
             selected_items: lista de tuplas (grupo, índice, costo, valor)
    """
    group_names = list(groups.keys())
    n_groups = len(group_names)
    
    # DP[i][c] = valor máximo usando los primeros i grupos con capacidad c
    dp = [[0] * (capacity + 1) for _ in range(n_groups + 1)]
    
    # Para reconstruir la solución
    choice = [[None] * (capacity + 1) for _ in range(n_groups + 1)]
    
    # Llenar la tabla DP
    for i in range(1, n_groups + 1):
        group_name = group_names[i-1]
        group_items = groups[group_name]
        
        for c in range(capacity + 1):
            # Valor por defecto si no se elige nada de este grupo
            dp[i][c] = dp[i-1][c]
            choice[i][c] = -1  # No seleccionar nada
            
            # Considerar cada item en el grupo actual
            for j, (weight, value) in enumerate(group_items):
                if weight <= c and dp[i-1][c-weight] + value > dp[i][c]:
                    dp[i][c] = dp[i-1][c-weight] + value
                    choice[i][c] = j
    
    # Reconstrucción de la solución
    max_value = dp[n_groups][capacity]
    selected_items = []
    
    c = capacity
    for i in range(n_groups, 0, -1):
        j = choice[i][c]
        if j != -1:  # Si se eligió un elemento del grupo
            group_name = group_names[i-1]
            weight, value = groups[group_name][j]
            selected_items.append({
                'group': group_name,
                'index': j,
                'cost': weight,
                'value': value
            })
            c -= weight
    
    selected_items.reverse()
    return max_value, selected_items


def parse_groups_data(groups_data):
    """
    Parsea los datos de grupos ingresados por el usuario.
    Formato esperado: 
    name: [(weight1,value1), (weight2,value2), ...]
    
    :param groups_data: str Datos de grupos como cadena
    :return: Dict[str, List[tuple]] Diccionario de grupos
    """
    groups = {}
    lines = groups_data.strip().split('\n')
    
    for line in lines:
        if not line.strip():
            continue
            
        parts = line.split(':', 1)
        if len(parts) != 2:
            raise ValueError(f"Formato inválido en la línea: {line}")
            
        group_name = parts[0].strip()
        items_str = parts[1].strip()
        
        # Evaluar la expresión para obtener la lista de tuplas
        try:
            items = eval(items_str)
            # Verificar que sea una lista de tuplas
            if not isinstance(items, list):
                raise ValueError(f"Los items deben ser una lista para el grupo {group_name}")
                
            for item in items:
                if not isinstance(item, tuple) or len(item) != 2:
                    raise ValueError(f"Cada item debe ser una tupla (peso, valor) en el grupo {group_name}")
            
            groups[group_name] = items
        except Exception as e:
            raise ValueError(f"Error al parsear los items para el grupo {group_name}: {str(e)}")
    
    return groups