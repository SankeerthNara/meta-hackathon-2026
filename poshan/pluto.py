"""Pluto: real size of an unknown object from a small camera move, then distance from its mask alone.

Copied from GraspBudget tag `pluto-v1` (tools/motion_stereo.py `solve`, tools/pipeline3_bench.py `measurements`,
`consensus`, `pluto`), unchanged except: the depth-network vote is dropped (no DA3 on a phone) and frames carry the
mask's Feret diameter as `fer`.

Each view (R, t world->camera in metres, OpenCV axes) gives linear equations in the object point P and W = s * z;
W = Feret px * distance is the object's size constant, so its real length is W / f and its distance in any later
frame is z = W / Feret px.
"""
import numpy as np

N_ENROL = 5  # motion windows per measurement (median of them)


def solve(views, K, px=1.0, rel=0.02, use_centroid=True, use_size=True):
    """views: list of (R 3x3, t 3 [m], (u, v) mask centroid px, s = sqrt(mask area) px), R, t world->camera.
    px: centroid noise (px); rel: relative noise of s. Returns dict(P, W, z (depth in the last view, m),
    sigma_z, chi2) or None if the motion does not constrain the depth."""
    fx, fy, cx, cy = K[0][0], K[1][1], K[0][2], K[1][2]
    rows, rhs, kind = [], [], []
    for R, t, (u, v), s in views:
        R, t = np.asarray(R, float), np.asarray(t, float)
        x, y = (u - cx) / fx, (v - cy) / fy
        if use_centroid:
            rows += [np.r_[R[0] - x * R[2], 0], np.r_[R[1] - y * R[2], 0]]
            rhs += [x * t[2] - t[0], y * t[2] - t[1]]
            kind += [fx, fy]
        if use_size:
            rows.append(np.r_[s * R[2], -1])
            rhs.append(-s * t[2])
            kind.append(-s)  # negative = size row, value = s
    A, b = np.array(rows), np.array(rhs)
    if not use_size:
        A = A[:, :3]  # W is unobservable from centroids alone
    zs = np.ones(len(views))
    for _ in range(2):  # pass 1 unweighted-ish (z = 1), pass 2 with the depths it found
        zr = np.repeat(zs, len(rows) // len(views))
        k = np.array(kind)
        wt = np.where(k > 0, k / (zr * px), 1 / (zr * rel * np.abs(k)))
        Aw, bw = A * wt[:, None], b * wt
        N = Aw.T @ Aw
        if np.linalg.cond(N) > 1e12:
            return None
        th = np.linalg.solve(N, Aw.T @ bw)
        zs = np.array([np.asarray(R, float)[2] @ th[:3] + np.asarray(t, float)[2] for R, t, _, _ in views])
        if (zs <= 0).any():
            return None
    r = Aw @ th - bw
    dof = max(len(r) - A.shape[1], 1)
    chi2 = float(r @ r / dof)
    cov = np.linalg.inv(N) * max(chi2, 1.0)  # inflate when the data are noisier than assumed
    R, t = np.asarray(views[-1][0], float), np.asarray(views[-1][1], float)
    g = np.r_[R[2], 0][: A.shape[1]]
    return dict(P=th[:3], W=float(th[3]) if use_size else float("nan"), z=float(R[2] @ th[:3] + t[2]),
                sigma_z=float(np.sqrt(g @ cov @ g)), chi2=chi2)


def mask_obs(mask):
    """(centroid (u, v), sqrt area) of a binary mask, or None if empty."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return (xs.mean(), ys.mean()), float(np.sqrt(len(xs)))


def feret(mask):
    """Largest distance between two mask pixels (px): for a standing child, head to heel."""
    ys, xs = np.nonzero(mask)
    pts = np.c_[xs, ys].astype(float)
    # shortcut: max over 180 projection directions (error < 0.02 %), not an exact rotating-calipers hull
    a = np.linspace(0, np.pi, 180, endpoint=False)
    proj = pts @ np.c_[np.cos(a), np.sin(a)].T
    return float((proj.max(0) - proj.min(0)).max()) + 1.0  # +1: pixel extent, not centre-to-centre


def measurements(frames, base, n_meas=3):
    """Consecutive, non-overlapping size measurements: each is the median W over N_ENROL motion windows; the next
    measurement only uses windows that start after the previous one ended. -> list of (end index, W, median z, idx)."""
    centre = [-f["R"].T @ f["t"] for f in frames]
    out, cur, start = [], [], 0
    for j in range(1, len(frames)):
        cands = [i for i in range(start, j) if abs(np.linalg.norm(centre[i] - centre[j]) - base) < 0.25 * base]
        if not cands:
            continue
        r = solve([(frames[k]["R"], frames[k]["t"], *frames[k]["obs"]) for k in range(cands[-1], j + 1)], frames[j]["K"])
        if not r or r["z"] <= 0:
            continue
        cur.append((j, r["z"]))
        if len(cur) == N_ENROL:
            out.append((j, float(np.median([frames[jj]["fer"] * z for jj, z in cur])), float(np.median([z for _, z in cur])),
                        [jj for jj, _ in cur]))
            cur, start = [], j + 1
            if len(out) == n_meas:
                break
    return out


def consensus(cands, tol):
    """cands: list of (W, is_motion). The value most others agree with (relative difference <= tol): median of it and
    its supporters. Ties prefer motion measurements, then later ones. -> (W, agreed?)"""
    best = None
    for i, (w, mot) in enumerate(cands):
        sup = [x for x, _ in cands if abs(x - w) / w <= tol]
        score = (len(sup), mot, i)
        if best is None or score > best[0]:
            best = (score, float(np.median(sup)))
    if best[0][0] >= 2:
        return best[1], True
    return float(np.median([w for w, m in cands if m])), False  # nobody agrees: low confidence


def pluto(frames, base=0.10, tol=0.05):
    """Two measurements; if they disagree by more than tol, a third and a 2-of-3 vote.
    -> dict(W, agreed, Ws (each measurement), z (median distance per measurement)) or None (< 2 measurements)."""
    M = measurements(frames, base)
    if len(M) < 2:
        return None
    Ws, zs = [m[1] for m in M], [m[2] for m in M]
    if abs(Ws[0] - Ws[1]) / Ws[1] <= tol:
        W, ok = (Ws[0] + Ws[1]) / 2, True
    else:
        W, ok = consensus([(w, True) for w in Ws], tol)
    return dict(W=W, agreed=ok, Ws=Ws, z=zs)


def rot(rx, ry, rz):
    """Rotation from small Euler angles (rad)."""
    cx, sx, cy, sy, cz, sz = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    return (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))


if __name__ == "__main__":
    # self-check 1 (from pluto-v1): exact synthetic views are recovered exactly
    K0 = [[1000.0, 0, 640], [0, 1000.0, 480], [0, 0, 1]]
    P0, W0 = np.array([0.05, -0.03, 0.6]), 55.0
    for Rs, cs in (([np.eye(3)] * 2, [np.zeros(3), np.array([0, 0, 0.1])]),
                   ([np.eye(3)] * 2, [np.zeros(3), np.array([0.05, 0, 0])]),
                   ([np.eye(3), rot(0.05, -0.1, 0.02)], [np.zeros(3), np.array([0.05, 0.01, 0.08])])):
        vs = []
        for R, c in zip(Rs, cs):
            Xc = R @ (P0 - c)
            vs.append((R, -R @ c, (1000 * Xc[0] / Xc[2] + 640, 1000 * Xc[1] / Xc[2] + 480), W0 / Xc[2]))
        r = solve(vs, K0)
        zt = (Rs[-1] @ (P0 - cs[-1]))[2]
        assert r and abs(r["z"] - zt) < 1e-9 and abs(r["W"] - W0) < 1e-6 and np.allclose(r["P"], P0), r
    assert solve([(np.eye(3), np.zeros(3), (640, 480), 90.0)] * 2, K0) is None  # no motion -> no depth

    # self-check 2: a 0.90 m tall "child" 1.5 m away, phone slid 20 cm sideways and back with hand shake
    rng = np.random.default_rng(0)
    K1, H, Pc = [[500.0, 0, 240], [0, 500.0, 520], [0, 0, 1]], 0.90, np.array([0.0, 0.0, 1.5])
    frames = []
    for i in range(60):
        c = np.array([0.10 * np.sin(i / 59 * 2 * np.pi), 0.005 * rng.standard_normal(), 0.0])
        R = rot(*np.deg2rad(rng.normal(0, 1.0, 3)))  # 1 deg hand wobble, known exactly (ARCore pose)
        Xc = R @ (Pc - c)
        fer_px = 500 * H / Xc[2] * (1 + 0.01 * rng.standard_normal())
        uv = (500 * Xc[0] / Xc[2] + 240 + rng.normal(0, 0.5), 500 * Xc[1] / Xc[2] + 520 + rng.normal(0, 0.5))
        frames.append(dict(R=R, t=-R @ c, K=K1, obs=(uv, 0.4 * fer_px), fer=fer_px))
    res = pluto(frames)
    assert res and abs(res["W"] / 500 - H) < 0.03, res  # centroid noise biases z low ~1 % at 10 cm, 1.5 m
    m = np.zeros((50, 50), bool); m[10:40, 20:23] = True
    assert abs(feret(m) - np.hypot(30, 3)) < 0.5
    print("pluto self-checks OK, synthetic height", round(res["W"] / 500, 3), "m")
