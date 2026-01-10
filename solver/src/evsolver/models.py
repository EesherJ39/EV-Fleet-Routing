from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any

NodeType = Literal["depot", "customer", "charger"]

class Location(BaseModel):
    lat: float
    lon: float

class TimeWindow(BaseModel):
    start_min: int
    end_min: int

class Node(BaseModel):
    id: str
    type: NodeType
    location: Location
    demand: int = 0
    service_min: int = 0
    time_window: Optional[TimeWindow] = None

    # Chargers only (type="charger")
    station_kw: Optional[float] = None
    stalls: Optional[int] = None
    available: Optional[bool] = True
    expected_wait_min: Optional[int] = 0

class Vehicle(BaseModel):
    id: str
    capacity: int
    start_node_id: str
    end_node_id: str

    battery_kwh: float
    start_soc: float = Field(ge=0.0, le=1.0, default=1.0)
    min_soc: float = Field(ge=0.0, le=1.0, default=0.05)
    kwh_per_km: float = Field(gt=0.0, default=0.2)

class Matrix(BaseModel):
    time_min: List[List[int]]
    distance_km: List[List[float]]

class SolveRequest(BaseModel):
    nodes: List[Node]
    vehicles: List[Vehicle]
    matrix: Matrix
    objective: Literal["min_time", "min_distance"] = "min_time"

class StopPlan(BaseModel):
    node_id: str
    arrival_min: int
    depart_min: int
    soc: float
    charge_added_kwh: float = 0.0
    charge_time_min: int = 0

class RoutePlan(BaseModel):
    vehicle_id: str
    stops: List[StopPlan]
    feasible: bool
    violations: List[str] = Field(default_factory=list)

class SolveResponse(BaseModel):
    feasible: bool
    routes: List[RoutePlan]
    solver_stats: Dict[str, Any] = Field(default_factory=dict)