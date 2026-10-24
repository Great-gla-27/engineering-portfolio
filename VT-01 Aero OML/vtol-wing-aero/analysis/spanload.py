import aerosandbox as asb, aerosandbox.numpy as np, json
from vlm import make, solve, V, rho, W, af
import neuralfoil as nf
ap, c_in, c_t = make(2.0)
def strips(alpha, ns=40):
    v, r = solve(ap, alpha, ns)
    F = np.array(v.forces_geometry); P = np.array(v.vortex_centers)
    y = P[:,1]; Lz = F[:,2]
    right = y > 0
    yb = np.round(y[right], 5); keys = np.unique(yb)
    Ls = np.array([Lz[right][yb == k].sum() for k in keys])
    return keys, Ls, float(r["CL"])
y_brk, b = 0.40, 2.0
chord = lambda y: np.where(y <= y_brk, c_in, c_in + (c_t-c_in)*(y-y_brk)/(b/2-y_brk))
# spanwise strip width
ys, Ls, CL = strips(2.41)
dy = np.gradient(ys) if len(ys) > 1 else 0
# local cl = L' / (q c)
q = 0.5*rho*V**2
# strip width: reconstruct from spacing
edges = np.concatenate([[0], 0.5*(ys[1:]+ys[:-1]), [b/2]])
w = np.diff(edges)
cl_loc = Ls/w/(q*chord(ys))
L_half = Ls.sum(); M_root = (Ls*ys).sum(); ybar = M_root/L_half
print(f"cruise: CL {CL:.3f}, half-wing lift {L_half:.2f} N (want {W/2:.2f}), spanwise centroid {ybar:.3f} m (elliptic 0.424)")
n_ult = 5.7; scale = n_ult*(W/2)/L_half
print(f"ultimate (n=5.7) root bending moment from VLM distribution = {M_root*scale:.1f} N.m (elliptic hand calc 47.5)")
# stall margin: raise alpha until any station local cl hits section clmax at local Re (Re at stall speed)
Vs = 11.0
for alpha in np.arange(6, 16.1, 1.0):
    ys2, Ls2, CL2 = strips(alpha, 30)
    e2 = np.concatenate([[0], 0.5*(ys2[1:]+ys2[:-1]), [b/2]]); w2 = np.diff(e2)
    cl2 = Ls2/w2/(q*chord(ys2))
    Re_loc = rho*Vs*chord(ys2)/1.81e-5
    clmax_loc = []
    for Re in Re_loc:
        a = np.linspace(4, 18, 57)
        r = af.get_aero_from_neuralfoil(alpha=a, Re=float(Re), mach=0.03, model_size="large")
        clmax_loc.append(float(np.max(r["CL"])))
    ratio = cl2/np.array(clmax_loc); i = int(np.argmax(ratio))
    print(f"alpha {alpha:4.1f}: CL_wing {CL2:.3f}, max cl/clmax {ratio.max():.2f} at y = {ys2[i]:.2f} m ({ys2[i]/(b/2)*100:.0f}% semispan)")
    if ratio.max() >= 1.0:
        print(f"  -> first section stall at {ys2[i]/(b/2)*100:.0f}% semispan, wing CLmax approx {CL2:.2f}")
        break
# FEA load table: lift per rib bay at ultimate
json.dump(dict(y=list(map(float, ys)), L_strip_cruise=list(map(float, Ls)), w=list(map(float, w)), c_in=float(c_in), c_t=float(c_t),
               y_brk=y_brk, scale_ult=float(scale), M_root_ult=float(M_root*scale), ybar=float(ybar)), open("spanload.json","w"), indent=1)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
yy = np.linspace(0, b/2, 200); ell = (4*(W/2)/(np.pi*b/2))*np.sqrt(1-(yy/(b/2))**2)
plt.figure(figsize=(7,3.5)); plt.plot(ys, Ls/w, label="VLM, 2° washout"); plt.plot(yy, ell, "--", label="elliptic, same lift")
plt.xlabel("spanwise position y (m)"); plt.ylabel("lift per unit span (N/m), cruise 1 g"); plt.legend(); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig("spanload.png", dpi=110)
