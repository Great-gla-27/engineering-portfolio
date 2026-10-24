# R9: nine-cylinder radial crank train

A single-row, nine-cylinder radial crank train modelled in Fusion as a working mechanism and checked against the closed-form kinematics. Fusion document: Engineering Portfolio / R9 Engine Assembly. Design notes: `docs/R9-DN-001_design_notes.pdf`, revision A.

150 x 170 mm bore and stroke, 27.04 L, 6.8:1, master rod 380 mm, eight link rods of 300 mm on individually tuned knuckle pins. The specification was set for the exercise, not taken from a source.

## Contents

| Folder | What it holds |
|---|---|
| `analysis/` | `design.py` design point and least-squares knuckle pin tuning (radius and angle per pin, output `design_point.json`), `kinematics.py` closed-form articulated rod kinematics, `balance.py` crankshaft balance, `pose.py` pose from crank angle. `tune_knuckles.py` and `kinematics_result.json` are the first, angle-only tuning study on the rejected 300 mm master rod, kept for the record |
| `docs/` | Design notes R9-DN-001 |
| `figures/` | Render, crank train view, one-revolution animation |

## Key numbers

| Check | Result |
|---|---|
| Joint model against the closed-form kinematics, 657 piston positions | Maximum error 0.00012 mm |
| Running clearance, 79 part pairs over a revolution | No contact; smallest 4.6 mm (link rod to skirt, cylinders 5 and 6) |
| TDC height spread between cylinders | 2.40 mm with equal pins, below 0.001 mm tuned |
| Crankshaft balance | 3,370 kg·mm modelled against 3,358 required, 0.4 % over |

## Limitations

A layout study: no valve train, bearings, induction or reduction gearing, and no gas loads or structural checks. The joints were made at crank angle zero, so changing stroke, rod length or deck height needs the assembly re-seated and the kinematic check rerun. Decisions are logged in `docs/decisions.md`.

Design record: "Design Records: Five CAD and Analysis Projects", section R9 Engine Assembly.

## Fusion source file

The Fusion design sits one level up, at `../R9 Engine Assembly.f3d`. Open it in Fusion with File > Open > Open from my computer. It is the archive copy; the live version is in the Fusion cloud project.
