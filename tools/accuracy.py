"""Accuracy table from real captures with tape-measured heights.

  accuracy.csv:  id,target,true_cm      (id = folder name in captures/)
  python -m tools.accuracy accuracy.csv  -> prints a markdown table (SAM results are cached, so re-runs are free)
"""
import csv, os, sys
import numpy as np
from poshan.analyze import measure

rows, errs = [], []
for r in csv.DictReader(open(sys.argv[1])):
    o = measure(os.path.join("captures", r["id"]))
    if "height_cm" not in o:
        rows.append(f"| {r['target']} | {r['true_cm']} | - | no height ({o['n_used']}/{o['n_frames']} frames) | - | - |")
        continue
    e = o["height_cm"] - float(r["true_cm"])
    errs.append(e)
    rows.append(f"| {r['target']} | {r['true_cm']} | {o['distance_m'][-1]:.2f} | {o['height_cm']:.1f} | {e:+.1f} | {'yes' if o['agreed'] else 'no'} |")
print("| Target | True height (cm) | Distance (m) | Phone (cm) | Error (cm) | Measurements agree |\n|---|---|---|---|---|---|")
print("\n".join(rows))
if errs:
    print(f"\nMedian |error| {np.median(np.abs(errs)):.1f} cm, mean error {np.mean(errs):+.1f} cm, n = {len(errs)}")
