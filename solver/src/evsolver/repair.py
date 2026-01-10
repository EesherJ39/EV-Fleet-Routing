from __future__ import annotations
from typing import List, Tuple

from .models import SolveRequest, Vehicle
from .energy import simulate_route


def repair_route_insert_chargers(
    req: SolveRequest,
    vehicle: Vehicle,
    route: List[int],
    max_repairs: int = 8
) -> Tuple[List[int], List[str]]:
    """
    Greedy repair:
    - Simulate SoC along route (now includes actual charging when a charger is present)
    - On first energy violation, insert an available charger before the violating node
    - Repeat until no violations or max_repairs reached
    """
    nodes = req.nodes
    time = req.matrix.time_min

    charger_indices = [
        i for i, n in enumerate(nodes)
        if n.type == "charger" and (n.available is None or n.available)
    ]

    violations_all: List[str] = []

    for _ in range(max_repairs):
        _, viol = simulate_route(req, vehicle, route)
        if not viol:
            return route, violations_all

        violations_all.extend(viol)

        # Parse: "ENERGY: ... before node <id>"
        bad_node_id = viol[0].split("before node ", 1)[-1].strip()
        bad_pos = next((p for p, idx in enumerate(route) if nodes[idx].id == bad_node_id), None)
        if bad_pos is None or bad_pos == 0:
            return route, violations_all

        insert_pos = bad_pos
        prev_idx = route[insert_pos - 1]
        next_idx = route[insert_pos]

        best = None
        best_cost = None

        for c in charger_indices:
            if c in route:
                continue
            added_time = time[prev_idx][c] + time[c][next_idx] - time[prev_idx][next_idx]
            if best_cost is None or added_time < best_cost:
                best = c
                best_cost = added_time

        if best is None:
            violations_all.append("REPAIR: no available charger to insert")
            return route, violations_all

        route = route[:insert_pos] + [best] + route[insert_pos:]

    return route, violations_all