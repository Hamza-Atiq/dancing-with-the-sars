# The blind 24 days (26 Jul – 19 Aug) at 5 m

**Status: rules written and committed on 15 Nov 2026 before any GSLC image was read.** Only the catalogue and the file layout (pixel size, flattening flags) were looked at. Results go in a section below, without changing anything above it.

## Question

In 26 Jul – 19 Aug the 20 m interferogram over the patch is a jumble (consistency 0.37), so no value was reported (`project/results.md` section 2). Others report the source speeding up in this period (a preprint quotes 0.96 m in these 24 days from NISAR offsets). Can the full-resolution images say how much the patch moved?

## Data

NISAR L2 GSLC (geocoded single-look complex), track 098 A frame 016, HH, release P05023, 5 m pixels, UTM 45N, topographic flattening applied (from the file's own parameters). Dates 2 Jul, 14 Jul, 26 Jul, 19 Aug, 31 Aug 2026. Crop: 6 × 6 km centred on the patch (x 352,525–358,525, y 3,127,015–3,133,015).

Pairs: 2–14 Jul and 14–26 Jul (before), **26 Jul – 19 Aug (target)**, 19–31 Aug (across the collapse).

Patch: the same 141 pixels at 20 m (`pipeline/series.py`), each covering 4 × 4 pixels at 5 m. Reference: the west block.

## Method 1 — phase at finer pixels

Interferogram = image 1 × conjugate(image 2). Averaged over L × L pixels with L = 2 (10 m) and L = 4 (20 m), then the same measurement as `series.measure`: patch against west block, unit phasors.
- **Check first:** at L = 4 the 14–26 Jul pair should give a step close to the GUNW value (−2.91 rad, −5.6 cm). If it is off by more than 1 rad, method 1 is reported as not working and not used.
- **Target:** a value is reported only if patch and reference consistency are both ≥ 0.6 (the same rule as before) at L = 2 or L = 4. Otherwise the fraction of patch pixels whose 10 m neighbourhood (3 × 3) has coherence ≥ 0.5 and the median phase change between neighbouring 10 m pixels are reported, to describe why it is unreadable.

## Method 2 — offset tracking on brightness

Amplitude of each image. Square windows of 48 × 48 pixels (240 m) on a grid every 10 pixels (50 m). Normalised cross-correlation within ±16 pixels (±80 m), peak refined by a parabola fit. A point counts if the peak correlation is ≥ 0.2.
- Bulk shift removed: the median offset of all counted points outside 1 km of the patch centre is subtracted.
- Patch offset: median east and north offset of counted points whose window centre lies in the patch box; uncertainty = 1.4826 × median absolute deviation / √n.
- Controls: all counted points more than 1 km from the patch centre, same pair.
- **Outcome for the target pair:**
  - **Measured:** at least 5 patch points, the patch offset magnitude is at or above the 95th percentile of control magnitudes, and it is at least 3 times the patch magnitude in 14–26 Jul. Reported as east, north, size in metres and per day.
  - **Not distinguishable:** at least 5 patch points but either test fails. An upper bound (magnitude + 2 × uncertainty) is reported.
  - **Not trackable:** fewer than 5 patch points.
- Offsets in a geocoded image are apparent map shifts, a mix of true movement and the radar's viewing geometry. They are not reported as ground displacement.
- The published 0.96 m is a comparison only; nothing is tuned to reach it.

Script: `scripts/gap_check.py`.

## Results (run once, 15 Nov 2026; `data/gap/gap_check_table.txt`)

Patch: 2,256 pixels at 5 m (the 141 pixels at 20 m). Reference: 8,160 pixels.

| Pair | Phase, 10 m: step (rad), consistency patch / ref | Phase, 20 m: step, consistency | Patch area coherent at 10 m | Offsets: patch points, east / north (m), size ± uncertainty | Percentile among controls | Control 95th pct |
|---|---|---|---:|---|---:|---:|
| 2–14 Jul | +0.20, 0.45 / 0.68 | +0.17, 0.63 / 0.85 | 37% | 76, +0.30 / +0.13, 0.32 ± 0.08 | 28 | 5.7 m |
| 14–26 Jul | −2.85, 0.64 / 0.68 | −2.78, 0.76 / 0.86 | 78% | 91, +0.09 / +0.39, 0.40 ± 0.03 | 52 | 4.1 m |
| **26 Jul – 19 Aug** | −0.11, 0.24 / 0.61 | +0.13, 0.22 / 0.79 | 51% | 94, −0.22 / −0.26, 0.34 ± 0.09 | 34 | 5.0 m |
| 19–31 Aug | +1.20, 0.06 / 0.04 | +0.83, 0.09 / 0.08 | 1% | 0 (too few) | | 15.1 m |

**Outcomes as defined above:**

- **Method 1 check passes.** The GSLC images, a different product from the GUNW interferogram, give −2.78 rad for 14–26 Jul at 20 m (GUNW: −2.91 rad) and −2.85 rad at 10 m. This is an independent reproduction of the July step from the full-resolution images.
- **Method 1, target: no value.** 26 Jul – 19 Aug is not readable at 10 m or 20 m (patch consistency 0.24 and 0.22). Half the patch is coherent at 10 m, so the images still match locally; the phase changes from place to place inside the patch (median 0.75 rad between neighbouring 10 m cells, against 0.52 in 14–26 Jul). That fits uneven movement inside the patch, but noise is not excluded, and no amount is read from it.
- **Method 2: not distinguishable.** The patch's apparent shift is 0.34 ± 0.09 m, ordinary among the controls (34th percentile), and not 3 times its 14–26 Jul value. Upper bound: **about 0.5 m of apparent map shift** in 24 days.
- **Noise level of the offsets:** in 2–14 Jul and 14–26 Jul, when phase shows at most about 6 cm, the same tracking gives 0.32 and 0.40 m. So shifts below about 0.4 m cannot be seen with this method on this patch.

**Reading.** At 5 m the blind 24 days stay blind: the phase cannot be read and the offsets show nothing above their noise. A shift of about 0.5 m or more of the patch as a whole would probably have shown. A preprint quotes 0.96 m in these 24 days from NISAR offsets (read only through a secondary summary); our result is in some tension with that figure, but the measurements differ (their area, window and product are not known to us; ours is an apparent map shift of this 0.056 km² patch). We do not claim either is wrong.
