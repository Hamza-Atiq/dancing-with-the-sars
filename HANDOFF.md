# Handoff — state on 15 Nov 2026

Read this first when resuming. Then `project/spec.md`, `project/plan.md`, `project/progress.md` (running log), `project/results.md` (all numbers).

## What exists

**SlopeWatch**: a reproducible analysis plus a static web app about the Langtang Lirung collapse (Nepal, 26 Aug 2026).

- App: `docs/` (static; `cd docs && python -m http.server 8765`, open http://127.0.0.1:8765/). Data for the app is in `docs/data` and is committed. Could be served by GitHub Pages from `/docs` (not enabled; needs the repo owner).
- Pipeline: `pipeline/build.py` regenerates `docs/data` from `data/` (about 8 minutes). `pipeline/write_results.py` regenerates the numeric sections of `project/results.md`.
- Tests: `python -m pytest tests -q` (19 tests; real-data tests skip if `data/` is absent).
- Raw extracts: `data/` (not in git). `data/series/` holds 34 interferogram windows fetched by `scripts/series_fetch.py`.
- Python: `C:/Users/HP/anaconda3/python.exe` (numpy, scipy, PIL, h5py work; matplotlib, pandas, skimage, rasterio, pyproj do not).

## Results in brief (details and caveats in `project/results.md`)

1. **Precursor present in standard products.** In the 20 m wrapped interferogram, a 0.056 km² patch on the slope shows a phase step equivalent to 4.7–5.6 cm line of sight in 14–26 Jul (five references agree), 0.6 cm in 2–14 Jul. It is the only pair in the year in which the patch exceeds every comparable slope (0 of 361). The 80 m unwrapped layer discards the patch; that caused Codex's earlier negative result. Codex has since reproduced the numbers.
2. **Final 24 days unresolved.** 26 Jul–19 Aug has spatially mixed phase; no value is reported.
3. **Winter observation, open.** The patch was readable in nine pairs from 28 Nov to 16 Mar with steps of 0.2–2.3 cm, mostly one sign, above the controls' 95% level in four pairs but never above all controls. Could be slow movement, snow, or topographic residual. Not claimed as a finding.
4. **Detector.** A "new movement" rule (frozen after calibration on Langtang) run over 22 pairs flags Langtang in exactly one pair (14–26 Jul) and raises 270 flags in total (median 6.5 per pass); the other 268 are unverified and cluster in spring and autumn.
5. **Collapse.** Backscatter change inside the UNOSAT polygon rises from 18.6% to 41.2% of pixels; 97 control areas rise by at most 8.5 points.
6. **No second look direction.** Descending track has valid data over the patch in one of eight pairs, and it is not readable there.

## What is not established

Ground movement as the cause of the phase step; direction and true size; onset date; anything about lead time or availability of products at the time; meaning of the other flags; performance anywhere else. The rule was tuned on Langtang, so its Langtang flag is not an independent detection.

## Data hunt, 15 Nov (session 3) — record: `Langtang data hunt - Claude.md`

- **Location confirmed.** Our patch centre is 44 m from Li (2026)'s mapped centroid and 147 m from the HiRISK position (both read from Sah's preprint).
- **NISAR:** still only tracks 098 A and 048 D. New validated GCOV/GSLC dates to 11 Nov. No product fills the 27 Jul – 10 Aug gap. GSLC (full resolution) is unused and available.
- **Sentinel-1 was not used before and covers the source on three tracks**, with passes on 31 Jul, 4, 7, 12, 16 Aug (inside NISAR's gap) and 24 Aug (50.6 h before failure). `scripts/s1_hyp3.py` is ready to order 24 burst interferograms from ASF HyP3.
- **Waiting on the user:** approve the ASF application once at `https://urs.earthdata.nasa.gov/approve_app?client_id=BO_n7nTIlMljdvU6kRRB3g`, then run `python scripts/s1_hyp3.py submit`, later `status` and `download`. Then measure the patch in the Sentinel-1 wrapped phase with the session-2 method.
- ALOS-2 ends Mar 2025 at this point; RCM and SAOCOM catalogues need their own logins and were not searched.

## Suggested next steps (none started)

1. **Independent test of the frozen rule** on a second, unrelated slope failure or a known slow landslide with NISAR coverage. This is what would make the watch-list idea credible.
2. Look at a sample of the 268 other flags against optical imagery to classify them (glacier margin, snow, real movement).
3. Follow up the winter observation: same patch measurement with a terrain model to test elevation-correlated phase; compare with snow data.
4. Quantify 26 Jul–19 Aug with proper unwrapping or offsets from higher-resolution products (RSLC/GSLC).
5. Enable GitHub Pages for `docs/`, update the team brief artifact (https://claude.ai/artifact/4VJB2yVSicxijtiRJvZFQ5 still describes Quetta), prepare the submission text and demo video.

## Decisions on record

- Working project: Langtang. Quetta subsidence paused (nine-pair stack dominated by atmosphere; details in `Quetta deep dive and alternatives - Claude.md`, kept locally and not in the public repository since 15 Nov). Fallbacks: glacier speed atlas; Manchar Lake.
- Wording rules for anything public: "phase step equivalent to X cm along the line of sight", "flag" not "warning", no casualty figures, no claims about what could have been done.
- Detector parameters are frozen (`pipeline/params.json`). Any change must be recorded in `project/results.md` section 6 with before/after numbers.

## Tooling notes

- Earthdata Login is in `C:\Users\HP\.netrc` (never print or commit it). `scripts/nisar_io.py` reads NISAR HDF5 remotely.
- In this environment bash heredocs fail on some content; write scripts to files instead.
- Codex plugin: model `gpt-6-sol` works; ask for read-only reviews and keep it out of `data/` while jobs run.
- Earlier records kept for provenance: `Langtang verification - Claude.md`, `Langtang local verification - Codex.md`, `Langtang continuation - Codex.md`, `Langtang collapse - Claude.md`.
