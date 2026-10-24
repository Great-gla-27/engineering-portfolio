"""WB-01 shell model of the ENG3081 wing box in CalculiX (independent cross-check of the hand
calculation and of the Fusion solid model).

Model:
  - walls on the 1.2 x 0.2 m midline, S8R quadratic shells of thickness t (CalculiX expands
    them to C3D20R bricks internally; results are reported on the shell mid-surface);
  - root nodes (z = 0) fully fixed;
  - lift introduced through the webs, as ribs would do on a real wing: at each span station
    5/6 of l(z) goes into the front web and 1/6 into the rear web, which places the resultant
    on the 0.4 m centre-of-pressure line and so carries the torque without a separate couple.
    The force is spread evenly over the web depth. Lift is not applied as pressure on the
    cover, because an unstiffened 1.2 m cover would then bend as a plate between the webs,
    a local effect the coursework model does not contain;
  - self-weight from gravity on the 4000 kg/m^3 material.

Axes: x chordwise from the leading edge, y up, z spanwise from the root. SI units.
Usage: python wingbox_shell.py <element size m> <t m> [static|buckle]
"""
import sys, os, subprocess, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hand_calc'))
import wingbox_hand as W

X0, X1 = W.BOX_LE, W.BOX_LE + W.BOX_WIDTH
BUCKLE_REF = 0.01        # reference load for *BUCKLE, as a fraction of the design load
Y0, Y1 = -W.BOX_DEPTH / 2, W.BOX_DEPTH / 2


def loop_stations(h):
    """points round the midline loop, as (x, y, wall) with wall in 'upper', 'rear', 'lower', 'front'.
    Corner points are shared. Returns arrays at half-element spacing (for quadratic elements)."""
    nw = max(2, int(round(W.BOX_WIDTH / h))); nh = max(2, int(round(W.BOX_DEPTH / h)))
    pts, walls = [], []
    def leg(p, q, n, name):
        for i in range(2 * n):
            f = i / (2 * n); pts.append((p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)); walls.append(name)
    leg((X0, Y1), (X1, Y1), nw, 'upper')
    leg((X1, Y1), (X1, Y0), nh, 'rear')
    leg((X1, Y0), (X0, Y0), nw, 'lower')
    leg((X0, Y0), (X0, Y1), nh, 'front')
    return np.array(pts), walls


