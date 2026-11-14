# Plan: SlopeWatch build

Follows `project/spec.md` v2 (after Codex review). Each step ends with a check and a line in `project/progress.md`. Commit after each numbered step.

Run everything with `C:/Users/HP/anaconda3/python.exe` from the repo root.

## Step 0 — Data (running)
- `scripts/series_fetch.py` fetches 34 pairs into `data/series/` (log: `data/series_fetch.log`). Re-running skips finished files.
- Check: 26 ascending + 8 descending `.npz`, each with a `.json` sidecar; all ascending grids identical; whether a wrapped-grid mask exists; processing version per pair; for the pairs that also exist in `data/lang`, compare the series file with the old extract (identical or not, and by how much in the patch measurement).

## Step 1 — `pipeline/geo.py` + tests
- Vectorised forward UTM (numpy), inverse UTM (series formula), `reproject(a, x, y, epsg, bounds, shape)` nearest-neighbour to a latitude/longitude grid, polygon rasteriser, UTM→lon/lat for outlines.
- Tests: agreement with `scripts/utm.py` < 1 mm; round trip < 1 mm; GDAL-exported polygon vertices < 1 cm; a known pixel lands at the right overlay position.

## Step 2 — `pipeline/anomaly.py` + tests
- `load_pair`, `anomaly(pair)` → anomaly phase, consistency, local coherence, background magnitude, measurable mask (spec 4.1).
- Tests on synthetic interferograms: flat phase + ramp + noise gives anomaly ≈ 0; inserted 30×30-pixel patch with 2.5 rad step is recovered within 0.3 rad; low-coherence area is not measurable.

## Step 3 — `pipeline/detect.py` + tests
- `detect(stack)` implementing spec 4.2 with parameters in one dictionary; blob labelling; persistence count; sensitivity sweep.
- Tests: new patch after quiet history → flagged once; patch anomalous in every pair (glacier) → never flagged; patch with no measurable history → not flagged; blob below size limit → not flagged.

## Step 3b — `pipeline/calibrate.py` (added after Codex review)
- Run anomaly + detector on the six old pairs (`data/lang`, 8 Jun – 31 Aug). Report: anomaly and measurability at the Langtang patch per pair; whether and where the rule flags it; all other flags; effect of background box 1.0/1.5/2.5 km. Record every setting tried in `project/results.md`. Freeze parameters in `pipeline/params.json`.
- Tests on real crops: the Langtang patch region in 14–26 Jul has |a| > 1.5 rad on most measurable pixels; a step close to π does not produce sign-flip artefacts in |a|; invalid pixels are excluded.

## Step 4 — `pipeline/series.py`
- Fixed patch/reference time series for all pairs and five references (spec 4.4); unwrapping attempt for the 24-day pair with the agreement rule; descending measurement.
- Check: reproduces +0.6 cm and −5.6 cm (west block) from the verification record, using `data/series` files. If the `P` product gives slightly different numbers from the old extract, record both.

## Step 5 — `pipeline/collapse.py`
- Backscatter change maps and control-polygon statistics (port of `scripts/verify_bs.py`).
- Check: HH 18.5% → 41.1%; control maximum +8.7.

## Step 6 — Run detector on the year; evaluation
- Run with the predeclared thresholds. Write `docs/data/flags.json`, `evaluation.json`, `sensitivity.json`.
- Record results in `project/results.md` exactly as they come out. If Langtang is not flagged, that is the result; do not retune. Any change to the rule after seeing year-long results must be listed in `results.md` as a post-hoc change with before/after numbers.

## Step 7 — `pipeline/render.py` + `build.py`
- Per pair: anomaly, wrapped phase, coherence PNGs (RGBA, reprojected, window-wide at about 20 m; transparent where not measurable). Collapse change PNGs. Outlines as GeoJSON in lon/lat. `manifest.json` listing pairs, bounds, legends.
- Check: total `docs/data` size < 30 MB; UNOSAT outline overlays the backscatter scar when viewed.

## Step 8 — App (`docs/`)
- `index.html`, `style.css`, `app.js` per spec section 5. Leaflet from cdnjs. All numbers read from JSON.
- Check in a real browser (Playwright): no console errors; slider changes overlay; flag click zooms; phone-width layout; outlines align with image features at three separate places (patch, debris path, a ridge far from the centre); screenshot saved to `previews/`.

## Step 9 — Review and records
- Codex review of code and results (independent recomputation of two headline numbers).
- `project/results.md`, `HANDOFF.md`, `README.md` updated; commit and push.

## Order and dependencies
Steps 1–3 and 5 do not need the fetch and start immediately. Steps 4, 6, 7 need Step 0. Step 8 can be built against partial data and finalised after Step 7.

## Risks
- Fetch failures or slow transfers: script retries and skips; the app works with however many pairs exist, and states the count.
- Winter snow makes early pairs unmeasurable: reported as measurable fraction, not hidden.
- Detector may flag many glacier margins: reported; sensitivity table shows the trade-off.
- Unwrapping the 24-day pair may be unreliable: fall back to "more than one fringe".
