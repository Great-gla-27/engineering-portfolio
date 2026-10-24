import aerosandbox as asb, aerosandbox.numpy as np, json
W, rho, V = 39.24, 1.225, 18.0
af = asb.Airfoil("sd7062")
def make(washout, y_brk=0.40, lam=0.6, b=2.0, S=0.407):
    c_in = S / (2*(y_brk + (b/2-y_brk)*(1+lam)/2))
    c_t = lam*c_in
    xs = [asb.WingXSec(xyz_le=[0,0,0], chord=c_in, twist=0, airfoil=af),
          asb.WingXSec(xyz_le=[0.25*(c_in-c_in),y_brk,0], chord=c_in, twist=0, airfoil=af),
          asb.WingXSec(xyz_le=[0.25*(c_in-c_t),b/2,0], chord=c_t, twist=-washout, airfoil=af)]   # 25% chord line straight
    w = asb.Wing(name="main", symmetric=True, xsecs=xs)
    return asb.Airplane(wings=[w], s_ref=w.area(), c_ref=w.mean_aerodynamic_chord(), b_ref=w.span()), c_in, c_t
def solve(ap, alpha, ns=40):
    v = asb.VortexLatticeMethod(airplane=ap, op_point=asb.OperatingPoint(velocity=V, alpha=alpha),
                                spanwise_resolution=ns, chordwise_resolution=8)
    return v, v.run()
res = {}
for wo in (0.0, 1.0, 2.0, 3.0):
    ap, c_in, c_t = make(wo)
    # find alpha for cruise CL
    a_lo, a_hi = -2.0, 8.0
    for _ in range(25):
        a = 0.5*(a_lo+a_hi); _, r = solve(ap, a, 24)
        (a_lo, a_hi) = (a, a_hi) if r["CL"] < 0.485 else (a_lo, a)
    v, r = solve(ap, a)
    CL, CDi = float(r["CL"]), float(r["CD"])
    e = CL**2/(np.pi*ap.wings[0].aspect_ratio()*CDi)
    res[wo] = dict(alpha=a, CL=CL, CDi=CDi, e=e, c_in=c_in, c_t=c_t, S=ap.s_ref, AR=ap.wings[0].aspect_ratio(), MAC=ap.c_ref)
    print(f"washout {wo:.0f}°: alpha_cruise {a:.2f}°, CL {CL:.3f}, CDi {CDi*1e4:.1f} cts, e = {e:.3f} | c_in {c_in*1000:.0f} mm, c_tip {c_t*1000:.0f} mm, AR {ap.wings[0].aspect_ratio():.2f}, MAC {ap.c_ref*1000:.0f} mm")
json.dump(res, open("vlm_summary.json","w"), indent=1)
