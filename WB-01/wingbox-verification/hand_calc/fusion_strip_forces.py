"""Web strip forces for the Fusion static study (gravity off, self-weight folded in).

Fusion cannot take a distributed lift on a line, so each 0.5 m strip of each web gets one
force in +Y. The lift on a strip is split 5/6 front web, 1/6 rear web, which puts the
resultant on the centre of pressure (x = 0.4 m) and so reproduces the root torque. The
strip's self-weight acts at the shear centre, so it is split half to each web.
Writes fusion_strip_forces.csv and prints a table.
"""
import csv
import wingbox_hand as W
from strip_loads import strips

T = 0.0038


def forces(t=T):
    w = W.weight_per_span(t)
    out = []
    for s in strips():
        wt = w * (s['z_end_m'] - s['z_start_m'])
        out.append(dict(strip=s['strip'], z_start_mm=s['z_start_m'] * 1e3, z_end_mm=s['z_end_m'] * 1e3,
                        front_N=5 / 6 * s['force_N'] - wt / 2, rear_N=1 / 6 * s['force_N'] - wt / 2))
    return out


if __name__ == '__main__':
    rows = forces()
    with open('fusion_strip_forces.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    for r in rows: print('| %d | %.0f-%.0f | %.1f | %.1f |' % tuple(r.values()))
    print('net %.1f N' % sum(r['front_N'] + r['rear_N'] for r in rows))
