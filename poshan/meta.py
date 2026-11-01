"""Meta Model API: SAM 3.1 masks and Muse Spark reports (OpenAI-compatible, https://api.meta.ai/v1)."""
import base64, json, os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from .samdecode import masks  # noqa: F401 (re-exported)

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
SPARK = os.getenv("MUSE_MODEL", "muse-spark-1.3")  # Standard mode (not -contributor)
_client = None


def client():
    global _client
    if _client is None:
        key = os.getenv("MODEL_API_KEY")
        if not key:
            raise RuntimeError("MODEL_API_KEY missing: put it in .env (see .env.example)")
        _client = OpenAI(base_url="https://api.meta.ai/v1", api_key=key)
    return _client


def _data_url(jpeg):
    return "data:image/jpeg;base64," + base64.b64encode(jpeg).decode()


def sam_raw(jpeg, prompt):
    """SAM 3.1 on one JPEG -> the raw output text (cache it: re-parsing is free, re-segmenting is billed)."""
    r = client().responses.create(model="sam-3.1", input=[{"type": "message", "role": "user", "content": [
        {"type": "input_text", "text": prompt}, {"type": "input_image", "image_url": _data_url(jpeg)}]}])
    return r.output_text or ""


def spark_json(system, user, image_jpeg=None):
    """Muse Spark with a JSON-only answer."""
    content = [{"type": "text", "text": user}]
    if image_jpeg:
        content.append({"type": "image_url", "image_url": {"url": _data_url(image_jpeg)}})
    r = client().chat.completions.create(model=SPARK, messages=[{"role": "system", "content": system},
                                                                 {"role": "user", "content": content}],
                                         response_format={"type": "json_object"})
    txt = r.choices[0].message.content
    return json.loads(txt[txt.find("{"): txt.rfind("}") + 1])


QC_SYSTEM = ("You check photos taken by a community health worker before a child's height is measured from them. "
             "Answer only JSON: {\"ok\": true|false, \"issue\": \"<short reason if not ok, in English>\"}. "
             "ok means: one person (or doll) fully visible head to feet, standing straight (or lying flat), "
             "not cut off by the frame, not sitting or crouching.")

REPORT_SYSTEM = """You are a screening assistant for Anganwadi workers in India (ICDS / POSHAN Abhiyaan).
You receive measurements that were already computed by software, WHO z-scores and WHO categories. Never recompute or
change the numbers or categories; explain them. This is a screening aid, not a diagnosis: anything severe means
"refer to the health centre / NRC today", never a treatment plan. Be kind and plain to parents; never blame them.
Answer only JSON:
{"worker_summary": "<2-3 sentences in English for the worker: what the numbers mean, what to do next>",
 "parent_message": "<3-5 short sentences in the requested language, in its own script, simple words>",
 "actions": ["<checklist items for the worker, English>"],
 "follow_up_days": <integer: when to measure again>,
 "record_note": "<one line for the growth register, English>"}"""


def report(record, language):
    return spark_json(REPORT_SYSTEM, f"Language for parent_message: {language}\nMeasurement record:\n"
                      + json.dumps(record, indent=1, ensure_ascii=False))
