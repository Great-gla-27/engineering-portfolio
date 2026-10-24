# VT-01 Aero OML: VTOL wing sizing, aerodynamics and outer surface

Main wing for a 4 kg twin-boom fixed-wing VTOL (Roc Wing class): 2.0 m span, 0.407 m² area, SD7062 aerofoil, straight inboard of the boom station at y = 400 mm, taper 0.6 outboard, 2° linear washout outboard. Fusion document: Engineering Portfolio / VTOL Wing - Aero OML.

`data/geom.json` holds every dimension of the wing, and the structure model (VT-01 Structure) takes its geometry from here.

## Pipeline

`./run.sh` runs it all from `analysis/` (about 2.5 minutes; needs `requirements.txt`).

| Step | Script | Output |
|---|---|---|
| 1. Sizing | `sizing.py` | Wing area, aspect ratio, chord, cruise CL and Reynolds number, root bending moment, spar tube options (printed) |
| 2. Aerofoil trade | `airfoils.py` | `data/airfoils.json`: NeuralFoil polars at Re 150k and 250k for seven candidates |
| 3. Vortex lattice | `vlm.py` | `data/vlm_summary.json`: washout sweep 0 to 3° at cruise CL |
| 4. Span loading | `spanload.py` | `data/spanload.json`: span loading at ultimate, stall progression |
| 5. Geometry | `geom.py` | `data/geom.json`, `data/af_unit.json`: sections, spar positions and clearances, ribs |
| 6. Wing polar | `cfd_ref.py` | `data/cfd_ref.json`: vortex lattice plus NeuralFoil wing polar at cruise conditions, the baseline for a CFD comparison |
| 7. Figures | `figs_aero.py` | `figures/airfoil_trade.png`, `figures/polar.png`, `figures/spanload.png` |

## Key numbers

| Quantity | Value | Source |
|---|---|---|
| Wing loading | 9.8 kg/m² | `sizing.py` |
| Cruise CL, Reynolds number | 0.485 at 248,000, 18 m/s | `sizing.py` |
| SD7062 at Re 250k | CLmax 1.56, cruise L/D 46.8, 14.0 % thick | `data/airfoils.json` |
| Span efficiency at 2° washout | 0.984 (0.974 at 0°, 0.987 at 1°) | `data/vlm_summary.json` |
| Ultimate root bending moment, n = 5.7 | 46.9 N·m vortex lattice, 47.5 N·m elliptic | `spanload.py`, `sizing.py` |
| First section to stall | Root, wing CL about 1.54 | `spanload.py` |

## Limitations

NeuralFoil and the vortex lattice are lower-order methods and do not resolve separation. Booms, propeller wash and control surfaces are not in the aerodynamic model. Decisions are logged in `docs/decisions.md`.

## Further work

Run the wing in STAR-CCM+ at 18 m/s and Re 248,000 and compare the polar with `data/cfd_ref.json`. The comparison matters most approaching stall, where the lower-order methods are weakest and the 2° washout decision depends on them.

Design record: "Design Records: Five CAD and Analysis Projects", section VTOL Wing - Aero OML.

## Fusion source file

The Fusion design sits one level up, at `../VTOL Wing - Aero OML.f3d`. Open it in Fusion with File > Open > Open from my computer. It is the archive copy; the live version is in the Fusion cloud project.
