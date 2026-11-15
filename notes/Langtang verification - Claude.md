# Langtang: independent verification of the Codex continuation, 14 Nov 2026

Claude's check of `Langtang continuation - Codex.md` and `Langtang local verification - Codex.md`. All numbers below were recomputed with new code (`scripts/verify_*.py`) from the raw extracts in `data/lang`, not by rerunning Codex's scripts.

## Verdict

Codex's bookkeeping is sound, but its main scientific conclusion is wrong. It reported that the published precursor "has not been reproduced". The precursor is clearly present in the standard NISAR product we already extracted. Codex missed it because its quality filter removed the moving ground before any measurement was made.

## What Codex got wrong

**1. The filter excluded the signal.** Codex kept only 80 m pixels with coherence ≥ 0.6 and connected component 1. A slope moving several centimetres between passes has low coherence at 80 m and fails unwrapping. In the moving patch, all 42 of the 80 m pixels have connected component 0 in every pair, and at most 4 reach coherence 0.6. The "19 of 307 usable pixels" are the stable leftovers. Codex's own `local_phase_diagnostic.png` shows the whole collapse area greyed out.

**2. It took a median over an area far larger than the moving patch.** The UNOSAT polygon is 1.96 km². The Brencher figure shows a moving patch roughly 600 m across inside a collapse outline of about 1 km. A polygon-wide median cannot show a patch that is a small fraction of the polygon. The same applies to the offset (GOFF) medians.

**3. It never looked at the 20 m wrapped interferogram as a map.** That layer was in every extract (`wrapped`, `wcoh`). Codex only summarised its coherence.

## What the 20 m wrapped phase shows

Patch: 355250–355800 E, 3129780–3130250 N (UTM 45N), pixels with 20 m coherence ≥ 0.45 in the 14–26 July pair (141 pixels, 0.056 km²), in the south-east corner of the UNOSAT polygon. Reference: coherent rock 300–600 m to the west (354650–354980 E, 3129900–3130500 N, 510 pixels). Phase is the patch minus the reference, averaged as complex numbers. L-band wavelength 24.2 cm, so one full cycle is 12.1 cm along the line of sight.

| Pair | Days | Patch phase vs reference | Line-of-sight equivalent | Consistency (0–1) | Reading |
|---|---:|---:|---:|---:|---|
| 8–20 Jun | 12 | +0.22 rad | — | 0.20 | patch not coherent |
| 20 Jun–2 Jul | 12 | −0.03 rad | — | 0.41 | patch weakly coherent, no offset |
| 2–14 Jul | 12 | +0.33 rad | 0.6 cm | 0.89 | no movement |
| 14–26 Jul | 12 | −2.91 rad | 5.6 cm (0.47 cm/day) | 0.83 | clear movement |
| 26 Jul–19 Aug | 24 | mixed | more than one cycle | 0.37 | several fringes across the patch; coherent (median 0.53) but aliased |
| 19–31 Aug | 12 | — | — | 0.15 | surface destroyed |

This matches the Brencher figure in pattern and size: nothing in 2–14 July, about 0.4–0.5 cm/day in 14–26 July, faster in 26 July–19 August. Images: `previews/lang_verify_phase_zoom.png` (close-up with coordinates) and `previews/lang_verify_phase_wide.png`.

### Reference-area test

Same patch, five reference areas (the west block, and four quadrants of a 0.7–2.5 km ring using pixels with 20 m coherence ≥ 0.7 in both pairs):

| Reference | 2–14 Jul | 14–26 Jul |
|---|---:|---:|
| West block (510 px) | +0.6 cm | −5.6 cm |
| Ring north (1,982 px) | +0.8 cm | −4.8 cm |
| Ring south (191 px) | +0.4 cm | −4.7 cm |
| Ring east (2,073 px) | −4.5 cm | −4.7 cm |
| Ring west (1,066 px) | +1.1 cm | −5.0 cm |

The 14–26 July step is 4.7–5.6 cm against every reference. The 2–14 July value is near zero against four of five. The east ring disagrees in that pair; its own phase is the least uniform (consistency 0.70) and the wide map shows a different phase over the terrain east of the slope in that pair, so the east ring is a poor reference there. This is unresolved, not dismissed.

### Limits of this result
- The patch was drawn after seeing the signal in the 14–26 July map. The coherence threshold was applied on that same pair. The 2–14 July "no movement" value is measured on the same pixels, which is the fair comparison.
- −2.91 rad is close to half a cycle, so the sign and the exact value are ambiguous by one cycle (5.6 cm one way or 6.5 cm the other). Colour gradients at the patch edge suggest the −2.9 reading. Direction (toward or away from the satellite) is not verified.
- The 26 July–19 August amount cannot be read from a wrapped average. It needs fringe counting or unwrapping at 20 m, or offsets.
- The reference block is inside the UNOSAT polygon and lost coherence after the event. It is adjacent rock, not proven stable ground.
- No atmospheric correction. Over 500 m this is small compared with a half-cycle step that appears in one pair and not the previous one.
- My patch (0.056 km²) is smaller than the published one. Only the coherent core was selected.
- One track, one look direction.

## What Codex got right (confirmed)

- **Backscatter change.** Recomputed with a different rasteriser: HH 18.54% → 41.11%, HV 18.67% → 36.43% of pixels changing by more than 3 dB (Codex: 18.55 → 41.22, 18.60 → 36.57; differences are edge pixels).
- **New control test (Codex listed this as missing).** The same polygon shape moved to 97 other positions in the window: the event-minus-quiet difference never exceeds +8.7 points (HH) or +7.7 (HV). At the collapse it is +22.6 and +17.8. The collapse stands well outside the background.
- All 18 extracts present and readable; grids match.
- UNOSAT polygon is broad and preliminary; the 24-day gap and two-track coverage mean no four-day cadence claim.
- Researcher is George Brencher; figure scale is cm/day.
- Offsets (GOFF) in the standard product are noisy on the slope. My maps (`previews/lang_verify_offsets.png`) show a steady glacier-flow signal east of the polygon in all three intervals and no clear acceleration. I agree offsets alone do not show the precursor here.

## Not checked by me
- Codex's descending-track mask results, the P05023 vs X05026 comparison, processing dates and the mask decoders. I read the code and found no error but did not recompute them.
- The primary sources Codex cites (UW article, Roy et al., Pramanik et al., Zenodo archives) beyond viewing the saved figures.

## Consequence for the project

The original question, "could NISAR have seen it coming?", has a supportable answer from public standard products: the slope shows no movement in early July, about 5–6 cm in 12 days in mid-July, and more than a cycle in the last 24 days. Codex's recommendation to fall back to a "change-and-data-quality explorer" was based on the wrong negative result.

## Path forward

1. **Harden the precursor result.** Count fringes or unwrap the 26 July–19 August pair at 20 m; extend the patch time series back to November 2025 (27 dates on track 098) to show the slope was quiet for months; test several reference areas; check the descending 23 July–16 August pair at 20 m for a second look direction.
2. **Build the detector.** A simple rule on the 20 m wrapped layer: a compact area that is coherent, has a phase step against its surroundings, and where the step grows between consecutive pairs. Tune nothing on Langtang beyond what is needed, then run it over the whole 30 km window to count false alarms.
3. **Test elsewhere.** Run the same rule over other steep glacierised slopes (other High Mountain Asia frames) to see what a watch list would contain.
4. **Build the app.** Langtang story (before, precursor, collapse, debris path) plus the watch-list map, with every limit stated.
