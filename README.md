# Poshan Lens: child growth screening from an ordinary phone camera

Meta Global AI Developer Hackathon 2026, Indie track. Built 1-4 Nov 2026.

India has about 1.4 million Anganwadi centres. Each one is supposed to measure every child under five every month,
but measuring boards are often missing or hard to use well, and height is the measurement most often wrong.
Poshan Lens gives an Anganwadi worker a child's **height from a 9-second phone video**, the **WHO z-scores**, a
**severe / moderate / normal** screening result, and a **message for the parent in their own language**. It runs on
any ARCore Android phone. It needs no LiDAR, no depth camera, no reference card and no extra hardware.

> Screening aid, not a diagnosis. A "severe" result means "refer to the health centre / NRC today".
> No real children were filmed for this project: the demo uses a doll and adults.

## How it works
```
phone (Chrome, WebXR + ARCore)        laptop / server
 camera frames + 6-DoF poses  ──►  SAM 3.1 ("child")  ──► mask per frame
                                   Pluto (motion measurement) ──► height in cm, 2-3 independent measurements
                                   WHO Child Growth Standards ──► HAZ, WHZ, categories   (deterministic code)
                                   Muse Spark (image) ──► photo check: full body visible, standing straight?
                                   Muse Spark (text)  ──► worker summary, parent message (Hindi, Telugu, ...),
                                                          checklist, follow-up date, register note
```
- **SAM 3.1** (Meta Model API, `sam-3.1`) finds the child in every frame from the text prompt "child".
- **Pluto** is my method for measuring the real size of an unknown object from a small sideways camera move
  (developed for onboard robot-grasping perception; frozen as tag `pluto-v1` on 31 Oct 2026). Each frame's camera
  pose (R, t from ARCore) and the mask's centroid and size give linear equations in the child's 3D position and
  the size constant W = size px × distance. The capture is cut into three time segments, and
  each one is solved over all its frames. A standing person sways a few cm, so the short 10 cm windows Pluto
  uses on rigid objects would read that sway as parallax. Pluto's 2-of-3 vote (5 % tolerance) then accepts the
  result, and one solve over every frame gives the final value. If the segments disagree, the app asks to measure again. Height = W / focal length, measured along
  ARCore's gravity direction. After that, distance in any frame is just W / mask size.
- **WHO z-scores** come from the WHO 2006 LMS tables (`data/who`, packaged by
  [pygrowup](https://github.com/ewheeler/pygrowup)), with WHO's restricted tails beyond ±3 SD. The LLM never
  does this maths: it gets the numbers and categories and explains them. Values WHO flags as implausible
  (|HAZ| > 6, |WHZ| > 5) are never classified. The app says "measure again" instead.
- **Muse Spark** (`muse-spark-1.3`, Standard mode) checks one frame (is the whole body visible and standing
  straight?), then writes the report as JSON. The phone reads the parent message aloud with the browser's
  text-to-speech.

## Run it
Requirements: Python 3.10+, a Meta Model API key, and an Android phone with ARCore ("Google Play Services for AR")
and Chrome.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
cp .env.example .env        # then open .env and paste your key after MODEL_API_KEY=
.venv/Scripts/python -m uvicorn server:app --host 0.0.0.0 --port 8000
```
WebXR only runs on a secure origin. The easiest way to get one is a USB cable and `adb reverse`, so the phone
reaches the laptop as `localhost`:
```bash
adb reverse tcp:8000 tcp:8000
```
Then open `http://localhost:8000` in Chrome on the phone. Without adb, open `chrome://flags` on the phone, add
`http://<laptop-ip>:8000` to "Insecure origins treated as secure", relaunch Chrome, and open that address.

How to measure: the child stands straight against a wall, about 1.5 m away, with the whole body in view. Press
**Start measuring** and slide the phone slowly left and right, about a hand's width each way, until the bar fills (9 seconds).

Re-run an analysis offline (SAM results are cached per frame, so a re-run costs only the Muse Spark call):
```bash
.venv/Scripts/python -m poshan.analyze captures/<id>
```

Accuracy: `python -m tools.hope_check <HOPE sequence> <prompt>` (real images with ground-truth poses) and
`python -m tools.accuracy accuracy.csv` (your own tape-measured captures). Results are in `ACCURACY.md`.

Tests (no API key needed):
```bash
.venv/Scripts/python -m poshan.pluto
.venv/Scripts/python -m poshan.who
.venv/Scripts/python -m tests.test_offline
```

## Cost
About 60 frames per measurement × $2.50 per 1,000 SAM images ≈ $0.15, plus less than $0.01 of Muse Spark.

## Limits (honest list)
- Accuracy on real captures: see `ACCURACY.md` (doll and adults with tape-measured heights).
- Children under 2 are measured lying down (length). The app then uses the Feret diameter of the mask, which
  is a shortcut that assumes the child lies straight.
- Height from a mask includes hair and shoes. Measure barefoot.
- MUAC is typed in from a tape for now. Estimating it from an "upper arm" mask is future work.

## Files
`poshan/pluto.py` Pluto (from `pluto-v1`) · `poshan/who.py` z-scores · `poshan/meta.py` SAM 3.1 + Muse Spark ·
`poshan/analyze.py` pipeline · `server.py` API · `static/` phone pages · `tests/` offline end-to-end test.
