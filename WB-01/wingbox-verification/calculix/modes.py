"""buckling mode post-processing: where the first mode sits and how long its buckles are."""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hand_calc'))
import wingbox_hand as W
from wingbox_shell import read_frd


def disp_blocks(path):
    out, cur = [], None
    for line in open(path):
        if line.startswith(' -4  DISP'): cur = {}; out.append(cur)
        elif line.startswith(' -4'): cur = None
        elif line.startswith(' -1') and cur is not None:
            cur[int(line[3:13])] = [float(line[13 + 12 * j:25 + 12 * j]) for j in range(3)]
        elif line.startswith(' -3'): cur = None
    return out


def describe(frd, t, mode_index=1, x=None, y=None):
    C = read_frd(frd)['COORD']; modes = disp_blocks(frd)
    u = modes[mode_index]                      # block 0 is the reference static solution
    ids = np.array(list(C)); c = np.array([C[i] for i in ids]); d = np.array([u[i] for i in ids])
    x = W.BOX_LE + W.BOX_WIDTH / 2 if x is None else x; y = W.BOX_DEPTH / 2 if y is None else y
    sel = np.isclose(c[:, 0], x, atol=1e-4) & np.isclose(c[:, 1], y, atol=1e-4)
    z, v = c[sel, 2], d[sel, 1]; o = np.argsort(z); z, v = z[o], v[o]
    amp = abs(v) / abs(v).max(); zp = z[np.argmax(amp)]
    zc = z[1:][np.sign(v[1:]) != np.sign(v[:-1])]
    active = z[amp > 0.2]
    return dict(peak_z=zp, active_from=active.min(), active_to=active.max(),
                half_wave=float(np.diff(zc[:6]).mean()) if len(zc) > 2 else float('nan'))


if __name__ == '__main__':
    print(describe(sys.argv[1], float(sys.argv[2])))
