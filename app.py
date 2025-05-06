from flask import Flask, render_template, request, flash, redirect, url_for
from algorithms.knapsack import solve_knapsack, solve_multiple_knapsack, parse_groups_data
from algorithms.shortest_path import parse_graph_data, dijkstra, get_path
from algorithms.distribucion import parse_distribution_data, solve_distribution
from algorithms.wagner_whitin import parse_wagner_whitin_data, solve_wagner_whitin
from algorithms.mst import parse_mst_data, solve_mst
from algorithms.diligencia import parse_costs_data, solve_diligencia


app = Flask(__name__)
app.secret_key = "supersecreto"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/knapsack", methods=["GET", "POST"])
def knapsack():
    result = None
    if request.method == "POST":
        mode = request.form.get("mode", "standard")
        try:
            if mode == "standard":
                # Leer listas de pesos y valores separados por coma
                try:
                    weights = [int(x) for x in request.form["weights_str"].split(",") if x.strip()]
                    values  = [int(x) for x in request.form["values_str"].split(",") if x.strip()]
                    capacity = int(request.form["capacity"])
                except ValueError:
                    flash("Por favor introduce solo números enteros separados por comas en pesos, valores y capacidad.", "error")
                    return render_template("knapsack.html", result=None)

                max_value, items = solve_knapsack(weights, values, capacity)
                result = {
                    "mode": mode,
                    "max_value": max_value,
                    "items": items
                }

            elif mode == "multiple":
                try:
                    groups = parse_groups_data(request.form["groups_data"])
                    capacity = int(request.form["total_capacity"])
                except ValueError:
                    flash("Por favor introduce los datos de los grupos en el formato correcto y la capacidad como número entero.", "error")
                    return render_template("knapsack.html", result=None)

                max_value, selection = solve_multiple_knapsack(groups, capacity)
                result = {
                    "mode": mode,
                    "max_value": max_value,
                    "selection": selection
                }

        except Exception as e:
            flash(f"Error al calcular Knapsack: {e}", "error")

    return render_template("knapsack.html", result=result)

@app.route("/shortest_path", methods=["GET", "POST"])
def shortest_path():
    result = None
    if request.method == "POST":
        try:
            # Parsea el grafo desde JSON enviado en un textarea llamado "graph_data"
            graph_json = request.form["graph_data"]
            graph = parse_graph_data(graph_json)

            start = request.form["start_node"].strip()
            end   = request.form["end_node"].strip()

            distances, previous = dijkstra(graph, start)
            path = get_path(previous, start, end)
            cost = distances.get(end, float("inf"))

            result = {
                "path": path,
                "cost": cost
            }
        except Exception as e:
            flash(f"Error al calcular camino más corto: {e}", "error")

    return render_template("shortest_path.html", result=result)

@app.route("/distribucion", methods=["GET", "POST"])
def distribucion():
    result = None
    if request.method == "POST":
        try:
            dist = parse_distribution_data(request.form["distribution_data"])
            total = int(request.form["total_resources"])
            max_val, alloc = solve_distribution(dist, total)
            result = {
                "max_value": max_val,
                "allocation": alloc
            }
        except Exception as e:
            flash(f"Error al calcular distribución: {e}", "error")
    return render_template("distribucion.html", result=result)


@app.route("/wagner_whitin", methods=["GET", "POST"])
def wagner_whitin():
    result = None
    if request.method == "POST":
        try:
            # Parsear datos de demanda, setup_cost y holding_cost
            demands, K, h = parse_wagner_whitin_data(request.form["ww_data"])
            # Calcular costo mínimo y plan de producción
            min_cost, schedule = solve_wagner_whitin(demands, K, h)
            result = {
                "min_cost": min_cost,
                "schedule": schedule
            }
        except Exception as e:
            flash(f"Error al calcular Wagner-Whitin: {e}", "error")
    return render_template("wagner_whitin.html", result=result)

@app.route("/mst", methods=["GET", "POST"])
def mst():
    result = None
    if request.method == "POST":
        try:
            # Parsear aristas
            edges = parse_mst_data(request.form["edges_data"])
            # Flag de dirigido
            directed = bool(request.form.get("directed"))
            # Leer root sólo si es dirigido y se proporcionó
            root = request.form.get("root") if directed and request.form.get("root") else None

            # Llamada con directed y root
            total_cost, mst_edges = solve_mst(edges, directed=directed, root=root)

            # Incluir root en el dict de resultado
            result = {
                "directed": directed,
                "root": root,
                "total_cost": total_cost,
                "mst": mst_edges
            }
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error interno al calcular MST: {e}", "error")

    return render_template("mst.html", result=result)


@app.route("/diligencia", methods=["GET", "POST"])
def diligencia():
    result = None
    if request.method == "POST":
        try:
            costs = parse_costs_data(request.form["costs_data"])
            start  = request.form["start"].strip()
            dest   = request.form["dest"].strip()
            stages = int(request.form["stages"])

            min_cost, path = solve_diligencia(costs, start, dest, stages)
            result = {"cost": min_cost, "path": path}
        except Exception as e:
            flash(f"Error al calcular diligencia: {e}", "error")
    return render_template("diligencia.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
