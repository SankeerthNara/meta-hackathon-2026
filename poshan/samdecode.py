"""SAM 3.1 output text -> masks. Kept free of the OpenAI SDK so decoding worker processes start fast."""
import re
import numpy as np
from meta_sam_parser import SegmentationMask, decode_mask_to_raster

_REC = re.compile(r"<\|box;x1=(\d+);y1=(\d+);x2=(\d+);y2=(\d+);[^|]*\|><\|mask;x=(\d+);y=(\d+);data=(\d+),(\d+),([^|]+)\|>")


def masks(raw, w, h, largest=False):
    """SAM output text -> list of full-size boolean masks (h, w). largest=True decodes only the biggest box.
    shortcut: regex over the documented record grammar instead of meta_sam_parser's parser, which decodes every
    mask once just to validate it (~0.8 s each in pure Python); upgrade if the grammar changes."""
    recs = [tuple(int(v) for v in g[:8]) + (g[8],) for g in _REC.findall(raw)]
    if largest and recs:
        recs = [max(recs, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))]
    out = []
    for x1, y1, x2, y2, mx, my, mh, mw, payload in recs:
        enc = "lossless" if payload.startswith("~") else "one_bit"
        crop = np.frombuffer(decode_mask_to_raster(SegmentationMask(encoding=enc, height=mh, width=mw, payload=payload)),
                             np.uint8).reshape(mh, mw).astype(bool)
        top, left = y1 + my, x1 + mx
        full = np.zeros((h, w), bool)
        full[top:top + mh, left:left + mw] = crop[: h - top, : w - left]
        out.append(full)
    return out
