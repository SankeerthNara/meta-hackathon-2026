# Accuracy

## 1. Real images, ground-truth camera poses (done 1 Nov)
The full pipeline (live SAM 3.1 masks from a text prompt + Pluto) on BOP HOPE onboarding sequences, which come
with ground-truth camera poses and object distances (`python -m tools.hope_check <sequence> <prompt>`, 57-60
frames each, 480 px wide like the phone). The objects are grocery items about 30 cm from the camera, and the camera
orbits them. This is a harder motion than the sideways slide the app asks for.

| Sequence | SAM prompt | Distance error, median abs. | 3 measurements agree? |
|---|---|---|---|
| obj_000001_up (soup can) | "can" | 2.8 % | yes |
| obj_000002_up (sauce bottle) | "bottle" | 6.3 % | yes |
| obj_000006_up (cookie box) | "box" | 4.9 % | no, the app asks to measure again |

Height error equals distance error, because height = W / f and distance = W / size px use the same W.

## 2. Phone captures, tape-measured (to do 2 Nov)
Doll, adult and box, each with a tape-measured height, 3 captures each at about 1 m and 1.5 m. List them in
`accuracy.csv` (`id,target,true_cm`) and run `python -m tools.accuracy accuracy.csv`.
