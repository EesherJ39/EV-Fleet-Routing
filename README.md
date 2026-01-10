# EV Fleet Routing with Real-Time Charging Constraints (Python + C++ + Java)

This is an interview-grade project starter:
- **Python**: OR-Tools VRPTW baseline + energy feasibility simulation + charging-stop repair
- **C++**: Non-linear charging time (tapering curve) via pybind11 extension
- **Java**: Spring Boot API gateway that forwards /solve to the Python solver

> Note (MVP honesty): This starter solves VRPTW first, then runs an energy simulation and greedily inserts charging stops if the route would violate minimum SoC.
> This is a realistic “shipping” approach for a portfolio MVP. The next step is integrating SoC into the optimization (layered SoC graph / discretized states).

---

## Quick start (local)

### 1) Build/install the C++ extension
```bash
cd cpp_energy
python -m pip install -U pip
python -m pip install -e .