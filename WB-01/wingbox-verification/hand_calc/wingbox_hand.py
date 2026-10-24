"""WB-01 hand calculation for the ENG3081 wing box.

Reproduces the coursework spreadsheet (ASM3_WingBox_Optimisation_2740042.xlsx) and adds
the checks needed for comparison with FEA: shear flow round the section, spanwise
stress, tip deflection and tip twist.

Coordinate system and conventions (used in every WB-01 file):
  z  spanwise from the root (0) to the tip (SEMI_SPAN), m
  x  chordwise from the leading edge, m
  y  vertical, positive up, measured from the box mid-plane, m
  Lift acts upward (+y) at the centre of pressure, x = X_CP.
  Positive bending moment puts the upper cover in compression.
SI units throughout (N, m, Pa). Stresses are reported in MPa.

Thin-wall idealisation, as in the coursework: BOX_WIDTH and BOX_DEPTH are midline
dimensions and every wall has the same thickness t.
"""
import numpy as np

# ---------------------------------------------------------------- coursework data
SEMI_SPAN = 10.0          # m
CHORD = 2.0               # m
BOX_WIDTH = 1.2           # m, midline, front web to rear web
BOX_DEPTH = 0.2           # m, midline, lower to upper cover
BOX_LE = 0.2              # m, front web position from the leading edge
X_CP = 0.4                # m, centre of pressure (20 % chord)
L0 = 3500.0               # N/m, root value of the elliptical lift distribution
RHO = 4000.0              # kg/m^3
G_ACC = 9.81              # m/s^2
SIGMA_ALLOW = 100e6       # Pa, direct (tension or compression) yield
E_MOD = 110e9             # Pa, chosen (titanium-like, matches the 4000 kg/m^3 density); not in the brief
POISSON = 0.33            # chosen with E_MOD
G_MOD = E_MOD / (2.0 * (1.0 + POISSON))
TAU_ALLOW = 50e6          # Pa, shear yield

X_CENTROID = BOX_LE + BOX_WIDTH / 2      # 0.8 m; also the shear centre (doubly symmetric box)
TORQUE_ARM = X_CENTROID - X_CP           # 0.4 m


# ---------------------------------------------------------------- loads
def lift_per_span(z):
    """elliptical lift distribution l(z), N/m."""
    z = np.asarray(z, dtype=float)
    return L0 * np.sqrt(np.clip(1.0 - (z / SEMI_SPAN) ** 2, 0.0, None))


def total_lift():
    return np.pi * L0 * SEMI_SPAN / 4.0                     # 27,489 N


def root_moment_lift():
    return L0 * SEMI_SPAN ** 2 / 3.0                        # 116,667 N.m


def root_torque():
    return total_lift() * TORQUE_ARM                        # 10,996 N.m


def weight_per_span(t):
    """self-weight of the box, N/m (uniform along the span)."""
    return 2.0 * (BOX_WIDTH + BOX_DEPTH) * t * RHO * G_ACC  # 109,872 t


# ---------------------------------------------------------------- section properties
def ixx(t):
    """second moment of area about the horizontal centroidal axis, thin wall, m^4."""
    return t * BOX_DEPTH ** 2 * (3.0 * BOX_WIDTH + BOX_DEPTH) / 6.0   # 0.02533 t


def enclosed_area():
    return BOX_WIDTH * BOX_DEPTH                            # 0.24 m^2


def torsion_constant(t):
    """Bredt-Batho J = 4 A^2 / (closed integral of ds/t), m^4."""
    return 4.0 * enclosed_area() ** 2 * t / (2.0 * (BOX_WIDTH + BOX_DEPTH))


# ---------------------------------------------------------------- spanwise resultants
def _grid(n=2001):
    return np.linspace(0.0, SEMI_SPAN, n)


def _tail_integral(z, f):
    """F(z) = integral from z to SEMI_SPAN of f, by the trapezium rule on the grid z."""
    seg = 0.5 * (f[1:] + f[:-1]) * np.diff(z)
    return np.concatenate([np.cumsum(seg[::-1])[::-1], [0.0]])


def resultants(t, n=2001, extra_weight=0.0):
    """shear force, bending moment and torque along the span, for lift plus self-weight.

    Returns z, S(z) [N, positive up], M(z) [N.m, positive with upper cover in compression],
    T(z) [N.m, about the shear centre, positive nose up].
    """
    z = _grid(n)
    q = lift_per_span(z) - weight_per_span(t) - extra_weight  # net upward load per span (extra_weight, N/m: ribs etc.)
    shear = _tail_integral(z, q)
    moment = _tail_integral(z, shear)                       # dM/dz = -S, M(tip) = 0
    torque = _tail_integral(z, lift_per_span(z) * TORQUE_ARM)
    return z, shear, moment, torque


