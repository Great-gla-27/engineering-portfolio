# AC-01 Design Notes: IATS hydrogen-electric STOL aircraft

*Sizing and stability were my workstream on a six-person team project. This model is my own interpretation of the team's design.*

Fusion document: Engineering Portfolio / AC-01 IATS Aircraft. Repository: `iats-cad`.

## 1. Conventions

Origin at the nose tip. x aft, y to starboard, z up, z = 0 on the fuselage keel line. Lengths in m in the tables, mm on the drawing; masses in kg; angles in degrees. Static margin and CG positions are in % of the mean aerodynamic chord (MAC).

## 2. Parameters

| Parameter | Value | Unit | Note |
|---|---|---|---|
| MTOW | 7000 | kg | Maximum take-off mass |
| PayloadMass | 1380 | kg | Crew + passengers + cargo; C-5 (1250 kg in Table 2 rejected) |
| PaxMass | 100 | kg | Mass per passenger |
| PaxCount | 12 | - | Passengers |
| CrewMass | 160 | kg | Two flight crew |
| LH2FuelMass | 240 | kg | C-9 (130 kg in the mass statement superseded, as the report says) |
| XcgStated | 9.32 | m | Stated CG at MTOW, the value the model is checked against |
| XLH2Tank | 14.5 | m | LH2 tank centroid |
| WingSpan | 23.96 | m | C-1 (25.36 m on p5 rejected) |
| WingArea | 73.6 | m^2 | Reference area, trapezoidal planform to the centreline |
| AspectRatio | 7.8 | - | Check: b^2/S = 7.80 |
| TaperRatio | 0.5 | - | C-2 (0.6 in initial_sizing.m L28 is stale) |
| RootChord | 4.096 | m | Source rounds to 4.09 m (Calculations/IATS_Wing_Flap_Parameters.txt L24) |
| TipChord | 2.048 | m | Source rounds to 2.045 m (Calculations/IATS_Wing_Flap_Parameters.txt L25) |
| LESweep | 0.0 | deg | Unswept leading edge |
| Dihedral | -2.0 | deg | Anhedral |
| RootAerofoil | NACA 4412 | - |  |
| TipAerofoil | NACA 23012 | - |  |
| WingIncidence | 1.34 | deg | A-1: fuselage level in cruise |
| WingRootLEx | 8.5 | m | Unswept LE, so the MAC leading edge is at the same x |
| FlapInboard | 0.05 | semi-span | Single-slotted flap |
| FlapOutboard | 0.7 | semi-span |  |
| FlapChordRatio | 0.3 | - |  |
| SlatInboard | 0.0 | semi-span |  |
| SlatOutboard | 0.75 | semi-span |  |
| SlatChordRatio | 0.15 | - |  |
| AileronInboard | 0.7 | semi-span |  |
| AileronOutboard | 0.95 | semi-span |  |
| AileronChordRatio | 0.2 | - |  |
| HTArea | 6.7 | m^2 |  |
| HTSpan | 5.49 | m |  |
| HTRootChord | 1.81 | m |  |
| HTTipChord | 0.63 | m |  |
| HTTipLEOffset | 0.3 | m | Tip LE aft of root LE, as drawn in the team tail figure |
| VTArea | 13.14 | m^2 |  |
| VTHeight | 4.59 | m |  |
| VTRootChord | 4.25 | m |  |
| VTTipChord | 1.49 | m |  |
| VTTipLEOffset | 1.5 | m | Fin tip LE aft of root LE |
| TailAerofoil | NACA 0012 | - | A-2 |
| VH | 0.26 | - | C-4 (0.40 in tail_sizing.m L14, 0.62 in Project Bank rejected) |
| VV | 0.06 | - |  |
| TailArmAssumed | 8.67 | m | Statistical tail arm used by the tail sizing |
| LiftSlopeWing | 4.5 | /rad | Course-supplied |
| LiftSlopeTail | 3.0 | /rad | Course-supplied |
| NPWingBody | 0.25 | MAC | Wing-body neutral point |
| Downwash | 0.3 | - | d(epsilon)/d(alpha) |
| NPStated | 0.3713 | MAC |  |
| CGStated | 0.2699 | MAC |  |
| SMStated | 0.1015 | MAC |  |
| FuselageLength | 18.69 | m | C-3 (17.7 m in tail sizing is the concept-summary value) |
| CabinLength | 7.1 | m |  |
| SeatBlockLength | 5.75 | m | Length occupied by seats |
| XPax | 8.0 | m | Passenger centroid; sets the seat rows |
| XCrew | 1.5 | m |  |
| FuselageWidth | 2.2 | m | A-3 |
| FuselageDepth | 2.4 | m | A-3 |
| NoseLength | 3.0 | m | A-3: nose tip to start of constant section |
| TailConeStart | 10.7 | m | A-3: underside starts to rise |
| TailKinkX | 15.6 | m | A-3: gentle upsweep ends, steep upsweep begins |
| TailKinkBottom | 0.47 | m | A-3: underside height at the kink |
| TailKinkWidth | 1.8 | m | A-3 |
| TailEndBottom | 2.03 | m | A-3: underside height at the tail end |
| NoseTipZ | 0.58 | m | A-3 |
| CabinStartX | 4.4 | m | A-4 |
| PropDiameter | 3.0 | m |  |
| PropBlades | 5 | - | Tractor, wing-mounted |
| PropRPM | 1400 | rpm |  |
| BladeTwist02 | 38 | deg | Blade angle at 0.2 R |
| BladeTwist05 | 24 | deg | at 0.5 R |
| BladeTwist075 | 17 | deg | at 0.75 R |
| BladeTwist09 | 11 | deg | at 0.9 R |
| BladeAerofoils | NACA 4415 / 4412 / 0010 | - | Root / mid / tip |
| BladeRootChord | 0.22 | m | A-5 |
| BladeTipChord | 0.1 | m | A-5 |
| SpinnerRadius | 0.3 | m | A-5 |
| NacelleRadius | 0.45 | m | A-5 |
| NacelleDrop | 0.4 | m | A-5: nacelle axis below the local wing chord line |
| WingChordZ | 2.45 | m | A-3: root chord line height, wing sits on the fuselage crown |
| NacelleY | 4.5 | m | Nacelle centreline from the aircraft centreline |
| XMotor | 6.5 | m | EPU centroid |
| PropPlaneAheadOfMotor | 0.9 | m | A-5 |
| MotorMass | 412 | kg | C-9 (400 kg + 435 kg inverters in the mass statement superseded) |
| FuelCellMass | 800 | kg | C-9 (560 kg in the mass statement) |
| XFuelCell | 8.0 | m | Under the cabin floor (zcg 0.3) |
| BatteryMass | 567 | kg | C-9 (200 kg in the mass statement) |
| XBattery | 6.3 | m |  |
| LH2TankSystemMass | 686 | kg | C-9 |
| LH2Density | 70.8 | kg/m^3 | A-6 |
| TankUllage | 0.05 | - | A-6 |
| TankInsulation | 0.08 | m | A-6: wall + MLI thickness |
| XMainGear | 9.2 | m |  |
| MainGearY | 2.2 | m | Half track |
| KeelHeight | 0.6 | m | A-7: keel above ground, gear statically deflected |
| MainTyreDia | 0.65 | m | A-7 |
| XNoseGear | 2.0 | m | A-7 |
| NoseTyreDia | 0.45 | m | A-7 |
| MWing | 1210 | kg | xcg 8.5 |
| MFuselage | 1180 | kg | xcg 8.2 |
| MEmpennage | 300 | kg | xcg 16.6 |
| MPropulsion | 2465 | kg | xcg range 7.3 to 14.5 |
| MGear | 150 | kg | xcg 9.2 |
| MEquipment | 315 | kg | xcg 7.1 |

