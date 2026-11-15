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

## What the outcome would mean

If A or B explains the steps, the winter observation is an artefact and the July step stands alone. If neither does and C shows no change, the steps remain unexplained and slow movement stays possible; it would still not be shown.

Script: `scripts/winter_check.py`.
