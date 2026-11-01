"""Poshan Lens server: the phone uploads a capture, the laptop runs SAM 3.1 + Pluto + WHO + Muse Spark.

  .venv/Scripts/python -m uvicorn server:app --host 0.0.0.0 --port 8000
"""
import json, os, re, secrets, time
from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from poshan.analyze import run

ROOT = os.path.dirname(os.path.abspath(__file__))
CAPS = os.path.join(ROOT, "captures")
app = FastAPI()


def cap_dir(cid):
    if not cid.isalnum():
        raise HTTPException(400, "bad id")
    d = os.path.join(CAPS, cid)
    if not os.path.isdir(d):
        raise HTTPException(404, "no such capture")
    return d


@app.post("/api/capture")
async def capture(meta: str = Form(...), files: list[UploadFile] = []):
    m = json.loads(meta)
    names = {f["file"] for f in m["frames"]}
    for f in files:
        if f.filename not in names or not re.fullmatch(r"f\d{3}\.jpg", f.filename):  # no paths from the client
            raise HTTPException(400, f"unexpected file {f.filename}")
    cid = time.strftime("%Y%m%d%H%M%S") + secrets.token_hex(2)
    d = os.path.join(CAPS, cid)
    os.makedirs(d)
    for f in files:
        open(os.path.join(d, f.filename), "wb").write(await f.read())
    json.dump(m, open(os.path.join(d, "meta.json"), "w", encoding="utf8"), indent=1, ensure_ascii=False)
    return {"id": cid}


@app.post("/api/analyze/{cid}")
def analyze(cid: str):
    d = cap_dir(cid)
    try:
        return {k: v for k, v in run(d).items() if k != "track_m"} | {"id": cid}
    except Exception as e:  # show the worker what failed instead of a blank page
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.get("/api/result/{cid}")
def result(cid: str):
    p = os.path.join(cap_dir(cid), "result.json")
    if not os.path.exists(p):
        raise HTTPException(404, "not analysed yet")
    return json.load(open(p, encoding="utf8")) | {"meta": json.load(open(os.path.join(cap_dir(cid), "meta.json"), encoding="utf8"))["child"]}


@app.get("/captures/{cid}/{name}")
def capture_file(cid: str, name: str):
    if not (name == "overlay.jpg" or (name.startswith("f") and name.endswith(".jpg") and name[1:-4].isdigit())):
        raise HTTPException(404)
    return FileResponse(os.path.join(cap_dir(cid), name))


@app.get("/api/captures")
def captures():
    return sorted(os.listdir(CAPS), reverse=True) if os.path.isdir(CAPS) else []


@app.get("/")
def index():
    return RedirectResponse("/static/capture.html")


app.mount("/static", StaticFiles(directory=os.path.join(ROOT, "static")), name="static")
