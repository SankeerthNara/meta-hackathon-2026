"""End-to-end without the API: a synthetic WebXR capture of a 90 cm 'child' 1.5 m away, SAM replaced by the true
silhouette. Checks pose/intrinsics conventions, mask selection, Pluto and WHO glue.  python -m tests.test_offline"""
import json, os, shutil, tempfile
import numpy as np
from PIL import Image
from poshan import analyze, meta
from poshan.pluto import rot

W, Hpx, F, HEIGHT = 480, 1040, 520.0, 0.90
cap = tempfile.mkdtemp()
rng = np.random.default_rng(1)
frames, sil = [], {}
for i in range(60):
    c = np.array([0.12 * np.sin(i / 59 * 2 * np.pi), 1.0, 0.0])  # XR world: y up, child stands on the floor at z = -1.5
    Rwc = rot(*np.deg2rad(rng.normal(0, 1.0, 3)))
    M = np.eye(4); M[:3, :3], M[:3, 3] = Rwc, c
    # projection matrix entries for K = (F, F, W/2 + 7, Hpx/2 - 11)
    cx, cy = W / 2 + 7, Hpx / 2 - 11
    p0, p5, p8, p9 = 2 * F / W, 2 * F / Hpx, 1 - 2 * cx / W, 2 * cy / Hpx - 1
    # silhouette: points of a 0.9 m x 0.25 m body, projected with OpenCV conventions
    R, t = analyze.pose_cv(M.T.ravel())
    ys, xs = np.mgrid[0:HEIGHT:0.004, -0.12:0.12:0.004]
    P = np.c_[xs.ravel(), ys.ravel(), np.full(xs.size, -1.5)]
    Xc = P @ R.T + t
    u, v = F * Xc[:, 0] / Xc[:, 2] + cx, F * Xc[:, 1] / Xc[:, 2] + cy
    m = np.zeros((Hpx, W), bool)
    m[np.clip(v.astype(int), 0, Hpx - 1), np.clip(u.astype(int), 0, W - 1)] = True
    name = f"f{i:03d}.jpg"
    sil[name] = m
    Image.fromarray((m * 200).astype(np.uint8)).convert("RGB").save(os.path.join(cap, name))
    pr = [0] * 16; pr[0], pr[5], pr[8], pr[9] = p0, p5, p8, p9
    K = [pr[0] * W / 2, pr[5] * Hpx / 2, (1 - pr[8]) * W / 2, (1 + pr[9]) * Hpx / 2]  # same formula as capture.html
    frames.append(dict(file=name, w=W, h=Hpx, K=K, view=list(M.T.ravel())))
json.dump(dict(prompt="child", frames=frames, child=dict(sex="girl", age_months=30, weight_kg=11.0)),
          open(os.path.join(cap, "meta.json"), "w"))

meta.sam_raw = lambda jpeg, prompt: "x"
names = iter(f["file"] for f in frames)
meta.masks = lambda raw, w, h: [sil[next(names)], np.zeros((h, w), bool)]  # true child + an empty decoy
try:
    out = analyze.run(cap, with_report=False)
    assert abs(out["height_cm"] - 100 * HEIGHT) < 3, out
    assert out["category"]["stunting"] == "normal" and "whz" in out["z"], out
    print("offline end-to-end OK:", round(out["height_cm"], 1), "cm", out["z"], out["category"])
finally:
    shutil.rmtree(cap)
