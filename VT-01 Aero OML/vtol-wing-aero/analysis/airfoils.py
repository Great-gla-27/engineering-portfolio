import aerosandbox as asb, numpy as np, json
names = ["sd7062","clarky","naca4412","e205","s4083","sd7037","e387"]
CLc = 0.485
out = {}
for n in names:
    try:
        af = asb.Airfoil(n)
    except Exception as e:
        print(n, "load fail", e); continue
    t = af.max_thickness()
    a = np.linspace(-4, 18, 89)
    row = {}
    for Re in (150e3, 250e3):
        r = af.get_aero_from_neuralfoil(alpha=a, Re=Re, mach=0.05, model_size="xlarge")
        CL, CD, CM, conf = r["CL"], r["CD"], r["CM"], r["analysis_confidence"]
        i_max = int(np.argmax(CL))
        # interpolate at cruise CL on pre-stall branch
        pre = slice(0, i_max+1)
        a_c = np.interp(CLc, CL[pre], a[pre]); CD_c = np.interp(CLc, CL[pre], CD[pre]); CM_c = np.interp(CLc, CL[pre], CM[pre])
        # stall softness: CL drop 3 deg after peak
        j = min(i_max+12, len(a)-1); drop = CL[i_max]-CL[j]
        row[int(Re)] = dict(CLmax=float(CL[i_max]), a_stall=float(a[i_max]), CD_cruise=float(CD_c), LD_cruise=float(CLc/CD_c),
                            CM_cruise=float(CM_c), a_cruise=float(a_c), LDmax=float(np.max(CL/CD)), drop3=float(drop), conf=float(np.min(conf[pre])))
    out[n] = dict(t=float(t), **{str(k): v for k, v in row.items()})
    r2 = row[250000]; r1 = row[150000]
    print(f"{n:9s} t/c={t*100:4.1f}% | Re250k: CLmax {r2['CLmax']:.2f} @{r2['a_stall']:4.1f}°  L/D@CLc {r2['LD_cruise']:5.1f}  CD {r2['CD_cruise']*1e4:4.0f}cts  CM {r2['CM_cruise']:+.3f}  drop {r2['drop3']:.2f} conf {r2['conf']:.2f} | Re150k CLmax {r1['CLmax']:.2f} L/Dmax {r1['LDmax']:.0f}")
json.dump(out, open("airfoils.json","w"), indent=1)
