#pragma once
#include <vector>

namespace energy {

struct PiecewisePower {
  std::vector<double> soc_bp;  // breakpoints (last must be 1.0)
  std::vector<double> mult;    // power multiplier per segment
};

PiecewisePower default_curve();

// minutes to go from soc0 -> soc1 (soc1 >= soc0)
int charge_time_minutes(double soc0, double soc1, double station_kw, double battery_kwh,
                        const PiecewisePower& curve);

} // namespace energy