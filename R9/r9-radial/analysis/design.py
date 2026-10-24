"""Design point and knuckle-pin tuning for the R9 radial (all mm)."""
import numpy as np, json
from scipy.optimize import least_squares
import kinematics as K
N = 9
SPEC = dict(bore=150.0, stroke=170.0, master_rod=380.0, knuckle_radius_nominal=80.0)
r = SPEC['stroke'] / 2; L = SPEC['master_rod']; a0 = SPEC['knuckle_radius_nominal']; l = L - a0
SPEC['link_rod'] = l

def solve(th, ak, dk):
    th = np.atleast_1d(th); C = r*K.unit(th); u0 = K.unit(np.zeros_like(th))
    cu = np.sum(C*u0, 1); s0 = cu + np.sqrt(L**2 - (np.sum(C*C, 1) - cu**2)); P0 = s0[:, None]*u0
    beta = np.arctan2(P0[:, 0]-C[:, 0], P0[:, 1]-C[:, 1]); S = np.zeros((len(th), N)); S[:, 0] = s0
    Kp = np.zeros((len(th), N, 2)); Kp[:, 0] = P0
    for k in range(1, N):
        Kk = C + ak[k]*K.unit(beta + K.PHI[k] + dk[k]); uk = K.unit(np.full_like(th, K.PHI[k]))
        ku = np.sum(Kk*uk, 1); S[:, k] = ku + np.sqrt(l**2 - (np.sum(Kk*Kk, 1) - ku**2)); Kp[:, k] = Kk
    return S, beta, C, Kp
th = np.linspace(0, 2*np.pi, 1441)
def stats(ak, dk):
    S, beta, C, Kp = solve(th, ak, dk); smax = S.max(0)
    lag = (np.degrees(th[S.argmax(0)]) - np.degrees(K.PHI) + 180) % 360 - 180
    return smax, smax - S.min(0), lag, np.degrees(np.abs(beta).max())
def res(x):
    ak = np.r_[a0, x[:8]]; dk = np.r_[0, np.radians(x[8:])]
    smax, st, lag, _ = stats(ak, dk)
    return np.r_[4.0*(smax[1:] - smax[0]), 2.0*(st[1:] - SPEC['stroke']), 0.2*lag[1:], 0.05*(x[:8] - a0), 0.05*x[8:]]
if __name__ == '__main__':
    base = stats(np.full(N, a0), np.zeros(N))
    sol = least_squares(res, np.r_[np.full(8, a0), np.zeros(8)], xtol=1e-10, ftol=1e-12)
    ak = np.r_[a0, sol.x[:8]]; dk = np.r_[0, sol.x[8:]]
    tuned = stats(ak, np.radians(dk))
    for nm, s in (('equal pins', base), ('tuned pins', tuned)):
        print('%-10s TDC spread %.3f | stroke %.2f..%.2f | TDC lag %.2f..%.2f | master rod max angle %.1f' % (nm, np.ptp(s[0]), s[1].min(), s[1].max(), s[2].min(), s[2].max(), s[3]))
    print('a_k', ak.round(2)); print('d_k', dk.round(2))
    disp = N * np.pi/4 * SPEC['bore']**2 * SPEC['stroke'] / 1e6
    print('displacement %.2f L, pin BDC radius %.1f, TDC radius %.1f' % (disp, L - r, L + r))
    json.dump(dict(spec=SPEC, a_k=list(ak), d_k_deg=list(dk), displacement_L=disp,
                   equal_pins=dict(tdc_spread=float(np.ptp(base[0])), stroke_max=float(base[1].max()), lag_max=float(np.abs(base[2]).max())),
                   tuned_pins=dict(tdc_spread=float(np.ptp(tuned[0])), stroke_max=float(tuned[1].max()), lag_max=float(np.abs(tuned[2]).max()))),
              open('design_point.json', 'w'), indent=1)
