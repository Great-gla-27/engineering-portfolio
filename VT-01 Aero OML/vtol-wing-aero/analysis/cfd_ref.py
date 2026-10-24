import aerosandbox as asb, numpy as np, json
from vlm import make, solve
ap, c_in, c_t = make(2.0)
af = asb.Airfoil("sd7062")
rows = []
for a in [-2, 0, 2, 2.41, 4, 6, 8, 10]:
    v, r = solve(ap, a, 24)
    CL, CDi = float(r["CL"]), float(r["CD"])
    # profile drag: NeuralFoil at MAC Re, section cl ~ CL (strip-mean approximation)
    nf = af.get_aero_from_neuralfoil(alpha=np.linspace(-6, 14, 81), Re=248e3, mach=0.05, model_size="xlarge")
    cd0 = float(np.interp(CL, nf["CL"][:np.argmax(nf["CL"])+1], nf["CD"][:np.argmax(nf["CL"])+1]))
    rows.append((a, CL, CDi, cd0, CDi+cd0, CL/(CDi+cd0)))
print(" alpha   CL     CDi     CD0    CD     L/D   (VLM + NeuralFoil, 18 m/s, Re 248k)")
for r in rows: print(" %5.2f  %.3f  %.4f  %.4f  %.4f  %5.1f" % r)
json.dump(rows, open("cfd_ref.json","w"))