def build(h, t, mode='static', path='.', rib_pitch=None, rib_t=None):
    pts, walls = loop_stations(h)
    m = len(pts)                                   # nodes round the loop (closed, even)
    nz = int(round(W.SEMI_SPAN / h)); zs = np.linspace(0.0, W.SEMI_SPAN, 2 * nz + 1)
    nid = lambda i, k: k * m + (i % m) + 1        # i round the loop, k along the span
    lines = ['*HEADING', 'WB-01 wing box, S8R shells, h = %.4f m, t = %.4f m, %s' % (h, t, mode), '*NODE']
    for k, z in enumerate(zs):
        for i, (x, y) in enumerate(pts):
            lines.append('%d, %.6f, %.6f, %.6f' % (nid(i, k), x, y, z))
    lines.append('*ELEMENT, TYPE=S8R, ELSET=EBOX')
    e = 0; elset = {'upper': [], 'rear': [], 'lower': [], 'front': []}
    for k in range(0, 2 * nz, 2):
        for i in range(0, m, 2):
            e += 1
            c = [nid(i, k), nid(i + 2, k), nid(i + 2, k + 2), nid(i, k + 2)]
            mid = [nid(i + 1, k), nid(i + 2, k + 1), nid(i + 1, k + 2), nid(i, k + 1)]
            lines.append('%d, %s' % (e, ', '.join(str(n) for n in c + mid)))
            elset[walls[i]].append(e)
    # optional ribs: flat shell diaphragms closing the section at every rib station
    nw = max(2, int(round(W.BOX_WIDTH / h))); nh = max(2, int(round(W.BOX_DEPTH / h)))
    rib_ids = []
    if rib_pitch:
        def loop_index(a, b):
            if b == 2 * nh: return a
            if a == 2 * nw: return 2 * nw + (2 * nh - b)
            if b == 0: return 2 * nw + 2 * nh + (2 * nw - a)
            if a == 0: return (4 * nw + 2 * nh + b) % m
            return None
        next_id = len(zs) * m + 1
        n_ribs = int(round(W.SEMI_SPAN / rib_pitch))
        for r_ in range(1, n_ribs + 1):
            k = int(round(r_ * rib_pitch / (zs[1] - zs[0])))
            assert k % 2 == 0, 'rib stations must sit on element corner rows'
            grid = {}
            for a in range(2 * nw + 1):
                for b in range(2 * nh + 1):
                    if a % 2 and b % 2: continue
                    li = loop_index(a, b)
                    if li is not None: grid[a, b] = nid(li, k)
                    else:
                        grid[a, b] = next_id
                        lines.insert(lines.index('*ELEMENT, TYPE=S8R, ELSET=EBOX'),
                                     '%d, %.6f, %.6f, %.6f' % (next_id, X0 + a * W.BOX_WIDTH / (2 * nw), Y0 + b * W.BOX_DEPTH / (2 * nh), zs[k]))
                        next_id += 1
            for a in range(0, 2 * nw, 2):
                for b in range(0, 2 * nh, 2):
                    e += 1
                    c = [grid[a, b], grid[a + 2, b], grid[a + 2, b + 2], grid[a, b + 2]]
                    md = [grid[a + 1, b], grid[a + 2, b + 1], grid[a + 1, b + 2], grid[a, b + 1]]
                    lines.append('%d, %s' % (e, ', '.join(str(x) for x in c + md))); rib_ids.append(e)
        elset['ribs'] = rib_ids
    # corner normals: give the corner nodes one averaged (diagonal, inward) normal in every
    # element that uses them, so CalculiX does not insert rigid knots at the corners. Knots
    # spoil the *BUCKLE eigenproblem (spurious factors near 1 that do not scale with load).
    corners = {0: (1, -1), 2 * nw: (-1, -1), 2 * nw + 2 * nh: (-1, 1), 4 * nw + 2 * nh: (1, 1)}
    normals = ['*NORMAL']
    eid = 0
    for k in range(0, 2 * nz, 2):
        for i in range(0, m, 2):
            eid += 1
            for ii in (i, (i + 2) % m):
                if ii in corners:
                    nx, ny = corners[ii]; r2 = 2 ** -0.5
                    for kk in (k, k + 1, k + 2):
                        normals.append('%d, %d, %.6f, %.6f, 0.0' % (eid, nid(ii, kk), nx * r2, ny * r2))
    for name, ids in elset.items():
        lines.append('*ELSET, ELSET=%s' % name.upper())
        lines += [', '.join(str(x) for x in ids[j:j + 16]) for j in range(0, len(ids), 16)]
    lines += normals
    lines += ['*NSET, NSET=ROOT'] + [', '.join(str(nid(i, 0)) for i in range(j, min(j + 16, m))) for j in range(0, m, 16)]
    lines += ['*MATERIAL, NAME=ENG3081', '*ELASTIC', '%.6e, %.4f' % (W.E_MOD, W.POISSON),
              '*DENSITY', '%.1f' % W.RHO]
    walls_set = [x for x in ('UPPER', 'REAR', 'LOWER', 'FRONT')]
    lines += ['*ELSET, ELSET=SKIN'] + [', '.join(walls_set)]
    lines += ['*SHELL SECTION, ELSET=SKIN, MATERIAL=ENG3081', '%.6f' % t]
    if rib_pitch:
        lines += ['*SHELL SECTION, ELSET=RIBS, MATERIAL=ENG3081', '%.6f' % (rib_t or t)]
    lines += [
              '*BOUNDARY', 'ROOT, 1, 6']
    # lift: nodal forces on web nodes. Each span node takes the exact lift over its tributary
    # length (integrated in closed form); the root node's share goes to the first free node so
    # the applied total equals the coursework lift.
    def cum_lift(z):
        u = np.clip(z / W.SEMI_SPAN, 0.0, 1.0)
        return 0.5 * W.L0 * W.SEMI_SPAN * (u * np.sqrt(1.0 - u ** 2) + np.arcsin(u))
    edges = np.concatenate([[0.0], 0.5 * (zs[1:] + zs[:-1]), [W.SEMI_SPAN]])
    trib = np.diff(cum_lift(edges)); trib[1] += trib[0]; trib[0] = 0.0
    front = sorted([i for i, w in enumerate(walls) if w == 'front'] + [0], key=lambda i: pts[i][1])
    rear = sorted([i for i, w in enumerate(walls) if w == 'rear'] + [walls.index('lower')], key=lambda i: pts[i][1])
    loads = []
    for idx, share in ((front, 5.0 / 6.0), (rear, 1.0 / 6.0)):
        for k in range(1, len(zs)):
            # S8R has no centre node, so on mid-element span rows only even loop nodes exist
            use = idx if k % 2 == 0 else [i for i in idx if i % 2 == 0]
            wy = np.ones(len(use)); wy[0] = wy[-1] = 0.5; wy /= wy.sum()
            for j, i in enumerate(use):
                loads.append('%d, 2, %.6e' % (nid(i, k), share * trib[k] * wy[j]))
    # CalculiX's *BUCKLE eigen-solver returns factors clustered near 1 when the true factor is
    # far below 1 (verified: they do not scale with the load). The buckling step therefore uses
    # a reference load of BUCKLE_REF times the design load, and the factors are rescaled.
    scale = 1.0 if mode == 'static' else BUCKLE_REF
    if scale != 1.0:
        loads = ['%s, 2, %.6e' % (l.split(',')[0], float(l.split(',')[2]) * scale) for l in loads]
    step = ['*STEP'] if mode == 'static' else ['*STEP', '*BUCKLE', '6']
    if mode == 'static': step += ['*STATIC']
    step += ['*CLOAD'] + loads + ['*DLOAD', 'EBOX, GRAV, %.6f, 0., -1., 0.' % (9.81 * scale)]
    if mode == 'static':
        step += ['*NODE FILE, OUTPUT=2D', 'U', '*EL FILE, OUTPUT=2D', 'S', '*NODE PRINT, NSET=ROOT, TOTALS=ONLY', 'RF']
    else:
        step += ['*NODE FILE, OUTPUT=2D', 'U']
    step += ['*END STEP']
    name = 'wb01_h%03d_t%03d_%s%s' % (round(h * 1000), round(t * 1e4), mode, '_ribs%03d' % round(rib_pitch * 100) if rib_pitch else '')
    with open(os.path.join(path, name + '.inp'), 'w') as fh:
        fh.write('\n'.join(lines + step) + '\n')
    total = sum(float(l.split(',')[2]) for l in loads)
    return name, dict(nodes=len(zs) * m, elements=e, applied_lift=total, pts=pts, walls=walls, zs=zs, m=m)


