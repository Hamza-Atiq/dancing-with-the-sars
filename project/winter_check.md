# The winter steps — elevation, height-model error or snow?

**Status: rules written and committed on 15 Nov 2026 before the tests were run.** The winter steps themselves were seen earlier (`project/results.md` section 2). The height model (Copernicus GLO-30), the baselines and the snow images for these tests had not been looked at. Results go in a section below, without changing anything above it.

## Question

In nine winter pairs (28 Nov 2025 – 16 Mar 2026) the patch shows steps of 0.2–2.3 cm against the west block; the first five are negative; four are above the controls' 95% level. Three ordinary causes could produce this without any ground movement. Each is tested on its own.

## Data

- Steps: the nine readable winter pairs and 2–14 Jul (readable, no step), measured exactly as in `pipeline/series.py` (patch, west block, signed phase).
- Controls: the same construction as `control_ranks` in `pipeline/series.py` (boxes of patch size on a 1 km grid with their own west-type reference block), signed phase, resolved in that pair.
- Heights: Copernicus GLO-30 DEM tile N28 E085 (AWS open data), sampled at each 20 m radar pixel (nearest neighbour after converting the radar grid to longitude/latitude).
- Baselines: perpendicular baseline of each pair from the GUNW metadata cube (`metadata/radarGrid/perpendicularBaseline`), interpolated to the patch at 5,050 m.
- Snow: HLS Fmask snow/ice bit (same reading as `scripts/flag_check.py`), scene within ±5 days of each radar date with at least 70% of the box clear.

## Tests (fixed now)

**A. Phase that grows with height (air layers).** In each pair, fit control phase = a + k × (height of control box − height of its reference block), ordinary least squares, 95% interval for k from 2,000 bootstrap resamples (seed 0). Predicted patch step = a + k × (patch height − west-block height), using medians of the DEM.
- In a pair, height **explains** the step if the interval for k excludes zero and the corrected step |observed − predicted| is less than half of |observed|.
- Verdict over nine pairs: explains in 5 or more = **yes**; 2–4 = **partly**; 0–1 = **no**.

**B. Height-model error.** A wrong height on the patch gives a phase proportional to the perpendicular baseline. Fit patch step = c + m × baseline over the ten readable pairs (nine winter + 2–14 Jul; 14–26 Jul is left out as the signal under study). The implied height error is reported.
- **Consistent with height error** if the correlation is significant (permutation test, 10,000 shuffles, seed 0, p < 0.05) and the fit removes at least half of the spread (residual RMS < 0.5 × RMS of the steps).
- Otherwise **not explained by height error**.

