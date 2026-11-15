# Independent test of the frozen rule — Budhi Gandaki, 11 Oct 2026

**Status: rules written and committed on 15 Nov 2026 before any radar data of this area was opened.** Only the NASA catalogue (granule names and times) was looked at. Results go in a section below this one, without changing anything above it.

## Why this case

The rule in `pipeline/params.json` was tuned on Langtang, so its Langtang flag is not a fair test. A fair test is a slope that failed which the rule has never seen.

- **Event:** rock slope failure that became a rock avalanche and debris flow, Budhi Gandaki valley, Gorkha district, Nepal. The flood reached Chumchet at about 04:00 Nepal time on 11 Oct 2026 (22:15 UTC on 10 Oct). The failure itself happened some time before that; its exact time is not known to us.
- **Source:** scar at about 28.5336 N, 84.9345 E (D. Petley, Landslide Blog, from a Sentinel-2 image of 21 Oct), south side of Chamar mountain; about 500 m wide and 850 m long, crown about 6,600 m, toe about 5,400 m. A government technical report describes ice and debris at about 5,500 m in the upper Ungdilung Khola.
- **Sources:** https://eos.org/thelandslideblog/budhi-gandaki-2 and https://eos.org/thelandslideblog/the-11-october-2026-landslide-and-debris-flow-flood-on-the-budhi-gandaki-river-in-gorkha-district-nepal
- **Why it is fair:** different slope, about 60 km west of Langtang, never used in calibration. Same product (NISAR GUNW, 20 m wrapped interferogram) and the ascending track is the same frame as Langtang (098 A 016).
- **Considered and rejected:** Hanjia, Chongqing, 17 Jul 2026 (NISAR coverage starts 19–27 Jun there, so at most two pairs exist before the event and the rule needs four earlier pairs). Palos Verdes (moving continuously, so never "quiet"; the rule is not built for it).

## Data (from the catalogue)

| Track | Pairs | Last pair ending before the flood | Pair spanning the event |
|---|---|---|---|
| 098 A 016 | 26, 28 Nov 2025 – 18 Oct 2026 | 24 Sep – 6 Oct (ends 23:39 UTC 6 Oct, about 4 days before) | 6 – 18 Oct |
| 149 D 074 | 8, 24 Jun – 10 Oct | 28 Sep – 10 Oct (ends 13:06 UTC 10 Oct, about 9 hours before the flood) | none |
| 048 D 074 | 8, 29 Jun – 15 Oct | 21 Sep – 3 Oct (ends 12:58 UTC 3 Oct) | 3 – 15 Oct |

Version rule as for Langtang: forward-processed `P` products first, `X` otherwise.

## Rules (fixed now)

1. **Window:** 84.79–85.08 E, 28.45–28.62 N (same size as the Langtang window, 0.29° × 0.17°).
2. **Rule:** `pipeline/params.json` unchanged, `pipeline/anomaly.py` and `pipeline/detect.py` unchanged, run on each track's pairs in time order, exactly as the Langtang year-long run. The rule's sizes are in pixels; it is applied only to grids with 20 m spacing (the grid it was tuned on). A track with another spacing is reported as not tested.
3. **Source zone:** all pixels within 600 m of 28.5336 N, 84.9345 E (half the 850 m length plus about 175 m for the uncertainty of a coordinate read from imagery).
4. **Outcome per track**, using pairs that end before the failure:
   - **HIT** — a flag (a group of at least 40 flagged pixels) with at least one pixel inside the source zone, in a pair that ends before the failure.
   - **MISS** — no such flag, although at least one pre-event pair had eligible pixels in the source zone (quiet history and measurable now).
   - **NOT TESTABLE** — no pre-event pair had any eligible pixel in the source zone.
   Overall: HIT if any track is a HIT; MISS if no HIT and at least one MISS; otherwise NOT TESTABLE.
5. **Pair 28 Sep – 10 Oct on track 149 D** counts as pre-event unless a source shows the failure happened before 13:06 UTC on 10 Oct. If the source zone's coherence collapses in that pair (median coherence below half its median over the four pairs before), the failure may already have happened, and the pair is reported but not counted for HIT or MISS.
6. **Also reported, whatever they are:** flags elsewhere in the window in every pair (the false-alarm load); measurable and eligible pixels in the source zone per pair; which pair, if any, shows the source zone losing coherence (the event itself).
7. A HIT would show that the rule can flag a slope it was not tuned on. It would not show that the flag could be told apart from the others in the same pair, and one case is not a detection rate. A MISS or NOT TESTABLE is reported as plainly.

Scripts: `scripts/indep_catalogue.py` (catalogue), `scripts/indep_fetch.py` (data), `scripts/indep_run.py` (rule and outcome).
