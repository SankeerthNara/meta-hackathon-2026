"""One capture -> SAM 3.1 masks -> Pluto height -> WHO z-scores -> Muse Spark report.

  python -m poshan.analyze captures/<id> [--no-report]
A capture folder holds meta.json (written by the phone page) and f000.jpg, f001.jpg, ...
"""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
from PIL import Image
from . import meta, samdecode, who
from .pluto import feret, mask_obs, pluto_sweep

D = np.diag([1.0, -1.0, -1.0])  # WebXR camera axes (x right, y up, looking down -z) -> OpenCV (y down, z forward)


def pose_cv(view):
    """WebXR view.transform.matrix (column-major camera-to-world) -> (R, t) world->camera in OpenCV axes."""
    M = np.array(view, float).reshape(4, 4).T
    Rwc, c = M[:3, :3], M[:3, 3]
    return D @ Rwc.T, -(D @ Rwc.T) @ c


def length_px(mask, R):
    """Child's length in the image: extent along world 'up' (ARCore gravity) when standing in front of the camera;
    Feret diameter when the phone looks down on a child lying flat (up then points along the optical axis)."""
    up = (R @ np.array([0.0, 1.0, 0.0]))[:2]  # world up (XR +y) in OpenCV camera axes, image-plane part
    if np.linalg.norm(up) < 0.7:
        return feret(mask)
    ys, xs = np.nonzero(mask)
    proj = np.c_[xs, ys] @ (up / np.linalg.norm(up))
    return float(proj.max() - proj.min()) + 1.0


def segment(cap, m):
    """SAM 3.1 on every frame, cached in sam/<frame>.txt."""
    os.makedirs(os.path.join(cap, "sam"), exist_ok=True)

    def one(f):
        path = os.path.join(cap, "sam", f["file"] + ".txt")
        if not os.path.exists(path):
            raw = meta.sam_raw(open(os.path.join(cap, f["file"]), "rb").read(), m["prompt"])
            open(path, "w").write(raw)
        return open(path).read()

    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(one, m["frames"]))


def decode_all(raws, frames):
    """Largest mask per frame. SAM masks decode in pure Python (~1 s each): spread over processes."""
    with ProcessPoolExecutor(min(8, os.cpu_count() or 1)) as ex:
        return list(ex.map(samdecode.masks, raws, [f["w"] for f in frames], [f["h"] for f in frames],
                           [True] * len(frames)))


def overlay(cap, f, mask, path):
    img = Image.open(os.path.join(cap, f["file"])).convert("RGB")
    a = np.asarray(img).copy()
    a[mask] = (0.45 * a[mask] + 0.55 * np.array([255, 120, 40])).astype(np.uint8)
    Image.fromarray(a).save(path)


def measure(cap):
    m = json.load(open(os.path.join(cap, "meta.json"), encoding="utf8"))
    raws = segment(cap, m)
    frames, lost = [], 0
    for f, ms in zip(m["frames"], decode_all(raws, m["frames"])):  # the child is the biggest match
        if not ms:
            lost += 1
            continue
        mk = ms[0]
        if mk[0].any() or mk[-1].any():
            lost += 1  # touches top/bottom edge: head or feet cut off, Feret is not the height
            continue
        fx, fy, cx, cy = f["K"]
        R, t = pose_cv(f["view"])
        frames.append(dict(R=R, t=t, K=[[fx, 0, cx], [0, fy, cy], [0, 0, 1]], obs=mask_obs(mk), fer=length_px(mk, R),
                           f=(fx + fy) / 2, file=f["file"], mask=mk))
    res = pluto_sweep(frames) if len(frames) >= 15 else None
    out = dict(n_frames=len(m["frames"]), n_used=len(frames), n_lost=lost, prompt=m["prompt"])
    if res:
        fbar = float(np.median([fr["f"] for fr in frames]))
        out.update(height_cm=100 * res["W"] / fbar, agreed=res["agreed"],
                   measurements_cm=[100 * w / fbar for w in res["Ws"]], distance_m=res["z"])
        # Pluto tracking: once W is known, distance in every frame from the mask alone
        out["track_m"] = [res["W"] / fr["fer"] for fr in frames]
        out["track_files"] = [fr["file"] for fr in frames]
    if frames:
        mid = frames[len(frames) // 2]
        overlay(cap, mid, mid["mask"], os.path.join(cap, "overlay.jpg"))
        out["qc_frame"] = mid["file"]
    return out


def run(cap, with_report=True):
    m = json.load(open(os.path.join(cap, "meta.json"), encoding="utf8"))
    out = measure(cap)
    child = m.get("child", {})
    if "height_cm" in out and child.get("age_months") is not None:
        age = float(child["age_months"])
        wt = float(child["weight_kg"]) if child.get("weight_kg") else None
        muac = float(child["muac_cm"]) if child.get("muac_cm") else None
        out["z"] = who.zscores(child["sex"], age, out["height_cm"], wt)
        out["category"] = who.classify(out["z"], muac, age)
    if with_report and "qc_frame" in out:
        jpg = open(os.path.join(cap, out["qc_frame"]), "rb").read()
        out["photo_check"] = meta.spark_json(meta.QC_SYSTEM, "Is this photo usable?", jpg)
    if with_report and "category" in out and not out["category"]["implausible"]:
        rec = dict(child={k: v for k, v in child.items() if k != "language"}, height_cm=round(out["height_cm"], 1),
                   height_measurements_cm=[round(x, 1) for x in out["measurements_cm"]],
                   measurements_agree=out["agreed"], who_z_scores={k: round(v, 2) for k, v in out["z"].items()},
                   who_categories=out["category"], photo_check=out.get("photo_check"))
        out["report"] = meta.report(rec, child.get("language", "Hindi"))
    json.dump(out, open(os.path.join(cap, "result.json"), "w", encoding="utf8"), indent=1, ensure_ascii=False)
    return out


if __name__ == "__main__":
    r = run(sys.argv[1], "--no-report" not in sys.argv)
    print(json.dumps({k: v for k, v in r.items() if not k.startswith("track")}, indent=1, ensure_ascii=False))
