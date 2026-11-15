# Independent verification of the Codex notes — 14 Nov 2026

Method: link targets were scraped from the live challenge Resources tab in Chrome. Each was then fetched directly. The NISAR catalog was queried through NASA's CMR API (the backend of Earthdata Search and Vertex), not through the search UIs.

## 1. The 14 links as they actually appear on the challenge page

| # | Resource | Real target | Status |
|---|---|---|---|
| 1 | Earthdata Search | search.earthdata.nasa.gov/search | Checked via CMR API, UI not driven |
| 2 | ASF Vertex | search.asf.alaska.edu | Same catalog as CMR, UI not driven |
| 3 | NISAR Data User Guide | nisar-docs.asf.alaska.edu | Read: home, availability, products, GCOV, known issues |
| 4 | Intro to Remote Sensing | earthdata.nasa.gov/learn/earth-observation-data-basics/remote-sensing | Read; lands on the broader "Earth Observation Data Basics" hub |
| 5 | Intro to SAR | earthdata.nasa.gov/learn/earth-observation-data-basics/sar | Read |
| 6 | ARSET | appliedsciences.nasa.gov/get-involved/training → 301 → earthdata.nasa.gov/data/projects/arset | Read |
| 7 | StoryMaps | nisar.jpl.nasa.gov/applications/arcgis-storymaps → 301 → science.nasa.gov/mission/nisar/arcgis-storymaps | Index read; the 5 stories themselves not opened |
| 8 | White papers | nisar.jpl.nasa.gov/applications/societal-benefit → 301 → science.nasa.gov/mission/nisar/societal-benefits | Index read (26 PDFs); PDFs not opened |
| 9 | UAVSAR postcards | uavsar.jpl.nasa.gov/education/postcards.html | Read (18 postcards) |
| 10 | RCM data | donnees-data.asc-csa.gc.ca/en/dataset/rcm | Read in Chrome |
| 11 | CSA SAR tutorial | github.com/asc-csa/Synthetic_Aperture_Radar_Tutorial | README read |
| 12 | RADARSAT-1 | donnees-data.asc-csa.gc.ca/en/dataset/radarsat1 | Read in Chrome |
| 13 | SAOCOM catalogue | catalogos.conae.gov.ar/catalogo/catalogoSatSaocomInfo.html | Read |
| 14 | SAOCOM registration | argentina.gob.ar/noticias/la-informacion-saocom-cada-vez-mas-accesible | Read |

## 2. Codex claims that hold

- 52 collections match "NISAR" in the catalog; `NISAR_L2_GCOV_PROVISIONAL_V1` has 163,672 granules.
- Release timeline: samples 23 Jan 2026; Beta 27 Feb 2026 (acquisitions 17 Oct 2025 – 20 Jan 2026); Provisional 20 Jul 2026 (CRID P05023); Validated 6 Nov 2026 (CRID P05036, acquisitions from 21 Oct 2026, Levels 0–2 only).
- Permanent instrument gap 2026-07-27T22:03:25Z to 2026-08-10T00:55:27Z.
- Validated SME2 soil moisture is pending until 2027.
- GCOV pixel spacing 10/20/80 m by bandwidth; GUNW 80 m; SME2 200 m.
- SAOCOM open registration covers archive products over Argentina only.
- RCM: certain products are public through EODMS under a user licence.
- Downloads need Earthdata Login (confirmed: the .h5 redirects to urs.earthdata.nasa.gov; browse PNGs are public).

## 3. Where Codex is wrong, imprecise, or unverified

