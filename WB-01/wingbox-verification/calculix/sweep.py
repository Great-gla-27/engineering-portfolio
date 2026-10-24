"""WB-01 phase 4: thickness sweep, hand calculation against CalculiX.

For each skin thickness the S8R shell model is run twice:
  static, with 0.5 m rib diaphragms (ribs hold the section shape, as the hand method assumes)
  buckle, unstiffened (the coursework design as drawn)
Rib self-weight is passed to the hand calculation as extra_weight so both carry the same load.
Results go to results/sweep.csv. Usage: python sweep.py [run dir]
"""
import sys, os, csv, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hand_calc')); sys.path.insert(0, HERE)
import wingbox_hand as W
import wingbox_shell as SH
from compare import compare

H = 0.05
RIB_PITCH = 0.5
T_MM = [3.0, 3.4, 3.8, 4.2, 5.0]


def rib_weight_per_m(t):
    return W.RHO * W.G_ACC * W.BOX_WIDTH * W.BOX_DEPTH * t / RIB_PITCH


def ccx(name, path):
    subprocess.run(['ccx', '-i', name], cwd=path, stdout=open(os.path.join(path, name + '.log'), 'w'),
                   stderr=subprocess.STDOUT, check=True)


def main(path):
    os.makedirs(path, exist_ok=True)
    out = []
    for tm in T_MM:
        t = tm / 1e3
        name, _ = SH.build(H, t, 'static', path, rib_pitch=RIB_PITCH)
        if not os.path.exists(os.path.join(path, name + '.frd')): ccx(name, path)
        rows, tip = compare(os.path.join(path, name + '.frd'), t, extra_weight=rib_weight_per_m(t),
                            stations=[0.75, 1.25, 2.25, 5.25])   # mid-bay: rib nodes average in the unloaded rib
        r1 = rows[1]                                     # z = 1.25 m, mid-bay, clear of the root
        bname, _ = SH.build(H, t, 'buckle', path)
        if not os.path.exists(os.path.join(path, bname + '.dat')): ccx(bname, path)
        lam = SH.buckling_factors(os.path.join(path, bname + '.dat'))[0]
        hand = W.root_stresses(t); bk = W.buckling_summary(t)
        out.append(dict(t_mm=tm, weight_N_per_m=hand['weight_per_m'],
                        sigma_root_hand=hand['sigma'] / 1e6, tau_root_hand=hand['tau_total'] / 1e6,
                        sigma_mid_hand=r1['sigma_hand'], sigma_mid_fe=r1['sigma_cover'],
                        tau_front_mid_hand=r1['tau_front_hand'], tau_front_mid_fe=r1['tau_front'],
                        v_tip_hand_mm=tip['v_hand_mm'], v_tip_fe_mm=tip['v_tip_mm'],
                        twist_hand_deg=tip['twist_hand_deg'], twist_fe_deg=tip['twist_deg'],
                        buckle_hand=bk['cover_factor'], buckle_fe=lam))
        print(' '.join('%s=%.4g' % kv for kv in out[-1].items()), flush=True)
    os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
    with open(os.path.join(HERE, '..', 'results', 'sweep.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    return out


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'runs', 'sweep'))
