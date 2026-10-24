# WB-01 brief: inputs, sources and decisions

## Inputs (all from the ENG3081 brief or report)

| Quantity | Value | Source |
|---|---|---|
| Semi-span | 10 m | Brief p1 |
| Chord | 2 m | Brief p1 |
| Box, midline | 1.2 m wide x 0.2 m deep, front web at 0.2 m from LE | Brief Fig 1; `Figures_Code.py` |
| Box centroid / shear centre | 0.8 m from LE | Derived, doubly symmetric |
| Centre of pressure | 0.4 m from LE (20 % chord), constant along span | Brief p1 |
| Lift | elliptical, l0 = 3500 N/m | Brief Fig 3 |
| Density | 4000 kg/m3 | Brief p1 |
| Allowables | 100 MPa direct, 50 MPa shear, yield only | Brief p1 |
| E, Poisson's ratio | not given | Open question 1 |

## Hand calculation port: status

`hand_calc/wingbox_hand.py` reproduces all 71 rows of `ASM3_WingBox_Optimisation_2740042.xlsx`: weight to 0.05 N, bending stress to 0.002 MPa (the sheet carried rounded constants), total shear to 0.0005 MPa. It also reproduces the report's 3.8 mm optimum. Tests are in `hand_calc/test_wingbox_hand.py`.

## Discrepancies found in the report (the spreadsheet is right in each case)

1. Table 2 gives 25.9 MPa total shear at 3 mm. The spreadsheet and the code give 27.8 MPa: 20.16 MPa direct plus 7.64 MPa torsion.
2. Section 4.2.2 gives a direct web shear of 15.38 MPa at 3.8 mm. 23,314 / (0.4 x 0.0038) is 15.34 MPa. The 21.4 MPa total still stands, because the spreadsheet was correct.
3. The torsional shear is printed as 6.02 MPa. 22,908 / 3.8 is 6.03 MPa. This is rounding only.

None of these changes the 3.8 mm result or the 24.0 % saving.

## New results from the added methods (t = 3.8 mm, root)

- Peak web shear from the full shear flow distribution, including torsion, is 21.77 MPa, against 21.37 MPa from the average-web method used in the report: 1.9 % higher, still under half the 50 MPa allowable.
- Numerical integration of the spanwise load gives a root moment of 95,790 N.m, against 95,791 N.m in closed form.

## Questions resolved

1. **Modulus and Poisson's ratio.** Stresses do not depend on E here, but deflection, twist and buckling all do. The options are E = 110 GPa, ν = 0.33 (titanium-like, the closest match to a density of 4000 kg/m3, which sits between aluminium at 2700 and titanium at 4430) or E = 70 GPa, ν = 0.33 (aluminium-like).
2. **Solid geometry in Fusion.** The coursework treats 1.2 x 0.2 m as midline dimensions. A Fusion solid needs real faces, so either offset the walls by t/2 each side of the midline, which matches the hand calculation exactly, or use 1.2 x 0.2 m as outer dimensions, which lowers Ixx by 4.1 % at 3.8 mm and pushes the root bending stress to about 101.8 MPa. The recommendation is the midline offset, so the comparison tests the method and not a geometry change.
3. **Buckling functions.** (`cover_buckling_stress`, `web_shear_buckling_stress`, `web_bending_buckling_stress`). Each docstring gives the source of its k values.

## Decision log

| Decision | Options | Reason |
|---|---|---|
| Port the spreadsheet as written, including the average-web shear method, and add the shear flow method alongside it rather than replacing it | Replace the method / keep both | Keeping both lets the FEA comparison show which assumption matters |
| E = 110 GPa, ν = 0.33, G = 41.4 GPa | Titanium-like / aluminium-like | Closest to the 4000 kg/m3 density in the brief |
| Fusion solid walls offset t/2 either side of the 1.2 x 0.2 m midline | Midline offset / outer dimensions | Model section identical to the hand calculation, so differences come from the method, not the geometry |
| Lift applied as 20 strip forces of 0.5 m each, at each strip's lift centroid on the 0.4 m line | Pressure on strips / remote force per strip | Remote force at the centroid gives exact root shear, moment and torque and carries the torque in the model |
| Lift applied in FE as nodal forces on the two webs, 5/6 front and 1/6 rear, exact tributary integral per span row | Cover pressure / remote force / web forces | Puts the resultant on the 0.4 m line without bending the unstiffened 1.2 m cover as a plate; reaction within 0.03 % |
| Shell corners given one averaged normal | Rigid knots (CalculiX default) / averaged normals | Knots gave 0.075 against 0.093 from the solid model; averaged normals agree with the solid |
| *BUCKLE run at 1 % of the design load and rescaled | Full load / reference load | At full load the factors clustered near 1 and did not scale with load; checked on a cantilever strip against Euler (1.4 %) |
| FE stresses compared at mid-bay stations only | Any station / mid-bay | Nodal averaging with the unloaded rib reads two-thirds of the skin stress at rib stations |
| Redesign criteria: coursework load is limit, 1.5 ultimate; stress allowables at limit, no buckling or column failure at ultimate, 100 MPa as yield in Johnson | Coursework criteria only / limit-ultimate | The coursework had no buckling check, so a factor and a yield stress had to be chosen; 1.5 is the standard ultimate factor |
| Both covers stiffened identically | Symmetric / tension cover unstiffened | Neutral axis stays at mid-depth so the hand method stays simple, and a reversed load is covered; tapering and an asymmetric section are next steps |
| Ribs in the stiffened FE model as diaphragms rigid in plane, free out of plane (*EQUATION) | Shell ribs / rigid in-plane | No shell knots at blade roots, and it is the rib the hand method assumes; costs about 6 % extra stiffness through Poisson restraint |
| Fusion study loads applied by hand from a setup sheet | Script / by hand | The Simulation API in this Fusion build cannot reach a study from a script |
