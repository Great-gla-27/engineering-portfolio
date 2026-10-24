"""Geometry generator: all wing dimensions come from here (single source of truth)."""
import aerosandbox as asb, numpy as np, json
P = dict(b=2.0, S=0.407, y_brk=0.40, taper=0.6, washout_deg=2.0, airfoil="sd7062",
         spar_x=0.25, spar_OD=16.0, spar_ID=14.0, rear_x=0.62, rear_OD=6.0, rear_ID=4.0,
         rib_t=3.0, rib_pitch=100.0, boom_y=400.0, n_pts=70)
c_in = P["S"]/(2*(P["y_brk"]+(P["b"]/2-P["y_brk"])*(1+P["taper"])/2))*1000   # mm
c_t = P["taper"]*c_in; half = P["b"]/2*1000
af = asb.Airfoil(P["airfoil"]).repanel(n_points_per_side=P["n_pts"]//2)
xy = np.array(af.coordinates)                       # unit chord, TE->upper->LE->lower->TE
def chord(y): return c_in if y <= P["boom_y"] else c_in+(c_t-c_in)*(y-P["boom_y"])/(half-P["boom_y"])
def twist(y): return 0.0 if y <= P["boom_y"] else -P["washout_deg"]*(y-P["boom_y"])/(half-P["boom_y"])
def section(y):
    """3D points (x aft, y span, z up) in mm; 25% chord line straight at x=0; twist about 25% chord (nose-down = negative)."""
    c = chord(y); th = np.radians(twist(y))
    x = (xy[:,0]-0.25)*c; z = xy[:,1]*c
    xr = x*np.cos(th) + z*np.sin(th); zr = -x*np.sin(th) + z*np.cos(th)
    return np.c_[xr, np.full_like(xr, y), zr]
def thick_at(xc, y):
    """upper/lower surface z (mm) at chord fraction xc for the twisted section at y (approx, small twist)."""
    c = chord(y); up = xy[:np.argmin(xy[:,0])+1][::-1]; lo = xy[np.argmin(xy[:,0]):]
    zu = np.interp(xc, up[:,0], up[:,1])*c; zl = np.interp(xc, lo[:,0], lo[:,1])*c
    th = np.radians(twist(y)); xloc = (xc-0.25)*c
    return zu - xloc*np.sin(th), zl - xloc*np.sin(th)
# straight spar: choose centre z constant (inboard) and check clearance along whole span
ys = np.linspace(0, half-5, 200)
def spar_fit(xc, OD, zc=None):
    zu = np.array([thick_at(xc, y)[0] for y in ys]); zl = np.array([thick_at(xc, y)[1] for y in ys])
    if zc is None:  # best straight horizontal line: maximise min clearance
        cands = np.linspace(zl.max(), zu.min(), 200)
        clr = [min((zu-z).min(), (z-zl).min()) - OD/2 for z in cands]
        zc = cands[int(np.argmax(clr))]
    margin = min((zu-zc).min(), (zc-zl).min()) - OD/2
    return zc, margin, zu, zl
zs, ms, zu, zl = spar_fit(P["spar_x"], P["spar_OD"])
zr, mr, _, _ = spar_fit(P["rear_x"], P["rear_OD"])
print(f"chords: root/inboard {c_in:.1f} mm, tip {c_t:.1f} mm; half span {half:.0f} mm")
print(f"main spar {P['spar_OD']:.0f} mm at {P['spar_x']*100:.0f}% chord: centre z = {zs:.2f} mm, min skin clearance = {ms:.2f} mm (local depth root {zu[0]-zl[0]:.1f}, tip {zu[-1]-zl[-1]:.1f} mm)")
print(f"rear spar {P['rear_OD']:.0f} mm at {P['rear_x']*100:.0f}% chord: centre z = {zr:.2f} mm, min clearance = {mr:.2f} mm")
ribs = [0.0] + [y for y in np.arange(P["rib_pitch"], half-P["rib_pitch"]/2, P["rib_pitch"])] + [half - P["rib_t"]/2]
if P["boom_y"] not in ribs: ribs.append(P["boom_y"])
ribs = sorted(set(round(r,1) for r in ribs))
out = dict(P=P, c_in=c_in, c_t=c_t, half=half, spar_z=zs, rear_z=zr, ribs=ribs,
           sections={str(y): section(y).round(3).tolist() for y in [0.0, P["boom_y"], half]},
           rib_sections={str(y): section(y).round(3).tolist() for y in ribs})
# x positions of spars (25% line is x=0) per rib for hole placement
out["spar_x_mm"] = {str(y): float((P["spar_x"]-0.25)*chord(y)) for y in ribs}   # 0
out["rear_x_mm"] = {str(y): float((P["rear_x"]-0.25)*chord(y)) for y in ribs}
print("ribs at y =", ribs)
print("rear spar x at root/tip:", out["rear_x_mm"][str(ribs[0])], out["rear_x_mm"][str(ribs[-1])], "(not straight: rear spar must be straight, check)")
json.dump(out, open("geom.json","w"))

# rear spar as a single straight tube from 62% root chord to 62% tip chord
x0, x1 = out["rear_x_mm"][str(ribs[0])], out["rear_x_mm"][str(ribs[-1])]
best = None
for zc in np.linspace(0, 12, 241):
    m = 1e9
    for y in ys:
        xmm = x0 + (x1-x0)*y/half; xc = xmm/chord(y) + 0.25
        u, l = thick_at(xc, y); m = min(m, u-zc, zc-l)
    m -= P["rear_OD"]/2
    if best is None or m > best[1]: best = (zc, m)
out["rear_line"] = dict(x0=x0, x1=x1, z=best[0]); out["rear_z"] = best[0]
out["rear_x_mm"] = {str(y): float(x0 + (x1-x0)*y/half) for y in ribs}
print(f"straight rear spar: x {x0:.1f} -> {x1:.1f} mm, z = {best[0]:.2f} mm, min clearance {best[1]:.2f} mm; chord fraction at boom rib = {(x0+(x1-x0)*0.4)/c_in+0.25:.3f}")
json.dump(out, open("geom.json","w"))
