# Fusion static study: setup sheet

Document: **WB-01 Wing Box** (Engineering Portfolio). Study: a Static Stress study, already created. Rename it **WB-01 Static, t = 3.8 mm** in the browser.

The Simulation API in this Fusion build cannot reach a study from a script, so the study is set up by hand. It takes about 20 minutes. Everything below comes from `hand_calc/fusion_strip_forces.py`.

## Axes and geometry

The design axes match the hand calculation. x is chordwise from the leading edge, y is up, and z runs spanwise from the root (z = 0) to the tip (z = 10,000 mm). The body is the single solid **Wing Box**, with walls offset 1.9 mm either side of the 1.2 x 0.2 m midline. The **Load strips** feature splits each web face into 20 strips, 500 mm long.

## 1. Material

Make a custom material (Manage Materials, then copy a generic metal):

| Property | Value |
|---|---|
| Name | ENG3081 Box |
| Young's modulus | 110 GPa |
| Poisson's ratio | 0.33 |
| Density | 4000 kg/m3 |
| Yield strength | 100 MPa |

Assign it to Wing Box under Study Materials.

## 2. Constraint

Add a **Fixed** constraint on the root end face (z = 0), with all three directions fixed. This matches the CalculiX models.

## 3. Gravity

Leave gravity **off**. The self-weight is already folded into the strip forces below, half to each web, because it acts at the shear centre.

## 4. Loads

Add 40 **Force** loads, one on each web strip face, in the **+Y** direction (Direction: vector, Y = 1). On the outer face of each web strip, the front web is at x = 200 mm and the rear web at x = 1400 mm. Name each one by web and strip, for example "Front web strip 01".

| Strip | z (mm) | Front web (N) | Rear web (N) |
|---|---|---|---|
| 1 | 0-500 | 1353.3 | 187.2 |
| 2 | 500-1000 | 1349.7 | 186.4 |
| 3 | 1000-1500 | 1342.4 | 185.0 |
| 4 | 1500-2000 | 1331.3 | 182.8 |
| 5 | 2000-2500 | 1316.4 | 179.8 |
| 6 | 2500-3000 | 1297.6 | 176.0 |
| 7 | 3000-3500 | 1274.6 | 171.4 |
| 8 | 3500-4000 | 1247.3 | 166.0 |
| 9 | 4000-4500 | 1215.5 | 159.6 |
| 10 | 4500-5000 | 1178.7 | 152.2 |
| 11 | 5000-5500 | 1136.6 | 143.8 |
| 12 | 5500-6000 | 1088.5 | 134.2 |
| 13 | 6000-6500 | 1033.7 | 123.2 |
| 14 | 6500-7000 | 971.2 | 110.7 |
| 15 | 7000-7500 | 899.6 | 96.4 |
| 16 | 7500-8000 | 816.6 | 79.8 |
| 17 | 8000-8500 | 718.9 | 60.3 |
| 18 | 8500-9000 | 600.3 | 36.6 |
| 19 | 9000-9500 | 446.9 | 5.9 |
| 20 | 9500-10000 | 200.7 | -43.4 |

The total is 23,313.8 N, equal to the root shear: the lift of 27,488.9 N less the 4,175 N self-weight. The 5/6 to 1/6 split of the lift puts its resultant on the 0.4 m centre of pressure line, so the root torque is right as well. Strip 20's rear force is negative because there the strip's self-weight is more than its share of the lift.

## 5. Mesh

| Setting | Value |
|---|---|
| Element order | Parabolic |
| Size | Absolute, 25 mm |
| Curvature refinement | Off (flat walls only) |
| Local mesh control | 10 mm on the root face and the first strip of each web |

With 25 mm elements there is one parabolic tetrahedron through each wall. That is fine for membrane stress, which governs here, but it is not a converged bending answer. Re-run once at 15 mm and quote the change between the two meshes.

## 6. Solve and read off

Solve locally (Solve, then On Cloud unticked). Local solve uses no cloud credits.

Read these values with the probe tool. Upper cover, at mid-chord (x = 800 mm, outer face):

| z (m) | Hand (MPa) | CalculiX S8R shells, no ribs (MPa) |
|---|---|---|
| 0.5 | 87.8 | 87.6 |
| 1.0 | 76.9 | 78.2 |
| 2.0 | 57.5 | 57.9 |
| 5.0 | 17.5 | 17.8 |

Tip, mean vertical displacement of the two webs: hand 201.8 mm, CalculiX 204.2 mm (shells) and 204.1 mm (solids).

Tip twist will **not** match the hand value. The Fusion box has no ribs, so the section distorts. The hand value is 0.21 deg; CalculiX without ribs gives 1.38 deg (shells) and 1.13 deg (solids). That is a finding about the model, not an error in Fusion. Phase 3 of the report covers it.

Read normal stress in z (Stress, then Normal ZZ), not von Mises, to compare with the hand bending stress. At the root the corners carry a stress concentration that grows with mesh refinement. Ignore the first 200 mm when comparing.

## 7. Save

Save with the description "Static study set up: root fixed, 40 web strip forces, ENG3081 material, 25 mm parabolic mesh". Put a screenshot of the ZZ stress plot in `figures/fig5_fusion_static.png`, then add a Fusion column to Table 2 of the report.
