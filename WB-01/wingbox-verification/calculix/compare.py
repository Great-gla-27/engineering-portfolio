"""Compare a CalculiX static result with the hand calculation along the span.

Quantities, at each station:
  sigma_cover   bending stress at the middle of the upper cover (x = 0.8 m), SZZ
  sigma_corner  bending stress at the upper cover corners (mean of front and rear), SZZ
  tau_front     shear stress at the front web neutral axis, |SYZ|
  tau_rear      same, rear web
plus tip deflection (mean v at the tip) and tip twist ((v_front - v_rear) / width).
"""
import sys, os, numpy as np, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hand_calc'))
import wingbox_hand as W
from wingbox_shell import read_frd

STATIONS = [0.0, 0.2, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]


def nearest(coord, x, y, z):
    ids = np.array(list(coord)); c = np.array([coord[i] for i in ids])
    d = (c[:, 0] - x) ** 2 + (c[:, 1] - y) ** 2 + (c[:, 2] - z) ** 2
    return ids[np.argmin(d)], np.sqrt(d.min())


def hand_at(t, z, extra_weight=0.0):
    zg, S, M, T = W.resultants(t, 20001, extra_weight)
    i = np.argmin(abs(zg - z))
    sigma = M[i] * (W.BOX_DEPTH / 2) / W.ixx(t)
    s, q, xy = W.shear_flow_section(t, S[i], T[i])
    na = np.isclose(xy[:, 1], 0.0, atol=W.BOX_DEPTH / 400)
    front = np.isclose(xy[:, 0], -W.BOX_WIDTH / 2) & na
    rear = np.isclose(xy[:, 0], W.BOX_WIDTH / 2) & na
    return sigma, abs(q[front]).max() / t, abs(q[rear]).max() / t


def compare(frd, t, out_csv=None, extra_weight=0.0, stations=None):
    r = read_frd(frd); C, S, U = r['COORD'], r['STRESS'], r['DISP']
    xm, x0, x1, yt = W.BOX_LE + W.BOX_WIDTH / 2, W.BOX_LE, W.BOX_LE + W.BOX_WIDTH, W.BOX_DEPTH / 2
    rows = []
    for z in (stations or STATIONS):
        n_mid, _ = nearest(C, xm, yt, z)
        n_c0, _ = nearest(C, x0, yt, z); n_c1, _ = nearest(C, x1, yt, z)
        n_f, _ = nearest(C, x0, 0.0, z); n_r, _ = nearest(C, x1, 0.0, z)
        zz = C[n_mid][2]
        sig_h, tf_h, tr_h = hand_at(t, zz, extra_weight)
        rows.append(dict(z=zz, sigma_hand=sig_h / 1e6, sigma_cover=-S[n_mid][2] / 1e6,
                         sigma_corner=-0.5 * (S[n_c0][2] + S[n_c1][2]) / 1e6,
                         tau_front_hand=tf_h / 1e6, tau_front=abs(S[n_f][4]) / 1e6,
                         tau_rear_hand=tr_h / 1e6, tau_rear=abs(S[n_r][4]) / 1e6))
    n_ft, _ = nearest(C, x0, 0.0, W.SEMI_SPAN); n_rt, _ = nearest(C, x1, 0.0, W.SEMI_SPAN)
    v_tip = 0.5 * (U[n_ft][1] + U[n_rt][1]); twist = (U[n_ft][1] - U[n_rt][1]) / W.BOX_WIDTH
    _, vh = W.tip_deflection(t, W.E_MOD, 20001, extra_weight); _, th = W.tip_twist(t, W.G_MOD, 20001)
    tip = dict(v_tip_mm=v_tip * 1e3, v_hand_mm=vh[-1] * 1e3, twist_deg=np.degrees(twist), twist_hand_deg=np.degrees(th[-1]))
    if out_csv:
        with open(out_csv, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows, tip


if __name__ == '__main__':
    rows, tip = compare(sys.argv[1], float(sys.argv[2]))
    print('%6s %9s %9s %9s %9s %9s %9s %9s' % ('z m', 'sig hand', 'sig mid', 'sig cnr', 'tF hand', 'tF fe', 'tR hand', 'tR fe'))
    for r in rows:
        print('%6.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f' % tuple(r.values()))
    print(tip)
