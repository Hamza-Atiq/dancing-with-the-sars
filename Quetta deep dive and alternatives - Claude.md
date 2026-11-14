# Quetta deep dive and multi-angle research — 14 Nov 2026

Continues `Independent verification - Claude.md`. Preview images are in `previews/`.

## 1. Correction accepted from Codex
Granule counts can overstate visits. At the Hunza point, 18 GCOV granules on track 055 A 020 come from 10 distinct dates. Same at Quetta: track 020 D 073 has two granules on 7 Sep 2026. Use distinct dates, not granule counts.

## 2. Everything NISAR holds over the Quetta valley
Search box 66.80–67.20 E, 30.00–30.45 N. The valley straddles two frames on two of the tracks.

| Collection | Granules | Notes |
|---|---|---|
| GUNW Provisional | 52 | 6 track-frames, pairs listed below |
| GUNW Beta | 10 | ascending only, Nov 2025 – Jan 2026, CRID X05010 |
| GUNW Validated | 0 | |
| GCOV Provisional | 58 | 9–10 dates per track-frame |
| GCOV Beta | 13 | ascending only, Nov 2025 – Jan 2026 |
| GCOV Validated | 4 | 22–27 Oct 2026 |
| GSLC Provisional / Validated | 58 / 6 | |
| RSLC Provisional | 59 | |
| SME2 Provisional | 58 | |
| GOFF, RIFG, RUNW Provisional | 0 | |
| Urgent Response L1/L2 | 0 | |
| OPERA DISP-S1 | 0 | |

No data at all between 12 Jan 2026 and 17 Jun 2026.

### GUNW Provisional pairs (12-day nearest neighbour, HH, full frame, CRID P05023)
- **041 A 017** (40 MHz): 17 Jun→29 Jun, 29 Jun→11 Jul, 11 Jul→23 Jul, 23 Jul→16 Aug (24 days, spans the instrument gap), 16 Aug→28 Aug, 28 Aug→9 Sep, 9 Sep→21 Sep, 21 Sep→3 Oct, 3 Oct→15 Oct. 9 pairs, unbroken chain.
- **142 A 016 and 017** (40 MHz): 24 Jun→6 Jul, 6 Jul→18 Jul, 18 Jul→11 Aug (24 days), 11 Aug→23 Aug, 23 Aug→4 Sep, 4 Sep→16 Sep, 16 Sep→28 Sep, 28 Sep→10 Oct. 8 pairs each.
- **092 D 073 and 074** (20 MHz, one pair at 40): 20 Jun→2 Jul, 2 Jul→14 Jul, 14 Jul→26 Jul, 26 Jul→19 Aug (24 days), 19 Aug→31 Aug, 31 Aug→12 Sep, 12 Sep→24 Sep, 24 Sep→6 Oct, 6 Oct→18 Oct. 9 pairs each.
- **020 D 073** (20 MHz, one pair at 40): 27 Jun→9 Jul, 9 Jul→21 Jul, 21 Jul→14 Aug (24 days), 14 Aug→26 Aug, 26 Aug→7 Sep (two granules), 7 Sep→19 Sep, 19 Sep→1 Oct, 1 Oct→13 Oct. 8 distinct pairs.

GCOV modes: ascending tracks are always `4005 DHDH` (10 m, HH/HV). Descending tracks alternate `4005 DHDH` and `2005 QPDH` (20 m, quad-pol) on successive passes.

### File facts
- One GUNW .h5 is 2.3 GB. All 52 would be about 120 GB; D: has 83 GB free. Subsetting or streaming is required.
- Each granule ships a QA report PDF, QA stats, QA summary CSV, KML and two browse PNGs. Only the browse PNGs are public.
- QA summary for 041 A 017, 17→29 Jun: file opens; 47–51 % of pixels are NaN or fill (the frame is rotated inside its grid); the `identification` group check is marked FAIL; all other checks PASS.

### What the GUNW product contains (ASF GUNW page)
- Unwrapped phase in radians at 80 m; wrapped interferogram and coherence at 20 m; connected components; pixel offsets; ionospheric phase screen with uncertainty.
- Ionosphere is estimated but not applied. Troposphere and solid-earth-tide tables are supplied but not removed.
- Only co-pol, only frequency A, only 12-day pairs.
- HDF5 dataset names, phase sign convention and reference point are not on that page. They are in the product specification PDF, not yet read.

### What the public previews show
- Coherence is high across the arid basin; phase is smooth rather than noisy.
- Each single 12-day pair is dominated by broad atmospheric or ionospheric patterns that change sign from pair to pair. No Quetta subsidence bowl is visible by eye.
- Expected signal: 12–16 cm/yr is 4–5 mm per 12 days, about 5 cm over June–October. One L-band fringe is 12 cm of range change, so each pair holds about 1/25 of a fringe. Detection needs stacking and ionosphere correction.
- Track 142: Quetta sits near the eastern swath edge, and two pairs show a sharp straight phase discontinuity across the crop.
- Track 092 D 073, 6→18 Oct: four dark no-data stripes cross the frame.
- Track 041 A 017 looks cleanest and has the unbroken 9-pair chain.

