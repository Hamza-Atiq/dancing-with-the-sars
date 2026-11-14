# Quetta deep dive — independent verification

November 14, 2026. I checked [Claude Code's Quetta notes](Quetta%20deep%20dive%20and%20alternatives%20-%20Claude.md) against NASA's catalog, the saved browse images, the published Quetta studies, and agency documentation.

## What NASA's catalog confirms

I ran live NASA CMR queries using the same rectangle, 66.80°E to 67.20°E and 30.00°N to 30.45°N. All collection counts listed for Quetta in Claude's report reproduced. A match means a catalog footprint intersects the rectangle. [NASA CMR API](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html) · [Reproduce the Provisional GUNW query](https://cmr.earthdata.nasa.gov/search/granules.json?short_name=NISAR_L2_GUNW_PROVISIONAL_V1&bounding_box=66.80%2C30.00%2C67.20%2C30.45&page_size=100)

| Product | Provisional | Beta | Validated |
| --- | ---: | ---: | ---: |
| GUNW phase comparison | 52 | 10 | 0 |
| GCOV radar backscatter | 58 | 13 | 4 |
| GSLC map-aligned radar signal | 58 | — | 6 |
| RSLC radar-geometry signal | 59 | — | — |
| SME2 soil moisture | 58 | — | — |

An em dash means the release was outside the scope of the comparison. Provisional GOFF, RIFG and RUNW, Urgent Response L1 and L2, and OPERA DISP-S1 each returned zero matches. For the collections queried, the latest Beta acquisition ended January 12 and the first Provisional acquisition began June 17. That date gap describes these query results and does not establish that every possible data source was empty.

| Track and frame | GUNW granules | Distinct date pairs | First to last observation |
| --- | ---: | ---: | --- |
| 041 A 017 | 9 | 9 | June 17 to October 15 |
| 092 D 073 | 9 | 9 | June 20 to October 18 |
| 092 D 074 | 9 | 9 | June 20 to October 18 |
| 142 A 016 | 8 | 8 | June 24 to October 10 |
| 142 A 017 | 8 | 8 | June 24 to October 10 |
| 020 D 073 | 9 | 8 | June 27 to October 13 |

All 52 Provisional GUNW records have the full-frame code, HH polarization and processing release P05023. Track 020 has two product versions, `001` and `002`, for the same August 26–September 7 pair. Each track-frame has one 24-day pair across the permanent instrument outage. The other pairs are 12 days. ASF's overview describes the standard 12-day cadence. The catalog confirms these local exceptions. Track 041 A 017 has a connected chain of nine pairs and ten observation dates, with one 24-day interval. [ASF GUNW guide](https://nisar-docs.asf.alaska.edu/gunw/) · [ASF outage notice](https://nisar-docs.asf.alaska.edu/nisar-known-issues/)

The Provisional ascending GCOV records in the rectangle all use `4005 DHDH` (10 m on the main band). Descending records commonly use `4005 DHDH` and `2005 QPDH` (20 m on the main band), with exceptions to the alternating pattern. Tracks 092 and 020 have consecutive main-band 40 MHz acquisitions across the gap. Track 020 also has both `4005 SHSH` and `4005 DHDH` on September 7. Use the actual granule settings when comparing intensity. [ASF GCOV layer and naming guide](https://nisar-docs.asf.alaska.edu/gcov/)

## What the files and previews establish

- CMR's size fields imply about 2.3 GB per GUNW science file, 121 GB for all 52, and 20.9 GB for the nine files on track 041 A 017. Workspace drive D: reported 88.4 GB available during this check. A complete bulk download exceeds that space. ASF documents a Harmony option to extract selected GUNW layers and crop them in Earthdata Search. I did not run a Harmony order. [ASF Harmony guide](https://nisar-docs.asf.alaska.edu/harmony/)
- The June 17–29 track 041 record lists the HDF5, browse and thumbnail images, QA PDF, stats and summary files, and KML. I verified the links in CMR. I did not open the science or protected QA files and cannot confirm the reported 47–51% fill or the failed identification check. Fill over the whole grid would not tell us the usable fraction inside the Quetta study area.
- The [track 041 sheet](previews/sheet_041_A_017.png) shows strong, varying broad phase patterns. The [track 142 sheet](previews/sheet_142_A_017.png) shows sharp discontinuities in two panels. The [track 092 sheet](previews/sheet_092_D_073.png) shows a wide dark strip repeated near the edge. The montage alone cannot confirm its no-data status or the claim of four separate stripes in the October 6–18 pair. The previews also cannot quantify coherence or determine if a broad pattern is atmospheric, ionospheric, or ground motion. Track 041 is a sensible first test based on its connected, consistent-mode chain.
- ASF confirms 80 m unwrapped phase, 20 m wrapped interferogram, coherence at 20 and 80 m, connected components, and an ionospheric estimate that is supplied separately. The listed troposphere and solid-Earth-tide corrections, where available, are also unapplied. Test whether the chosen corrections improve consistency. I did not verify the dataset paths, reference convention, or phase-to-displacement sign from the product specification. [ASF GUNW guide](https://nisar-docs.asf.alaska.edu/gunw/)

## What the Quetta studies actually measured

The 2024 study reports about 2 m of cumulative sinking at the permanent QTIT GNSS station from October 2008 to January 2023. The GPS-like ground measurements show about 12 cm/year before 2016 and 16.6 cm/year afterward in the period studied. Those are local historical rates. The groundwater figures are rates with different measurement windows. The paper reports an average 1.7 m/year across monitoring wells for 1987–2021 and up to 6.1 m/year at one well over 2011–2015. The 2025 study reports 273.6 cm from March 2003 to January 2023 by combining Envisat, Sentinel-1 and GNSS. It shares authors and overlaps the earlier study's evidence. Neither paper supplies a 2026 measurement for the NISAR window. [2024 Sentinel-1 and GNSS study](https://www.mdpi.com/2072-4292/16/9/1521) · [2025 multi-sensor study](https://link.springer.com/article/10.1007/s11069-025-07226-y)

If the historical 12–16.6 cm/year **vertical** rate persisted, it would imply roughly 4–5.5 mm of vertical motion in 12 days and 4–5.5 cm over the 120-day track 041 span. NISAR measures the component along its slanted viewing direction. One L-band fringe corresponds to about 12 cm of range change. The fraction of a fringe therefore depends on viewing angle and any horizontal motion. These are estimates of scale, not 2026 results or a detection threshold. [Quetta study's vertical-conversion method](https://www.mdpi.com/2072-4292/16/9/1521) · [NASA on interferometry](https://nisar.jpl.nasa.gov/mission/get-to-know-sar/interferometry/)

The Balochistan Energy Department confirms a plan covering 27,437 agricultural tube wells at a cost of Rs 55 billion. The provincial water policy identifies solar pumping and groundwater depletion as related concerns. Those sources establish the electricity–water context without showing which wells operated near Quetta in 2026 or what caused any observed displacement. I did not verify the other press figures on subsidies, illegal wells, or predicted shortages. [Energy Department](https://energy.balochistan.gov.pk/?page_id=974) · [Balochistan Integrated Water Policy](https://bcsw.balochistan.gov.pk/wp-content/uploads/2025/03/Balochistan-Water-policy-2024.pdf)

## Alternatives and what would settle them

- **Manchar Lake and Sukkur.** The saved thumbnails show changing tones around the water and repeated dark strips at Sukkur. Colors alone do not establish water extent across modes. For June 17 to October 18, CMR returned 17 OPERA DSWx-S1 records on 16 distinct dates at each of the two checked points. For both points, those dates fall in June and September–October, so the reference choice must account for the timing gap. Check the actual comparison area and the usable layers before assigning a water-area change. [OPERA surface-water collection](https://search.earthdata.nasa.gov/search?q=OPERA_L3_DSWX-S1_V1)
- **Karachi and Lahore.** Tirmizi et al. report subsidence up to 17 mm/year at particular Karachi locations. Other studies report higher local rates, including 26–29 mm/year at two measured sites. A Lahore study reports a range from −114 to +15 mm/year over its study area. Results from different places, dates and methods cannot establish a citywide rate or prove four months of NISAR data are unusable. [Karachi multi-track study](https://authors.library.caltech.edu/records/3wdm3-hab57) · [Karachi persistent-scatterer study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8964713/) · [Lahore study](https://doi.org/10.5814/j.issn.1674-764x.2022.05.007)
- **Hunza.** Pakistan's NDMA dates a documented 2025 Shishper outburst to July 20. August reporting also describes Shishper-linked flooding and erosion. Specify the event and exact location before choosing scenes. The claimed September 2026 road closure was not independently tied to the Shishper scene. [NDMA report](https://www.ndma.gov.pk/public/storage/ia-books/February2026/epjfF0hIfEZk9Dc40ADm.pdf)

Quetta has a well-documented history of subsidence and enough repeated NISAR coverage for a focused test. The test is whether the 041 A 017 science layers yield a consistent displacement signal across pairs, relative to a stable reference area, after screening low-quality pixels and checking phase corrections. Historical GNSS and Sentinel-1 give a comparison for the location and order of magnitude. To independently validate a 2026 rate, look for time-matched observations.