- Several URLs in its table are not the challenge's links (Vertex, ARSET, StoryMaps, white papers, RCM, RADARSAT-1 were swapped for other pages).
- It recommends the validated short name `NISAR_L2_GUNW_V1`. That collection has 140 granules worldwide and none over Pakistan. `NISAR_L2_GOFF_V1` has 32. Interferometry work must use the Provisional collections.
- "SAOCOM 1A and 1B": the catalogue page names only SAOCOM-1A.
- "One Click route described by CONAE": the linked article does not use that term (it is the challenge page's wording).
- "About 1.8 million images" for RADARSAT-1 is not on the linked page; unverified.
- SME2 spacing is 500 m over the Sahara, not 200 m everywhere.
- The power-line conclusions (no wire detection, no buried-fault detection) are physically sound at 10 m pixels and 24 cm wavelength, but they are reasoning, not tested results.

## 4. What Codex did not find

### Pakistan coverage (it left this "still open")
Bounding box 60.8–77.9 E, 23.6–37.1 N (includes border strips of neighbours).

| Collection | Global | Pakistan box | Pakistan dates |
|---|---|---|---|
| GCOV Provisional | 163,672 | 1,978 | 2025-10-29 → 2026-10-21 |
| GCOV Validated | 15,358 | 194 | 2026-10-22 → 2026-11-11 |
| GCOV Beta | 23,527 | 391 | 2025-10-17 → 2026-01-20 |
| GUNW Provisional | 94,150 | 1,676 | 2025-10-29 → 2026-10-09 |
| GUNW Validated | 140 | 0 | – |
| GSLC Provisional | 162,907 | 1,965 | 2025-10-29 → 2026-10-21 |
| GOFF Provisional | 27,717 | 432 | 2025-11-17 → 2026-10-09 |
| SME2 Provisional | 103,943 | 1,808 | 2025-10-29 → 2026-10-21 |
| Urgent Response L2 | 6,794 | 298 | 2026-07-06 → 2026-11-13 |
| OPERA DSWx-S1 | 5,363,680 | 89,665 | 2024-08-21 → 2026-11-14 |
| OPERA DISP-S1 | 205,761 | 0 | – |

GCOV Provisional per month over the box: 2025-11: 24, 12: 28, 2026-01: 38, 02: 38, 03: 30, 04: 37, 05: 44, 06: 247, 07: 389, 08: 309, 09: 484, 10: 309. Dense 12-day sampling starts mid-June 2026.

### Repeat stacks at specific sites (GCOV Provisional; add 1–2 Validated scenes after 21 Oct)

| Site | Track / direction / frame | Scenes | Span |
|---|---|---|---|
| Sukkur, Indus | 041 A 015 | 10 | 17 Jun – 15 Oct |
| | 164 D 075 | 13 | 25 Jun – 11 Oct |
| Manchar Lake | 092 D 075, 142 A 015, 164 D 075 | 10, 9, 10 | 20 Jun – 18 Oct |
| Karachi | 092 D 076, 142 A 014 | 15, 9 | 20 Jun – 18 Oct |
| Lahore | 084 A 017, 135 D 073 | 10, 10 | 20 Jun – 21 Oct |
| Quetta | 020 D 073, 041 A 017, 092 D 073, 142 A 017 | 10, 10, 10, 9 | 17 Jun – 18 Oct |
| Islamabad | 063 D 072, 084 A 018, 084 A 019 | 15, 10, 9 | 18 Jun – 18 Oct |
| Gilgit / Hunza | 055 A 020, 063 D 070, 156 A 020 | 18, 10, 8 | 18 Jun – 16 Oct |

GUNW Provisional pairs exist on the same tracks (8–12 per track, 16 at Hunza), ending early October.

### Other findings
- Usual mode over Pakistan is `4005 DHDH`: 40 MHz + 5 MHz, dual-pol HH/HV, so GCOV at 10 m. Some scenes are quad-pol (`2005 QPDH`, e.g. track 092 D 075 on 18 Oct 2026).
- Urgent Response collections (`NISAR_UR_L1`, `NISAR_UR_L2`, `NISAR_UR_L0B_RRSD`) exist and are active to 14 Nov 2026. Most of the 298 in the box sit over north India and the Karakoram.
- The instrument gap (27 Jul – 10 Aug) falls inside the 2026 monsoon peak.
- Known-issues page lists only two items for Validated data: incomplete L0B products (resolved in P05036; in Provisional data it shows as defocused RSLC, missing data, InSAR decorrelation) and the instrument gap.
- GCOV layout: HDF5, `/science/LSAR/GCOV/grids/frequency[A|B]/`, layers HHHH, HVHV, VVVV (+ off-diagonals for quad-pol only), `mask`, `numberOfLooks`, `rtcGammaToSigmaFactor`; gamma-0, terrain corrected with Copernicus DEM, UTM projection.
- Two NISAR-specific ARSET trainings: "Monitoring Surface Water with SAR for Water Resource Management" (20–27 Oct 2026, NISAR + OPERA surface water) and "Identifying Disaster Extent and Risk Using NISAR Surface Displacement" (12–19 Nov 2026).
- StoryMaps: exactly 5 (Floods, Wildfires, Oil Slicks, Glacial Motion, Land Subsidence).
- White papers: 26 (21 from 2017, 3 from 2019, 1 from 2022, 1 from 2023), including Floods, Subsidence, Levees and Dams, Drought and Groundwater Withdrawal, Food Security, Damage Mapping.
- RADARSAT-1 is on EODMS and AWS as TIFF, with a Python tutorial; the page lists region "Canada".
- CSA tutorial uses one RCM3 scene of British Columbia wildfires, GDAL + cartopy, modified MIT licence.
- 2026 monsoon news (search results, headline level): NDMA toll 126 by 2 Aug and 136 by 3 Aug, Punjab worst hit; a 26 Jul report said major river flows were "within safe limits"; an Express Tribune headline of 2 Aug says electrocution was the top cause of deaths.

## 5. Not done
- Earthdata Search and Vertex UIs were not clicked through.
- The 5 StoryMaps, the 26 white-paper PDFs and the two ARSET course pages were not read in full.
- No NISAR science file has been opened; that needs an Earthdata Login.