## 3. Published ground truth for Quetta
- Kakar, Zhao, Li, Zhao, *Remote Sensing* 16(9):1521, 2024. SBAS-InSAR on Sentinel-1 (195 ascending, 183 descending scenes, Dec 2015 – Dec 2022) with GNSS and piezometers, Quetta and Mastung. Continuous GNSS in central Quetta: 2 m cumulative Oct 2008 – Jan 2023; acceleration from 12 to 16.6 cm/yr after 2016. Groundwater decline 1.7–6 m (1987–2022). Fissures damage infrastructure and contaminate the aquifer.
- *Natural Hazards* 2025 (s11069-025-07226-y). Maximum −11.4 cm/yr (2003–2010), −12 (2010–2016), −16 after 2016; −273 cm cumulative 2003–2023; Mastung −14.1 cm/yr, Gulistan −13 cm/yr.
- Earlier PS-InSAR, 2014–2016: about 12.5 cm/yr.
- Full texts not read; figures come from abstracts and search snippets.

## 4. Electricity–water link in Balochistan (news, search-result level)
- Federal government paid Rs 500 billion over a decade in electricity bills for Balochistan tubewells; a $197 million plan (July 2024) to solarise 27,000 tubewells.
- Ministry of Water Resources opposed the solarisation in Oct 2024, citing water-table decline.
- Dawn, April 2026: Quetta valley wells may run dry in 5–10 years; drop of 2–5 m per year; more than 30,000 illegal tubewells.
- Express Tribune, Nov 2025: subsidised solar has intensified extraction.
- No QESCO-specific 2025–26 figures found.

## 5. Other directions examined

| Direction | Data checked | Independent reference | Assessment |
|---|---|---|---|
| Lahore subsidence | 2 tracks, 9 GUNW pairs each | Sentinel-1 studies disagree: −20 to −114 mm/yr | Weaker signal than Quetta, urban and vegetated, inconsistent reference values |
| Karachi subsidence | 2 tracks, 8–12 pairs | 15–17 mm/yr (Tirmizi 2023; IGARSS 2018) | About 6 mm over the window; too small for four months of L-band |
| Manchar Lake / Indus water extent | GCOV previews, 9 dates on 164 D 075 | OPERA DSWx-S1 (89,665 granules in the Pakistan box) | Lake and river channel visibly change between dates; Manchar is at the swath edge on this track; the gap removes 27 Jul – 10 Aug |
| Sukkur / Indus channel | GCOV previews, 9 dates | same | Channel change visible; a dark data stripe crosses several dates |
| Hunza glaciers and Karakoram Highway | GCOV previews, 10 dates on 055 A 020 | Sept 2026: KKH closed Sost–Khunjerab by landslides; the Shishper outburst flood was Aug 2025 | Test point is at the swath edge; steep terrain; no confirmed 2026 event at the site |
| Soil moisture (SME2) | 1,808 granules in Pakistan box, 58 at Quetta | none identified | 200 m, Provisional only; a supporting layer rather than a headline |
| Quad-pol land cover | `2005 QPDH` on descending tracks every second pass | none identified | Context layer for any site |

No published NISAR study over Pakistan, the Karakoram or the Indus was found.

## 6. Other documents read
- Subsidence white paper (2017, 2 pages): gives no NISAR rates or accuracy figures; examples are New Orleans (UAVSAR, Jones et al. 2016), Millennium Tower, Washington Monument (about 2 inches); states that slow subsidence needs many repeated images over several years.
- Drought and Groundwater Withdrawal white paper (2017): over-pumping collapses aquifer pores and permanently cuts storage; the California Aqueduct sank more than 12 inches beside a pumping bowl (Farr et al. 2015); time series separate long-term decline from the seasonal cycle.
- ARSET "Identifying Disaster Extent and Risk Using NISAR Surface Displacement": Part 1 was 12 Nov 2026, Part 2 is 19 Nov 2026; instructors Erika Podest and Eric Fielding; QGIS demo; Part 1 slides PDF (7.9 MB) is published but not yet read.
- Land Subsidence StoryMap: the page is script-rendered and returned only its title; still unread.
- ASF access page: Vertex, Earthdata Search, Worldview, asf_search, earthaccess, S3, GDAL vsicurl, Harmony; `.netrc` with `machine urs.earthdata.nasa.gov`.

## 7. Access status
- Earthdata Login verified in Chrome; a protected QA CSV downloaded through it.
- Scripted access not set up: no `.netrc`; `earthaccess` and `asf_search` not installed; `h5py` 3.16 is present.

## 8. Not done
- No science file opened yet.
- GUNW product specification PDF, ARSET slides, the 5 StoryMaps, and the other 24 white papers unread.
- Full texts of the Quetta papers unread.
