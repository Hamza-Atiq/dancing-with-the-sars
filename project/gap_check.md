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
