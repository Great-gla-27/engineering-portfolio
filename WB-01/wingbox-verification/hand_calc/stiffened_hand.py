"""WB-01 phase 5: stiffened redesign of the ENG3081 wing box, hand method and sizing.

The coursework design (3.8 mm unstiffened skin) meets its stress allowables but buckles at
about 4 % of the design load. This file sizes a box that meets the same stress allowables
and also does not buckle, then compares its mass with the coursework design.

Load levels and criteria (decision log):
  limit load    = the coursework load (elliptical lift, self weight)
  ultimate load = 1.5 x limit
  at limit:     direct stress <= 100 MPa, shear <= 50 MPa (the coursework criteria)
  at ultimate:  no buckling of any kind, and no column failure; the material allowable
                (100 MPa) is treated as the yield stress in the Johnson column curve
The section is constant along the span, so the root bay governs every check.

Layout, both covers identical (keeps the neutral axis at mid-depth, and covers a reversed
load as well):
  skin t_s on both covers, webs t_w, n_s blade stringers per cover at even pitch
  b = BOX_WIDTH / (n_s + 1), blade height h_b and thickness t_b, standing inward from the
  inner face of the skin; ribs every L, flat plates of thickness t_r (no lightening holes,
  so rib mass is an upper bound).

Methods (all linear elastic plate theory, no imperfections, no post-buckling credit):
  skin between stringers      k = 4.0 compression, k_s = 5.35 + 4 (b/L)^2 shear, interaction
                              R_c + R_s^2 = 1
  blade local buckling        one free edge, k = 0.43
  stringer column             blade plus a skin width b, pinned at the ribs (length L),
                              Euler, with the Johnson parabola above half yield
  web panel between ribs      shear k_s = 5.35 + 4 (h/L)^2, bending k = 23.9,
                              interaction R_b^2 + R_s^2 = 1
Shear in each wall is the coursework split: V / (2 h) in each web plus the Bredt-Batho
flow T / (2 A) round the box.
SI units throughout.
"""
import numpy as np
import wingbox_hand as W

ULT = 1.5
SIGMA_Y = W.SIGMA_ALLOW
D_FAC = np.pi ** 2 * W.E_MOD / (12.0 * (1.0 - W.POISSON ** 2))   # sigma_cr = k D_FAC (t/b)^2
H = W.BOX_DEPTH
A_ENC = W.enclosed_area()


def section(t_s, t_w, n_s, h_b, t_b):
    """second moment of area (thin-wall skin and webs, exact blade position), m^4."""
    y_b = H / 2 - t_s / 2 - h_b / 2                    # blade centroid from the box mid-plane
    i_skin = 2 * W.BOX_WIDTH * t_s * (H / 2) ** 2
    i_web = 2 * t_w * H ** 3 / 12
    i_blade = 2 * n_s * (h_b * t_b * y_b ** 2 + t_b * h_b ** 3 / 12)
    return i_skin + i_web + i_blade


def weight_per_m(t_s, t_w, n_s, h_b, t_b, L, t_r):
    """structural weight per metre of span including ribs, N/m."""
    area = 2 * W.BOX_WIDTH * t_s + 2 * H * t_w + 2 * n_s * h_b * t_b
    rib = W.BOX_WIDTH * H * t_r / L
    return W.RHO * W.G_ACC * (area + rib)


def root_loads(w):
    """root shear, moment and torque at limit load for a uniform structural weight w (N/m)."""
    V = W.total_lift() - w * W.SEMI_SPAN
    M = W.root_moment_lift() - w * W.SEMI_SPAN ** 2 / 2
    return V, M, W.root_torque()


def column_stress(sigma_e):
    """Euler stress capped by the Johnson parabola above half yield."""
    return np.where(sigma_e > SIGMA_Y / 2, SIGMA_Y - SIGMA_Y ** 2 / (4 * sigma_e), sigma_e)


def interaction_factor(r1, r2):
    """load factor lam solving lam r1 + (lam r2)^2 = 1."""
    r2s = r2 ** 2
    return np.where(r2s > 1e-30, (-r1 + np.sqrt(r1 ** 2 + 4 * r2s)) / (2 * np.maximum(r2s, 1e-30)), 1 / np.maximum(r1, 1e-30))


