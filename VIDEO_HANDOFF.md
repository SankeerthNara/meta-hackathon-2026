# Demo video hand-off (continue in Antigravity if Claude credits run out)

Goal: a 3:00 AI-made explainer for Poshan Lens. Voice: ElevenLabs. Cinematic b-roll: Runway (`runway-gen4-turbo`,
through the ElevenLabs creative suite). App and diagram scenes: Remotion (code, free, renders locally) in `video/`.
Final file: `video/out/poshan-lens.mp4`. Upload it unlisted (YouTube or Drive) and paste the link into the form.

Rules: no real children's faces. AI-generated children only from behind or at a distance. Don't show the
Nov 1 volunteer's photos (no consent for publishing). Say "screening aid, not a diagnosis".

## Status (update as you go)
- [ ] Narration generated (ElevenLabs, `eleven_v4`) -> `video/public/narration.mp3`
- [ ] Runway clips 1, 2, 3, 7 -> `video/public/clip1.mp4` ... (silent, 5-10 s each)
- [ ] Remotion project renders all scenes with narration -> `video/out/poshan-lens.mp4`
- [ ] Uploaded, link pasted into the form

## Narration script (about 430 words, about 3:00)
See `video/narration.txt` (same text, single source). Scene timings below follow it.

## Scenes
| # | Time | Visual | Source |
|---|---|---|---|
| 1 | 0:00-0:20 | Morning, rural Anganwadi centre in India, a worker in a sari opens the growth register; children play in the background, out of focus | Runway clip1 |
| 2 | 0:20-0:42 | Close-up: the worker's hands with a cloth tape measure and a wooden measuring board, frustrated; overlay "35.5 % of Indian children under 5 are stunted (NFHS-5)" | Runway clip2 + Remotion text |
| 3 | 0:42-1:05 | Over the worker's shoulder: she holds an Android phone and slides it slowly left and right in front of a small child standing against a painted wall (child seen from a distance, face not visible) | Runway clip3 |
| 4 | 1:05-1:35 | Pipeline diagram animates: phone frames -> SAM 3.1 outline -> Pluto 3D -> WHO z-score -> Muse Spark | Remotion |
| 5 | 1:35-2:05 | Pluto: camera dots moving along a sweep, three measurement bars (107 / 148 / 148 cm), the outlier crossed out, "2 of 3 agree" | Remotion |
| 6 | 2:05-2:35 | Phone mockup of the result page: height, red "Severe stunting / Refer today" badge, the Hindi parent message (real Muse Spark output, `scratch/rep.json`), "Read aloud" | Remotion |
| 7 | 2:35-2:50 | Worker and mother sitting together, looking at the phone, mother nods, warm light | Runway clip7 |
| 8 | 2:50-3:00 | Title card: "Poshan Lens · SAM 3.1 + Muse Spark · screening aid, not a diagnosis" + repo URL | Remotion |

Runway prompts (silent, 16:9, ~10 s):
1. "Cinematic morning in a rural Indian Anganwadi centre, a woman health worker in a cotton sari opens a large paper register at a wooden desk, colourful wall charts, soft sunlight through a window, young children playing out of focus in the background, documentary style, slow dolly in"
2. "Close-up of a health worker's hands holding a cloth measuring tape next to a worn wooden height board leaning on a wall, she sighs and puts it down, shallow depth of field, natural light, documentary"
3. "Over-the-shoulder shot, an Indian woman health worker holds an Android smartphone and slowly slides it left and right, pointing at a small child standing against a pale painted wall about one and a half metres away, child seen from a distance with face not visible, calm, natural light"
7. "An Indian health worker and a young mother sit together on a mat in a village home, looking at a smartphone screen, the mother nods and smiles with relief, warm afternoon light, documentary style"

## Assembly (Remotion)
```bash
cd video && npm install && npx remotion render Main out/poshan-lens.mp4
```
`video/src/` holds the composition. Scene durations are in `video/src/Main.tsx`. Adjust them to the narration
length (Remotion's `getAudioDurationInSeconds`).
