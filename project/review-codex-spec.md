# Codex review of spec v1 and plan — 15 Nov 2026

Read-only review requested by Claude. Codex did not modify files.

## Independent reproduction (Codex's own code)

| Pair | Patch minus reference phase | Patch consistency |
|---|---:|---:|
| 2–14 Jul | +0.327 rad | 0.886 |
| 14–26 Jul | −2.907 rad | 0.829 |
| 26 Jul–19 Aug | −0.122 rad | 0.368 |

Matches Claude's +0.33, −2.91, 0.37. Codex also confirmed all 42 pixels of the 80 m layer in the patch have connected component 0 in all three pairs, with 0, 4 and 1 pixels reaching coherence 0.6, and agrees the earlier negative conclusion was caused by the 80 m coherence/component filter.

Codex's caution: this establishes a localized wrapped-phase anomaly, not yet a validated displacement or acceleration. Open alternatives: atmosphere/ionosphere varying between patch and reference, residual topography, layover and mixed scattering, change of scatterers or snow, processing or mask effects, movement of the reference, selection bias (patch drawn after seeing the 14–26 Jul image), half-cycle sign ambiguity. A consistency of 0.368 in the last pair does not by itself prove more than one fringe.

## Must fix (all applied in spec v2 / plan)

1. Replace "more than one fringe" with "spatially mixed wrapped phase; magnitude unresolved"; no chart value for that interval. → spec §2, §4.4, §5.
2. Define phasor weighting, valid-pixel handling, mask decoding, minimum sample counts. → spec §4.1.
3. Show the detector flags the measured Langtang patch before freezing thresholds; freeze after documented calibration; keep the year-wide evaluation untouched. → spec §4.2, plan Step 3b.
4. Rename "false-alarm rate" to "unverified flags per km² per pass". → spec §4.3.
5. Qualify "no movement in early July" and "5 cm"; no proven onset date, direction or lead time in the app. → spec §2, §5.

## Should fix

- Background box sensitivity and negative-control patches. → applied (spec §4.1, §4.3).
- Temporal behaviour for long gaps and repeat flags; do not compare signs between pairs. → applied (spec §4.2).
- Report eligible ground separately; do not pool 12- and 24-day pairs. → applied (spec §4.3).
- Check version, masks, grids before the time series; record P vs X differences. → applied (plan Step 0).
- Tests on real crops, wrap-boundary patterns, overlay alignment at several places. → applied (plan Steps 3b, 8).

## Optional (not yet done)

- Optical or field corroboration of the patch.
- Uncertainty ranges across patch boundaries and coherence cut-offs.
- Show raw wrapped phase beside the anomaly in the app. → already a layer in the app design.