# ---------------------------------------------------------------- coursework root stresses
def root_stresses(t):
    """the coursework method, at the root section. Returns a dict in SI units."""
    w = weight_per_span(t)
    m_weight = -0.5 * w * SEMI_SPAN ** 2
    m_net = root_moment_lift() + m_weight
    sigma = m_net * (BOX_DEPTH / 2.0) / ixx(t)
    v_net = total_lift() - w * SEMI_SPAN
    tau_direct = v_net / (2.0 * BOX_DEPTH * t)              # average web shear, as in the report
    tau_torsion = root_torque() / (2.0 * enclosed_area() * t)
    return dict(t=t, weight_per_m=w, weight_total=w * SEMI_SPAN, m_weight=m_weight, m_net=m_net,
                ixx=ixx(t), sigma=sigma, v_net=v_net, tau_direct=tau_direct,
                tau_torsion=tau_torsion, tau_total=tau_direct + tau_torsion)


def sweep(t_values):
    return [root_stresses(t) for t in t_values]


# ---------------------------------------------------------------- shear flow round the section
def shear_flow_section(t, shear_force, torque, n=400):
    """shear flow q(s) round the closed box, N/m.

    Vertical shear is taken through the shear centre (the box centroid). By symmetry the
    open-section shear flow is zero at the middle of each cover, so the cut is made at the
    middle of the upper cover and no redundant shear flow is needed. The torque adds the
    uniform Bredt-Batho flow T / (2A).

    s runs from the middle of the upper cover towards the rear web, round the box and back.
    Returns s (m), q (N/m) and the (x, y) position of each point.
    """
    w, h, I = BOX_WIDTH, BOX_DEPTH, ixx(t)
    k = -shear_force / I
    legs = [((0.0, h / 2), (w / 2, h / 2)), ((w / 2, h / 2), (w / 2, -h / 2)),
            ((w / 2, -h / 2), (-w / 2, -h / 2)), ((-w / 2, -h / 2), (-w / 2, h / 2)),
            ((-w / 2, h / 2), (0.0, h / 2))]
    s_all, q_all, xy_all, q0, s0 = [], [], [], 0.0, 0.0
    for (x1, y1), (x2, y2) in legs:
        length = np.hypot(x2 - x1, y2 - y1)
        u = np.linspace(0.0, length, n)
        y = y1 + (y2 - y1) * u / length
        # integral of t*y ds along the leg, analytically for a straight leg
        ty = t * (y1 * u + 0.5 * (y2 - y1) / length * u ** 2)
        q = q0 + k * ty
        s_all.append(s0 + u); q_all.append(q)
        xy_all.append(np.column_stack([x1 + (x2 - x1) * u / length, y]))
        q0, s0 = q[-1], s0 + length
    q_open = np.concatenate(q_all)
    q_torque = torque / (2.0 * enclosed_area())
    return np.concatenate(s_all), q_open + q_torque, np.vstack(xy_all)


def peak_web_shear(t, shear_force, torque):
    """maximum shear stress in the webs from the shear flow distribution, Pa."""
    s, q, xy = shear_flow_section(t, shear_force, torque)
    web = np.isclose(np.abs(xy[:, 0]), BOX_WIDTH / 2)
    return np.max(np.abs(q[web])) / t


# ---------------------------------------------------------------- deflection and twist
def tip_deflection(t, youngs_modulus, n=2001, extra_weight=0.0):
    """vertical tip deflection from double integration of M / EI, m (positive up)."""
    z, _, moment, _ = resultants(t, n, extra_weight)
    curvature = moment / (youngs_modulus * ixx(t))
    slope = np.concatenate([[0.0], np.cumsum(0.5 * (curvature[1:] + curvature[:-1]) * np.diff(z))])
    defl = np.concatenate([[0.0], np.cumsum(0.5 * (slope[1:] + slope[:-1]) * np.diff(z))])
    return z, defl


def tip_twist(t, shear_modulus, n=2001):
    """twist about the shear centre, rad, positive nose up."""
    z, _, _, torque = resultants(t, n)
    rate = torque / (shear_modulus * torsion_constant(t))
    return z, np.concatenate([[0.0], np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(z))])


def spanwise_bending_stress(t, n=2001):
    """cover stress from M(z) y / Ixx along the span, Pa (compression in the upper cover)."""
    z, _, moment, _ = resultants(t, n)
    return z, moment * (BOX_DEPTH / 2.0) / ixx(t)


# ---------------------------------------------------------------- buckling
def plate_buckling_coefficient(t, youngs_modulus, poisson, b):
    """D-free plate buckling stress per unit k: pi^2 E / (12 (1 - nu^2)) (t / b)^2, Pa."""
    return np.pi ** 2 * youngs_modulus / (12.0 * (1.0 - poisson ** 2)) * (t / b) ** 2


