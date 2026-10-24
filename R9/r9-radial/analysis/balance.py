"""Counterweight sizing for the R9 crankshaft.

In a single-row radial with three or more cylinders the primary reciprocating forces add up
to a vector of constant magnitude (N/2) m_rec r w^2 that rotates with the crank, so it can be
balanced completely by crank counterweights, together with the rotating mass at the crankpin.
Masses are taken from the CAD bodies (steel 7.85 g/cc, aluminium 2.80 g/cc).
"""
import numpy as np
from shapely.geometry import Polygon

RHO = 7.85e-6                      # kg/mm^3
WEB_T = 2 * 40.0                   # two webs, 40 mm each
R_THROW = 85.0

def web(R, half_deg, n=180):
    boss = [(55*np.sin(a), 85 + 55*np.cos(a)) for a in np.radians(np.linspace(-90, 90, n))]
    cw = [(R*np.sin(a), R*np.cos(a)) for a in np.radians(np.linspace(180 - half_deg, 180 + half_deg, n))]
    return Polygon(boss + cw)

def moment(R, half):
    p = web(R, half)
    return p.area * p.centroid.y * WEB_T * RHO      # kg.mm about the crank axis, +ve towards crankpin

if __name__ == '__main__':
    base = moment(190, 60)
    crank_now = -1787.0                              # measured on the CAD crank with R190 / 60 deg
    need = -3358.0
    print('web contribution now %.0f kg.mm' % base)
    for half in (60, 65, 70, 75):
        for R in np.arange(190, 231, 2.0):
            m = crank_now - base + moment(R, half)
            if m <= need:
                print('half-angle %d deg -> R %.0f mm (crank moment %.0f)' % (half, R, m)); break
