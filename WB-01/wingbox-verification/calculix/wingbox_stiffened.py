"""WB-01 phase 5: CalculiX check of the stiffened wing box.

The cross-section (covers, webs, blade stringers) is meshed as 8-node quads, one element
through every wall, and extruded along the span into C3D20R bricks. A solid model avoids
the rigid knots CalculiX inserts where shells meet at an angle (box corners and blade
roots), which were shown in phase 3 to upset *BUCKLE.

Ribs are modelled as diaphragms that are rigid in their own plane and free out of plane:
at each rib station every section node follows a planar rigid motion (u, v, rotation)
of a reference node, by *EQUATION. That is the rib assumed by the hand method; it holds
the section shape and gives the skin, blades and webs simply supported edges at the ribs.
Rib weight is applied at the reference node.

Loads as in the other models: root fixed, lift into the webs (5/6 front, 1/6 rear), gravity.
Usage: python wingbox_stiffened.py [static|buckle]
"""
import sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hand_calc')); sys.path.insert(0, HERE)
import wingbox_hand as W
from wingbox_shell import BUCKLE_REF

X0, X1 = W.BOX_LE, W.BOX_LE + W.BOX_WIDTH
Y0, Y1 = -W.BOX_DEPTH / 2, W.BOX_DEPTH / 2

# lightest design from stiffened_hand.optimise()
DESIGN = dict(t_s=0.0052, t_w=0.0021, n_s=3, h_b=0.060, t_b=0.0030, L=0.4, t_r=0.002)


class Section:
    """quad8 mesh of the cross-section built from rectangular patches that share nodes."""
    def __init__(self):
        self.nodes, self.key, self.quads, self.tag = [], {}, [], []

    def node(self, x, y):
        k = (round(x * 1e7), round(y * 1e7))
        if k not in self.key:
            self.key[k] = len(self.nodes); self.nodes.append((x, y))
        return self.key[k]

    def patch(self, xa, xb, ya, yb, nx, ny, tag):
        for i in range(nx):
            for j in range(ny):
                x = [xa + (xb - xa) * (i + f) / nx for f in (0, 0.5, 1)]
                y = [ya + (yb - ya) * (j + f) / ny for f in (0, 0.5, 1)]
                c = [self.node(x[0], y[0]), self.node(x[2], y[0]), self.node(x[2], y[2]), self.node(x[0], y[2])]
                m = [self.node(x[1], y[0]), self.node(x[2], y[1]), self.node(x[1], y[2]), self.node(x[0], y[1])]
                self.quads.append(c + m); self.tag.append(tag)


def build_section(d, cover_el=0.05, web_el=0.05, blade_el=0.02):
    s = Section(); ts, tw, tb, hb = d['t_s'], d['t_w'], d['t_b'], d['h_b']
    xs = [X0 + W.BOX_WIDTH * (j + 1) / (d['n_s'] + 1) for j in range(d['n_s'])]
    for yc, sgn, tag in ((Y1, -1, 'upper'), (Y0, +1, 'lower')):
        ya, yb = yc - ts / 2, yc + ts / 2
        s.patch(X0 - tw / 2, X0 + tw / 2, ya, yb, 1, 1, 'corner')
        s.patch(X1 - tw / 2, X1 + tw / 2, ya, yb, 1, 1, 'corner')
        edges = [X0 + tw / 2] + [e for x in xs for e in (x - tb / 2, x + tb / 2)] + [X1 - tw / 2]
        for a, b in zip(edges[0::2], edges[1::2]):                      # skin bays
            s.patch(a, b, ya, yb, max(2, int(round((b - a) / cover_el))), 1, tag)
        for x in xs:                                                    # skin under each blade
            s.patch(x - tb / 2, x + tb / 2, ya, yb, 1, 1, tag)
            y_in = yc + sgn * ts / 2                                    # inner face of the skin
            lo, hi = sorted((y_in, y_in + sgn * hb))
            s.patch(x - tb / 2, x + tb / 2, lo, hi, 1, max(2, int(round(hb / blade_el))), 'blade_' + tag)
    for xc, tag in ((X0, 'front'), (X1, 'rear')):
        s.patch(xc - tw / 2, xc + tw / 2, Y0 + ts / 2, Y1 - ts / 2, 1,
                max(2, int(round((W.BOX_DEPTH - ts) / web_el))), tag)
    # every quad counter-clockwise in x-y so the extruded bricks have positive volume
    xy = np.array(s.nodes)
    for q in s.quads:
        p = xy[q[:4]]; area = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
        assert area > 0
    return s