## 3. Conflicts, assumptions and decisions

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

## 4. MAC and static margin re-check

The team stability numbers (CG 26.99 %, neutral point 37.13 %, static margin 10.15 % MAC) are reproduced exactly by `initial_sizing.m` and `initial_tail_sizing.m` with b = 23.7 m and c̄ = b/AR = 3.038 m. That chord is the mean geometric chord of an older wing, not the MAC of the final one.

| | c̄ (m) | CG (% MAC) | NP (% MAC) | Static margin |
|---|---|---|---|---|
| As reported (b/AR, old span) | 3.038 | 26.99 % | 37.13 % | 10.15 % |
| True MAC, tail area and arm as built (V_H falls to 0.248) | 3.186 | 25.74 % | 36.56 % | 10.82 % |
| True MAC, V_H held at 0.26 (tail resized) | 3.186 | 25.74 % | 37.13 % | 11.39 % |

MAC = (2/3) c_r (1 + λ + λ²) / (1 + λ) = 3.186 m for c_r = 4.096 m and λ = 0.5, at y = 5.324 m from the centreline. The mean geometric chord is 3.072 m.

**Result:** 10.15 % does not hold. With the right MAC, the CG moves forward in MAC terms and the margin goes up, to 10.82 % with the tail as built. The error is on the safe side, but it is an error, and the CAD model is what found it.

