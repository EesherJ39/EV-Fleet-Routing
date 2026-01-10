#include "charge_curve.h"
#include <algorithm>
#include <cmath>

namespace energy {

PiecewisePower default_curve() {
  // Simple taper approximation:
  // 0-80%: full power
  // 80-90%: 60% power
  // 90-100%: 30% power
  PiecewisePower c;
  c.soc_bp = {0.8, 0.9, 1.0};
  c.mult   = {1.0, 0.6, 0.3};
  return c;
}

static double clamp01(double x) {
  return std::max(0.0, std::min(1.0, x));
}

int charge_time_minutes(double soc0, double soc1, double station_kw, double battery_kwh,
                        const PiecewisePower& curve) {
  soc0 = clamp01(soc0);
  soc1 = clamp01(soc1);
  if (soc1 <= soc0) return 0;
  if (station_kw <= 0.0 || battery_kwh <= 0.0) return 0;

  double minutes = 0.0;
  double prev = 0.0;

  for (size_t i = 0; i < curve.soc_bp.size(); i++) {
    double bp = curve.soc_bp[i];
    double seg_start = prev;
    double seg_end = bp;
    prev = bp;

    double a = std::max(seg_start, soc0);
    double b = std::min(seg_end, soc1);
    if (b <= a) continue;

    double seg_mult = curve.mult[i];
    double power_kw = station_kw * std::max(1e-6, seg_mult);
    double delta_kwh = (b - a) * battery_kwh;
    double hours = delta_kwh / power_kw;
    minutes += hours * 60.0;
  }

  return static_cast<int>(std::lround(minutes));
}

} // namespace energy