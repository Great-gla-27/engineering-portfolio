"""Phase 1: wing sizing for a ~4 kg twin-boom VTOL (Roc Wing class)."""
import numpy as np
g, rho, mu = 9.81, 1.225, 1.81e-5          # ISA sea level
m, b = 4.0, 2.0                              # kg, m
V_c, V_s = 18.0, 11.0                        # m/s
CLmax_wing = 1.30                            # clean 3D wing CLmax (aerofoil ~1.45, x0.9)
n_lim, SF = 3.8, 1.5
W = m*g
S = 2*W/(rho*V_s**2*CLmax_wing)
AR = b**2/S; c = S/b
CL_c = 2*W/(rho*V_c**2*S)
Re = rho*V_c*c/mu
q = 0.5*rho*V_c**2
n_ult = n_lim*SF
L_half = n_ult*W/2
y_bar = 4*(b/2)/(3*np.pi)
M_root = L_half*y_bar
print(f"W = {W:.2f} N | S = {S:.3f} m^2 | AR = {AR:.2f} | mean chord = {c*1000:.0f} mm")
print(f"wing loading = {W/S:.1f} N/m^2 ({m/S:.2f} kg/m^2) | q_cruise = {q:.1f} Pa")
print(f"cruise CL = {CL_c:.3f} | Re_cruise = {Re:,.0f} | Re_stall = {rho*V_s*c/mu:,.0f}")
print(f"n_ult = {n_ult:.1f} | half-wing ultimate lift = {L_half:.1f} N | elliptic centroid y = {y_bar:.3f} m | root BM = {M_root:.1f} N.m")
for D,d in ((12,10),(14,12),(16,14),(20,18)):
    I = np.pi*(D**4-d**4)/64; sig = M_root*1e3*(D/2)/I
    print(f"  carbon tube {D}/{d} mm: I = {I:.0f} mm^4, sigma_ult = {sig:.0f} MPa, mass/m = {1550e-9*np.pi*(D**2-d**2)/4*1e3*1e3:.1f} g/m")
