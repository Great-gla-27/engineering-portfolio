"""Compare the stiffened CalculiX model with stiffened_hand.py: bending stress in the skin and
at a blade tip, front web shear, tip deflection, and the buckling factor.
Usage: python stiffened_compare.py <run dir>
"""
import sys, os, csv, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hand_calc')); sys.path.insert(0, HERE)
import wingbox_hand as W
import stiffened_hand as SK
from wingbox_shell import read_frd, buckling_factors
from compare import nearest
from wingbox_stiffened import DESIGN as D

STATIONS = [0.6, 1.0, 2.2, 5.0]          # mid rib bay (ribs every 0.4 m)


def hand_resultants(z):
    w = SK.weight_per_m(D['t_s'], D['t_w'], D['n_s'], D['h_b'], D['t_b'], D['L'], D['t_r'])
    zg = np.linspace(z, W.SEMI_SPAN, 20001); q = W.lift_per_span(zg) - w
    V = np.trapezoid(q, zg); M = np.trapezoid(q * (zg - z), zg)
    T = np.trapezoid(W.lift_per_span(zg), zg) * W.TORQUE_ARM
    return V, M, T


def main(run):
    r = read_frd(os.path.join(run, 'wb01k_static.frd')); C, S, U = r['COORD'], r['STRESS'], r['DISP']
    I = SK.section(D['t_s'], D['t_w'], D['n_s'], D['h_b'], D['t_b'])
    b = W.BOX_WIDTH / (D['n_s'] + 1); x_bay = W.BOX_LE + b / 2; x_bl = W.BOX_LE + b
    y_tip = W.BOX_DEPTH / 2 - D['t_s'] / 2 - D['h_b']
    rows = []
    for z in STATIONS:
        V, M, T = hand_resultants(z)
        n_s, _ = nearest(C, x_bay, W.BOX_DEPTH / 2, z); n_b, _ = nearest(C, x_bl, y_tip, z)
        n_f, _ = nearest(C, W.BOX_LE, 0.0, z)
        tau_h = (V / (2 * W.BOX_DEPTH) + T / (2 * W.enclosed_area())) / D['t_w']
        rows.append(dict(z=C[n_s][2], sigma_skin_hand=M * W.BOX_DEPTH / 2 / I / 1e6, sigma_skin_fe=-S[n_s][2] / 1e6,
                         sigma_blade_hand=M * y_tip / I / 1e6, sigma_blade_fe=-S[n_b][2] / 1e6,
                         tau_web_hand=tau_h / 1e6, tau_web_fe=abs(S[n_f][4]) / 1e6))
    n_ft, _ = nearest(C, W.BOX_LE, 0.0, W.SEMI_SPAN); n_rt, _ = nearest(C, W.BOX_LE + W.BOX_WIDTH, 0.0, W.SEMI_SPAN)
    v_fe = 0.5 * (U[n_ft][1] + U[n_rt][1])
    zg = np.linspace(0, W.SEMI_SPAN, 2001); Mz = np.array([hand_resultants(z)[1] for z in zg])
    kappa = Mz / (W.E_MOD * I)
    slope = np.concatenate([[0], np.cumsum(0.5 * (kappa[1:] + kappa[:-1]) * np.diff(zg))])
    v_h = np.trapezoid(slope, zg)
    lam_fe = buckling_factors(os.path.join(run, 'wb01k_buckle.dat'))
    h = SK.evaluate(D['t_s'], D['t_w'], D['n_s'], D['h_b'], D['t_b'], D['L'], D['t_r'])
    elastic = dict(skin=float(h['f_skin']), blade=float(h['f_blade']), column_euler=float(h['sig_e'] / h['sigma']),
                   column_johnson=float(h['f_col']), web=float(h['f_web']))
    return rows, dict(v_tip_fe_mm=v_fe * 1e3, v_tip_hand_mm=v_h * 1e3), lam_fe, elastic


if __name__ == '__main__':
    run = sys.argv[1]
    rows, tip, lam, el = main(run)
    for r in rows: print('  '.join('%s %.2f' % kv for kv in r.items()))
    print(tip); print('FE buckling factors', ['%.3f' % x for x in lam]); print('hand factors', el)
    out = os.path.join(HERE, '..', 'results'); os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'stiffened_compare.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
