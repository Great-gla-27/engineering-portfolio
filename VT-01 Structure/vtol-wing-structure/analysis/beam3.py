import numpy as np
from beam import static, Im, Ir, Dm, Dr, E, le
loads = [(0.200, 42.5), (0.500, 36.75), (0.800, 25.41)]
w, M = static(loads)
share = Im/(Im+Ir)
s = lambda Mx: Mx*share*(Dm/2)/Im/1e6
print("PREDICTION for the 3-load FEA case (written before the solve):")
print(f"  root moment {M[0]:.2f} N.m, total force {sum(f for _,f in loads):.2f} N")
for y in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3):
    print(f"  main spar bending stress at y={y*1000:.0f} mm: {s(M[int(round(y/le))]):.0f} MPa")
print(f"  tip deflection (y=1000): {w[-1]*1000:.1f} mm ; at y=800: {w[int(0.8/le)]*1000:.1f} mm")
print(f"  rear spar stress at root (same curvature, smaller radius): {M[0]*(Ir/(Im+Ir))*(Dr/2)/Ir/1e6:.0f} MPa")
