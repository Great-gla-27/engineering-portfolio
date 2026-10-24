# VT-01 Structure: VTOL wing spars, ribs and FEA check

Spar and rib structure for the VT-01 wing: 16/14 mm CFRP main spar at 25 % chord, 6/4 mm rear spar held straight, 3 mm ribs every 100 mm. Fusion document: Engineering Portfolio / VTOL Wing - Structure.

The loads and the geometry come from VT-01 Aero OML. `data/from_aero/` holds the three files this model takes from it (`geom.json`, `spanload.json`, `af_unit.json`); refresh them from that repository's `data/` if the aerodynamic model changes.

## Pipeline

`./run.sh` runs it all from `analysis/` (seconds; numpy, scipy, matplotlib).

| Step | Script | Output |
|---|---|---|
| 1. Rib loads | `ribdata.py` | `data/ribdata.json`: rib loads from the span loading, lightening holes |
| 2. Beam model | `beam.py` | `data/beam.json`: Euler-Bernoulli FE, flight ultimate, hover ultimate, modal |
| 3. Prediction | `beam3.py` | The three-load Fusion FEA case predicted before the solve (printed) |
| 4. Figures | `figs_structure.py` | `figures/beam.png` |

The Fusion static stress results are `figures/fea_*.png`.

## Key numbers

| Quantity | Beam | Fusion FEA |
|---|---|---|
| Tip deflection, ultimate (n = 5.7), three-load case | 76.6 mm predicted before the solve | 76.3 mm |
| Peak main spar bending stress, same case | 273 MPa predicted | 295 MPa (σyy, model maximum) |
| Root bending moment | 46.9 N·m | - |
| First bending frequency, cantilever | 8.0 Hz | - |
| Half-wing primary structure mass | 173 g (Fusion mass properties) | - |

The FEA case idealises the ultimate span loading as three point loads (42.5, 36.75 and 25.41 N at y = 200, 500 and 800 mm, `beam3.py`) so that it can be applied in Fusion. The beam model with every rib load gives 77.3 mm and 272 MPa (`data/beam.json`). The 285 MPa in the decision log is the earlier sizing estimate, with the main spar carrying the whole elliptic root moment; the beam model shares the moment with the rear spar by stiffness.

Deflection agrees to 0.4 %. The FEA stress is 8 % above the beam value: the beam gives the nominal section stress, while the FEA figure is the maximum anywhere in the model, including the fully fixed root face, where beam theory has no local effects.

## Limitations

CFRP is isotropic at E = 100 GPa, so torsional stiffness is overestimated. Joints, bonds and the spar root fitting are not analysed, and nor is local buckling of the tube walls. Boom, motor and covering masses are estimates. The FEA is linear static. Decisions are logged in `docs/decisions.md`.

Design record: "Design Records: Five CAD and Analysis Projects", section VTOL Wing - Structure.

## Fusion source file

The Fusion design sits one level up, at `../VTOL Wing - Structure.f3d`. Open it in Fusion with File > Open > Open from my computer. It is the archive copy; the live version is in the Fusion cloud project.