**C. Snow.** Snow fraction on the patch box and on the west-block box at both dates of each pair.
- A pair has a **snow change** if the fraction changes by 0.3 or more on either box.
- Reported: which pairs have a snow change, and whether those are the pairs with the larger steps (the four above the controls' 95% level). No verdict beyond that, because a snow-covered surface can also change phase without a visible change in the snow mask.

**D. Weather-model delay (added the same day, after seeing that the GUNW metadata holds `hydrostaticTroposphericPhaseScreen` and `wetTroposphericPhaseScreen`, before running anything).** For each pair, model step = (hydrostatic + wet screen at the patch) − (same at the west block), each interpolated from the metadata cube at the box centre and its DEM median height. The product's own sign convention is used: corrected step = observed − model.
- In a pair, the model **explains** the step if |corrected| < half |observed|.
- Verdict: 5 or more of nine = **yes**; 2–4 = **partly**; 0–1 = **no**. The model's size is also reported, since a model step much smaller than the observed one means the weather model cannot be the cause, whatever the sign convention.

## What the outcome would mean

If A or B explains the steps, the winter observation is an artefact and the July step stands alone. If neither does and C shows no change, the steps remain unexplained and slow movement stays possible; it would still not be shown.

Script: `scripts/winter_check.py`.

## Results (run once, 15 Nov 2026; `data/winter/winter_check_table.txt`, `data/winter/winter_check.json`)

Heights (Copernicus GLO-30): patch **5,075 m**, west block **4,300 m**, a difference of **775 m**. Cross-check with the height model inside the Sentinel-1 products (`data/s1`, a separate file): patch box 4,977 m, west block 4,271 m. The large difference is real; the patch and its reference sit at very different heights, which is what makes air-layer delay worth testing.

| Pair | Step (cm) | Controls | k (rad/km) [95%] | Predicted by A (cm) | A explains | Baseline (m) | Weather model D (cm) | D explains |
|---|---:|---:|---|---:|:-:|---:|---:|:-:|
| 28 Nov–10 Dec | −1.66 | 263 | −0.01 [−0.18, +0.14] | +0.05 | no | +101 | +0.26 | no |
| 10–22 Dec | −1.07 | 254 | +0.02 [−0.13, +0.16] | −0.00 | no | −126 | −0.10 | no |
| 22 Dec–3 Jan | −1.64 | 266 | −0.52 [−0.68, −0.35] | −0.84 | **yes** | −86 | −0.47 | no |
| 3–15 Jan | −0.55 | 248 | +0.49 [+0.33, +0.63] | +0.79 | no | +152 | +0.74 | no |
| 15–27 Jan | −2.33 | 250 | −0.99 [−1.15, −0.83] | −1.48 | **yes** | −141 | −1.35 | **yes** |
| 27 Jan–8 Feb | +1.33 | 242 | +0.80 [+0.60, +0.99] | +1.19 | **yes** | +188 | +1.18 | **yes** |
| 8–20 Feb | −0.22 | 286 | −0.34 [−0.52, −0.14] | −0.61 | no | −73 | −0.44 | no |
| 20 Feb–4 Mar | +1.18 | 276 | +0.14 [−0.02, +0.30] | +0.26 | no | −66 | +0.70 | **yes** |
| 4–16 Mar | −0.31 | 292 | +0.33 [+0.21, +0.45] | +0.45 | no | +21 | −0.77 | no |
| 2–14 Jul (not winter) | +0.63 | 292 | −0.40 [−0.54, −0.25] | −0.72 | — | −25 | −0.43 | — |

- **Test A (height-linked air delay, from the controls): explains 3 of 9 → partly.**
- **Test D (NASA weather model in the product): explains 3 of 9 → partly.**
- **Test B (height-model error): not explained.** r = +0.38, permutation p = 0.28; the fit removes almost nothing (residual 0.57 against 0.61 rad). Implied height error would be +24 m.
- **Test C (snow): could not be done.** For almost every winter date no HLS image had 70% of the patch or west block clear; this steep, shaded face is marked as shadow or cloud in winter. Only 22 Dec–3 Jan has the patch on both dates (snow fraction 0.6 → 0.5, no change).

**What this shows.** Tests A and D are independent (one comes from 250–290 other slopes in the same image, the other from a global weather model) and they agree closely in most pairs (e.g. 15–27 Jan −1.48 and −1.35 cm; 27 Jan–8 Feb +1.19 and +1.18 cm; 3–15 Jan +0.79 and +0.74 cm). So **air layers between 4,300 and 5,075 m do add steps of up to about 1.5 cm on this patch in winter**, and they account for the biggest single winter step (15–27 Jan) and the one positive large step (27 Jan–8 Feb). They do **not** account for the steps in late November and December (−1.66 and −1.07 cm), where both tests predict almost nothing. Height-model error does not explain them; snow could not be checked. The winter observation is therefore partly an air effect and partly still unexplained. It stays an open observation, now weaker than before.

## Added after seeing the results: does air delay explain the July step?

Not part of the rules above; added because the winter results showed air delay matters on this patch. Same tests A and D, on 14–26 Jul and 2–14 Jul (`scripts/july_air_check.py`, `data/winter/july_air_check.json`).

| Pair | Step (cm) | k (rad/km) [95%] | Predicted by A (cm) | Weather model D (cm) | Step after A / after D (cm) |
|---|---:|---|---:|---:|---|
| 2–14 Jul | +0.63 | −0.40 [−0.55, −0.26] | −0.72 | −0.43 | +1.35 / +1.06 |
| **14–26 Jul** | **−5.60** | +0.02 [−0.07, +0.11] | **+0.12** | **+0.01** | **−5.71 / −5.61** |

- In 14–26 Jul there is **no height-linked delay** among the 361 controls (k indistinguishable from zero), and the weather model predicts 0.01 cm. **The July step is not an air effect.**
- 44 controls have a height difference of 500 m or more to their own reference; their largest step in 14–26 Jul is 0.61 rad, against 2.91 rad on the patch. Height difference alone does not produce steps like the patch's.
- Only 5 of 392 control boxes have a height difference as large as the patch's 775 m, so the controls cover this height range thinly; the fit and the weather model are what close this gap.
