# WB-01 Wing box verification

The ENG3081 coursework wing box, re-checked by finite element analysis and redesigned so that it does not buckle.

The coursework sized a 10 m semi-span box by thin-wall beam theory: a uniform 3.8 mm wall at 417.5 N/m. This repository ports that hand calculation to Python, checks it against shell and solid CalculiX models, and finds that the design buckles at under a tenth of its load. It then sizes a stiffened box that meets the same stress criteria and survives 1.5 times the load without buckling.

## Results

| | Hand | FE | |
|---|---|---|---|
| Bending stress, 3.8 mm, z = 1.25 m | 68.9 MPa | 70.3 MPa | +2.0 % |
| Web shear, same station | 17.8 MPa | 17.9 MPa | +0.5 % |
| Tip deflection | 193.3 mm | 195.9 mm | +1.3 % |
| Tip twist (ribs every 0.5 m) | 0.207 deg | 0.202 deg | -2.5 % |
| Cover buckling factor, coursework design | 0.041 | 0.091 | needs 1.5 |
| Stiffened design, first buckling factor | 1.68 | 1.78 | |

The viable stiffened box weighs 612 N/m: 5.2 mm skin, 3 blade stringers per cover, ribs every 0.4 m. That is 47 % heavier than the coursework box and half the weight of an unstiffened box that passes the same checks. The full write-up, with limitations, is in [docs/WB-01_verification_report.md](docs/WB-01_verification_report.md).

## Layout

```
hand_calc/   wingbox_hand.py         coursework method, ported, plus shear flow, deflection, twist, buckling
             test_wingbox_hand.py    reproduces all 71 spreadsheet rows (set WB01_SHEET to the .xlsx)
             strip_loads.py          equivalent strip loads
             fusion_strip_forces.py  the 40 web forces for the Fusion study
             stiffened_hand.py       stiffened redesign: checks and exhaustive sizing
calculix/    wingbox_shell.py        S8R shell model (optional rib diaphragms)
             wingbox_solid.py        C3D20R solid model
             wingbox_stiffened.py    C3D20R stiffened box, ribs as in-plane rigid diaphragms
             compare.py, stiffened_compare.py, modes.py, sweep.py
results/     sweep.csv, stiffened_compare.csv
figures/     make_figures.py and the four report figures
docs/        brief and decision log, report, Fusion setup sheet
```

## Running it

Python 3.11+ with numpy, scipy, matplotlib, openpyxl and pytest; CalculiX 2.21 (`ccx`) on the path.

```
cd hand_calc && pytest && python wingbox_hand.py && python stiffened_hand.py
cd ../calculix && python sweep.py ../runs/sweep
python wingbox_stiffened.py static ../runs/stiff && (cd ../runs/stiff && ccx -i wb01k_static)
python wingbox_stiffened.py buckle ../runs/stiff && (cd ../runs/stiff && ccx -i wb01k_buckle)
python stiffened_compare.py ../runs/stiff
cd ../figures && python make_figures.py ../runs
```

The sweep takes about 8 minutes on two cores; the stiffened model takes about 1.5 minutes.

## Conventions

x is chordwise from the leading edge, y is up, z is spanwise from the root. SI units in the code; reports in MPa and mm. E = 110 GPa, ν = 0.33. The brief gives no stiffness; the reason for this choice is in the decision log.

## Fusion source file

The Fusion design sits one level up, at `../WB-01 Wing Box.f3d`. Open it in Fusion with File > Open > Open from my computer. It is the archive copy; the live version is in the Fusion cloud project.

The file also holds the six simulation cases set up for the Fusion comparison, which the report lists as further work.
