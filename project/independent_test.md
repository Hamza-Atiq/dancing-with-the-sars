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

## Results (run once, 15 Nov 2026; `data/indep_bg/indep_result.txt`, `data/indep_bg/indep_result.json`)

All 42 pairs were fetched (`P05023` from 20 Jun, `X05026` before, as for Langtang); all three tracks have 20 m grids, so the rule was applied on every track. The source zone (600 m around the scar) has about 2,830 pixels on each ascending and 149 D grid; on 048 D most of it is outside valid data until mid-August.

**Outcome by the rules as written: HIT** (track 098 A). Track 149 D: MISS. Track 048 D: MISS.

| Track | Pre-event pairs counted | Pairs with the zone eligible | Flag in the zone | Flags in the window (pairs with history) |
|---|---:|---:|---|---:|
| 098 A | 21 (15 Jan – 6 Oct) | 21 | **one, in 27 Jan – 8 Feb 2026** (91 pixels, mean 2.46 rad, centre 107 m from the scar point) | 329 in 22 pairs, median 9 |
| 149 D | 4 (23 Aug – 10 Oct) | 4 | none | 50 in 4 pairs, median 14.5 |
| 048 D | 3 (28 Aug – 3 Oct) | 2 | none | 33 in 4 pairs, median 7.5 |

- **The only flag at the source is 8 months before the failure**, in winter. In every one of the last 20 ascending pairs (8 Feb – 6 Oct), including the last four after the monsoon, the zone was measurable and eligible (700–2,000 pixels) and **no flag was raised there**. The descending pair ending about 9 hours before the flood (28 Sep – 10 Oct, 837 eligible pixels) raised no flag at the source.
- **The pair spanning the event (6 – 18 Oct, track 098 A)** shows zone coherence 0.30, against a median of about 0.36 in the four pairs before; this is not a collapse by rule 5, and the failure is not obvious in the coherence at this scale.
- **The weakness of the rule as written.** Rule 4 counted any pre-event pair, however early. A flag 8 months before a failure, followed by 20 quiet pairs, is not a warning of that failure. This was not foreseen when the rules were written; the outcome is reported as "HIT" because that is what the rule says, and explained here.

### Added after seeing the result: how often does chance give the same?

Not part of the rules above (`scripts/indep_chance.py`, `data/indep_bg/indep_chance.json`). 2,000 zones of the same size placed at random on eligible ground of the same 098 A window (at least 2 km from the scar), same 21 counted pairs:

- **42% of random zones collect at least one flag** in some counted pair. One flag in 21 pairs is what chance gives.
- 13% of random zones collect a flag in the last four pre-event pairs; the real source collected none.

**Reading.** On a slope the rule had never seen, it raised nothing before the failure that stands out from chance: one winter flag 8 months early (as likely as not for any spot of this size) and silence in the eight months before the failure, on all three tracks. **This is not an independent detection.** It does not show the rule is useless either: the Budhi Gandaki source is at 5,400–6,600 m on a snow and ice face, where any precursor may have been fast, brittle or hidden in snow; and one case is not a rate. What it does show is that the Langtang flag cannot be taken as evidence that the rule works elsewhere.
