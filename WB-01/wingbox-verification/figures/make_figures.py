"""Figures for the WB-01 report. Reads the CalculiX run directories and results/*.csv.
Usage: python make_figures.py <runs dir>
"""
import sys, os, csv, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'hand_calc')); sys.path.insert(0, os.path.join(ROOT, 'calculix'))
import wingbox_hand as W
from compare import compare, hand_at
from modes import disp_blocks
from wingbox_shell import read_frd

HAND, FE, GREY, INK, MUTED = '#2a78d6', '#eb6834', '#8a8984', '#0b0b0b', '#52514e'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': GREY, 'axes.labelcolor': INK, 'xtick.color': MUTED,
                     'ytick.color': MUTED, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e6e5e0', 'grid.linewidth': 0.6, 'lines.linewidth': 2,
                     'legend.frameon': False, 'figure.dpi': 150, 'savefig.bbox': 'tight'})


def read_csv(name):
    with open(os.path.join(ROOT, 'results', name)) as fh:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(fh)]


def spanwise(runs):
    t = 0.0038; rib = 0.5
    frd = os.path.join(runs, 'sweep', 'wb01_h050_t038_static_ribs050.frd')
    st = list(np.arange(0.25, 9.8, 0.5))
    rows, tip = compare(frd, t, extra_weight=W.RHO * W.G_ACC * W.BOX_WIDTH * W.BOX_DEPTH * t / rib, stations=st)
    z = [r['z'] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    zz = np.linspace(0, W.SEMI_SPAN, 400)
    hs = [hand_at(t, x, W.RHO * W.G_ACC * W.BOX_WIDTH * W.BOX_DEPTH * t / rib) for x in zz]
    ax[0].plot(zz, [h[0] / 1e6 for h in hs], color=HAND, label='Hand (beam theory)')
    ax[0].plot(z, [r['sigma_cover'] for r in rows], 'o', ms=4, color=FE, label='CalculiX S8R, mid-bay')
    ax[0].set(xlabel='Span z (m)', ylabel='Upper cover stress (MPa)', title='Bending stress, t = 3.8 mm')
    ax[1].plot(zz, [h[1] / 1e6 for h in hs], color=HAND, label='Hand (shear flow)')
    ax[1].plot(z, [r['tau_front'] for r in rows], 'o', ms=4, color=FE, label='CalculiX S8R, mid-bay')
    ax[1].set(xlabel='Span z (m)', ylabel='Front web shear (MPa)', title='Web shear at the neutral axis')
    for a in ax: a.legend(loc='upper right'); a.set_xlim(0, 10); a.set_ylim(bottom=0)
    fig.savefig(os.path.join(HERE, 'fig1_spanwise_3p8mm.png')); plt.close(fig)


def sweep():
    r = read_csv('sweep.csv'); t = [x['t_mm'] for x in r]
    fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.6))
    ax[0].plot(t, [x['sigma_mid_hand'] for x in r], color=HAND, label='Hand')
    ax[0].plot(t, [x['sigma_mid_fe'] for x in r], 'o', ms=5, color=FE, label='CalculiX')
    ax[0].set(xlabel='Skin t (mm)', ylabel='MPa', title='Cover stress, z = 1.25 m')
    ax[1].plot(t, [x['v_tip_hand_mm'] for x in r], color=HAND, label='Hand')
    ax[1].plot(t, [x['v_tip_fe_mm'] for x in r], 'o', ms=5, color=FE, label='CalculiX')
    ax[1].set(xlabel='Skin t (mm)', ylabel='mm', title='Tip deflection')
    ax[2].plot(t, [x['buckle_hand'] for x in r], color=HAND, label='Hand, SS edges')
    ax[2].plot(t, [x['buckle_fe'] for x in r], 'o', ms=5, color=FE, label='CalculiX')
    ax[2].set(xlabel='Skin t (mm)', ylabel='Load factor', title='Cover buckling (needs 1.5)')
    for a in ax: a.legend()
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'fig2_thickness_sweep.png')); plt.close(fig)


def mode_map(frd, ax, title, ymin):
    C = read_frd(frd)['COORD']; u = disp_blocks(frd)[1]
    ids = np.array([i for i in C if i in u]); c = np.array([C[i] for i in ids]); d = np.array([u[i] for i in ids])
    sel = c[:, 1] > ymin
    x, z, v = c[sel, 0], c[sel, 2], d[sel, 1]
    v = v / abs(v).max()
    keep = z < 3.0
    sc = ax.scatter(z[keep], x[keep], c=v[keep], s=2, cmap='RdBu_r', vmin=-1, vmax=1, linewidths=0)
    ax.set(xlabel='Span z (m)', ylabel='Chord x (m)', title=title); ax.grid(False)
    return sc


def modes(runs):
    fig, ax = plt.subplots(2, 1, figsize=(7.2, 4.8), gridspec_kw=dict(hspace=0.55))
    mode_map(os.path.join(runs, 'wb01_h050_t038_buckle.frd'), ax[0], 'Coursework box, 3.8 mm, no ribs: first mode, factor 0.09', 0.0999)
    sc = mode_map(os.path.join(runs, 'stiff', 'wb01k_buckle.frd'), ax[1], 'Stiffened box: first mode, factor 1.78 (skin bay with blade roll)', 0.0999)
    cb = fig.colorbar(sc, ax=ax, shrink=0.8); cb.set_label('Normalised upper cover v')
    fig.savefig(os.path.join(HERE, 'fig3_buckling_modes.png')); plt.close(fig)


def mass():
    names = ['Coursework\n3.8 mm, unstiffened', 'Stiffened\n5.2 mm skin, 3 blades', 'Unstiffened\n10.7 mm']
    w = [417.5, 612.1, 1175.6]; ok = ['buckles below 0.1 x load', 'meets all checks', 'meets all checks']
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    bars = ax.barh(names, w, color=[GREY, HAND, HAND], height=0.55)
    for b, val, s in zip(bars, w, ok):
        ax.text(val + 15, b.get_y() + b.get_height() / 2, '%.0f N/m, %s' % (val, s), va='center', color=INK)
    ax.set(xlabel='Structural weight per metre of span (N/m)', xlim=(0, 1700)); ax.invert_yaxis(); ax.grid(axis='y'); ax.set_axisbelow(True)
    fig.savefig(os.path.join(HERE, 'fig4_mass.png')); plt.close(fig)


if __name__ == '__main__':
    runs = sys.argv[1]
    spanwise(runs); sweep(); modes(runs); mass()
