import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
A = json.load(open("airfoils.json"))
names = {"sd7062":"SD7062","clarky":"Clark Y","naca4412":"NACA 4412","e205":"E205","sd7037":"SD7037","s4083":"S4083","e387":"E387"}
OFF={"clarky":(-48,-12),"naca4412":(6,4)}
fig, ax = plt.subplots(figsize=(7,3.6))
for k, v in A.items():
    r = v["250000"]; ok = r["conf"] > 0.5
    ax.scatter(r["LD_cruise"], r["CLmax"], s=60, color="#1f6feb" if k=="sd7062" else ("#888" if ok else "#ddd"), edgecolor="k" if ok else "#bbb", zorder=3)
    ax.annotate(f'{names[k]} ({v["t"]*100:.0f}%)' + ("" if ok else " *low confidence"), (r["LD_cruise"], r["CLmax"]), xytext=OFF.get(k,(5,4)), textcoords="offset points", fontsize=8.5, color="k" if ok else "#999")
ax.axhline(1.30/0.9, ls="--", color="#c33", lw=1); ax.text(49.5, 1.452, "section CLmax needed for 11 m/s stall (wing 1.30 / 0.9)", fontsize=8, color="#c33")
ax.set_xlabel("section L/D at cruise CL 0.49, Re 250k"); ax.set_ylabel("section CLmax, Re 250k"); ax.set_title("Aerofoil trade (NeuralFoil); label = thickness", fontsize=10, loc="left")
plt.tight_layout(); plt.savefig("../figures/airfoil_trade.png", dpi=150)
R = json.load(open("cfd_ref.json")); R = np.array(R)
fig, ax = plt.subplots(1,2, figsize=(8,3.2))
ax[0].plot(R[:,0], R[:,1], "o-", color="#1f6feb"); ax[0].set_xlabel("alpha (deg)"); ax[0].set_ylabel("wing CL"); ax[0].axhline(0.485, ls=":", color="#888"); ax[0].text(-2, 0.51, "cruise CL 0.485", fontsize=8, color="#666")
ax[1].plot(R[:,4], R[:,1], "o-", color="#1f6feb"); ax[1].set_xlabel("wing CD (induced + profile)"); ax[1].set_ylabel("wing CL"); ax[1].set_title("Prediction to check in STAR-CCM+", fontsize=10, loc="left")
plt.tight_layout(); plt.savefig("../figures/polar.png", dpi=150)
import shutil; shutil.copy("spanload.png", "../figures/spanload.png")
print("ok")

