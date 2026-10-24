# VT-01 Aero OML: decision log

| Decision | Options | Reason |
|---|---|---|
| Targets: 4.0 kg all-up, 2.0 m span, 18 m/s cruise, 11 m/s stall, n = 3.8 limit with a 1.5 factor | - | Build targets for a Roc Wing class VTOL |
| SD7062 aerofoil | SD7062, Clark Y, NACA 4412, E205, S4083, SD7037, E387 | Highest CLmax (1.56) and thickest (14 %), so it sets the stall speed and carries a 16 mm spar; costs about 23 % of cruise L/D against SD7037 |
| 2° linear washout outboard of the boom | 0, 1, 2, 3° | Span efficiency 0.984 against 0.987 at 1°, a difference inside the method's error; chosen for the stall progression |
| Straight inboard of y = 400 mm, taper 0.6 outboard | Constant chord, or taper over the whole span | Full chord where the boom and spar join; taper only where it buys induced drag |
