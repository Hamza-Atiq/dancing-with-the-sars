# Spec: SlopeWatch — did NISAR see Langtang coming, and what else would it flag?

Version 2, 15 Nov 2026. Author: Claude. Reviewed by Codex (read-only); its points are applied here and listed in `project/review-codex-spec.md`.

## 1. Purpose

A reproducible analysis and a static web app for the NASA Space Apps 2026 challenge "Dancing with the SARs". It answers two questions with public NISAR standard products:

1. **Langtang case.** Is slope movement visible on the north face of Langtang Lirung in the passes before the 26 Aug 2026 collapse, and when does it first appear?
2. **Watch list.** If the same simple rule had been run on every pass over the surrounding 30 km window for a year, what would it have flagged, and how many flags are not Langtang?

The product is a research demonstrator. It is not a warning service and makes no forecast.

## 2. What the research supports (basis for the design)

Established by `Langtang verification - Claude.md`:

- The 20 m wrapped interferogram in GUNW products shows a compact patch (about 0.06 km², near 355500 E, 3130000 N, UTM 45N) with no comparable phase offset against the reference in 2–14 Jul (four of five references), a wrapped-phase step equivalent to about 5 cm line-of-sight in 14–26 Jul (4.7–5.6 cm across five references; the value is near half a cycle, so sign and exact amount are ambiguous by one cycle), and spatially mixed wrapped phase in 26 Jul–19 Aug whose magnitude is unresolved. Codex reproduced these numbers with separate code.
- The 80 m unwrapped layer discards this patch (connected component 0). It must not be used for detection.
- Backscatter (GCOV) changes by more than 3 dB in 41% of the UNOSAT polygon across the collapse, against 18.5% in a quiet interval; 97 shifted control polygons never exceed +8.7 points.
- Standard offsets (GOFF) do not show the precursor on this slope.
- A single-pair anomaly rule fires on glaciers every pass (23–130 blobs per pair in a prototype). "New movement where it was quiet before" is the necessary discriminator.

Not established, and to be stated in the app: that the phase step is ground movement rather than atmosphere, residual topography, layover or a change of scatterers (the pattern matches the published analysis, which is the main support); a proven onset date; direction of motion, three-dimensional displacement, amount of movement in the final 24 days, atmospheric contribution, performance anywhere outside this window, and whether products were publicly available in time.

## 3. Data

| Input | Source | Use |
|---|---|---|
| GUNW 20 m wrapped interferogram + coherence, track 098 A 016, 26 pairs, 28 Nov 2025 – 18 Oct 2026 | ASF, fetched by `scripts/series_fetch.py` into `data/series/` | main analysis |
| Same, track 048 D 074, 8 pairs, 29 Jun – 15 Oct 2026 | same | second look direction (report whatever it shows, including nothing) |
| GCOV 10 m HH/HV, six dates 14 Jul – 24 Sep | `data/lang/` (existing) | collapse scar and debris change map |
| UNOSAT detachment polygon | `data/lang_sources/detachment*.geojson` | context outline, labelled preliminary |

Version rule: forward-processed (`P`) product where one exists, otherwise reprocessed (`X`); the choice and alternatives are recorded per file. Pairs before 20 Jun 2026 exist only as `X` (processed after the event); the app says so.

Window: 85.33–85.62 E, 28.20–28.37 N. Grid: EPSG:32645, 20 m.

## 4. Analysis

