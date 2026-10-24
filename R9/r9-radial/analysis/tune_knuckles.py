"""SUPERSEDED. First tuning study: angle-only offsets on the 300 mm master rod, which was rejected
(piston skirts foul at BDC, see docs/decisions.md). The design point, 380 mm master rod with radius and
angle tuned per pin, is design.py -> design_point.json. Kept for the record.

Choose per-cylinder knuckle-pin angular offsets so every cylinder reaches the same TDC height
as the master cylinder (equal compression ratio and equal head clearance)."""
import numpy as np, json
from scipy.optimize import least_squares
from kinematics import summary, N

r, L, a = 85.0, 300.0, 68.0          # crank throw (stroke 170), master rod, knuckle-pin radius
l = L - a                            # link rod length

def resid(x):
    dk = np.r_[0.0, np.radians(x)]
    s = summary(r, L, a, l, dk, n=2881)
    return s['smax'][1:] - s['smax'][0]

sol = least_squares(resid, np.zeros(N - 1), xtol=1e-10)
dk = np.r_[0.0, np.radians(sol.x)]
base = summary(r, L, a, l)
tuned = summary(r, L, a, l, dk)
print('knuckle offsets deg:', sol.x.round(3))
for nm, s in (('equal spacing', base), ('tuned', tuned)):
    print('%-14s TDC spread %.3f mm | stroke %.2f..%.2f mm | TDC timing lag %.2f..%.2f deg' % (
        nm, np.ptp(s['smax']), s['stroke'].min(), s['stroke'].max(), s['tdc_lag'].min(), s['tdc_lag'].max()))
json.dump(dict(r=r, L=L, a=a, l=l, dk_deg=[0.0] + list(sol.x), base={k: list(map(float, v)) if hasattr(v, '__len__') else float(v) for k, v in base.items()},
               tuned={k: list(map(float, v)) if hasattr(v, '__len__') else float(v) for k, v in tuned.items()}), open('kinematics_result.json', 'w'), indent=1)
