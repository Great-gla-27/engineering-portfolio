"""Loads IATS_master_parameters.csv: every value the model, the checks and the drawing use,
with the file and line it came from and its status (source, resolved, derived or AC-01)."""
import csv, os


def load(path=None):
    path = path or os.path.join(os.path.dirname(__file__), 'IATS_master_parameters.csv')
    out = {}
    for r in csv.DictReader(open(path)):
        v = r['value']
        try: v = float(v)
        except ValueError: pass
        out[r['parameter']] = v
    return out
