from evsolver.scenario import demo_request
from evsolver.ortools_vrptw import solve_vrptw

def test_can_solve_demo():
    req = demo_request()
    sol = solve_vrptw(req, time_limit_s=2)
    assert sol.routes