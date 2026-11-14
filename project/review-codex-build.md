# Codex review of the build and results — 15 Nov 2026

Read-only review requested by Claude after the full-year build. Codex changed no files.

## Independent recomputation (Codex's own code, pipeline modules not imported)

- **Detector, 14–26 Jul, frozen rule:** 4 flags in the window. Two have centroids within 300 m of the patch box: 57 pixels at about (355657, 3130071) and 41 pixels at (355141, 3129602). The other two have 60 and 47 pixels. No discrepancy with the claim.
- **Control comparison, 14–26 Jul:** Langtang patch 2.9073 rad; 361 controls readable in that pair; 0 at or above Langtang; control maximum 1.3468 rad. No discrepancy. (The 289 figure in results section 3 is the stricter set readable in both July pairs.)

## Code review

No verified numerical bug in `anomaly.py`, `detect.py`, `series.py`, `build.py`, `geo.py`, `render.py`. History slice uses exactly the four preceding pairs; mask decoding and box sums match the stated rule; labelling is four-connected; grids are checked; no orientation, centroid, pair-ordering or reprojection error found.

## Results record against shipped data

The winter observation is supported by `series.json` (nine readable pairs, 0.2–2.3 cm, first five negative, four above the control 95% level, none above all controls) and is appropriately left open. Detector totals and sensitivity figures match the JSON.

## Points raised and what was done

| Priority | Point | Action |
|---|---|---|
| Must fix | `project/spec.md` §4.2 still said two measurable history pairs; code and §8 use one | Fixed in the spec text |
| Should fix | "Rule not changed after the year-long run" cannot be proven from the JSON files alone | Checked git: it does not prove the order either (the frozen `params.json` first appears in commit `4eb4ad5` together with the year-long results, because the intended freeze commit missed the file). `results.md` section 6 now states this plainly and lists what can be checked instead |
| Should fix | "Every number from JSON" is not literally met: case dates (14–26 Jul, 26 Aug), the 24-day gap, product resolutions (20 m, 80 m, 10 m), window size and the 95% wording are typed in the app | Spec §5 reworded: every *result value* comes from JSON; fixed case identifiers and product constants are text |
| Optional | 289 vs 361 controls can look contradictory | App headline now says the 289 are slopes readable in both July passes |
