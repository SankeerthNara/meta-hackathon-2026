# Build plan: phone-video child growth screening (working name: **Poshan Lens**)

Deadline: **Thu 5 Nov 2026, 07:30 IST**. Target: submit **Wed 4 Nov, 22:00 IST** (9.5 h buffer).

## What it does
1. Anganwadi worker opens the app on an ordinary Android phone, points it at the child standing (or a doll, in our demo), and slides the phone ~10 cm sideways.
2. **SAM 3.1** (text prompt "child", later "upper arm") masks the child in every frame.
3. **Pluto** (my motion-measurement method) turns camera poses + masks into the child's real height: three measurements from different parts of a 9 s left-right sweep, 2-of-3 vote.
4. Code computes **WHO growth-standard z-scores** (height-for-age; weight-for-height when the worker types the weight from the scale). Deterministic: the LLM never does the maths.
5. **Muse Spark** classifies with the WHO cut-offs it is given (severe / moderate / normal), explains to the worker and parent in their language (Hindi, Telugu, ... selectable), and fills the growth record (JSON + printable card).
6. Framed as a **screening aid** that tells the worker who to refer, not a diagnosis.

Camera poses: Chrome on Android with **WebXR (ARCore)** gives the phone pose for every frame (no LiDAR, no depth sensor). Fallback if the phone has no ARCore: slide the phone along a table edge between two marks 10 cm apart (known baseline).

## Remaining work (updated Tue 3 Nov, 17:00 IST; deadline Thu 5 Nov 07:30 IST)
Done: app end to end (phone capture, SAM 3.1, Pluto, WHO, Muse Spark), live API tested, first phone capture
(145.8 cm, measurements agree), real-image accuracy check (ACCURACY.md section 1), README and submission draft.

| When | What | Who |
|---|---|---|
| Tue 3 Nov, now | Tape-measure the person from Nov 1 (barefoot) and send the number. | you |
| Tue 3 Nov, 18-20 | **Accuracy set:** 3 targets (that person, a second adult, a doll or chair), 2 captures each with the 9 s sweep, about 1.5 m away, whole body in view with a gap above the head and below the feet. Note each true height. | you, I analyse |
| Tue 3 Nov, 20-21 | ACCURACY.md table and fixes from what the captures show. | me |
| Tue 3 Nov, 21-23 | **Record the demo video** (DEMO_SCRIPT.md), using the doll or an adult. | you |
| Wed 4 Nov, 09-13 | Edit the video (under 3 min), upload it unlisted, put the real numbers in SUBMISSION.md. | you + me |
| Wed 4 Nov, 13-18 | Buffer: re-shoot anything weak; make the repo public or add the judges. | you |
| Wed 4 Nov, 22:00 | **Submit.** Thursday 00:00-07:30 is emergency buffer only. | you |

## What you must film (no real children anywhere)
- **Accuracy set** (Tue evening, see table above): 3 targets with tape-measured height: an adult standing against a wall, a ~50-70 cm doll or soft toy standing on a table, a box. Each target 3 captures at ~1 m and ~1.5 m. Write the true heights in a note.
- **Demo footage** (Tue): the doll "child" on a mat/against a wall in a home or classroom-like setting; you playing the worker; phone screen recording of the capture; laptop screen recording of the result.
- **You on camera**, ~20 s: who you are, the problem, why a phone.

## Budget
SAM 3.1 at $2.50/1k images: ~30 frames per capture -> ~$0.08/capture; 100 captures ~= $8. Muse Spark Standard: < $0.01 per report. Well inside $150.