## 5. CG

**The stated 9.32 m cannot be reproduced from the report's own numbers.** Report Table 3 gives every group at a station except propulsion (2,465 kg, "7.3 to 14.5 m"). With propulsion split per Table 10 and placed at the mass-statement stations, Table 3 sums to x = 8.885 m. To give 9.32 m, the propulsion group would have to sit at 10.40 m, against 9.17 m from its parts. The detailed mass statement rows (6816 kg) give 9.080 m.

Fuel-burn CG shift, burning 240 kg from the tank at 14.5 m with the CG at 9.32 m: 0.184 m forward exactly, 0.178 m by the report's formula (which divides by MTOW rather than the landing mass).

## 6. Checks measured off the model

Measured off the Fusion model (wing end-section leading and trailing edge points, body volumes and centroids, propeller blade mesh, fuselage surface mesh) and reduced by `analysis/design_checks.py`.

### 6.1 Planform (criterion: within 0.5 % of the master table)

| | Model | Analytic | Error |
|---|---|---|---|
| Span (m) | 23.9600 | 23.9600 | +0.000 % |
| Area (m²) | 73.6000 | 73.6000 | +0.000 % |
| Aspect ratio | 7.8000 | 7.8000 | -0.000 % |
| MAC (m) | 3.1856 | 3.1856 | +0.000 % |
| Root / tip chord (m) | 4.0957 / 2.0479 | 4.0957 / 2.0479 | -0.000 / +0.000 % |

MAC leading edge at x = 8.5002 m, y = ±5.324 m; aerodynamic centre at x = 9.2966 m. Tailplane area measured 6.698 m² (Table 5: 6.70 m²).

### 6.2 Propeller clearance

The report certifies to CS-23 Amendment 5, which is performance based and gives no clearance figure. The check uses the prescriptive rule it replaced, 14 CFR 23.925 (7 in to the ground with the nose wheel on the ground, 1 in radial to the airframe). This is a benchmark, not a certification finding.

| Propeller | Tip radius (m) | To ground (m) | To fuselage (m) |
|---|---|---|---|
| Propeller:1 | 1.5018 | 0.991 | 1.956 |
| Propeller:2 | 1.5018 | 0.991 | 1.956 |

### 6.3 Ground angles

Tail-strike angle about the main wheel contact point: 9.14°.

| Tip-back angle over the main gear (guideline 15°, Raymer) | Angle |
|---|---|
| Model CG, MTOW | 5.2° |
| Model CG, fuel burnt | 10.7° |
| Stated CG (9.32 m) | -3.5° |

Main gear station that would give 15° with the model CG: x = 9.55 m (built at 9.20 m; see C-11).

### 6.4 CG and stability from the model