def cover_buckling_stress(t, youngs_modulus, poisson, k=4.0):
    """critical compressive stress of the unstiffened upper cover, Pa.

    The cover is a long flat plate between the two webs, loaded in uniform compression
    along the span. With no ribs, the panel length (10 m) is far greater than its width
    (b = BOX_WIDTH), so the buckle half-wavelength settles at about b and the coefficient
    tends to its long-plate minimum. Unloaded edges simply supported by the webs gives
    k = 4.0; fully clamped edges would give 6.97. The webs are as thin as the cover and
    will rotate with it, so simple support is the realistic and conservative choice.
    Linear elastic, no imperfections; real panels buckle below this.
    """
    return k * plate_buckling_coefficient(t, youngs_modulus, poisson, BOX_WIDTH)


def web_shear_buckling_stress(t, youngs_modulus, poisson, rib_pitch=SEMI_SPAN):
    """critical shear stress of a web panel between ribs, Pa.

    Simply supported rectangular panel, short side b = BOX_DEPTH, long side a = rib pitch.
    k_s = 5.35 + 4 (b / a)^2 for a >= b (Timoshenko and Gere); with no ribs a is the
    semi-span and k_s is effectively 5.35.
    """
    a = max(rib_pitch, BOX_DEPTH); b = min(rib_pitch, BOX_DEPTH)
    ks = 5.35 + 4.0 * (b / a) ** 2
    return ks * plate_buckling_coefficient(t, youngs_modulus, poisson, b)


def web_bending_buckling_stress(t, youngs_modulus, poisson):
    """critical edge stress of a web panel in in-plane bending, Pa (k = 23.9, simply supported)."""
    return 23.9 * plate_buckling_coefficient(t, youngs_modulus, poisson, BOX_DEPTH)


def buckling_summary(t, youngs_modulus=None, poisson=None):
    E = E_MOD if youngs_modulus is None else youngs_modulus
    nu = POISSON if poisson is None else poisson
    r = root_stresses(t)
    tau_peak = peak_web_shear(t, r['v_net'], root_torque())
    cover = cover_buckling_stress(t, E, nu)
    web_s = web_shear_buckling_stress(t, E, nu)
    web_b = web_bending_buckling_stress(t, E, nu)
    return dict(cover_crit=cover, cover_applied=r['sigma'], cover_factor=cover / r['sigma'],
                web_shear_crit=web_s, web_shear_applied=tau_peak, web_shear_factor=web_s / tau_peak,
                web_bending_crit=web_b, web_bending_factor=web_b / r['sigma'])


# ---------------------------------------------------------------- report
if __name__ == '__main__':
    print('Loads: L = %.1f N, M_lift = %.1f N.m, T = %.1f N.m'
          % (total_lift(), root_moment_lift(), root_torque()))
    print('\n%-6s %-10s %-11s %-11s %-11s' % ('t mm', 'w N/m', 'sigma MPa', 'tau MPa', 'Ixx m^4'))
    for r in sweep([0.0050, 0.0030, 0.0038]):
        print('%-6.1f %-10.2f %-11.2f %-11.2f %-11.4e'
              % (r['t'] * 1e3, r['weight_per_m'], r['sigma'] / 1e6, r['tau_total'] / 1e6, r['ixx']))
    t = 0.0038
    r = root_stresses(t)
    print('\nAt t = 3.8 mm: average web shear %.2f MPa, peak from shear flow %.2f MPa (with torsion)'
          % (r['tau_direct'] / 1e6, peak_web_shear(t, r['v_net'], root_torque()) / 1e6))
    z, s_span, m_span, _ = resultants(t)
    print('Numerical root moment %.0f N.m against closed form %.0f N.m' % (m_span[0], r['m_net']))
    _, v = tip_deflection(t, E_MOD); _, th = tip_twist(t, G_MOD)
    print('Tip deflection %.1f mm, tip twist %.3f deg (E = %.0f GPa, G = %.1f GPa)'
          % (v[-1] * 1e3, np.degrees(th[-1]), E_MOD / 1e9, G_MOD / 1e9))
    b = buckling_summary(t)
    print('Cover buckling %.2f MPa against %.1f MPa applied, load factor %.3f'
          % (b['cover_crit'] / 1e6, b['cover_applied'] / 1e6, b['cover_factor']))
    print('Web shear buckling %.2f MPa against %.2f MPa, factor %.3f; web bending buckling %.1f MPa, factor %.3f'
          % (b['web_shear_crit'] / 1e6, b['web_shear_applied'] / 1e6, b['web_shear_factor'],
             b['web_bending_crit'] / 1e6, b['web_bending_factor']))
