# AC-01 configuration control: conflicts and assumptions

Every value used by the model is in `params/IATS_master_parameters.csv`, with its source. This file records each place where the sources disagree (C-n) and each value the team work never defined (A-n). Paths are relative to `University/3rd Year/Semester 2/Aircraft Design/`.

Each decision is a single row in the master table, so changing one means changing that row.

## Conflicts between sources

| ID | Quantity | Values found | Chosen | Reason |
|---|---|---|---|---|
| C-1 | Wing span | 23.96 m (`Calculations/IATS_Wing_Flap_Parameters.txt` L20; report p11); 25.36 m (report p5, Fig 2); 23.7 m (`initial_sizing.m` L26) | **23.96 m** | It is the only span consistent with S = 73.6 m² and AR = 7.8 (23.96² / 73.6 = 7.80). The 25.36 m is a dimension on the team three-view and no calculation produces it. The 23.7 m came from the "High Mark Example Report" and is stale. |
| C-2 | Taper ratio | 0.50 (wing summary L23; report p11); 0.6 (`initial_sizing.m` L28) | **0.50** | It is the final value from the Oswald efficiency study (report Fig 8). `initial_sizing.m` predates it. |
| C-3 | Fuselage length | 18.69 m (report p5, Fig 2); 17.7 m (`initial_tail_sizing.m` L38, `tail_sizing.m` L19, from the concept summary) | **18.69 m** | It is the latest value. The 17.7 m only fed the statistical tail arm (0.49 × 17.7 = 8.67 m). The model measures the real tail arm instead (see the check results). |
| C-4 | Horizontal tail volume ratio | 0.26 (`tail_design_summary.txt` L10; report Table 5); 0.40 (`tail_sizing.m` L14); 0.62 (Project Bank, from a presentation slide) | **0.26** | It is the value behind S_T = 6.70 m² and the stated neutral point. The report itself says (p16) that the 0.62 was a typo. **The Project Bank entry needs correcting.** |
| C-5 | Payload | 1,250 kg "useful load" (report Table 2, p6); 1,380 kg (report Table 3, p7) | **1,380 kg** | Table 3 is the table that sums to the 7,000 kg MTOW and sets the CG. Table 2 is an early estimate the report never reconciled. |
| C-6 | MAC | c̄ = b/AR = 3.04 m (`initial_sizing.m` L33, with b = 23.7 m) | **3.186 m** (true MAC) | b/AR is the mean geometric chord, not the MAC. For λ = 0.5 the MAC is 3.7 % longer. See the static margin re-check. |
| C-7 | Stated CG at MTOW | 9.32 m (report Table 3 and the mass statement totals row) | **checked, not used to place anything** | Neither mass table reproduces it (see below). The model computes its own CG and reports it against 9.32 m. |
| C-8 | Cargo position | Forward of the cabin (report p8 and floorplan Fig 4); 400 kg at x = 12.5 m, aft (mass statement row 7.4 to 7.6) | **Forward cargo bay, 20 kg** | Table 3's payload of 1,380 kg is 12 × 100 kg passengers plus 160 kg crew, which leaves 20 kg. The 400 kg aft luggage in the detailed mass statement belongs to the earlier mass set (see C-9). |
| C-9 | Propulsion masses | Detailed mass statement: EPUs 400 kg, fuel cells 560 kg, inverters 435 kg, battery 200 kg, LH2 130 kg + tank 480 kg. Report Table 10: EPUs 412 kg (with inverters), fuel cells 800 kg, battery 567 kg, LH2 system 686 kg with 240 kg fuel | **Report Table 10** | The report states (s3.3) that Table 10 supersedes the preliminary mass statement. The positions still come from the mass statement, because Table 10 gives none. |
| C-11 | Main gear station | One landing gear row in the mass statement (row 5.1): 150 kg at x = 9.2 m, y = 2.2 m, labelled "Tyres & Struts", and the same 9.2 m in report Table 3. No separate nose gear row anywhere | **Main gear at 9.2 m, the team's value (as built)** | Read as the main gear station, the stated CG (9.32 m) is 0.12 m aft of the main wheels, so the aircraft would sit on its tail. Read as the centroid of all the gear, with a 20 kg nose gear at 2.0 m, the main gear would be at (150 x 9.2 - 20 x 2.0) / 130 = 10.3 m, which gives a normal tip-back angle. Kept at the team's value so the model checks the team design rather than fixing it; the tip-back check therefore fails (section 6). Moving it is one parameter (XMainGear). |
| C-10 | Rear cargo access | Considered for the model | **Not modelled** | No team source shows a rear door, and the LH2 tank occupies the tail cone from 13.2 to 15.8 m. A rear ramp is incompatible with that tank position. |

