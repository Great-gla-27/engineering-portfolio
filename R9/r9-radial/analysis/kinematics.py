"""Planar kinematics of a 9-cylinder master-and-articulating-rod radial.

Frame: engine plane = x-z, crank axis along y. Cylinder k axis at angle phi_k = k*40 deg,
measured from +z (cylinder 1 at top) anti-clockwise seen from the anti-propeller end. Crank angle theta is
measured the same way, theta = 0 with the crankpin on the cylinder 1 axis.
Cylinder 1 carries the master rod; cylinders 2..9 carry link rods pinned to the master
rod big end on knuckle pins at radius a and angle (phi_k + d_k) from the master rod centreline.
"""
import numpy as np

N = 9
PHI = np.radians(np.arange(N) * 360.0 / N)

def unit(a):
    return np.stack([np.sin(a), np.cos(a)], axis=-1)       # (x, z)

def solve(theta, r, L, a, l, dk=None):
    """piston pin distance s_k from crank centre for crank angle(s) theta (rad)."""
    dk = np.zeros(N) if dk is None else np.asarray(dk)
    theta = np.atleast_1d(theta)
    C = r * unit(theta)                                      # crankpin centre
    u0 = unit(np.full_like(theta, PHI[0]))
    # master piston: |s0*u0 - C| = L
    cu = np.sum(C * u0, axis=1)
    s0 = cu + np.sqrt(L**2 - (np.sum(C*C, axis=1) - cu**2))
    P0 = s0[:, None] * u0
    beta = np.arctan2(P0[:, 0] - C[:, 0], P0[:, 1] - C[:, 1])  # master rod angle from +z
    S = np.zeros((len(theta), N)); S[:, 0] = s0
    K = np.zeros((len(theta), N, 2))
    for k in range(1, N):
        Kk = C + a * unit(beta + PHI[k] + dk[k])
        uk = unit(np.full_like(theta, PHI[k]))
        ku = np.sum(Kk * uk, axis=1)
        S[:, k] = ku + np.sqrt(l**2 - (np.sum(Kk*Kk, axis=1) - ku**2))
        K[:, k] = Kk
    return S, beta, C, K

def summary(r, L, a, l, dk=None, n=7201):
    th = np.linspace(0, 2*np.pi, n)
    S, beta, C, K = solve(th, r, L, a, l, dk)
    smax = S.max(0); smin = S.min(0); stroke = smax - smin
    tdc_ang = np.degrees(th[S.argmax(0)])
    ideal = np.degrees(PHI)
    lag = (tdc_ang - ideal + 180) % 360 - 180
    return dict(smax=smax, smin=smin, stroke=stroke, tdc_lag=lag, maxrod=np.degrees(np.abs(beta).max()))

if __name__ == '__main__':
    r, L, a = 85.0, 300.0, 68.0
    for l in (L - a, 230.0, 235.0):
        s = summary(r, L, a, l)
        print('l=%.1f' % l, 'TDC s:', s['smax'].round(2), '\n  stroke:', s['stroke'].round(2), '\n  TDC lag deg:', s['tdc_lag'].round(2))
