"""Euler-Bernoulli beam FE of the half-wing spar system: static (flight, hover) + modal."""
import numpy as np, json
G = json.load(open("geom.json")); R = json.load(open("ribdata.json"))
E = 100e9                                    # CFRP (same isotropic approx as Fusion material)
Dm, dm, Dr, dr = 16e-3, 14e-3, 6e-3, 4e-3
Im = np.pi*(Dm**4-dm**4)/64; Ir = np.pi*(Dr**4-dr**4)/64
EI = E*(Im+Ir)                               # ribs tie the spars; bending about own axes (conservative: ignores couple)
L = 1.0; n = 200; le = L/n; xs = np.linspace(0, L, n+1)
def assemble(m_lin, point_masses):
    K = np.zeros((2*n+2,)*2); M = np.zeros_like(K)
    k = EI/le**3*np.array([[12,6*le,-12,6*le],[6*le,4*le**2,-6*le,2*le**2],[-12,-6*le,12,-6*le],[6*le,2*le**2,-6*le,4*le**2]])
    for e in range(n):
        idx = slice(2*e, 2*e+4); xm = (e+0.5)*le
        mm = m_lin(xm)*le/420*np.array([[156,22*le,54,-13*le],[22*le,4*le**2,13*le,-3*le**2],[54,13*le,156,-22*le],[-13*le,-3*le**2,-22*le,156]])
        K[idx, idx] += k; M[idx, idx] += mm
    for y, m in point_masses:
        i = int(round(y/le)); M[2*i, 2*i] += m
    return K, M
def static(forces):
    K, _ = assemble(lambda x: 0, [])
    F = np.zeros(2*n+2)
    for y, f in forces: F[2*int(round(min(y, L)/le))] += f
    free = np.arange(2, 2*n+2); u = np.zeros_like(F)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    w = u[0::2]
    M = np.array([sum(f*(y-x) for y, f in forces if y > x) for x in xs])   # statics for moment
    return w, M
ribs = np.array(G["ribs"])/1000; Fr = np.array(R["F"])
# ---- Case 1: flight ultimate (n = 5.7) rib loads from VLM
w1, M1 = static(list(zip(ribs, Fr)))
sig = lambda M, D, I: M*(D/2)/I
share = Im/(Im+Ir)                           # moment shared by stiffness
print(f"CASE 1 flight ultimate: total half-wing lift {Fr.sum():.1f} N, root BM {M1[0]:.1f} N.m")
for y in (0.0, 0.05, 0.10, 0.20, 0.40, 0.70):
    i = int(round(y/le)); print(f"   y={y*1000:4.0f} mm: M = {M1[i]:5.1f} N.m, main spar sigma = {sig(M1[i]*share, Dm, Im)/1e6:5.0f} MPa")
print(f"   tip deflection = {w1[-1]*1000:.1f} mm ({w1[-1]/L*100:.1f}% of semispan)")
# limit load (n=3.8) deflection
print(f"   at LIMIT load (n=3.8): tip deflection {w1[-1]*1000/1.5:.1f} mm, root stress {sig(M1[0]*share, Dm, Im)/1e6/1.5:.0f} MPa")
# ---- Case 2: hover, full thrust, ultimate: boom carries 2 motors at y=0.40
T_motor = 2*4*9.81/4                          # T/W = 2 per motor
F_boom = 2*T_motor*1.5
w2, M2 = static([(0.40, F_boom)])
print(f"CASE 2 hover ultimate: boom force {F_boom:.1f} N up at y=400 mm, root BM {M2[0]:.1f} N.m, sigma {sig(M2[0]*share, Dm, Im)/1e6:.0f} MPa, tip defl {w2[-1]*1000:.1f} mm")
# torsion from front/rear motor imbalance (one at full, one at idle), boom arms +-0.30 m
Tq = T_motor*1.5*0.30; J = 2*Im
print(f"   worst torsion (one motor full, other idle): {Tq:.1f} N.m -> shear {Tq*(Dm/2)/J/1e6:.0f} MPa (isotropic G); real CFRP G is lower, so twist is underestimated")
# ---- Modal: structure mass + covering + servo, boom+motors point mass
m_struct = 0.1727                              # kg, from Fusion (half wing)
m_cover = 0.040; m_servo = 0.020               # film covering + aileron servo/linkage (estimate)
m_lin = lambda x: (m_struct+m_cover)/L
pm = [(0.40, 0.26), (0.70, m_servo)]           # boom + 2 motors/props/ESCs ~260 g (estimate)
K, M = assemble(m_lin, pm)
free = np.arange(2, 2*n+2)
from scipy.linalg import eigh
ev, vec = eigh(K[np.ix_(free, free)], M[np.ix_(free, free)])
f = np.sqrt(ev[:3])/(2*np.pi)
print(f"MODAL (cantilever at root): f1 = {f[0]:.1f} Hz, f2 = {f[1]:.1f} Hz, f3 = {f[2]:.1f} Hz")
rpm = 4500; print(f"   hover prop at ~{rpm} rpm: 1P = {rpm/60:.0f} Hz, 2P (2-blade pass) = {2*rpm/60:.0f} Hz")
json.dump(dict(tip_defl_ult_mm=w1[-1]*1000, root_sig_ult=sig(M1[0]*share, Dm, Im)/1e6, sig_100=sig(M1[int(0.1/le)]*share, Dm, Im)/1e6,
               M=M1.tolist(), w=w1.tolist(), x=xs.tolist(), f=f.tolist(), hover_BM=M2[0], hover_tip=w2[-1]*1000), open("beam.json","w"))
