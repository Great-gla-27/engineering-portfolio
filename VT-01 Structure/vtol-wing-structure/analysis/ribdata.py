import json, numpy as np
G = json.load(open("geom.json")); L = json.load(open("spanload.json"))
ribs = G["ribs"]; half = G["half"]
y = np.array(L["y"])*1000; Ls = np.array(L["L_strip_cruise"])*L["scale_ult"]   # N per strip, ultimate
# tributary: each strip's load goes to nearest rib, split linearly between the two bounding ribs (lever rule)
F = np.zeros(len(ribs))
for yi, li in zip(y, Ls):
    k = np.searchsorted(ribs, yi) - 1; k = max(0, min(k, len(ribs)-2))
    t = (yi - ribs[k])/(ribs[k+1]-ribs[k]); F[k] += li*(1-t); F[k+1] += li*t
M_check = (F*np.array(ribs)/1000).sum()
print("rib loads (N):", dict(zip(ribs, F.round(2)))); print(f"sum {F.sum():.1f} N (want {Ls.sum():.1f}); root moment from rib loads {M_check:.1f} N.m (VLM {L['M_root_ult']:.1f})")
def chord(yy): c_in, c_t = G["c_in"], G["c_t"]; return c_in if yy <= 400 else c_in+(c_t-c_in)*(yy-400)/(half-400)
holes = {}
for yy in ribs:
    sec = np.array(G["rib_sections"][str(yy)]); xr = G["rear_x_mm"][str(yy)]
    # lightening hole between spars: span between spar edges, centred on local mid-camber
    x_a, x_b = 0 + G["P"]["spar_OD"]/2 + 4, xr - G["P"]["rear_OD"]/2 - 4
    xm = 0.5*(x_a+x_b)
    up = sec[:, 2][np.argsort(sec[:,0])]; 
    # local upper/lower at xm
    pts = sec[:, [0,2]]; ile = np.argmin(pts[:,0]); U = pts[:ile+1][::-1]; Lo = pts[ile:]
    zu = np.interp(xm, U[:,0], U[:,1]); zl = np.interp(xm, Lo[:,0], Lo[:,1])
    d = min(0.6*(zu-zl), 0.8*(x_b-x_a))
    holes[str(yy)] = dict(spar=[0.0, G["spar_z"], G["P"]["spar_OD"]], rear=[xr, G["rear_z"], G["P"]["rear_OD"]],
                          light=[float(xm), float(0.5*(zu+zl)), float(d)] if d > 6 else None)
    print(f"rib {yy:6.1f}: chord {chord(yy):5.1f}, lightening hole d={d:4.1f} mm at x={xm:5.1f}")
json.dump(dict(F=F.tolist(), holes=holes), open("ribdata.json","w"))
