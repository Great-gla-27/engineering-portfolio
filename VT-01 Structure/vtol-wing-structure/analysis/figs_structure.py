import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
B = json.load(open("beam.json")); x = np.array(B["x"])*1000
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from beam import static
w3, M3 = static([(0.200, 42.5), (0.500, 36.75), (0.800, 25.41)])
fig, ax = plt.subplots(1,2, figsize=(8,3.2))
ax[0].plot(x, np.array(B["M"]), color="#1f6feb", label="11 rib loads (VLM)"); ax[0].plot(x, M3, color="#888", ls="--", label="3-load FEA equivalent"); ax[0].legend(frameon=False, fontsize=8.5); ax[0].set_xlabel("spanwise y (mm)"); ax[0].set_ylabel("bending moment (N·m), ultimate n = 5.7"); ax[0].set_title("Root moment 46.9 N·m", fontsize=10, loc="left")
ax[1].plot(x, w3*1000, color="#1f6feb", label="beam theory (FEA load set)"); ax[1].scatter([1000],[76.3], color="#c33", zorder=3, label="Fusion FEA tip 76.3 mm")
ax[1].set_xlabel("spanwise y (mm)"); ax[1].set_ylabel("deflection (mm), ultimate"); ax[1].legend(frameon=False, fontsize=8.5); ax[1].set_title("Tip 76.6 mm (beam) vs 76.3 mm (FEA)", fontsize=10, loc="left")
plt.tight_layout(); plt.savefig("../figures/beam.png", dpi=150)
print("ok")
