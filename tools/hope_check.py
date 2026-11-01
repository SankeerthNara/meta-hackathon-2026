"""Real-image check of the whole pipeline (live SAM 3.1 + Pluto) on a BOP HOPE onboarding sequence, which has
ground-truth camera poses and object distances. Writes it as a phone capture, runs poshan.analyze, compares
Pluto's tracked distance with the truth.

  python -m tools.hope_check D:/GraspBudget/data/hope/onboarding_static/obj_000001_up "can" [--every 3]
"""
import json, os, sys
import numpy as np
from PIL import Image
from poshan import analyze

D = np.diag([1.0, -1.0, -1.0])
src, prompt = sys.argv[1], sys.argv[2]
every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 3
cap = os.path.join("scratch", "hope_" + os.path.basename(src))
os.makedirs(cap, exist_ok=True)
cams, gts = json.load(open(os.path.join(src, "scene_camera.json"))), json.load(open(os.path.join(src, "scene_gt.json")))
frames, ztrue = [], {}
for k in sorted(cams, key=int)[::every][:60]:
    c = cams[k]
    s = 480 / c["width"]
    name = f"f{len(frames):03d}.jpg"
    if not os.path.exists(os.path.join(cap, name)):
        rgb = [f for f in os.listdir(os.path.join(src, "rgb")) if f.startswith(f"{int(k):06d}.")][0]
        Image.open(os.path.join(src, "rgb", rgb)).convert("RGB").resize((480, round(c["height"] * s))).save(os.path.join(cap, name), quality=90)
    R, t = np.array(c["cam_R_w2c"]).reshape(3, 3), np.array(c["cam_t_w2c"]) / 1000
    M = np.eye(4); M[:3, :3], M[:3, 3] = R.T @ D, -R.T @ t  # inverse of analyze.pose_cv
    K = c["cam_K"]
    frames.append(dict(file=name, w=480, h=round(c["height"] * s), K=[K[0] * s, K[4] * s, K[2] * s, K[5] * s],
                       view=list(M.T.ravel())))
    ztrue[name] = gts[k][0]["cam_t_m2c"][2] / 1000
json.dump(dict(prompt=prompt, frames=frames, child=dict(sex="girl", age_months=30)), open(os.path.join(cap, "meta.json"), "w"))
for f in frames:  # round trip of the pose convention
    R, t = analyze.pose_cv(f["view"])
assert np.allclose(R, np.array(cams[sorted(cams, key=int)[::every][len(frames) - 1]]["cam_R_w2c"]).reshape(3, 3))

out = analyze.measure(cap)
print({k: v for k, v in out.items() if not k.startswith("track")})
if "track_m" in out:
    zt = np.array([ztrue[n] for n in out["track_files"]])
    err = np.array(out["track_m"]) / zt - 1
    print(f"distance error over {len(err)} frames: median {100 * np.median(err):+.1f} %, median |err| {100 * np.median(abs(err)):.1f} %")
