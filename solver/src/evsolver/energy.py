from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

from .models import SolveRequest, Vehicle

try:
    from cpp_energy import charge_time_minutes  # C++ extension module
except Exception:  # pragma: no cover
    charge_time_minutes = None


@dataclass
class SimStop:
    node_idx: int
    arrival_min: int
    depart_min: int
    soc: float  # SoC AFTER any charging at this stop
    charge_added_kwh: float = 0.0
    charge_time_min: int = 0


def energy_kwh(distance_km: float, kwh_per_km: float) -> float:
    return distance_km * kwh_per_km


def compute_charge_time_minutes(soc0: float, soc1: float, station_kw: float, battery_kwh: float) -> int:
    if soc1 <= soc0:
        return 0
    if charge_time_minutes is not None:
        return int(charge_time_minutes(float(soc0), float(soc1), float(station_kw), float(battery_kwh)))

    # fallback: linear power
    delta_kwh = max(0.0, (soc1 - soc0) * battery_kwh)
    hours = delta_kwh / max(1e-9, station_kw)
    return int(round(hours * 60))


def _required_soc_to_next_charge_point(
    req: SolveRequest,
    vehicle: Vehicle,
    route: List[int],
    pos: int,
) -> float:
    """
    From current position `pos` (typically a charger stop), compute how much SoC is
    required to reach the next charger (after this stop) OR the route end, plus min_soc buffer.
    """
    nodes = req.nodes
    dist = req.matrix.distance_km

    # find the next "charge point" after pos: next charger OR end of route
    end_pos = len(route) - 1
    next_cp = end_pos
    for j in range(pos + 1, len(route)):
        if nodes[route[j]].type == "charger":
            next_cp = j
            break

    # sum energy needed from pos -> next_cp
    need_kwh = 0.0
    for k in range(pos, next_cp):
        a = route[k]
        b = route[k + 1]
        need_kwh += energy_kwh(dist[a][b], vehicle.kwh_per_km)

    batt = float(vehicle.battery_kwh)
    return (need_kwh / batt) + float(vehicle.min_soc)


def simulate_route(req: SolveRequest, vehicle: Vehicle, route: List[int]) -> Tuple[List[SimStop], List[str]]:
    nodes = req.nodes
    dist = req.matrix.distance_km
    time = req.matrix.time_min

    soc = float(vehicle.start_soc)
    batt = float(vehicle.battery_kwh)
    min_soc = float(vehicle.min_soc)

    t = 0
    stops: List[SimStop] = []
    violations: List[str] = []

    for pos, idx in enumerate(route):
        node = nodes[idx]

        # travel from previous node
        if pos == 0:
            arrival = 0
        else:
            prev = route[pos - 1]
            arrival = t + int(time[prev][idx])

            used = energy_kwh(dist[prev][idx], vehicle.kwh_per_km)
            soc -= used / batt

        # energy feasibility check upon arrival
        if soc < min_soc - 1e-9:
            violations.append(f"ENERGY: soc {soc:.3f} below min {min_soc:.3f} before node {node.id}")

        base_service = int(node.service_min or 0)

        # charging behavior
        charge_added_kwh = 0.0
        charge_time_min = 0

        if node.type == "charger" and (node.available is None or node.available) and node.station_kw is not None:
            station_kw = float(node.station_kw)
            wait = int(node.expected_wait_min or 0)

            # decide how much to charge
            required = _required_soc_to_next_charge_point(req, vehicle, route, pos)
            # cap for fast charging / taper realism (typical field practice)
            target_soc = min(0.90, max(soc, required))

            # if we still can't reach required due to cap, later we may violate again (repair can add more chargers)
            if target_soc > soc + 1e-12:
                charge_time_min = compute_charge_time_minutes(soc, target_soc, station_kw, batt)
                charge_added_kwh = (target_soc - soc) * batt
                soc = target_soc  # update SOC AFTER charging

            depart = arrival + base_service + wait + int(charge_time_min)
        else:
            depart = arrival + base_service

        stops.append(
            SimStop(
                node_idx=idx,
                arrival_min=int(arrival),
                depart_min=int(depart),
                soc=float(max(0.0, min(1.0, soc))),
                charge_added_kwh=float(charge_added_kwh),
                charge_time_min=int(charge_time_min),
            )
        )
        t = depart

    return stops, violations