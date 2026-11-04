# Submission text (paste into the hackathon form)

**Project name:** Poshan Lens

**Tagline (one line):** A child's height, WHO growth status and a parent message in their own language, all from a 9-second phone video. No measuring board needed.

**Track / theme:** Indie · Build for Your World (also fits Push the Frontier: metric 3D measurement from a moving phone camera)

## Short description (~100 words)
India's 1.4 million Anganwadi workers are meant to measure every child under five every month. Height is the
measurement that reveals stunting, and it is the one most often skipped or wrong. With Poshan Lens the worker
slides an ordinary Android phone left and right for nine seconds. SAM 3.1 finds the child in every frame. Pluto, my
motion-measurement method, turns the phone's ARCore motion and the masks into a height in centimetres, using two
independent measurements and a third vote if they disagree. Code computes the WHO z-scores. Muse Spark checks the
photo and explains the result to the worker and the parent in Hindi, Telugu or another Indian language. It is
a screening aid, not a diagnosis.

## How we used Meta AI
- **SAM 3.1** (`sam-3.1`, Responses API): text-prompted segmentation of "child" in every frame of the capture. The masks'
  centroid and size, together with the camera poses, are the input to the 3D measurement. Masks are decoded with
  Meta's `meta-sam-parser`.
- **Muse Spark** (`muse-spark-1.3`, Standard mode), two roles:
  1. *Vision quality gate:* checks one frame and says whether the whole body is visible and the child is standing
     straight, before a number reaches the growth register.
  2. *Explainer and record writer:* takes the computed measurements, WHO z-scores and categories (it is told never
     to recompute them) and returns structured JSON: a worker summary, a parent message in the chosen language and
     script, a checklist, a follow-up interval and a register note.
- The division of labour is deliberate. Geometry and WHO maths are deterministic code, so they can be audited.
  The Meta models do what code can't: find the child in arbitrary scenes, judge a photo, and talk to people in
  their language.

## Technical depth
- Pluto solves a weighted linear system per motion window: each frame adds centroid-parallax rows and a size
  (looming) row, with unknowns the child's 3D position and the size constant W = size px × distance. It takes
  three time-segment measurements (each solved over all its frames, robust to a person's sway; short windows
  were not: 131/156/204 cm on the first phone capture vs 107/148/148 with segments), and a 2-of-3 consensus
  with 5 % tolerance. Height comes from the mask extent along ARCore's gravity vector.
- Camera poses come from WebXR `camera-access` (ARCore) in Chrome, so it needs no app install, no LiDAR and no
  depth sensor. The phone saves each frame with its exact intrinsics, taken from the projection matrix.
- WHO 2006 LMS tables are used with WHO's restricted-tail rule beyond ±3 SD, length vs height switching at
  24 months, and weight-for-length vs weight-for-height.
- Self-checks: exact recovery on synthetic views, a synthetic end-to-end WebXR capture (90 cm → 90.2 cm), and
  z-scores checked against WHO's published SD columns. On real images with ground-truth camera poses (BOP HOPE),
  live SAM 3.1 + Pluto gets distance/size right to within 2.8-6.3 % (median), and it flags the one sequence
  where its measurements disagree. On the first real phone capture (an adult, ARCore poses, live SAM 3.1), the three
  segment measurements gave 107 / 148 / 148 cm, and the 2-of-3 vote rejected the outlier. A tape-measure
  comparison on the phone was not finished before the deadline.
- Guard rails: frames where the head or feet touch the image edge are dropped, WHO implausible-value flags
  block classification, and the Muse Spark photo check warns on a bad pose.

## Impact
Stunting affects about a third of Indian children under five (NFHS-5: 35.5 %). Screening only works if height is
measured, and measured right. Poshan Lens needs only a phone that workers already have (Poshan Tracker already
runs on phones), costs about $0.15 of API per child, and gives the parent an answer they can understand on the
spot. Next steps: an offline on-device version (SAM and an open-weight Muse model on the phone), MUAC from the arm
mask, and a pilot with an ICDS block, validated against measuring boards.

## Safety
Screening aid only. "Severe" always means refer today. The language model never changes the numbers. No real
children were filmed. The demo uses a doll and adults. Captured frames stay on the worker's own server
(gitignored) and are sent only to the Meta Model API in Standard mode, where they are not used for training.

**Repo:** https://github.com/SankeerthNara/meta-hackathon-2026 (private; add the judges or make it public before submitting)
**Video:** <link>
