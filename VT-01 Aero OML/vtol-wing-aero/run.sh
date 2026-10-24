#!/bin/bash
# Aerodynamic pipeline: sizing, aerofoil trade, vortex lattice, span loading, geometry. Outputs go to data/ and figures/.
# data/geom.json, data/spanload.json and data/af_unit.json are the inputs the structure model takes (copy them to its data/from_aero/).
set -e
cd "$(dirname "$0")/analysis"
python3 sizing.py
python3 airfoils.py
python3 vlm.py
python3 spanload.py
python3 geom.py
python3 cfd_ref.py
python3 figs_aero.py
mv *.json ../data/
rm -f spanload.png