## Values the team work never defined

| ID | Values | Basis |
|---|---|---|
| A-1 | Wing incidence 1.34° | The XFLR5 wing angle of attack at the cruise CL of 0.373 (wing summary L45), so the cabin floor is level in cruise. |
| A-2 | Tail sections NACA 0012 | The only symmetric section in the team's polar files. |
| A-3 | Fuselage width 2.20 m, depth 2.40 m, nose and tail-cone stations, wing chord-line height 2.45 m | Scaled from the team three-view (report p5, Fig 2), about ±5 % from a 220 dpi raster. There is no plan view, so the tail-cone width at the kink (1.80 m) is chosen. |
| A-4 | Cabin from 4.4 to 11.5 m. Seats 2+1 in five rows at 1.2 m pitch: ten on the left, singles on the right in rows 1 and 5 | The rows are centred on the mass statement passenger station (8.0 m). They span about the 5.75 m seat block (report p8) and give 12 seats, as in the floorplan (Fig 4). |
| A-5 | Propeller plane 0.9 m ahead of the EPU centroid. Blade chord 0.22 m tapering to 0.10 m. Spinner radius 0.30 m. Nacelle radius 0.45 m, axis 0.40 m below the local wing chord line | The report gives the disc diameter, blade count, twist and blade sections, but not these. |
| A-6 | LH2 density 70.8 kg/m³, 5 % ullage, 80 mm wall and insulation, outer radius 0.85 m | Standard normal-boiling-point density for LH2. The radius is the largest tank that clears the tail cone at 14.5 m. The cylinder length comes from the 240 kg fuel load. |
| A-7 | Keel 0.60 m above the ground, main tyre diameter 0.65 m, nose gear at 2.0 m, nose tyre diameter 0.45 m | The team gives only one gear station (9.2 m) and half-track (2.2 m), from mass statement row 5.1 (see C-11). |
| A-8 | Gear mass split 130 kg main, 20 kg nose | The team gives only the 150 kg total. The split is an assumption; compared with putting all 150 kg at 9.2 m it moves the model CG 20 mm forward (20 kg x 7.2 m / 7000 kg). |
| A-9 | Occupant CG 0.05 m ahead of and 0.25 m above the centroid of the seat body | A seated person's mass sits on the cushion and against the back, not at the centroid of the seat shape. |

## Decision log

| Decision | Options | Reason |
|---|---|---|
| C-1 to C-10 and A-1 to A-7 as above | As listed in each row | As listed in each row |
| Place the wing from the team's MAC leading-edge station (8.5 m), not from the stated CG | Place the wing to give 10 % static margin / keep the team station | The aim is to check the team's numbers, not to re-design the aircraft to make them come out right |
| CG computed two ways: (A) the report's Table 3 masses at their stated stations; (B) the same masses at the centroids of the CAD bodies | One / both | (A) shows whether the report is self-consistent. (B) shows what the geometry implies. |
| Fuselage modelled as a solid outer mould line. The skin centroid is taken from its surface faces | Shell the solid / surface centroid | Shelling failed at the nose point; the area-weighted face centroid is the centroid of a uniform skin |
| Propeller clearances checked against 14 CFR 23.925 (7 in ground, 1 in radial to structure) | CS-23 Amdt 5 (performance based, no figure) / the prescriptive FAR text | The report certifies to CS-23 Amdt 5, which no longer gives a number. The superseded prescriptive rule is the usual benchmark. |
| Drawing text no smaller than 1.8 mm capital height; centre lines on the plan and front views | Keep the first layout, or meet BS EN ISO 3098 and BS ISO 128-20 | The first pass failed both on the checklist |
