"""Equivalent strip loads for applying the elliptical lift in FEA.

The upper cover is split into LoadStripCount equal spanwise strips. Each strip gets one
remote force equal to the lift over that strip, placed at the strip's lift centroid on the
centre of pressure line (x = X_CP, y = 0). Using the centroid makes the root shear, root
bending moment and root torque of the stepped load exactly equal to the continuous ones.
"""
import csv, numpy as np
from scipy.integrate import quad
import wingbox_hand as W

N_STRIPS = 20


def strips(n=N_STRIPS):
    edges = np.linspace(0.0, W.SEMI_SPAN, n + 1)
    rows = []
    for k in range(n):
        z0, z1 = edges[k], edges[k + 1]
        f = quad(W.lift_per_span, z0, z1)[0]
        zc = quad(lambda z: z * W.lift_per_span(z), z0, z1)[0] / f
        rows.append(dict(strip=k + 1, z_start_m=z0, z_end_m=z1, force_N=f, z_centroid_m=zc,
                         x_m=W.X_CP, y_m=0.0))
    return rows


if __name__ == '__main__':
    rows = strips()
    with open('strip_loads.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    F = sum(r['force_N'] for r in rows); M = sum(r['force_N'] * r['z_centroid_m'] for r in rows)
    print('%-6s %-8s %-8s %-10s %-10s' % ('strip', 'z0 m', 'z1 m', 'F N', 'z_c m'))
    for r in rows: print('%-6d %-8.2f %-8.2f %-10.1f %-10.4f' % (r['strip'], r['z_start_m'], r['z_end_m'], r['force_N'], r['z_centroid_m']))
    print('sum F %.1f N (exact %.1f), root moment %.1f N.m (exact %.1f)' % (F, W.total_lift(), M, W.root_moment_lift()))
