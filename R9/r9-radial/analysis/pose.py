"""Mechanism pose from crank angle, using the tuned design point. All mm / radians.
Engine plane x-z, crank axis +Y, angles from +z, anti-clockwise seen from the anti-propeller end (the build mirrors this)."""
import json, os, numpy as np
import design as D

DP = json.load(open(os.path.join(os.path.dirname(__file__), 'design_point.json')))
AK = np.array(DP['a_k']); DK = np.radians(DP['d_k_deg'])
PHI = D.K.PHI

def pose(theta):
    S, beta, C, Kp = D.solve(np.atleast_1d(theta), AK, DK)
    S, beta, C, Kp = S[0], float(beta[0]), C[0], Kp[0]
    P = np.array([S[k] * np.array([np.sin(PHI[k]), np.cos(PHI[k])]) for k in range(9)])
    gam = np.array([np.arctan2(P[k, 0] - Kp[k, 0], P[k, 1] - Kp[k, 1]) for k in range(9)])
    gam[0] = beta
    return dict(theta=float(theta), beta=beta, C=C, K=Kp, S=S, P=P, gamma=gam)

if __name__ == '__main__':
    p = pose(0.0)
    np.set_printoptions(precision=3, suppress=True)
    for k, v in p.items(): print(k, v)