def read_frd(path):
    """minimal CalculiX .frd reader: returns {block name: {node: values}} for the last increment."""
    out, cur, coords = {}, None, {}
    with open(path) as fh:
        for line in fh:
            if line.startswith('    2C'):
                cur = 'COORD'; out[cur] = {}
            elif line.startswith(' -4  '):
                cur = line.split()[1]; out[cur] = {}
            elif line.startswith(' -1') and cur:
                nid = int(line[3:13]); vals = [float(line[13 + 12 * j:25 + 12 * j]) for j in range((len(line.rstrip()) - 13) // 12)]
                out[cur][nid] = vals
            elif line.startswith(' -3'):
                cur = None
    return out


def run(name, path='.'):
    subprocess.run(['ccx', '-i', name], cwd=path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    h, t = float(sys.argv[1]), float(sys.argv[2]); mode = sys.argv[3] if len(sys.argv) > 3 else 'static'
    ribs = float(sys.argv[4]) if len(sys.argv) > 4 else None
    name, info = build(h, t, mode, rib_pitch=ribs)
    print(name, info['nodes'], 'nodes', info['elements'], 'elements, applied lift %.1f N' % info['applied_lift'])


def buckling_factors(dat):
    """design-load buckling factors from a .dat file of a run built with mode='buckle'."""
    out, on = [], False
    for line in open(dat):
        if 'B U C K L I N G' in line: on = True; continue
        if on:
            p = line.split()
            if len(p) == 2 and p[0].isdigit(): out.append(float(p[1]) * BUCKLE_REF)
            elif out and not p: break
    return out
