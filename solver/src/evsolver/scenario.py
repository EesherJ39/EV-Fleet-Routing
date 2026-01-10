from __future__ import annotations
from typing import List
import random
import math

from .models import SolveRequest, Node, Vehicle, Location, TimeWindow, Matrix

def haversine_km(a: Location, b: Location) -> float:
    R = 6371.0
    lat1, lon1 = math.radians(a.lat), math.radians(a.lon)
    lat2, lon2 = math.radians(a.lat), math.radians(b.lon)
    lat2, lon2 = math.radians(b.lat), math.radians(b.lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = (math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2)
    return 2*R*math.asin(math.sqrt(h))

def build_matrix(nodes: List[Node], km_per_min: float = 0.8) -> Matrix:
    n = len(nodes)
    dist = [[0.0]*n for _ in range(n)]
    tmin = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            d = haversine_km(nodes[i].location, nodes[j].location)
            dist[i][j] = d
            tmin[i][j] = int(round(d / km_per_min))
    return Matrix(time_min=tmin, distance_km=dist)

def demo_request(seed: int = 7) -> SolveRequest:
    rng = random.Random(seed)

    depot = Node(
        id="depot",
        type="depot",
        location=Location(lat=43.651, lon=-79.383),
        demand=0,
        service_min=0,
        time_window=TimeWindow(start_min=0, end_min=24*60),
    )

    chargers: List[Node] = []
    for k in range(4):
        chargers.append(Node(
            id=f"charger-{k}",
            type="charger",
            location=Location(
                lat=43.651 + rng.uniform(-0.08, 0.08),
                lon=-79.383 + rng.uniform(-0.12, 0.12),
            ),
            station_kw=rng.choice([50.0, 100.0, 150.0]),
            stalls=rng.choice([2, 4, 6]),
            expected_wait_min=rng.choice([0, 5, 10, 15]),
            available=True,
            service_min=0,
        ))

    customers: List[Node] = []
    for i in range(12):
        start = rng.randint(8*60, 12*60)       # 8:00–12:00
        end = start + rng.randint(240, 420)    # +4–7 hours (looser windows)
        customers.append(Node(
            id=f"cust-{i}",
            type="customer",
            location=Location(
                lat=43.651 + rng.uniform(-0.10, 0.10),
                lon=-79.383 + rng.uniform(-0.15, 0.15),
            ),
            demand=rng.randint(1, 3),
            service_min=rng.randint(5, 12),
            time_window=TimeWindow(start_min=start, end_min=end),
        ))

    nodes = [depot] + chargers + customers
    matrix = build_matrix(nodes)

    # FORCE CHARGING: smaller battery + lower start SoC + higher consumption
    vehicles = [
        Vehicle(
            id="veh-0",
            capacity=25,
            start_node_id="depot",
            end_node_id="depot",
            battery_kwh=24.0,
            start_soc=0.45,
            min_soc=0.12,
            kwh_per_km=0.30,
        ),
        Vehicle(
            id="veh-1",
            capacity=25,
            start_node_id="depot",
            end_node_id="depot",
            battery_kwh=24.0,
            start_soc=0.45,
            min_soc=0.12,
            kwh_per_km=0.30,
        ),
    ]

    return SolveRequest(nodes=nodes, vehicles=vehicles, matrix=matrix, objective="min_time")