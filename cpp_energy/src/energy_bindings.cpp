#include <pybind11/pybind11.h>
#include "charge_curve.h"

namespace py = pybind11;

PYBIND11_MODULE(cpp_energy, m) {
  m.doc() = "C++ helpers for EV charging curves (piecewise taper)";

  m.def("charge_time_minutes",
        [](double soc0, double soc1, double station_kw, double battery_kwh) {
          auto curve = energy::default_curve();
          return energy::charge_time_minutes(soc0, soc1, station_kw, battery_kwh, curve);
        },
        py::arg("soc0"),
        py::arg("soc1"),
        py::arg("station_kw"),
        py::arg("battery_kwh"));
}