"""checks that the code reproduces the ENG3081 spreadsheet and report, and that the extra
methods agree with closed-form results."""
import numpy as np
import openpyxl, os, pytest
import wingbox_hand as W

SHEET = os.environ.get('WB01_SHEET', '')


def test_loads():
    assert round(W.total_lift(), 1) == 27488.9
    assert round(W.root_moment_lift(), 1) == 116666.7
    assert round(W.root_torque(), 1) == 10995.6


def test_report_optimum():
    r = W.root_stresses(0.0038)
    assert round(r['weight_per_m'], 1) == 417.5
    assert abs(r['m_net'] - 95792) < 1.5                  # report used rounded inputs
    assert round(r['sigma'] / 1e6, 1) == 99.5
    assert round(r['tau_torsion'] / 1e6, 2) == 6.03          # report rounds 22908/3.8 to 6.02
    assert round(r['tau_direct'] / 1e6, 2) == 15.34
    assert round(r['tau_total'] / 1e6, 1) == 21.4


@pytest.mark.skipif(not SHEET, reason='set WB01_SHEET to the coursework .xlsx')
def test_spreadsheet_every_row():
    ws = openpyxl.load_workbook(SHEET).active
    rows = 0
    for row in ws.iter_rows(min_row=13, max_row=83, values_only=True):
        t_mm = 3.8 if isinstance(row[0], str) else row[0]
        r = W.root_stresses(t_mm / 1e3)
        assert abs(r['weight_total'] - row[1]) < 0.06
        assert abs(r['sigma'] / 1e6 - row[2]) < 0.005         # sheet carried rounded constants
        assert abs(r['tau_total'] / 1e6 - row[3]) < 0.0006
        rows += 1
    assert rows == 71


def test_numerical_resultants_match_closed_form():
    t = 0.0038
    z, S, M, T = W.resultants(t, n=20001)
    r = W.root_stresses(t)
    assert abs(S[0] - r['v_net']) / r['v_net'] < 1e-4
    assert abs(M[0] - r['m_net']) / r['m_net'] < 1e-4
    assert abs(T[0] - W.root_torque()) / W.root_torque() < 1e-4


def test_shear_flow_closes_and_balances():
    t, V = 0.0038, 23314.0
    s, q, xy = W.shear_flow_section(t, V, 0.0)
    assert abs(q[0]) < 1e-9 and abs(q[-1]) < 1e-6 * V       # zero at the cut, by symmetry
    web = np.isclose(xy[:, 0], W.BOX_WIDTH / 2)
    y, qw = xy[web, 1], q[web]
    order = np.argsort(y)
    vertical = abs(np.trapezoid(qw[order], y[order])) * 2         # two webs carry the shear
    assert abs(vertical - V) / V < 1e-3


def test_stiffened_design_passes_and_weighs_612():
    import stiffened_hand as SK
    d = dict(t_s=0.0052, t_w=0.0021, n_s=3, h_b=0.060, t_b=0.0030, L=0.4, t_r=0.002)
    r = SK.evaluate(**d)
    assert bool(SK.feasible(r))
    assert round(float(r['weight']), 1) == 612.1
    thinner = SK.evaluate(**dict(d, t_s=0.0051))
    assert not bool(SK.feasible(thinner))          # the skin is at its minimum
