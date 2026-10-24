"""AC-01 design checks computed from the Fusion model.

Input: results/ac01_measure.json, measured off the Fusion model (body volumes and
centroids in aircraft axes, wing and tailplane end-section LE/TE points, propeller hub and tip
radius, fuselage surface mesh points, fuselage skin centroid).
Output: results/design_checks.json and a printed summary.

Mass method. The CG is computed two ways:
  A  the report's Table 3 group masses at the stations Table 3 gives (propulsion split per
     Table 10 at the mass-statement stations), i.e. the team's own numbers, re-added
  B  the same masses placed at the centroids of the CAD bodies that carry them (uniform
     density within each group)
Neither uses the stated 9.32 m; both are compared with it.
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'params')); sys.path.insert(0, HERE)
from params import load
import sizing_check as SC

M = load()
CFR_GROUND = 7 * 0.0254          # 14 CFR 23.925(a), nose-wheel aeroplane: 7 in
CFR_RADIAL = 1 * 0.0254          # 14 CFR 23.925(d)(1): 1 in radial clearance to structure
TIPBACK_GUIDE = 15.0             # deg, design guideline (Raymer, Aircraft Design, landing gear chapter)
GEAR_SPLIT = (130.0, 20.0)       # A-8: main / nose share of the 150 kg gear mass


def planform_from_points(root, tip):
    (rl, rt), (tl, tt) = root, tip
    cr, ct = math.dist(rl, rt), math.dist(tl, tt)
    b = 2 * (tl[1] - rl[1])
    S = b / 2 * (cr + ct); lam = ct / cr
    mac = 2 / 3 * cr * (1 + lam + lam ** 2) / (1 + lam)
    y_mac = b / 6 * (1 + 2 * lam) / (1 + lam)
    x_le_mac = rl[0] + (tl[0] - rl[0]) * y_mac / (b / 2)
    return dict(root_chord=cr, tip_chord=ct, span=b, area=S, AR=b * b / S, taper=lam, mac=mac,
                y_mac=y_mac, x_le_mac=x_le_mac, x_ac=x_le_mac + 0.25 * mac)


def centroid(rows):
    m = sum(r[0] for r in rows)
    return m, np.array([sum(r[0] * r[k] for r in rows) / m for k in (1, 2)])


def group(bodies, pred):
    sel = [b for b in bodies if pred(b)]
    v = sum(b[2] for b in sel)
    return np.array([sum(b[2] * b[3] for b in sel) / v, sum(b[2] * b[5] for b in sel) / v]), len(sel)


def main():
    meas = json.load(open(os.path.join(HERE, '..', 'results', 'ac01_measure.json')))
    B = meas['bodies']
    an = SC.planform(M['WingSpan'], M['WingArea'], M['TaperRatio'])
    wing = planform_from_points(meas['sections']['wing_root'], meas['sections']['wing_tip'])
    ht = planform_from_points(meas['sections']['ht_root'], meas['sections']['ht_tip'])
    planform_err = {k: (wing[k2] - ref) / ref * 100 for k, k2, ref in
                    (('span', 'span', M['WingSpan']), ('area', 'area', M['WingArea']),
                     ('AR', 'AR', M['WingSpan'] ** 2 / M['WingArea']),
                     ('MAC', 'mac', an['mac']), ('root_chord', 'root_chord', an['root_chord']), ('tip_chord', 'tip_chord', an['tip_chord']))}
    l_T = ht['x_ac'] - wing['x_ac']

    # ---------------- propeller clearances
    fus = np.array(meas['fus_pts']); props = {}
    zg = -M['KeelHeight']
    for nm in ('Propeller:1', 'Propeller:2'):
        hx, hy, hz, R = meas[nm]
        rho = np.hypot(fus[:, 1] - hy, fus[:, 2] - hz)
        d = np.hypot(fus[:, 0] - hx, np.maximum(0.0, rho - R))
        props[nm] = dict(hub=[hx, hy, hz], tip_radius=R, ground=hz - R - zg, fuselage=float(d.min()))

    # ---------------- tail strike about the main wheel contact point
    xg = M['XMainGear']
    aft = fus[fus[:, 0] > xg + 0.5]
    ang = np.degrees(np.arctan2(aft[:, 2] - zg, aft[:, 0] - xg))
    i = int(np.argmin(ang)); tail_strike = dict(angle=float(ang[i]), point=aft[i].tolist())

    # ---------------- CG, method A (Table 3 stations)
    A_rows = [(M['MWing'], 8.5, 1.9), (M['MFuselage'], 8.2, 0.85), (M['MEmpennage'], 16.6, 4.0),
              (M['MGear'], 9.2, -0.2), (M['MEquipment'], 7.1, 1.0), (M['PayloadMass'], 8.0, 0.85),
              (M['MotorMass'], M['XMotor'], 1.95), (M['FuelCellMass'], M['XFuelCell'], 0.3),
              (M['BatteryMass'], M['XBattery'], 1.9), (M['LH2TankSystemMass'], M['XLH2Tank'], 0.85)]
    mA, cgA = centroid(A_rows)

    # ---------------- CG, method B (CAD centroids)
    occ = lambda o: (lambda b: b[0].startswith(o))
    wing_c, _ = group(B, occ('Wing'))
    seats_c, _ = group(B, lambda b: b[1].startswith('Passenger Seat'))
    crew_c, _ = group(B, lambda b: b[1].startswith('Crew Seat'))
    floor_c, _ = group(B, lambda b: b[1] == 'Cabin Floor')
    cargo_c, _ = group(B, lambda b: b[1] == 'Forward Cargo Bay')
    ht_c, _ = group(B, occ('Horizontal Tail'))
    vt_c, _ = group(B, occ('Vertical Tail'))
    epu_c, nepu = group(B, lambda b: b[1].startswith('EPU'))
    fc_c, nfc = group(B, lambda b: b[1].startswith('Fuel Cell Module'))
    bat_c, _ = group(B, lambda b: b[1] == 'Battery Buffer Pack')
    tank_c, _ = group(B, lambda b: b[1] == 'LH2 Tank Shell')
    mg_c, _ = group(B, occ('Main Landing Gear'))
    ng_c, _ = group(B, occ('Nose Landing Gear'))
    skin = np.array([meas['fus_skin'][1], meas['fus_skin'][2]])
    pax_c = seats_c + np.array([0.05, 0.25])          # A-9: occupant CG above and ahead of the seat-body centroid
    crew_cc = crew_c + np.array([0.05, 0.25])
    B_rows = [('Wing structure and controls', M['MWing'], wing_c),
              ('Fuselage structure (skin centroid)', 885.0, skin), ('Seats', 140.0, seats_c), ('Internal accommodation (floor)', 155.0, floor_c),
              ('Horizontal tail', 185.0, ht_c), ('Vertical tail', 115.0, vt_c),
              ('EPUs (2)', M['MotorMass'], epu_c), ('Fuel cell modules (8)', M['FuelCellMass'], fc_c),
              ('Battery buffer pack', M['BatteryMass'], bat_c), ('LH2 tank system incl. fuel', M['LH2TankSystemMass'], tank_c),
              ('Main landing gear', GEAR_SPLIT[0], mg_c), ('Nose landing gear', GEAR_SPLIT[1], ng_c),
              ('Equipment (Table 3 station, no body)', M['MEquipment'], np.array([7.1, 1.0])),
              ('Passengers (12 x 100 kg)', M['PaxCount'] * M['PaxMass'], pax_c), ('Crew (2)', M['CrewMass'], crew_cc),
              ('Cargo (balance of 1,380 kg)', M['PayloadMass'] - M['PaxCount'] * M['PaxMass'] - M['CrewMass'], cargo_c)]
    mB, cgB = centroid([(m, c[0], c[1]) for _, m, c in B_rows])
    # zero-fuel case: remove 240 kg at the tank centroid
    mf = M['LH2FuelMass']
    cgB_empty_tank = (mB * cgB - mf * tank_c) / (mB - mf)

    # ---------------- stability with the measured geometry
    S_T_meas = ht['area']
    def stab(x_cg, l_t, S_t):
        VH = S_t * l_t / (M['WingArea'] * wing['mac'])
        hn = SC.neutral_point(VH); h = (x_cg - wing['x_le_mac']) / wing['mac']
        return dict(VH=VH, h_n=hn, h_cg=h, SM=hn - h, x_np=wing['x_le_mac'] + hn * wing['mac'])
    stability = dict(stated_cg_assumed_arm=stab(M['XcgStated'], M['TailArmAssumed'], M['HTArea']),
                     stated_cg_measured_arm=stab(M['XcgStated'], l_T, S_T_meas),
                     cgA_measured_arm=stab(cgA[0], l_T, S_T_meas),
                     cgB_measured_arm=stab(cgB[0], l_T, S_T_meas))

    # ---------------- tip-back over the main gear (CAD CG)
    def tipback(cg): return math.degrees(math.atan2(xg - cg[0], cg[1] - zg))
    gear = dict(tipback_B=tipback(cgB), tipback_B_fuel_burnt=tipback(cgB_empty_tank),
                tipback_stated=tipback((M['XcgStated'], cgB[1])),
                x_main_gear_for_15deg=cgB[0] + (cgB[1] - zg) * math.tan(math.radians(TIPBACK_GUIDE)))

    out = dict(analytic_planform=an, measured_wing=wing, measured_tailplane=ht, planform_error_pct=planform_err,
               tail_arm_measured=l_T, propellers=props, cfr_23_925=dict(ground_m=CFR_GROUND, radial_m=CFR_RADIAL),
               tail_strike=tail_strike, cg_A=dict(mass=mA, x=cgA[0], z=cgA[1]),
               cg_B=dict(mass=mB, x=cgB[0], z=cgB[1], rows=[(n, m, c.tolist()) for n, m, c in B_rows]),
               cg_B_fuel_burnt=dict(x=cgB_empty_tank[0], z=cgB_empty_tank[1], shift=cgB[0] - cgB_empty_tank[0]),
               stability=stability, gear=gear)
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'design_checks.json'), 'w'), indent=1, default=float)
    return out


if __name__ == '__main__':
    o = main()
    w, e = o['measured_wing'], o['planform_error_pct']
    print('Wing measured: b %.4f, S %.4f, AR %.4f, MAC %.4f at y %.3f, x_LE,MAC %.4f' % (w['span'], w['area'], w['AR'], w['mac'], w['y_mac'], w['x_le_mac']))
    print('  error vs analytic (%%): ' + ', '.join('%s %+.3f' % kv for kv in e.items()))
    print('Tail arm measured %.3f m (assumed 8.67); tailplane S %.3f' % (o['tail_arm_measured'], o['measured_tailplane']['area']))
    for k, p in o['propellers'].items(): print(k, 'R %.4f, ground %.3f m, fuselage %.3f m' % (p['tip_radius'], p['ground'], p['fuselage']))
    print('Tail strike %.2f deg at %s' % (o['tail_strike']['angle'], o['tail_strike']['point']))
    print('CG A %.0f kg at x %.3f; CG B %.0f kg at x %.3f z %.3f; fuel burn shift %.3f m' % (o['cg_A']['mass'], o['cg_A']['x'], o['cg_B']['mass'], o['cg_B']['x'], o['cg_B']['z'], o['cg_B_fuel_burnt']['shift']))
    for k, s in o['stability'].items(): print(k, 'VH %.3f hn %.2f%% h %.2f%% SM %.2f%%' % (s['VH'], s['h_n'] * 100, s['h_cg'] * 100, s['SM'] * 100))
    print('gear', {k: round(v, 2) for k, v in o['gear'].items()})
