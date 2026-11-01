"""WHO Child Growth Standards (2006) z-scores and screening categories. Deterministic: the LLM never does this maths.

Tables (LMS, data/who/*.json) are the WHO expanded tables as packaged by pygrowup.
"""
import json, os
import numpy as np

_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "who")
_cache = {}


def _table(name):
    if name not in _cache:
        rows = json.load(open(os.path.join(_DIR, name + ".json")))
        key = "Month" if "Month" in rows[0] else ("Height" if "Height" in rows[0] else "Length")
        _cache[name] = np.array([[float(r[key]), float(r["L"]), float(r["M"]), float(r["S"])] for r in rows])
    return _cache[name]


def _lms(name, x, rows=slice(None)):
    t = _table(name)[rows]
    if not t[0, 0] <= x <= t[-1, 0]:
        return None
    return [float(np.interp(x, t[:, 0], t[:, i])) for i in (1, 2, 3)]


def _z(y, L, M, S):
    """LMS z-score with WHO's restricted tails beyond +-3 SD (matters for weight; height has L = 1, linear)."""
    z = ((y / M) ** L - 1) / (L * S)
    sd = lambda k: M * (1 + L * S * k) ** (1 / L)
    if z > 3:
        z = 3 + (y - sd(3)) / (sd(3) - sd(2))
    elif z < -3:
        z = -3 + (y - sd(-3)) / (sd(-2) - sd(-3))
    return float(z)


def zscores(sex, age_months, height_cm, weight_kg=None):
    """sex 'boy'/'girl'. Height-for-age (0-60 months) and, with a weight, weight-for-length (< 24 months) or
    weight-for-height (24-60 months). -> dict of z-scores (missing ones absent)."""
    s = {"boy": "boys", "girl": "girls"}[sex]
    out = {}
    # month 24 is listed twice: length (lying, < 24 months) then height (standing, 24-60 months)
    p = _lms(f"lhfa_{s}_0_5", age_months, slice(25, None) if age_months >= 24 else slice(0, 25))
    if p:
        out["haz"] = _z(height_cm, *p)
    if weight_kg:
        p = _lms(f"wfl_{s}_0_2", height_cm) if age_months < 24 else _lms(f"wfh_{s}_2_5", height_cm)
        if p:
            out["whz"] = _z(weight_kg, *p)
    return out


def classify(z, muac_cm=None, age_months=None):
    """WHO cut-offs. -> dict(stunting, wasting, muac, refer)."""
    band = lambda v, sev, mod: None if v is None else ("severe" if v < sev else "moderate" if v < mod else "normal")
    c = dict(stunting=band(z.get("haz"), -3, -2), wasting=band(z.get("whz"), -3, -2),
             muac=band(muac_cm, 11.5, 12.5) if muac_cm and age_months and 6 <= age_months < 60 else None)
    c["refer"] = "severe" in c.values()  # SAM (WHZ < -3 or MUAC < 11.5 cm) or severe stunting: refer
    return c


if __name__ == "__main__":
    # self-check against the tables' own SD columns
    rows = json.load(open(os.path.join(_DIR, "lhfa_boys_0_5.json")))
    r = rows[25]  # month 24, standing height row
    assert abs(zscores("boy", 24, float(r["SD0"]))["haz"]) < 0.05
    assert abs(zscores("boy", 24, float(r["SD2neg"]))["haz"] + 2) < 0.05
    rows = json.load(open(os.path.join(_DIR, "wfh_girls_2_5.json")))
    r = next(x for x in rows if float(x["Height"]) == 85.0)
    assert abs(zscores("girl", 30, 85.0, float(r["SD3neg"]))["whz"] + 3) < 0.06
    assert abs(zscores("girl", 30, 85.0, float(r["SD0"]))["whz"]) < 0.05
    c = classify(zscores("girl", 30, 85.0, float(r["SD3neg"]) - 0.3), muac_cm=12.0, age_months=30)
    assert c["wasting"] == "severe" and c["muac"] == "moderate" and c["refer"], c
    print("who self-checks OK")
