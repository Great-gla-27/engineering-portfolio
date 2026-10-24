"""AC-01 phase 0: re-check of the ENG3006 sizing and stability numbers.

1. Wing planform from the master table: root and tip chord, mean geometric chord, true MAC
   and its spanwise position.
2. Reproduce the stated stability result (CG 26.99 %, NP 37.13 %, SM 10.15 % MAC) from the
   inputs the team scripts actually used, to find out which wing it was computed for.
3. Recompute the static margin with the true MAC of the final wing.
4. Recompute the CG at MTOW from the two mass tables the report gives.
5. Fuel-burn CG shift, exactly.
Writes results/sizing_check.json. Usage: python sizing_check.py
"""
import json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'params'))
from params import load

M = load()


def planform(b, S, lam):
    cr = 2 * S / (b * (1 + lam)); ct = lam * cr
    mgc = S / b
    mac = 2 / 3 * cr * (1 + lam + lam ** 2) / (1 + lam)
    y_mac = b / 6 * (1 + 2 * lam) / (1 + lam)
    return dict(root_chord=cr, tip_chord=ct, mgc=mgc, mac=mac, y_mac=y_mac)


def neutral_point(VH):
    return M['NPWingBody'] + M['LiftSlopeTail'] / M['LiftSlopeWing'] * VH * (1 - M['Downwash'])


def stated_reproduction():
    """the team scripts: S = 73.6, b = 23.7 (initial_sizing.m L26), c_bar = b / AR (L33)."""
    c_bar = 23.7 / 7.8
    h = (M['XcgStated'] - M['WingRootLEx']) / c_bar
    hn = neutral_point(M['VH'])
    S_T = M['VH'] * M['WingArea'] * c_bar / M['TailArmAssumed']
    S_F = M['VV'] * M['WingArea'] * 23.7 / (0.45 * 17.7)
    return dict(c_bar=c_bar, h_cg=h, h_n=hn, SM=hn - h, S_T=S_T, S_F=S_F)


def corrected(pf):
    mac = pf['mac']
    h = (M['XcgStated'] - M['WingRootLEx']) / mac
    # a) tail area and arm held at the team values; V_H recomputed with the true MAC
    VH_a = M['HTArea'] * M['TailArmAssumed'] / (M['WingArea'] * mac)
    hn_a = neutral_point(VH_a)
    # b) V_H held at 0.26 (as if the tail were re-sized for the new MAC)
    hn_b = neutral_point(M['VH'])
    return dict(mac=mac, h_cg=h, VH_held_area=VH_a, h_n_held_area=hn_a, SM_held_area=hn_a - h,
                h_n_held_VH=hn_b, SM_held_VH=hn_b - h)


def cg_tables():
    # report Table 3 groups, with the propulsion group split per Table 10 at mass-statement stations
    t3 = [(M['MWing'], 8.5), (M['MFuselage'], 8.2), (M['MEmpennage'], 16.6), (M['MGear'], 9.2),
          (M['MEquipment'], 7.1), (M['PayloadMass'], 8.0),
          (M['MotorMass'], M['XMotor']), (M['FuelCellMass'], M['XFuelCell']),
          (M['BatteryMass'], M['XBattery']), (M['LH2TankSystemMass'], M['XLH2Tank'])]
    m3 = sum(m for m, _ in t3); x3 = sum(m * x for m, x in t3) / m3
    # the propulsion x that Table 3 would need to give 9.32 m
    rest = [(m, x) for m, x in t3[:6]]
    x_prop_needed = (M['MTOW'] * M['XcgStated'] - sum(m * x for m, x in rest)) / M['MPropulsion']
    # the detailed mass statement (Group Stuff/Mass statement.pdf), every listed row
    ms = [(1045, 8.5), (40, 10.2), (85, 9.8), (15, 8.4), (15, 8.4), (10, 9.2), (12, 8.5), (8, 8.5),
          (885, 8.85), (140, 8.2), (155, 7.5), (185, 16.8), (115, 16.4), (400, 6.5), (560, 8.0),
          (435, 7.5), (150, 9.2), (120, 1.2), (121, 8.5), (110, 10.5), (160, 1.5), (840, 8.0),
          (400, 12.5), (130, 14.5), (480, 14.5), (200, 6.3)]
    mm = sum(m for m, _ in ms); xm = sum(m * x for m, x in ms) / mm
    return dict(table3_mass=m3, table3_xcg=x3, propulsion_x_needed=x_prop_needed,
                propulsion_x_from_items=sum(m * x for m, x in t3[6:]) / sum(m for m, _ in t3[6:]),
                massstatement_rows_mass=mm, massstatement_rows_xcg=xm)


def fuel_burn(x_cg):
    mf = M['LH2FuelMass']; m0 = M['MTOW']
    exact = mf * (M['XLH2Tank'] - x_cg) / (m0 - mf)
    report = mf * (M['XLH2Tank'] - M['XcgStated']) / m0
    return dict(shift_exact=exact, shift_report_formula=report)


def main():
    pf = planform(M['WingSpan'], M['WingArea'], M['TaperRatio'])
    out = dict(planform=pf, stated=stated_reproduction(), corrected=corrected(pf), cg=cg_tables(),
               fuel_burn_at_stated_cg=fuel_burn(M['XcgStated']))
    os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'sizing_check.json'), 'w'), indent=1)
    return out


if __name__ == '__main__':
    o = main()
    p, s, c, g = o['planform'], o['stated'], o['corrected'], o['cg']
    print('Planform: c_r %.3f, c_t %.3f, MGC %.3f, MAC %.3f m at y = %.3f m' % (p['root_chord'], p['tip_chord'], p['mgc'], p['mac'], p['y_mac']))
    print('Stated result reproduced with b = 23.7 m, c_bar = b/AR = %.3f m: h %.2f %%, hn %.2f %%, SM %.2f %%; S_T %.2f, S_F %.2f'
          % (s['c_bar'], s['h_cg'] * 100, s['h_n'] * 100, s['SM'] * 100, s['S_T'], s['S_F']))
    print('True MAC %.3f m: h %.2f %%; tail held: V_H %.3f, hn %.2f %%, SM %.2f %%; V_H held: SM %.2f %%'
          % (c['mac'], c['h_cg'] * 100, c['VH_held_area'], c['h_n_held_area'] * 100, c['SM_held_area'] * 100, c['SM_held_VH'] * 100))
    print('CG: Table 3 groups %.0f kg at %.3f m (propulsion items at %.2f m; 9.32 m needs %.2f m); mass statement rows %.0f kg at %.3f m'
          % (g['table3_mass'], g['table3_xcg'], g['propulsion_x_from_items'], g['propulsion_x_needed'], g['massstatement_rows_mass'], g['massstatement_rows_xcg']))
    print('Fuel burn shift: %.3f m exact, %.3f m by the report formula' % tuple(o['fuel_burn_at_stated_cg'].values()))
