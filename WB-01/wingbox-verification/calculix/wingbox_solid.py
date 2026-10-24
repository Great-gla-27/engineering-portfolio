"""WB-01 solid model of the wing box in CalculiX: one layer of C3D20R bricks through the wall.

This is the closest independent match to the Fusion solid model (Fusion uses tetrahedra), and
it settles the corner question raised by the shell model: shells need a modelling choice at
the four box corners (rigid knots or averaged normals), solids do not.

Walls are offset t/2 either side of the 1.2 x 0.2 m midline (as in Fusion). Loads and support
are the same as wingbox_shell.py: root fixed, lift into the webs 5/6 front and 1/6 rear,
gravity on the material. Usage: python wingbox_solid.py <element size m> <t m> [static|buckle] [rib pitch m]
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hand_calc'))
import wingbox_hand as W
from wingbox_shell import BUCKLE_REF, read_frd, buckling_factors

X0, X1 = W.BOX_LE, W.BOX_LE + W.BOX_WIDTH
Y0, Y1 = -W.BOX_DEPTH / 2, W.BOX_DEPTH / 2


def ring(h, off):
    """closed loop at offset `off` outward from the midline, at half-element spacing."""
    nw = max(2, int(round(W.BOX_WIDTH / h))); nh = max(2, int(round(W.BOX_DEPTH / h)))
    a0, a1, b0, b1 = X0 - off, X1 + off, Y0 - off, Y1 + off
    pts, walls = [], []
    def leg(p, q, n, name):
        for i in range(2 * n):
            f = i / (2 * n); pts.append((p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)); walls.append(name)
    leg((a0, b1), (a1, b1), nw, 'upper'); leg((a1, b1), (a1, b0), nh, 'rear')
    leg((a1, b0), (a0, b0), nw, 'lower'); leg((a0, b0), (a0, b1), nh, 'front')
    return np.array(pts), walls, nw, nh


def build(h, t, mode='static', path='.', rib_pitch=None):
    rings = [ring(h, +t / 2), ring(h, 0.0), ring(h, -t / 2)]     # r = 0 outer, 1 mid, 2 inner
    m = len(rings[0][0]); walls = rings[0][1]; nw, nh = rings[0][2], rings[0][3]
    nz = int(round(W.SEMI_SPAN / h)); zs = np.linspace(0.0, W.SEMI_SPAN, 2 * nz + 1)
    ids, lines = {}, ['*HEADING', 'WB-01 wing box, C3D20R solid, h = %.4f, t = %.4f, %s' % (h, t, mode), '*NODE']
    def exists(i, r, k): return ((i % 2) + (r % 2) + (k % 2)) <= 1
    n = 0
    for k, z in enumerate(zs):
        for r in range(3):
            for i in range(m):
                if exists(i, r, k):
                    n += 1; ids[i, r, k] = n; x, y = rings[r][0][i]
                    lines.append('%d, %.7f, %.7f, %.7f' % (n, x, y, z))
    N = lambda i, r, k: ids[i % m, r, k]
    lines.append('*ELEMENT, TYPE=C3D20R, ELSET=EBOX'); e = 0
    for k in range(0, 2 * nz, 2):
        for i in range(0, m, 2):
            e += 1
            # face 1-2-3-4 at z_k ordered so its right-hand normal points to the z_k+2 face
            c = [N(i, 0, k), N(i, 2, k), N(i + 2, 2, k), N(i + 2, 0, k)]
            ct = [N(i, 0, k + 2), N(i, 2, k + 2), N(i + 2, 2, k + 2), N(i + 2, 0, k + 2)]
            mb = [N(i, 1, k), N(i + 1, 2, k), N(i + 2, 1, k), N(i + 1, 0, k)]
            mt = [N(i, 1, k + 2), N(i + 1, 2, k + 2), N(i + 2, 1, k + 2), N(i + 1, 0, k + 2)]
            mv = [N(i, 0, k + 1), N(i, 2, k + 1), N(i + 2, 2, k + 1), N(i + 2, 0, k + 1)]
            nodes = c + ct + mb + mt + mv
            lines.append('%d, %s,' % (e, ', '.join(str(x) for x in nodes[:15])))
            lines.append(', '.join(str(x) for x in nodes[15:]))
    root = [v for (i, r, k), v in ids.items() if k == 0]
    lines += ['*NSET, NSET=ROOT'] + [', '.join(str(x) for x in root[j:j + 16]) for j in range(0, len(root), 16)]
    lines += ['*MATERIAL, NAME=ENG3081', '*ELASTIC', '%.6e, %.4f' % (W.E_MOD, W.POISSON), '*DENSITY', '%.1f' % W.RHO,
              '*SOLID SECTION, ELSET=EBOX, MATERIAL=ENG3081', '*BOUNDARY', 'ROOT, 1, 3']
    # lift into the webs: same tributary integration as the shell model, spread over all web nodes
    def cum_lift(z):
        u = np.clip(z / W.SEMI_SPAN, 0.0, 1.0)
        return 0.5 * W.L0 * W.SEMI_SPAN * (u * np.sqrt(1.0 - u ** 2) + np.arcsin(u))
    edges = np.concatenate([[0.0], 0.5 * (zs[1:] + zs[:-1]), [W.SEMI_SPAN]])
    trib = np.diff(cum_lift(edges)); trib[1] += trib[0]; trib[0] = 0.0
    front = [i for i, w in enumerate(walls) if w == 'front'] + [0]
    rear = [i for i, w in enumerate(walls) if w == 'rear'] + [walls.index('lower')]
    scale = 1.0 if mode == 'static' else BUCKLE_REF
    loads = []
    for idx, share in ((front, 5.0 / 6.0), (rear, 1.0 / 6.0)):
        for k in range(1, len(zs)):
            use = [(i, r) for i in idx for r in range(3) if (i, r, k) in ids]
            for i, r in use:
                loads.append('%d, 2, %.6e' % (ids[i, r, k], scale * share * trib[k] / len(use)))
    step = ['*STEP', '*STATIC'] if mode == 'static' else ['*STEP', '*BUCKLE', '6']
    step += ['*CLOAD'] + loads + ['*DLOAD', 'EBOX, GRAV, %.6f, 0., -1., 0.' % (9.81 * scale), '*NODE FILE', 'U']
    if mode == 'static':
        step += ['*EL FILE', 'S', '*NODE PRINT, NSET=ROOT, TOTALS=ONLY', 'RF']
    step += ['*END STEP']
    name = 'wb01s_h%03d_t%03d_%s' % (round(h * 1000), round(t * 1e4), mode)
    with open(os.path.join(path, name + '.inp'), 'w') as fh:
        fh.write('\n'.join(lines + step) + '\n')
    return name, dict(nodes=n, elements=e)


if __name__ == '__main__':
    h, t = float(sys.argv[1]), float(sys.argv[2]); mode = sys.argv[3] if len(sys.argv) > 3 else 'static'
    name, info = build(h, t, mode)
    print(name, info['nodes'], 'nodes', info['elements'], 'elements')