| Mass item | Mass (kg) | x (m) | z (m) |
|---|---|---|---|
| Wing structure and controls | 1210 | 9.876 | 2.360 |
| Fuselage structure (skin centroid) | 885 | 8.775 | 1.269 |
| Seats | 140 | 8.037 | 0.771 |
| Internal accommodation (floor) | 155 | 7.950 | 0.410 |
| Horizontal tail | 185 | 16.469 | 6.990 |
| Vertical tail | 115 | 16.324 | 3.772 |
| EPUs (2) | 412 | 6.500 | 1.893 |
| Fuel cell modules (8) | 800 | 8.000 | 0.270 |
| Battery buffer pack | 567 | 6.300 | 0.270 |
| LH2 tank system incl. fuel | 686 | 14.500 | 1.382 |
| Main landing gear | 130 | 9.282 | 0.287 |
| Nose landing gear | 20 | 2.000 | -0.277 |
| Equipment (Table 3 station, no body) | 315 | 7.100 | 1.000 |
| Passengers (12 x 100 kg) | 1200 | 8.087 | 1.021 |
| Crew (2) | 160 | 1.587 | 1.021 |
| Cargo (balance of 1,380 kg) | 20 | 4.750 | 1.020 |
| **Total** | **7000** | **9.019** | **1.390** |

Fuel-burn shift from the model: 0.195 m forward.

Tail arm measured between the wing and tailplane aerodynamic centres: 6.938 m. The tail sizing assumed 8.67 m (0.49 x 17.7 m).

| CG used, tail arm used | V_H | NP (% MAC) | CG (% MAC) | Static margin |
|---|---|---|---|---|
| Stated 9.32 m, assumed 8.67 m arm | 0.248 | 36.56 % | 25.73 % | 10.83 % |
| Stated 9.32 m, measured arm | 0.198 | 34.25 % | 25.73 % | 8.51 % |
| Table 3 re-added, measured arm | 0.198 | 34.25 % | 12.08 % | 22.17 % |
| Model CG, measured arm | 0.198 | 34.25 % | 16.27 % | 17.98 % |

### 6.5 What the measurement changes

The tail sizing assumed a tail arm of 8.67 m, a statistical 0.49 x 17.7 m. The arm measured between the wing and tailplane aerodynamic centres on the model is 6.938 m, 20 % shorter, because the wing sits at mid-fuselage and the tailplane, centred on the fin tip chord, has its aerodynamic centre 2.45 m ahead of the tail end. With the 6.70 m² tail at that arm, V_H falls from 0.248 to 0.198 and the neutral point moves forward from 36.56 % to 34.25 % MAC.

Two errors in the team numbers act in opposite directions. Correcting the chord (section 4) raises the margin at the stated CG to 10.83 %; correcting the tail arm then lowers it to 8.51 %. That is still inside the 5 to 15 % target band, but below the 10.15 % quoted, and it is reached only by fixing both.

With the CG the geometry itself implies, 9.019 m, the margin is 17.98 %, outside the band on the stable side. Which CG is right is the question to settle first, because the report's own Table 3 does not reproduce the stated value (section 5).

On the ground the model CG gives a tip-back angle of 5.2 degrees over the main gear at 9.2 m, against a 15 degree guideline. The main gear would need to move aft to about 9.55 m. That is consistent with C-11: the 9.2 m in the mass statement is more plausibly the centroid of all the gear than the main gear station.

### 6.6 Containment

A containment check reports the two crew seats extending 0.14 litres outside the fuselage skin at the nose. It is a modelling nicety rather than a design issue, and is left as found.

## 7. Limitations

- The fuselage cross-section, nose and tail-cone shape are scaled from a raster three-view (about ±5 %). There is no plan view, so the tail-cone width is chosen.
- Masses are the report's group masses placed at CAD centroids. No structural layout, no material densities.
- The neutral point uses the course-supplied lift slopes and downwash gradient from the team scripts, not values for this wing and tail.
- No rear cargo door is modelled (C-10).
- Propeller clearances are checked against the superseded prescriptive FAR rule, because CS-23 Amendment 5 gives no number.
- The model is a general arrangement, not a production design: no structure, no systems routing.
- The lift slopes, downwash gradient and wing-body neutral point are the course-supplied values in the team scripts. The measured tail arm changes V_H, but those three are not re-derived.
