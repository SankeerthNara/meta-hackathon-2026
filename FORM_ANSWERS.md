# Form answers (paste as is)

## Project Description*
Poshan Lens measures a young child's height with an ordinary Android phone, then tells an Anganwadi worker and
the parent what the measurement means. India has about 1.4 million Anganwadi centres, and their workers are meant
to measure every child under five every month. Height is the number that reveals stunting, which affects 35.5 % of
Indian children under five (NFHS-5), and it is the measurement most often skipped or done wrong.

How it works: the worker types the child's age (and weight from the scale), points the phone at the standing
child, and slides it slowly left and right for nine seconds. Chrome's WebXR (ARCore) records the camera frames and
the exact phone motion. SAM 3.1 finds the child in every frame. Pluto, my motion-measurement method, turns the
masks and the phone motion into a height in centimetres. It takes three independent measurements from different
parts of the sweep and keeps the value at least two agree on. Code then computes the WHO Child Growth Standards
z-scores and categories (severe / moderate / normal). Muse Spark checks one frame (is the whole body visible, is
the child standing straight?) and writes a summary and checklist for the worker, a message for the parent in their
own language and script (Hindi, Telugu, Tamil, ...), read aloud on the phone, and a note for the growth register.
It needs no LiDAR, no depth camera, no measuring board and no app install, and costs about $0.15 of API per child.
It is a screening aid that tells the worker whom to refer, not a diagnosis.

## Describe your use of Meta products to build the submitted project*
- **SAM 3.1** (`sam-3.1` on the Meta Model API, Responses endpoint): every captured frame (about 45 per measurement)
  is sent with the text prompt "child". The masks give the child's centroid, area and extent along gravity in
  each frame. These, together with the ARCore camera poses, are the input to the 3D measurement. I decode the masks
  with Meta's `meta-sam-parser` codec. I also used SAM 3.1 to validate the pipeline on real images with
  ground-truth camera poses (BOP HOPE): distance came out within 2.8-6.3 % (median).
- **Muse Spark** (`muse-spark-1.3`, Standard mode), in two roles:
  1. *Vision quality gate:* one frame plus a strict JSON prompt. It answers whether one person is fully visible and
     standing straight, so a bad photo is flagged before a number reaches the register. It correctly rejected
     photos with no person in them.
  2. *Explainer and record writer:* it gets the computed height, the WHO z-scores and categories (and is told never
     to recompute them), and returns JSON: a worker summary, a parent message in the chosen Indian language and
     script, a checklist, a follow-up interval and a register note.
- Both go through the OpenAI-compatible API at `https://api.meta.ai/v1` with the standard `openai` Python SDK.

## Why are Meta's models important to your solution?*
The two hard parts of the problem are exactly what these models do and ordinary code can't.
- **Finding the child, with no training.** The measurement needs a clean outline of the child in every frame, in any
  home or Anganwadi, with any clothes, background or lighting. SAM 3.1 does this from the single word "child",
  with no dataset collection and no model training on children's images (which would raise serious consent and
  privacy problems). Without it, I would have had to train a segmenter on photos of real children.
- **Reaching the parent.** A z-score of -3.2 means nothing to a mother. Muse Spark turns a fixed, auditable result
  into kind, plain sentences in her own language and script, and into the worker's checklist and register note. A
  template system would need human translation for every language and situation.
- **Catching bad captures.** Muse Spark's image understanding checks the photo itself (sitting, crouching, cut off)
  before a wrong number gets recorded.
- The design keeps each part where it is trustworthy: geometry and WHO maths are deterministic code, and the Meta
  models do perception and language. That combination makes the result both automatic and auditable.

## Provide feedback from your experience using partner technologies.
What worked well:
- The Meta Model API is OpenAI-compatible. The stock `openai` Python SDK worked first time for both SAM 3.1 and
  Muse Spark, with only a base-URL change.
- SAM 3.1's text-prompted masks were excellent on real phone frames: a clean full-body outline, head to feet, in
  every frame, from the one word "child". Image segmentation at $2.50 per 1,000 images is cheap enough for
  per-child screening.
- Muse Spark's JSON mode (`response_format: json_object`) gave parseable output every time. Its Hindi and Telugu
  were natural and in the right script.

What could be better:
- **Mask decoding speed.** The Python `meta-sam-parser` codec is pure Python: about 0.8-1.5 s to decode one
  full-body 480x1056 mask. Its stream parser also decodes every mask once just to validate it, so decoding cost
  twice that. With 45-60 frames per measurement this dominated my latency (3 minutes before I parsed the record
  grammar myself and decoded in parallel). A native or numpy decoder, or an option to get masks as COCO RLE or PNG,
  would help a lot.
- **`one_bit` vs lossless.** The `one_bit` encoding was much smaller on the wire but no faster to decode.
- **Docs.** The SAM overview is clear, but full request JSON for video, box/point prompts and Files API upload in
  Python was hard to find. A complete Python cookbook example (image + video, non-streaming) would save time.
- **Regional availability.** Muse Image is not available in India, where I am. It would have been useful for
  illustrated parent leaflets.
