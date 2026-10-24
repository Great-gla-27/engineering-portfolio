# AC-01: IATS hydrogen-electric STOL aircraft

A Fusion model of the IATS 12-passenger hydrogen-electric STOL aircraft (ENG3006 Aircraft Design, group project), used to check the team's sizing and stability numbers against the geometry they imply. Sizing and stability were my workstream on the six-person team; this model is my own interpretation of the team's design.

## What the model found

- The team's 10.15 % static margin used the mean geometric chord of an earlier wing. With the true MAC (3.186 m) and the tail arm measured on the model (6.94 m against the 8.67 m assumed), the margin at the stated CG is 8.51 %: still inside the 5 to 15 % band, but only after correcting both errors, which act in opposite directions.
- The stated 9.32 m CG cannot be reproduced from the report's own mass table, which sums to 8.885 m.
- With the main gear at the team's 9.2 m station, the tip-back angle is 5.2° against a 15° guideline. About 9.55 m would pass.
- Planform matches the parameter table to within 0.001 %, and both propellers clear the ground and fuselage.

## Contents

| Folder | What it holds |
|---|---|
| `params/` | `IATS_master_parameters.csv`: every value the model uses, with the team file and line it came from |
| `analysis/` | `sizing_check.py` MAC and static margin re-check, `design_checks.py` CG, stability, clearance and ground angle checks from values measured off the model |
| `results/` | Outputs of both checks and the measurements taken off the model |
| `docs/` | Design notes, conflicts and assumptions with the decision log, BS 8888 checklist |
| `outputs/` | General arrangement `AC-01-GA-001.pdf`, render, cutaway, STEP export |

## Fusion source file

The Fusion design sits one level up, at `../AC-01 IATS Aircraft.f3d`. Open it in Fusion with File > Open > Open from my computer. It is the archive copy; the live version is in the Fusion cloud project.