def evaluate(t_s, t_w, n_s, h_b, t_b, L, t_r=0.002):
    """every check for one design. Factors are applied-load multipliers at which each
    mode occurs; they must reach ULT (buckling) or 1 (stress at limit). Works on arrays."""
    w = weight_per_m(t_s, t_w, n_s, h_b, t_b, L, t_r)
    V, M, T = root_loads(w)
    I = section(t_s, t_w, n_s, h_b, t_b)
    sig = M * (H / 2) / I                               # cover stress, limit load
    q_t = T / (2 * A_ENC)
    tau_web = (V / (2 * H) + q_t) / t_w                 # front web, the worse one
    tau_skin = q_t / t_s
    b = W.BOX_WIDTH / (n_s + 1)
    # skin panel between stringers and ribs
    sig_cr = 4.0 * D_FAC * (t_s / b) ** 2
    a_s, b_s = np.maximum(b, L), np.minimum(b, L)
    tau_cr = (5.35 + 4 * (b_s / a_s) ** 2) * D_FAC * (t_s / b_s) ** 2
    f_skin = interaction_factor(sig / sig_cr, tau_skin / tau_cr)
    # blade local buckling; the blade root sees about the cover stress
    f_blade = 0.43 * D_FAC * (t_b / h_b) ** 2 / sig
    # stringer column: blade plus a skin width b, pinned at the ribs
    a_sk, a_bl = b * t_s, h_b * t_b
    y_sk, y_bl = 0.0, -(t_s / 2 + h_b / 2)              # from the skin midline, inward negative
    a_col = a_sk + a_bl
    y_c = (a_sk * y_sk + a_bl * y_bl) / a_col
    i_col = a_sk * (y_sk - y_c) ** 2 + b * t_s ** 3 / 12 + a_bl * (y_bl - y_c) ** 2 + t_b * h_b ** 3 / 12
    sig_e = np.pi ** 2 * W.E_MOD * i_col / (a_col * L ** 2)
    f_col = column_stress(sig_e) / sig
    # web panel between ribs
    a_w, b_w = np.maximum(H, L), np.minimum(H, L)
    tau_cr_w = (5.35 + 4 * (b_w / a_w) ** 2) * D_FAC * (t_w / b_w) ** 2
    sig_cr_wb = 23.9 * D_FAC * (t_w / H) ** 2
    # lam^2 (Rb^2 + Rs^2) = 1
    f_web = 1.0 / np.sqrt((sig / sig_cr_wb) ** 2 + (tau_web / tau_cr_w) ** 2)
    return dict(weight=w, V=V, M=M, I=I, sigma=sig, tau_web=tau_web, tau_skin=tau_skin, b=b,
                f_stress=SIGMA_Y / sig, f_shear=W.TAU_ALLOW / tau_web,
                f_skin=f_skin, f_blade=f_blade, f_col=f_col, f_web=f_web, sig_e=sig_e)


def feasible(r):
    return ((r['f_stress'] >= 1) & (r['f_shear'] >= 1) & (r['f_skin'] >= ULT)
            & (r['f_blade'] >= ULT) & (r['f_col'] >= ULT) & (r['f_web'] >= ULT))


# design space: practical gauges, 0.1 mm skin and web steps, 0.25 mm blade steps
T_S = np.arange(1.0, 8.01, 0.1) / 1e3
T_W = np.arange(1.0, 8.01, 0.1) / 1e3
N_S = np.arange(2, 25)
H_B = np.arange(20, 71, 5) / 1e3          # inward depth; two facing blades must clear each other
T_B = np.arange(1.0, 8.01, 0.25) / 1e3
L_R = np.array([0.25, 0.4, 0.5, 0.625, 1.0, 1.25, 2.0, 2.5])     # rib pitches dividing the span
T_RIB = 0.002


def optimise():
    """exhaustive search of the grid above for the lightest design that passes every check.
    The web is part of the search: a thin web only survives bending buckling under a lightly
    stressed cover, so the web and cover sizes cannot be chosen separately."""
    best = None
    S, NS, HB, TB = np.meshgrid(T_S, N_S, H_B, T_B, indexing='ij')
    for L in L_R:
        for tw in T_W:
            r = evaluate(S, tw, NS, HB, TB, L, T_RIB)
            ok = feasible(r)
            if not ok.any(): continue
            w = np.where(ok, r['weight'], np.inf)
            j = np.unravel_index(np.argmin(w), w.shape)
            cand = dict(t_s=S[j], t_w=tw, n_s=int(NS[j]), h_b=HB[j], t_b=TB[j], L=L, t_r=T_RIB, weight=w[j])
            if best is None or cand['weight'] < best['weight']: best = cand
    return best


def unstiffened_viable():
    """thinnest constant skin and web that meets the same criteria with no stringers or ribs."""
    for t in np.arange(3.8, 30.0, 0.1) / 1e3:
        r = evaluate(t, t, 0, 0.02, 1e-6, W.SEMI_SPAN, 0.0)
        r['f_blade'] = r['f_col'] = np.inf
        if feasible(r): return t, r
    return None


def report(d):
    r = evaluate(d['t_s'], d['t_w'], d['n_s'], d['h_b'], d['t_b'], d['L'], d['t_r'])
    print('skin %.1f mm, web %.1f mm, %d blades per cover %.0f x %.2f mm at %.0f mm pitch, ribs %.3f m x %.1f mm'
          % (d['t_s'] * 1e3, d['t_w'] * 1e3, d['n_s'], d['h_b'] * 1e3, d['t_b'] * 1e3, r['b'] * 1e3, d['L'], d['t_r'] * 1e3))
    print('weight %.1f N/m; root sigma %.1f MPa, web tau %.1f MPa' % (r['weight'], r['sigma'] / 1e6, r['tau_web'] / 1e6))
    print('factors: stress %.2f, shear %.2f, skin %.2f, blade %.2f, column %.2f, web %.2f'
          % tuple(float(r[k]) for k in ('f_stress', 'f_shear', 'f_skin', 'f_blade', 'f_col', 'f_web')))
    return r


if __name__ == '__main__':
    d = optimise(); print('Lightest stiffened design'); report(d)
    t, r = unstiffened_viable()
    print('\nUnstiffened box meeting the same criteria: t = %.1f mm, %.1f N/m' % (t * 1e3, r['weight']))
    print('Coursework design: 3.8 mm, %.1f N/m (cover buckling factor %.3f)'
          % (W.weight_per_span(0.0038), W.buckling_summary(0.0038)['cover_factor']))
