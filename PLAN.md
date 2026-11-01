# Build plan: phone-video child growth screening (working name: **Poshan Lens**)

Deadline: **Thu 5 Nov 2026, 07:30 IST**. Target: submit **Wed 4 Nov, 22:00 IST** (9.5 h buffer).

## What it does
1. Anganwadi worker opens the app on an ordinary Android phone, points it at the child standing (or a doll, in our demo), and slides the phone ~10 cm sideways.
2. **SAM 3.1** (text prompt "child", later "upper arm") masks the child in every frame.
3. **Pluto** (my motion-measurement method) turns camera poses + masks into the child's real height: two measurements from the sideways move, a third on disagreement, 2-of-3 vote.
4. Code computes **WHO growth-standard z-scores** (height-for-age; weight-for-height when the worker types the weight from the scale). Deterministic: the LLM never does the maths.
5. **Muse Spark** classifies with the WHO cut-offs it is given (severe / moderate / normal), explains to the worker and parent in their language (Hindi, Telugu, ... selectable), and fills the growth record (JSON + printable card).
6. Framed as a **screening aid** that tells the worker who to refer, not a diagnosis.

Camera poses: Chrome on Android with **WebXR (ARCore)** gives the phone pose for every frame (no LiDAR, no depth sensor). Fallback if the phone has no ARCore: slide the phone along a table edge between two marks 10 cm apart (known baseline).

## Hour-by-hour (IST)
| When | What |
|---|---|
| Sun 1 Nov, 17-23 | Repo skeleton; copy Pluto `solve`/`consensus` (with its self-checks) from `pluto-v1`; WHO z-score module + tests; Muse Spark and SAM 3.1 clients; first real API call on one photo. |
| Mon 2 Nov, 09-13 | Phone capture page (WebXR camera frames + poses -> laptop server). |
| Mon 2 Nov, 14-19 | End-to-end: capture -> SAM 3.1 masks -> Pluto height -> z-scores -> Muse Spark report. |
| Mon 2 Nov, 19-22 | **You film accuracy runs** (list below); I report error vs tape measure. |
| Tue 3 Nov, 09-14 | UI polish (worker view, record card, language picker); stretch: MUAC from "upper arm" mask. |
| Tue 3 Nov, 15-20 | **Record the demo video** (script: `DEMO_SCRIPT.md`). |
| Wed 4 Nov, 09-18 | Edit video, README, submission text, fix anything the video exposed. |
| Wed 4 Nov, 22:00 | **Submit.** Thu 00:00-07:30 is buffer only. |

## What you must film (no real children anywhere)
- **Accuracy set** (Mon evening): 3 targets with tape-measured height: an adult standing against a wall, a ~50-70 cm doll or soft toy standing on a table, a box. Each target 3 captures at ~1 m and ~1.5 m. Write the true heights in a note.
- **Demo footage** (Tue): the doll "child" on a mat/against a wall in a home or classroom-like setting; you playing the worker; phone screen recording of the capture; laptop screen recording of the result.
- **You on camera**, ~20 s: who you are, the problem, why a phone.

## Budget
SAM 3.1 at $2.50/1k images: ~30 frames per capture -> ~$0.08/capture; 100 captures ~= $8. Muse Spark Standard: < $0.01 per report. Well inside $150.
