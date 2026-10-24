#!/bin/bash
# Structure pipeline. Inputs come from the aerodynamic model (data/from_aero/); outputs go to data/ and figures/.
set -e
cd "$(dirname "$0")/analysis"
cp ../data/from_aero/*.json .
python3 ribdata.py      # rib loads from the span loading, lightening holes
python3 beam.py         # Euler-Bernoulli beam FE: flight, hover, modal
python3 beam3.py        # prediction for the three-load Fusion FEA case, written before the solve
python3 figs_structure.py
mv ribdata.json beam.json ../data/
rm -f geom.json spanload.json af_unit.json
