from __future__ import annotations

from fastapi import FastAPI
from .models import SolveRequest, SolveResponse, RoutePlan, StopPlan
from .config import settings
from .ortools_vrptw import solve_vrptw
from .repair import repair_route_insert_chargers
from .energy import simulate_route

app = FastAPI(title="EV Fleet Routing Solver", version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    sol = solve_vrptw(req, time_limit_s=settings.time_limit_seconds)

    # If no solution, return JSON-safe stats
    if not sol.routes:
        return SolveResponse(
            feasible=False,
            routes=[],
            solver_stats={"objective": None, "status": "no_solution"},
        )

    routes_out = []
    all_ok = True

    for v_idx, path in sol.routes.items():
        vehicle = req.vehicles[v_idx]

        repaired_path, violations = repair_route_insert_chargers(
            req, vehicle, path, max_repairs=settings.max_repairs_per_route
        )

        sim, viol2 = simulate_route(req, vehicle, repaired_path)
        violations.extend(viol2)

        feasible = (len(violations) == 0)
        all_ok = all_ok and feasible

        stops = [
            StopPlan(
                node_id=req.nodes[s.node_idx].id,
                arrival_min=s.arrival_min,
                depart_min=s.depart_min,
                soc=float(s.soc),
                charge_added_kwh=float(s.charge_added_kwh),
                charge_time_min=int(s.charge_time_min),
            )
            for s in sim
        ]

        routes_out.append(
            RoutePlan(
                vehicle_id=vehicle.id,
                stops=stops,
                feasible=feasible,
                violations=violations,
            )
        )

    obj = sol.objective_value
    return SolveResponse(
        feasible=all_ok,
        routes=routes_out,
        solver_stats={
            "objective": (None if obj == float("inf") else float(obj)),
            "status": "ok",
        },
    )