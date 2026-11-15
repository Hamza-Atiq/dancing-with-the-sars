# Glacier research — 14 Nov 2026

Started after the first Quetta test came back inconclusive. Catalogue figures are from NASA CMR point queries; event facts are from news search results and are not independently confirmed.

## 1. Why the Quetta test is inconclusive so far
- Nine consecutive GUNW pairs on track 041 A 017 (17 Jun → 15 Oct 2026) were cut to a 110 km window and summed.
- Mean coherence per pair 0.61–0.69. Per-pair spread after removing a plane: 1.6–5.2 cm.
- Cumulative background spread (more than 30 km from Quetta): 5.0 cm raw, 4.7 cm after subtracting the ionosphere screen. Expected sinking over the same period is about 5 cm.
- The summed map follows topography (positive over ranges, negative over the Sibi lowland): stratified tropospheric delay changing between June and October.
- Within 12 km of the city centre: median +1.9 cm, extremes −7.4 to +12.5 cm. No bowl is distinguishable.
- Not yet done: troposphere and solid-earth-tide correction (the cubes `hydrostaticTroposphericPhaseScreen`, `wetTroposphericPhaseScreen`, `slantRangeSolidEarthTidesPhase` are in each file's `metadata/radarGrid` and have been extracted), sign convention check, local referencing to bedrock.

## 2. How many glaciers
- Randolph Glacier Inventory 7.0: 274,531 glacier outlines in 20 first-order regions; Alaska alone has 27,509. Global area not retrieved.

## 3. NISAR coverage at 16 glaciers (Provisional collections, point queries)
GOFF is the pixel-offset product intended for ice motion. "Best track" is the track with the most distinct dates.

| Glacier | GOFF granules | Tracks | Best track, distinct dates | Date span |
|---|---|---|---|---|
| Baltoro, Karakoram | 32 | 2 | 055 A 020, 9 | 18 Jun – 9 Oct 2026 |
| Batura, Hunza | 31 | 3 | 055 A 020, 9 | 18 Jun – 4 Oct |
| Hispar | 48 | 4 | 055 A 020, 9 | 18 Jun – 9 Oct |
| Siachen | 58 | 6 | 055 A 019, 9 | 18 Jun – 9 Oct |
| Shishper | 31 | 3 | 055 A 020, 9 | 18 Jun – 4 Oct |
| Khumbu, Everest | 26 | 4 | 170 A 016, 8 | 22 Jun – 8 Oct |
| Fedchenko, Pamir | 42 | 4 | 084 A 021, 9 | 20 Jun – 6 Oct |
| Jakobshavn, Greenland | 36 | 4 | 059 A 037, 9 | 18 Jun – 9 Oct |
| Pine Island, Antarctica | 68 | 8 | 040 D 126, 9 | 17 Jun – 8 Oct |
| Thwaites, Antarctica | 75 | 7 | 106 A 140, 25 | 5 Nov 2025 – 5 Oct 2026 |
| Hubbard, Alaska | 44 | 5 | 063 A 032, 9 | 18 Jun – 7 Oct |
| Malaspina, Alaska | 45 | 5 | 063 A 032, 9 | 18 Jun – 7 Oct |
| Columbia, Alaska | 44 | 6 | 058 D 058, 9 | 18 Jun – 8 Oct |
| Upsala, Patagonia | 26 | 3 | 104 A 153, 9 | 21 Jun – 7 Oct |
| Vatnajökull, Iceland | 118 | 7 | 053 D 056, 27 | 1 Nov 2025 – 9 Oct 2026 |
| Kronebreen, Svalbard | 0 | 0 | – | no GOFF, GUNW or GCOV |

GUNW and GCOV counts are similar at every site. Three places have a much longer record than the rest: Thwaites, Vatnajökull and the Langtang area (below).

## 4. First real ice-motion numbers (one pair each, 17 → 29 Aug 2026)
Offsets come in three layers (`layer1`–`layer3`, increasing window size) with `alongTrackOffset`, `slantRangeOffset` (metres), their variances, `snr`, `correlationSurfacePeak`, on an 80 m grid. Scene-wide median removed; speed = offset magnitude / 12 days, in the radar's own plane, with no quality masking yet.

| Site | Projection | Valid | Layer 3 speed: median | 90th pct | 99th pct |
|---|---|---|---|---|---|
| Hubbard, Alaska (50 km window) | EPSG 3413 polar | 0.97 | 0.07 m/day | 7.7 | 21.9 |
| Baltoro, Karakoram (60 km window) | EPSG 32643 UTM | 0.70 | 0.03 m/day | 0.19 | 9.2 |

- Hubbard: glacier trunks show as smooth fast zones; fjord water is pure noise and must be masked by SNR.
- Baltoro: most of the window is near zero; the fast tail is probably noise, so glacier flow (expected well under 1 m/day) needs masking and a closer look before any claim.
- Both scenes reach the same maximum of about 28.8 m/day, which looks like the search-window limit, not real motion.
- Arrows in the public GOFF preview at Baltoro are uniform across the scene: a bulk image shift, not glacier flow.

## 5. Documented 2026 glacier events with NISAR coverage

### Langtang Lirung, Nepal — 26 Aug 2026 (point 85.52 E, 28.25 N)
- Search results: a collapse / ice-rock avalanche on Langtang Lirung on 26 Aug 2026 fell about 1,300 m, became a debris flow and flood that travelled about 100 km; a landslide dam on the Lhende Khola is reported; sources disagree on whether it was a glacial lake outburst and on the toll (at least 300 dead and 900 missing in one, more than a thousand in another).
- Track 098 A 016: 27 distinct GCOV dates from 28 Nov 2025 to 18 Oct 2026, every 12 days apart from the instrument gap. This is a year-long record, unlike most sites.
- Track 048 D 074: 9 dates, 29 Jun – 15 Oct 2026, alternating dual-pol and quad-pol.
- Pairs bracketing the event: 16 → 28 Aug (track 048) and 19 → 31 Aug (track 098), in GOFF and GUNW.
- `NISAR_UR_L2` (Urgent Response) has 32 granules at this point, the first on 28 Aug 2026 and none earlier. A third track, 149 D 074, covers the valley downstream.
- Public previews around the event are too coarse (about 200 m per pixel) to show the change; track 048's quad-pol dates have a dark no-data stripe through the crop.

### Suicide Basin / Mendenhall, Juneau — Aug 2026 (point −134.50, 58.46)
- Search results: glacial outburst flood, crest 14.7 ft, state disaster declaration; reported 11 Aug 2026.
- Five tracks, 9–10 dates each from 17 Jun to 21 Oct 2026. Nearest passes: 10 and 11 Aug, then 15, 16, 17 Aug.
- No Urgent Response granules.
- The instrument gap (27 Jul – 10 Aug) removes most of the basin-filling period.

## 6. Other angles found
- **Validation source:** NASA ITS_LIVE publishes glacier velocities from optical and Sentinel-1 data; a 2026 preprint validates it against GNSS. No published NISAR glacier velocity results or GOFF accuracy figures were found.
- **Karakoram surges:** inventories count between 187 and 354 surge-type glaciers depending on criteria; 74 surge events in 2000–2020; cycles of 15–20 years at Khurdopin, Shishper, Kyager, Chilinji. No per-day velocities retrieved.
- **Karakoram Highway hazard:** KKH closed Sost–Khunjerab by landslides in Sept 2026; the Shishper outburst flood was Aug 2025.

## 7. Candidate glacier project shapes

| Shape | Data in hand | Independent check | Main risk |
|---|---|---|---|
| Langtang collapse, before and after | Year-long stack, bracketing pairs, urgent-response scenes | USGS, Nature and other published analyses; optical imagery | Steep terrain causes layover and shadow; small source area |
| World glacier speed atlas (5–8 glaciers) | GOFF at every site tested | ITS_LIVE velocities | Needs SNR masking and conversion to ground velocity |
| Karakoram glacier pulse (Baltoro, Hispar, Batura, Shishper) | 9 dates each | ITS_LIVE; surge inventories | Slow flow close to noise in first read |
| Seasonal speed-up at Vatnajökull or Thwaites | 25–27 dates | ITS_LIVE; published records | Far from the team's home region |
| Juneau outburst flood | 5 tracks | USGS gauge, NWS | Gap removes the filling period |

## 8. Independent verification by Codex
Run with `gpt-6-sol` at low effort (two earlier attempts failed on the unsupported name `gpt-6.1-sol`). Codex could not reach the CMR endpoint from its sandbox, so the catalogue claims remain checked by one party only.

| Claim | Codex verdict | Notes |
|---|---|---|
| GOFF counts at 13 glaciers; nothing at Kronebreen | Could not check | No network access to CMR |
| Date ranges; 25–27 dates at Thwaites and Vatnajökull | Could not check | same |
| Langtang tracks and pairs bracketing 26 Aug | Could not check | same |
| Urgent Response: 32 granules at Langtang, none at Juneau | Could not check | same |
| Langtang collapse and Juneau flood | Partly confirmed | See corrections below |
| RGI 7.0: 274,531 outlines, 20 regions | Confirmed | RGI 7.0 user guide; region 20 (Antarctic mainland) has 0 outlines |
| GOFF structure and projections | Partly confirmed | ASF docs confirm 80 m posting, SNR layers, EPSG 3413 north of 60°N and UTM between 60°S and 60°N; `layer1`–`layer3` and dataset names not confirmed by Codex (they were read directly from the HDF5 files in section 4) |

Corrections and additions from Codex:
- **Langtang mechanism:** ICIMOD dates the flood to 26 Aug 2026, identifies a collapse on Langtang Lirung's north face, describes a rock and ice avalanche that became a debris flow with a possible temporary river blockage, and says it was not a glacial lake outburst at the source.
- **Langtang toll:** ICIMOD-linked reports give "at least 95 dead, nearly 400 missing" initially and "over 390 dead, over 1,400 missing" later. These differ from the figures in section 5; no single agreed number exists.
- **Juneau date:** the US National Weather Service reports the Suicide Basin release on 13 Aug 2026 with a 14.7 ft crest, not 11 Aug as written in section 5. The nearest NISAR passes are therefore 10–11 Aug before and 15–17 Aug after.
- A CMR point hit means the granule footprint touches the point, not that usable offset pixels exist over the glacier.
- ASF cautions that GOFF layers contain outliers and are distributed without conventional noise filtering.
- Which track actually covers each glacier body was not checked by either party.