### 4.1 Phase anomaly (per pair)
Definitions, per pair:
- **valid pixel:** wrapped value finite and non-zero, coherence finite and in (0, 1], and, where the product carries a mask on the wrapped grid, the mask decodes as valid land in both acquisitions (`scripts/lang_quality.py` decoding: subswath digits 1–5, no water, no anomaly bits). Where no mask is stored, this is recorded in the output and the first two conditions apply.
- `p` = wrapped / |wrapped| on valid pixels, 0 elsewhere (unit phasor); `c` = coherence on valid pixels, 0 elsewhere.
- local signal `s` = Σ(c·p) / Σ(c) over a 100 m box (5×5 pixels); requires at least 13 valid pixels of 25.
- background `b` = Σ(c·p) / Σ(c) over a 1.5 km box (75×75) excluding the inner 5×5; requires at least 20% valid pixels.
- anomaly `a` = angle(s · conj(b)), radians; line-of-sight equivalent = a · λ / 4π (λ = 24.2 cm). Wrapped: |a| ≤ π.
- **local consistency** = |s| (coherence-weighted resultant length, 0–1); **local coherence** = mean of `c` over valid pixels in the box; **background strength** = |b|.
- a pixel is **measurable** when sample counts are met, local consistency ≥ 0.6, local coherence ≥ 0.35 and background strength ≥ 0.3.

The background removes long-wavelength atmosphere and ionosphere. It does not remove effects that vary within 1.5 km (local atmosphere, residual topography), and the background itself may contain moving ground. Sensitivity to the background box (1.0 / 1.5 / 2.5 km) is reported.

### 4.2 Detector ("new movement")
A pixel is **flagged** in pair *k* when all hold:
1. measurable in pair *k* and |a| ≥ 1.5 rad (2.9 cm);
2. **quiet history:** in the previous four pairs it was measurable in at least two, and |a| < 0.75 rad in every pair where it was measurable.
Flagged pixels are grouped into connected blobs; blobs of at least 40 pixels (0.016 km²) are **flags**. Each flag records date, centroid, area, mean |a|, and how many consecutive pairs it persists.

**Calibration and freeze.** The rule is calibrated on the six pairs 8 Jun – 31 Aug only (`pipeline/calibrate.py`, results in `project/results.md`): it must be shown what it does at the measured Langtang patch in 14–26 Jul with these exact boxes and thresholds, since the detector is not the same calculation as the fixed patch/reference measurement. Thresholds may be adjusted in this step and every tried setting is recorded. The rule is then frozen and the year-long evaluation is run once. Because the rule is calibrated on Langtang, its detection of Langtang is not an independent test; the independent information is what else it flags.

Time handling: pairs are consecutive acquisitions; history means the four preceding pairs in acquisition order regardless of their length. Pair length (12 or 24 days) is recorded with every flag and flag counts are reported per pair with its length, never pooled without it. Anomaly signs are not compared between pairs; only |a| is used. A blob that overlaps a blob flagged in the preceding pair is marked "continuing". A sensitivity table varies each threshold one at a time (|a| 1.0/1.5/2.0; quiet limit 0.5/0.75/1.0; blob size 20/40/80) and reports the results without choosing a winner.

Known blind spots, stated in the app: motion faster than half a fringe per pair aliases; ground that was never coherent cannot be flagged; snow cover in winter reduces measurable area; the first four pairs of the record have no history.

### 4.3 Evaluation (reported, pass or fail)
- Is the Langtang patch flagged in 14–26 Jul? In 26 Jul–19 Aug? In any earlier pair?
- Total flags per pair and over the year, inside and outside a 1 km radius of the patch; rank of the Langtang flag by area and by mean |a|.
- **Unverified flags** per km² of eligible ground per pass. Non-Langtang flags have not been checked and are not called false alarms. Eligible ground = pixels with a qualifying quiet history, reported separately from measurable ground.
- Negative controls: the fixed-patch measurement repeated on patches of the same size on coherent slopes elsewhere in the window, for 2–14 Jul and 14–26 Jul.
- Fraction of the window measurable per pair.

### 4.4 Langtang time series
Fixed patch and reference from the verification record. Per pair: patch-minus-reference phase, consistency, line-of-sight equivalent, for all 26 ascending pairs, against five references. For 26 Jul–19 Aug, attempt two-dimensional unwrapping of the 20 m phase in the patch; report a number only if two independent seeds/paths agree within a quarter cycle, otherwise report "spatially mixed phase, magnitude unresolved". The chart draws no value for an unresolved pair; it marks it as unresolved. Descending pairs: same measurement if the patch is measurable; otherwise report unmeasurable.