def build(d=DESIGN, mode='static', path='.', span_el=0.05):
    s = build_section(d); xy = np.array(s.nodes); n2 = len(xy)
    corner = np.zeros(n2, bool)
    for q in s.quads: corner[q[:4]] = True
    nz = int(round(W.SEMI_SPAN / span_el)); zs = np.linspace(0.0, W.SEMI_SPAN, 2 * nz + 1)
    ids = {}; lines = ['*HEADING', 'WB-01 stiffened wing box, C3D20R, %s, %s' % (mode, d), '*NODE']; n = 0
    for k, z in enumerate(zs):
        for i in range(n2):
            if k % 2 == 0 or corner[i]:
                n += 1; ids[i, k] = n; lines.append('%d, %.7f, %.7f, %.7f' % (n, xy[i, 0], xy[i, 1], z))
    # rib reference nodes: R carries u, v; Q's first dof carries the in-plane rotation
    pitch_k = int(round(d['L'] / (zs[1] - zs[0]))); assert pitch_k % 2 == 0
    rib_k = list(range(pitch_k, 2 * nz + 1, pitch_k))
    ref = {}
    for k in rib_k:
        n += 1; r = n; n += 1; q = n; ref[k] = (r, q)
        lines.append('%d, %.7f, 0.0, %.7f' % (r, W.X_CENTROID, zs[k])); lines.append('%d, %.7f, 0.0, %.7f' % (q, W.X_CENTROID, zs[k]))
    lines.append('*ELEMENT, TYPE=C3D20R, ELSET=EBOX'); e = 0; etag = {}
    for k in range(0, 2 * nz, 2):
        for qd, tag in zip(s.quads, s.tag):
            e += 1; c, m = qd[:4], qd[4:]
            nodes = ([ids[i, k] for i in c] + [ids[i, k + 2] for i in c] + [ids[i, k] for i in m]
                     + [ids[i, k + 2] for i in m] + [ids[i, k + 1] for i in c])
            lines.append('%d, %s,' % (e, ', '.join(map(str, nodes[:15])))); lines.append(', '.join(map(str, nodes[15:])))
            etag.setdefault(tag, []).append(e)
    for tag, el in etag.items():
        lines.append('*ELSET, ELSET=%s' % tag.upper()); lines += [', '.join(map(str, el[j:j + 16])) for j in range(0, len(el), 16)]
    root = [ids[i, 0] for i in range(n2)]
    lines += ['*NSET, NSET=ROOT'] + [', '.join(map(str, root[j:j + 16])) for j in range(0, len(root), 16)]
    lines += ['*MATERIAL, NAME=ENG3081', '*ELASTIC', '%.6e, %.4f' % (W.E_MOD, W.POISSON), '*DENSITY', '%.1f' % W.RHO,
              '*SOLID SECTION, ELSET=EBOX, MATERIAL=ENG3081', '*BOUNDARY', 'ROOT, 1, 3']
    for k in rib_k:
        r, q = ref[k]; lines += ['%d, 3, 3' % r, '%d, 2, 3' % q]
    lines.append('*EQUATION')
    for k in rib_k:
        r, q = ref[k]
        for i in range(n2):
            if (i, k) not in ids: continue
            dx, dy = xy[i, 0] - W.X_CENTROID, xy[i, 1]
            lines += ['3', '%d, 1, 1.0, %d, 1, -1.0, %d, 1, %.7f' % (ids[i, k], r, q, dy)]
            lines += ['3', '%d, 2, 1.0, %d, 2, -1.0, %d, 1, %.7f' % (ids[i, k], r, q, -dx)]
    # lift into the webs: exact tributary integration, spread over the web nodes of each row
    def cum_lift(z):
        u = np.clip(z / W.SEMI_SPAN, 0.0, 1.0)
        return 0.5 * W.L0 * W.SEMI_SPAN * (u * np.sqrt(1.0 - u ** 2) + np.arcsin(u))
    edges = np.concatenate([[0.0], 0.5 * (zs[1:] + zs[:-1]), [W.SEMI_SPAN]])
    trib = np.diff(cum_lift(edges)); trib[1] += trib[0]; trib[0] = 0.0
    web = {'front': [], 'rear': []}
    for qd, tag in zip(s.quads, s.tag):
        if tag in web: web[tag] += qd
    scale = 1.0 if mode == 'static' else BUCKLE_REF
    loads = []
    for tag, share in (('front', 5.0 / 6.0), ('rear', 1.0 / 6.0)):
        wn = sorted(set(web[tag]))
        for k in range(1, len(zs)):
            use = [i for i in wn if (i, k) in ids]
            for i in use: loads.append('%d, 2, %.6e' % (ids[i, k], scale * share * trib[k] / len(use)))
    rib_w = W.RHO * W.G_ACC * W.BOX_WIDTH * W.BOX_DEPTH * d['t_r']
    loads += ['%d, 2, %.6e' % (ref[k][0], -scale * rib_w) for k in rib_k]
    step = ['*STEP', '*STATIC'] if mode == 'static' else ['*STEP', '*BUCKLE', '8']
    step += ['*CLOAD'] + loads + ['*DLOAD', 'EBOX, GRAV, %.6f, 0., -1., 0.' % (9.81 * scale), '*NODE FILE', 'U']
    if mode == 'static': step += ['*EL FILE', 'S', '*NODE PRINT, NSET=ROOT, TOTALS=ONLY', 'RF']
    step += ['*END STEP']
    name = 'wb01k_%s' % mode
    with open(os.path.join(path, name + '.inp'), 'w') as fh: fh.write('\n'.join(lines + step) + '\n')
    return name, dict(nodes=n, elements=e, section_quads=len(s.quads), applied=sum(float(l.split(',')[2]) for l in loads) / scale)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'static'
    name, info = build(mode=mode, path=sys.argv[2] if len(sys.argv) > 2 else '.')
    print(name, info)
