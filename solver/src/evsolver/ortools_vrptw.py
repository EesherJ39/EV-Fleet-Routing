from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from .models import SolveRequest

@dataclass
class OrtoolsSolution:
    routes: Dict[int, List[int]]  # vehicle index -> node indices (includes start/end)
    objective_value: float

def index_of(nodes, node_id: str) -> int:
    for i, n in enumerate(nodes):
        if n.id == node_id:
            return i
    raise KeyError(f"node_id not found: {node_id}")

def solve_vrptw(req: SolveRequest, time_limit_s: int = 10) -> OrtoolsSolution:
    nodes = req.nodes
    vehicles = req.vehicles
    n = len(nodes)
    m = len(vehicles)

    manager = pywrapcp.RoutingIndexManager(
        n, m,
        [index_of(nodes, v.start_node_id) for v in vehicles],
        [index_of(nodes, v.end_node_id) for v in vehicles],
    )
    routing = pywrapcp.RoutingModel(manager)

    time_matrix = req.matrix.time_min
    dist_matrix = req.matrix.distance_km

    def time_cb(from_idx, to_idx):
        a = manager.IndexToNode(from_idx)
        b = manager.IndexToNode(to_idx)
        return int(time_matrix[a][b])

    def dist_cb(from_idx, to_idx):
        a = manager.IndexToNode(from_idx)
        b = manager.IndexToNode(to_idx)
        # routing wants int costs; km -> meters
        return int(dist_matrix[a][b] * 1000)

    time_cb_i = routing.RegisterTransitCallback(time_cb)
    dist_cb_i = routing.RegisterTransitCallback(dist_cb)

    routing.SetArcCostEvaluatorOfAllVehicles(dist_cb_i if req.objective == "min_distance" else time_cb_i)

    # Capacity constraints
    demands = [n.demand for n in nodes]

    def demand_cb(from_idx):
        a = manager.IndexToNode(from_idx)
        return int(demands[a])

    demand_cb_i = routing.RegisterUnaryTransitCallback(demand_cb)
    capacities = [v.capacity for v in vehicles]
    routing.AddDimensionWithVehicleCapacity(demand_cb_i, 0, capacities, True, "Capacity")

    # Time windows (travel + service time at origin)
    service = [n.service_min for n in nodes]

    def time_with_service_cb(from_idx, to_idx):
        a = manager.IndexToNode(from_idx)
        b = manager.IndexToNode(to_idx)
        return int(time_matrix[a][b] + service[a])

    time_ws_cb_i = routing.RegisterTransitCallback(time_with_service_cb)
    routing.AddDimension(
        time_ws_cb_i,
        60,        # slack (waiting)
        24 * 60,   # horizon
        False,     # start not forced at 0
        "Time",
    )
    time_dim = routing.GetDimensionOrDie("Time")

    for i, node in enumerate(nodes):
        if node.time_window is None:
            continue
        idx = manager.NodeToIndex(i)
        tw = node.time_window
        time_dim.CumulVar(idx).SetRange(tw.start_min, tw.end_min)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.time_limit.FromSeconds(int(time_limit_s))
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH

    sol = routing.SolveWithParameters(params)
    if sol is None:
        return OrtoolsSolution(routes={}, objective_value=float("inf"))

    routes: Dict[int, List[int]] = {}
    for v in range(m):
        idx = routing.Start(v)
        path = []
        while not routing.IsEnd(idx):
            path.append(manager.IndexToNode(idx))
            idx = sol.Value(routing.NextVar(idx))
        path.append(manager.IndexToNode(idx))
        routes[v] = path

    return OrtoolsSolution(routes=routes, objective_value=float(sol.ObjectiveValue()))