### 4.5 Collapse map
Backscatter change 19 → 31 Aug (HH, 50 m box), with the quiet 14 → 26 Jul map for comparison and the control-polygon statistic.

## 5. App

Static site in `docs/` (works from GitHub Pages or `python -m http.server`). No server code, no build step. Leaflet 1.9.4 from cdnjs, satellite basemap tiles, all analysis layers as PNG overlays reprojected to latitude/longitude plus small JSON files, all generated by the pipeline.

Sections on one page:
1. **Header and finding.** One-sentence result with the measured numbers.
2. **Map with timeline.** Slider over the 26 ascending pairs. Layer choice: phase anomaly, wrapped phase, coherence, flags. Fixed overlays: patch outline, UNOSAT outline (labelled preliminary), collapse backscatter change. Jump buttons: "Langtang slope", "Whole window".
3. **Slope history chart.** Wrapped-phase line-of-sight equivalent per pair for the patch across the year (points only where consistency ≥ 0.6; unresolved pairs marked, not plotted as values), consistency shown, collapse date marked, 24-day gap marked.
4. **Watch list.** Table of flags for the selected pair and a year summary (flags per pass, Langtang rank). Clicking a flag zooms the map.
5. **What this does not show.** The limits from sections 2 and 4.2, in plain words.
6. **Method and sources.** Links to the repo records and data sources.

Requirements: readable on a phone (map above, panels below); keyboard-operable slider; colour scales with legends and units; every number shown comes from a pipeline JSON file, none typed by hand; total size under 30 MB.

Wording rules: "phase step equivalent to X cm along the line of sight" not "moved X cm"; no proven onset date, direction or lead time; pairs processed after the event are labelled; "line-of-sight change" not "displacement" or "sinking"; "flag" not "warning" or "alert"; no casualty figures; no claim about what authorities could have done.

## 6. Repository layout

```
pipeline/   geo.py (transforms, reprojection), anomaly.py, detect.py, calibrate.py, series.py, collapse.py, render.py, build.py (runs all)
tests/      unit tests on synthetic data (pytest)
docs/       index.html, app.js, style.css, data/*.json, data/img/*.png
project/    spec.md, plan.md, review notes
```
Python: Anaconda with numpy, scipy, PIL, h5py only (matplotlib, pandas, rasterio, pyproj are unavailable).

## 7. Acceptance

- `python pipeline/build.py` regenerates everything in `docs/data` from `data/`.
- Tests pass: synthetic patch recovered by the anomaly and detector code; glacier-like persistent anomaly not flagged; coordinate transform agrees with `scripts/utm.py` and GDAL-exported polygon to 1 cm; overlay bounds place the UNOSAT polygon correctly.
- Pipeline reproduces the verification numbers (2–14 Jul about 0.6 cm, 14–26 Jul about −5.6 cm against the west block).
- App loads without console errors, slider and layers work, every evaluation number in 4.3 is displayed whether favourable or not.
- Results recorded in `project/results.md`; `HANDOFF.md` updated.

## 8. Changes made during the build (v2 → as built)

- §4.2: `min_history_measurable` is 1, not 2 (calibration, `project/results.md` section 1). Parameters frozen in `pipeline/params.json`.
- §4.4: a number from the unwrapping attempt is reported only if the pair is also readable by the consistency rule. Per-pair control ranking added.
- §4.3: negative controls implemented as boxes of the patch size on a 1 km grid (`pipeline/series.py`).
- §5: Leaflet is vendored in `docs/vendor` instead of loaded from cdnjs. Anomaly and coherence images are stored at 40 m; wrapped phase at 20 m. Images are WebP.
- §5: the chart also shows, per readable pair, the level 95% of control slopes stay below.
- §6: added `pipeline/calibrate_try.py`, `pipeline/write_results.py`, `tests/test_real.py`.
