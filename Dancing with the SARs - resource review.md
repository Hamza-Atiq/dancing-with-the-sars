# Dancing with the SARs — resource review

Live source review, November 14, 2026. This report covers the 14 items in the challenge's data and resources list, plus the Earthdata information page and video shared separately. It examines what each source provides, access conditions, the major NISAR data products, and evidence for the two electrical-engineering ideas.

The [Pakistan catalog verification](#pakistan-catalog-verification) below updates the initial coverage discussion with live catalog results and checks Claude Code's independent notes.

The live challenge Details page confirms that the app should use NISAR to show at least one kind of surface change. It asks teams to pick a study area, describes an open-source and user-friendly outcome, and gives maps, animations, and dashboards as examples. It explicitly presents optical images and geographic layers as supplemental context. One carefully chosen site is a sensible starting point. [Live challenge details](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)

NISAR sends radio waves toward Earth and measures the echoes. Each map pixel combines signals from part of the ground. Brightness depends on the surface, moisture, and how the radar looks at it. Movement can be studied by comparing the phase, or position in the wave cycle, across two suitable observations. A stationary object can be bright or dark. [NASA SAR overview](https://nisar.jpl.nasa.gov/mission/get-to-know-sar/overview/) · [NASA interferometry guide](https://nisar.jpl.nasa.gov/mission/get-to-know-sar/interferometry/)

## Every resource on the challenge list

| Resource | What it gives us | When it helps |
| --- | --- | --- |
| [NASA Earthdata Search](https://search.earthdata.nasa.gov/search) | A catalog of satellite observations, searchable by location and date. | Check whether our chosen place and time have data. |
| [ASF Vertex](https://search.asf.alaska.edu/) | A radar-focused search tool with filters for track, frame, and radar settings. | Find comparable scenes. Either catalog is enough to start. |
| [NISAR Data User Guide](https://nisar-docs.asf.alaska.edu/products-overview/) | A guide to what each file measures. | Choose a file based on the question. |
| [Intro to Remote Sensing](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/remote-sensing) | A primer on measuring Earth from a distance and what image detail means. | Look up concepts as they come up. |
| [Intro to SAR](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar) | A primer on radar waves, echo strength, and polarization. | Understand why the same object can look different. |
| [NASA ARSET trainings](https://appliedsciences.nasa.gov/get-involved/training) | Worked Earth-observation lessons, including radar and flood mapping. | Follow the lesson that matches the research question. |
| [NISAR StoryMaps](https://nisar.jpl.nasa.gov/applications/arcgis-storymaps/) | Interactive examples covering floods, wildfires, sinking ground, oil slicks, and glaciers. | See how maps explain change to a viewer. |
| [NISAR applications white papers](https://nisar.jpl.nasa.gov/applications/societal-benefit/) | Short descriptions of scientific and public uses. | Connect a measurable change to a real problem. |
| [UAVSAR postcards](https://uavsar.jpl.nasa.gov/education/postcards.html) | Example images from airborne radar, with colors representing measurements. | Learn how radar changes can be displayed. |
| [RADARSAT Constellation Mission](https://donnees-data.asc-csa.gc.ca/en/dataset/rcm) | Canadian satellite radar data. Public users can access some products with registration. | Optional comparison if coverage and access fit. |
| [CSA Python/QGIS tutorial](https://github.com/asc-csa/Synthetic_Aperture_Radar_Tutorial) | Worked code and mapping examples with RADARSAT imagery. | Learn a processing workflow after we pick a question. |
| [RADARSAT-1 archive](https://donnees-data.asc-csa.gc.ca/en/dataset/radarsat1) | Open historical Canadian satellite radar imagery. | Optional historical baseline if the location and dates fit. |
| [SAOCOM catalog](https://catalogos.conae.gov.ar/catalogo/catalogoSatSaocomInfo.html) | Argentina's radar imagery catalog with searchable previews. | Optional comparison if suitable images exist. |
| [SAOCOM registration](https://www.argentina.gob.ar/noticias/la-informacion-saocom-cada-vez-mas-accesible) | Instructions for requesting access. CONAE lists conditions for downloads. | Check terms if we decide to use SAOCOM. |

I tried Google Search first and received its automated traffic check, then opened each publisher URL directly in a browser and checked supplemental sources through web search. The browser rendered ASF Vertex, Earthdata Search, the NASA SAR primer, the redirected Remote Sensing and ARSET pages, both NASA application libraries, the UAVSAR gallery, and the Canadian RCM listing. GitHub and both CONAE pages were readable through web retrieval, and the original RADARSAT-1 listing was supplemented by CSA's official access page and catalog index. The YouTube page gave the title but no readable transcript. The separate Earthdata information page failed to load live, so its description uses your pasted copy and ASF's instructions. The report covers all listed resources and the major product families. Individual catalog matches and the dates available at a specific project site require a site-based search.

## Which NISAR measurements fit which question?

- **GCOV** measures echo strength on a map. It is a starting point for changes in water or vegetation. **SME2** estimates soil moisture for questions about how wet the ground is.
- **GUNW** compares two observations to help estimate ground movement along the radar viewing direction. **GOFF** tracks shifts of image features and is primarily meant for ice movement.
- **GSLC** and **RSLC** retain more of the original radar signal for advanced processing. The catalog also has raw signals, calibration, and satellite orbit information for specialized work.
- **OPERA DSWx-S1** labels water using Sentinel-1. It can be an independent comparison if dates overlap. [ASF product guide](https://nisar-docs.asf.alaska.edu/products-overview/)

## The two power-line ideas

**Overhead aviation markers.** Special close-range millimeter-wave radar has detected thin wires in field experiments. Its results do not establish reliable wire detection from NISAR. GCOV data combine echoes over many meters of terrain, and wire returns depend on viewing direction and polarization. A visible tower would not establish the position or height of the wire between towers. Treat satellite observations as research evidence only, and use approved aviation obstacle information and markings for flight safety. [Wire detection field study](https://arxiv.org/abs/2602.03229) · [GCOV guide](https://nisar-docs.asf.alaska.edu/gcov/) · [FAA obstruction marking guidance](https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.current/documentnumber/70_7460-1)

**Buried cable faults.** An electrical fault can leave the surface looking the same. NISAR provides no practical way to trace a buried power cable or determine where it shorted. A time-domain reflectometer uses an echo too, but sends a pulse down the cable and estimates the distance to a fault from the returning signal. The cable route and exact ground location may require separate field tracing. [Cable fault location guide](https://www.megger.com/en-ca/applications/cables/cable-fault-location)

## Research questions to keep open

1. **Flood exposure near power infrastructure in Pakistan.** Can a GCOV before-and-after map identify likely surface water around known infrastructure? Check against a dated independent flood map. Proximity to water shows exposure, while confirming damage requires separate evidence. FAO has demonstrated Sentinel-1 flood mapping in Pakistan. [FAO assessment](https://www.fao.org/geospatial/news/news-detail/fao-releases-geospatial-flood-impact-assessment-for-pakistan--2025/)
2. **Ground movement near infrastructure.** Can GUNW show ground movement near a known corridor that a utility could investigate? Compare with an independent deformation reference. NASA has demonstrated NISAR mapping of subsidence in Mexico City, where sinking ground affects infrastructure. Coverage and reference data for a Pakistani site remain to be checked. [NASA's Mexico City case study](https://www.nasa.gov/missions/nisar/us-indian-space-mission-maps-extreme-subsidence-in-mexico-city/)

Before choosing a project, check for usable NISAR observations, a documented change, and an independent source that can test the result. No imagery has been downloaded or analyzed for these ideas yet.

## Detailed findings from the live sources

### 1. NASA Earthdata Search

The catalog searches collections first and then individual observations within each collection. A rectangle or point on the map filters by place. Dates filter by when the radar collected the observations. Granule IDs can also be filtered with wildcards. These are the filters that matter first. For a two-date comparison, verify that both actual footprints cover the target, even if the frame names match. NASA Earthdata Login is used for downloads. The live browser query for `NISAR_L2_GCOV_V1` returned one matching collection. Your pasted granule screen is evidence for the older Provisional collection's 40-of-163,672 display, which can change. [Live Validated GCOV search](https://search.earthdata.nasa.gov/search?q=NISAR_L2_GCOV_V1) · [ASF walkthrough](https://nisar-docs.asf.alaska.edu/earthdata-search/)

### 2. ASF Data Search Vertex

Vertex offers a NISAR-specific search with science product, maturity, direction, polarization, bandwidth, track, frame, and full or partial frame filters. That makes it easier to compare matching observations and spot partial images. ASF's guide says Vertex serves NISAR L-band. ISRO distributes S-band through Bhoonidhi. Search one catalog first, then use the other if its filters or file options help. [Vertex](https://search.asf.alaska.edu/) · [ASF Vertex documentation](https://nisar-docs.asf.alaska.edu/vertex/) · [NASA mission data page](https://science.nasa.gov/mission/nisar/data/)

### 3. NISAR Data User Guide

The guide covers data availability, technical product definitions, downloads, known issues, analysis techniques, and tutorials. The main product families are below. “Geocoded” means the pixels are arranged on a map grid. Complex data keep both echo strength and phase. Phase is the position within the radio wave's repeating cycle. [Product definitions](https://nisar-docs.asf.alaska.edu/products-overview/)

| Level | Product | What the numbers represent |
| --- | --- | --- |
| 0 | RRSD and associated raw calibration products | Raw radar measurements and calibration data for building specialized processing workflows. |
| 1 | RSLC | Detailed signal from one observation, in the radar's viewing geometry. It is an input to many of the other products. |
| 1 | RIFG and RUNW | Two-date radar comparisons in radar coordinates. The phase wraps like a clock in RIFG. RUNW estimates how many cycles belong in the difference. |
| 1 | ROFF | Estimated shifts of recognizable patterns between two observations, in radar coordinates. |
| 2 | GCOV | Echo power on a geographic grid after corrections for terrain and radar geometry. Many land products have 10 or 20 m pixel spacing, and some use 80 m. This is a starting point for floods, crops, or vegetation disturbance. |
| 2 | GSLC | Detailed echo strength and phase from one observation, on a map grid. Useful for advanced comparisons. |
| 2 | GUNW | Two-date phase differences on a map grid. Useful for measuring displacement in the radar's viewing direction. Coherence helps identify where the comparison is trustworthy. |
| 2 | GOFF | Map-based estimates of feature shifts, primarily designed for ice applications. |
| 3 | SME2 | Estimated soil moisture, with uncertainty information. Grid spacing is 200 m in most regions and 500 m in the Sahara. |

**Release choice matters.** ASF says Validated L-band collections at Levels 0–2 were released November 6, 2026, covering acquisitions from October 21, 2026. Validated Level 3 soil moisture was still pending. The July Provisional release is calibrated and validated at a limited set of sites. It covers routine acquisitions from June 17 through part of October 23, with supplemental earlier time series and a permanent instrument gap from late July 27 through early August 10 UTC. February Beta data cover selected earlier scenes. Differences between processing versions can look like landscape changes, so start with a pair from the same release when possible. For GCOV and GUNW, the validated short names are `NISAR_L2_GCOV_V1` and `NISAR_L2_GUNW_V1`. [Release dates and coverage](https://nisar-docs.asf.alaska.edu/availability-overview/) · [Known issues](https://nisar-docs.asf.alaska.edu/nisar-known-issues/) · [Exact catalog names](https://nisar-docs.asf.alaska.edu/earthdata-search/)

NISAR science files are generally HDF5 containers with multiple layers. ASF documents Harmony services to extract supported layers into map-friendly files. Pixel values come from the science layer. A browse image is a quick preview. [Harmony guide](https://nisar-docs.asf.alaska.edu/harmony/)

### 4. Intro to Remote Sensing

Remote sensing means measuring something from a distance. An active sensor such as radar sends its own signal. An optical camera can measure reflected sunlight. Spatial detail tells us which features can be separated. Revisit timing tells us whether we have observations near the day a change happened. Both matter for feasibility. For example, a widely spaced pair might miss a short flood entirely. [Original Earthdata primer](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/remote-sensing) · [NASA remote-sensing and SAR training material](https://science.nasa.gov/wp-content/uploads/2023/05/SNWGSAR_Podest2020_03_17_sml.pdf)

### 5. Intro to SAR

Radar wavelength, the direction of wave polarization, surface moisture and roughness, and the satellite's viewing angle all affect the echo. Calm water often sends the signal away from the satellite and appears dark. Flooded vegetation can behave differently because the wave can bounce between trunks and water. Strong stationary targets can look bright. Steep terrain can create shadow or make features appear in the wrong place. Those effects explain why brightness alone cannot identify a wire or certify a flood. For measuring movement, two compatible radar observations are needed. [Original Earthdata SAR primer](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar) · [NASA SAR overview](https://nisar.jpl.nasa.gov/mission/get-to-know-sar/overview/) · [NASA interferometry explainer](https://nisar.jpl.nasa.gov/mission/get-to-know-sar/interferometry/)

### 6. NASA ARSET trainings

NASA provides courses on radar fundamentals and applied work such as mapping floods, monitoring fires, and classifying crops. The Spanish course in your pasted results describes a workflow using NISAR observations and OPERA surface-water products. It is a lesson to consult if water mapping survives the data check. OPERA DSWx-S1 is a separate Sentinel-1-derived surface-water classification that can be compared with NISAR when the place and dates overlap. Two satellite products can agree and still share errors, so an official event map, optical scene, or field observation can strengthen a comparison. [NASA training collection](https://science.data.nasa.gov/disasters/training) · [Flood training from the pasted results](https://www.earthdata.nasa.gov/es/learn/trainings/monitoreo-de-inundaciones-con-sar-para-la-gestion-de-los-recursos-hidricos)

### 7. NISAR StoryMaps

NASA's current landing page lists interactive stories on floods, wildfires, land subsidence, oil slicks, and glaciers. They offer examples of how to make radar observations understandable through a map. The themes suggest different measurements. Floods and oil slicks can affect echo strength, wildfires can change vegetation and surface conditions, and subsidence and glaciers involve movement. A story can illustrate the method without proving that the corresponding NISAR scenes exist for our event. [NASA StoryMaps](https://science.nasa.gov/mission/nisar/arcgis-storymaps/)

### 8. NISAR applications white papers

NASA's applications library explains why the measurements matter to people managing land, infrastructure, water, and hazards. The levees and dams brief discusses radar observation of deformation around infrastructure. NASA's water overview connects subsidence with effects on aqueducts, highways, and other structures. These sources give us a reason to investigate ground movement near a known utility corridor. They give no evidence of direct electrical fault detection. [Applications library](https://science.nasa.gov/mission/nisar/societal-benefits/) · [Levees and dams brief](https://assets.science.nasa.gov/content/dam/science/missions/nisar/nisar-jpl/pdf/NISAR_Applications_Levees_and_Dams1.pdf) · [NASA water overview](https://science.nasa.gov/mission/nisar/water/)

### 9. UAVSAR postcards

NASA's airborne radar gallery includes examples of flooded vegetation, ground sinking near the California Aqueduct, earthquake deformation, volcanoes, and glaciers. The California image is useful to our power-infrastructure discussion because it shows how the *ground around a long structure* can be studied. The cards also show why a map needs a legend. Green can represent vegetation in one image and have a different meaning in another. NASA's NISAR data page separately links prototype data made from airborne UAVSAR for workflow practice. [Postcard gallery](https://uavsar.jpl.nasa.gov/education/postcards.html) · [NISAR prototype data](https://science.nasa.gov/mission/nisar/data/)

### 10. Canadian RADARSAT Constellation Mission data

Canada operates three radar satellites for tasks such as maritime monitoring, disaster response, and monitoring land and ecosystems. The public has access to certain imagery through Canada's Earth Observation Data Management System. Registration is required and access varies by user profile. Check a specific scene for location, date, and access before planning to use it alongside NISAR. [Original RCM portal](https://donnees-data.asc-csa.gc.ca/en/dataset/rcm) · [CSA access rules](https://www.asc-csa.gc.ca/eng/satellites/radarsat/access-to-data/about.asp) · [CSA mission FAQ](https://www.asc-csa.gc.ca/eng/satellites/radarsat/faq.asp)

### 11. Canadian SAR Python and QGIS tutorial

The repository uses a real RADARSAT Constellation scene from British Columbia wildfires. One option uses QGIS to display an image layer and a vector boundary layer. The other uses a Jupyter notebook with GDAL and Cartopy. The transferable part is how to show an image and geographic outlines together, such as a flood estimate and an infrastructure layer. NISAR's file format and measurement choices come from the ASF guide. [CSA tutorial and example data links](https://github.com/asc-csa/Synthetic_Aperture_Radar_Tutorial)

### 12. Canadian RADARSAT-1 data

The historical mission captured about 1.8 million images over its lifetime. CSA says its archive has been released under an Open Government Licence, with downloads through EODMS and AWS. The archive can help tell a long-term story where suitable scenes exist. A direct subtraction between an old RADARSAT image and a recent NISAR image would mix changes on the ground with differences in sensors, viewing geometry and processing. [Original archive listing](https://donnees-data.asc-csa.gc.ca/en/dataset/radarsat1) · [CSA archive access](https://www.asc-csa.gc.ca/eng/satellites/radarsat1/data-access.asp)

### 13. Argentina SAOCOM catalog

The linked catalog information page is specifically for SAOCOM-1A. It allows searching and viewing thumbnails without registering and describes separate conditions for downloads, processing requests and new acquisitions. CONAE describes 1A and 1B as the two L-band satellites in the broader mission. Scientific comparison needs access to the appropriate product and its metadata. [CONAE catalog rules](https://catalogos.conae.gov.ar/catalogo/catalogoSatSaocomInfo.html) · [CONAE mission and archive notice](https://www.argentina.gob.ar/noticias/la-informacion-saocom-cada-vez-mas-accesible)

### 14. Argentina SAOCOM registration

The challenge calls this the One Click route. CONAE's linked notice describes a registration form and license available to users worldwide **for archived imagery over Argentine territory**. To use SAOCOM observations of Pakistan, we would need to verify coverage and a separate applicable access path. [CONAE registration and license scope](https://www.argentina.gob.ar/noticias/la-informacion-saocom-cada-vez-mas-accesible)

### Two additional Earthdata links

- The Earthdata Search information page describes the catalog and sign-in for downloads. The pasted text and ASF's official step-by-step guide support the search workflow. [Original NASA information page](https://www.earthdata.nasa.gov/data/tools/earthdata-search) · [ASF search instructions](https://nisar-docs.asf.alaska.edu/earthdata-search/)
- YouTube's page title was *Discover and Access Earth Science Data Using Earthdata Search*. A NASA Earthdata Forum answer identifies it as a walkthrough of the search tool. [Video](https://www.youtube.com/watch?v=QtfMlkd7kII) · [Earthdata Forum reference](https://forum.earthdata.nasa.gov/viewtopic.php?sid=f52335ef7683cf52886385c0b702cd7&t=6545)

## What would make the power-line research testable?

| Question | What we could measure | What would confirm it |
| --- | --- | --- |
| Can we see an overhead wire or marker? | Look for a repeatable signal in suitable radar imagery at known, independently surveyed locations. A close-range millimeter-wave study detected thin wires, but that study used a different instrument at distances up to 10 m. It offers no performance estimate for NISAR. | A surveyed reference, controls with no wires, and measured detection and false-alarm rates. The available evidence gives no basis for replacing aviation markers. |
| Can we find a short circuit in a buried cable? | NISAR can measure surface conditions. If a buried line shorts without changing the surface, the satellite has no observable signal of the short. An electrical reflectometer sends a pulse through the cable itself. | Utility inspection and cable measurements establish the fault, using a known or independently traced route. |
| Can we map flooding around infrastructure? | Compare GCOV before and after a documented flood, then intersect likely water with known infrastructure on an interactive map. | Independent flood mapping, with checks for both missed water and false detections. An overlap indicates exposure. |
| Can we flag ground movement near infrastructure? | Compare quality-screened GUNW displacement near a known corridor or structure. The displacement is along the satellite's viewing direction. | Independent surveys, reference measurements, or a published deformation map. Movement identifies locations to investigate. |

The wire and fault sources are linked in the earlier section. For flood exposure, FAO's Pakistan report demonstrates an independent Sentinel-1 approach. For ground movement, NASA published a NISAR case study of Mexico City subsidence. Those studies establish that the *kind of measurement* is possible. The catalog verification below establishes repeat coverage at several Pakistani sites. A specific event, suitable observations, and independent reference evidence still need to be matched.

## What we would actually need to download

For each candidate, start with a published event date and a small area. Use one catalog to verify dates before downloading files. For a flood question, look for a compatible GCOV pair and a dated reference map. For a deformation question, look for a GUNW pair spanning the event or several pairs for gradual movement, with suitable coherence and independent evidence. Add an infrastructure layer if the research question concerns exposure. The Canadian and Argentine data can serve as optional case studies, practice data, or comparisons when scene access and dates fit. Their inclusion on the challenge page gives teams options.

Other topics remain open. Crop or wetland change needs several comparable observations plus agricultural or land-cover context. Wildfire disturbance needs a fire perimeter and dated before-and-after observations. Glacier movement can use GOFF and an independent ice-velocity or feature reference. SME2 can support a soil-moisture story where its grid is appropriate and suitable reference observations exist. Select the project only after verifying that both the NISAR measurement and a way to test its interpretation are available. [ASF product overview](https://nisar-docs.asf.alaska.edu/products-overview/) · [NASA application examples](https://science.nasa.gov/mission/nisar/arcgis-storymaps/)

## Pakistan catalog verification

On November 14, 2026, I independently reran the collection queries from [Claude Code's notes](Independent%20verification%20-%20Claude.md) against NASA CMR. I used the same rectangle (60.8°E, 23.6°N to 77.9°E, 37.1°N), and sorted by acquisition start. The rectangle includes parts of neighboring countries. Counts refer to catalog records with intersecting footprints and can change as products are added. [NASA CMR Search API](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)

| Collection | Worldwide | Intersecting rectangle | Earliest to latest start date (UTC) |
| --- | ---: | ---: | --- |
| `NISAR_L2_GCOV_PROVISIONAL_V1` | 163,672 | 1,978 | 2025-10-29 to 2026-10-21 |
| `NISAR_L2_GCOV_V1` | 15,536 | 194 | 2026-10-22 to 2026-11-11 |
| `NISAR_L2_GCOV_BETA_V1` | 23,527 | 391 | 2025-10-17 to 2026-01-20 |
| `NISAR_L2_GUNW_PROVISIONAL_V1` | 94,150 | 1,676 | 2025-10-29 to 2026-10-09 |
| `NISAR_L2_GUNW_V1` | 140 | 0 | — |
| `NISAR_L2_GSLC_PROVISIONAL_V1` | 162,907 | 1,965 | 2025-10-29 to 2026-10-21 |
| `NISAR_L2_GOFF_PROVISIONAL_V1` | 27,717 | 432 | 2025-11-17 to 2026-10-09 |
| `NISAR_L2_GOFF_V1` | 32 | 0 | — |
| `NISAR_L3_SME2_PROVISIONAL_V1` | 103,943 | 1,808 | 2025-10-29 to 2026-10-21 |
| `NISAR_UR_L2` | 6,809 | 298 | 2026-07-06 to 2026-11-13 |
| `OPERA_L3_DSWX-S1_V1` | 5,363,824 | 89,665 | 2024-08-21 to 2026-11-14 |
| `OPERA_L3_DISP-S1_V1` | 205,761 | 0 | — |

Every rectangle total in Claude's table reproduced. Three worldwide totals had increased by the time I queried them: Validated GCOV, Urgent Response L2, and OPERA surface water. Sort dates for GUNW and GOFF are the first acquisitions in pairs. For example, the latest-starting Provisional GUNW result starts October 9 and includes an acquisition on October 21. **Validated GUNW returned zero matches in the rectangle**. Provisional GUNW is the catalog starting point for investigating movement in the confirmed period. [Reproduce the Validated GUNW query](https://cmr.earthdata.nasa.gov/search/granules.umm_json?short_name=NISAR_L2_GUNW_V1&bounding_box=60.8%2C23.6%2C77.9%2C37.1&page_size=1)

The Provisional GCOV monthly totals also reproduced. Claude's monthly list starts in November 2025 and omits one October 2025 granule. From June through October 2026 the counts were 247, 389, 309, 484, and 309. The `4005 DHDH` mode matched 1,178 of the 1,978 results, about 60%. I confirmed one `2005 QPDH` result on track 092 descending, frame 075, on October 18. Match the radar settings when selecting acquisitions to compare. [GCOV naming and grid spacing](https://nisar-docs.asf.alaska.edu/gcov/)

I also queried one point per site from June 17 onward. A point tests that a catalog footprint intersects that coordinate. A project around the whole lake, a specific glacier, or a utility corridor would need its own area and a check of usable pixels.

| Site | Point (longitude, latitude) | Provisional GCOV | Validated GCOV | Provisional GUNW |
| --- | --- | ---: | ---: | ---: |
| Sukkur | 68.8574, 27.7052 | 30 | 3 | 25 |
| Manchar Lake | 67.685, 26.418 | 29 | 2 | 26 |
| Karachi | 67.0011, 24.8607 | 24 | 2 | 20 |
| Lahore | 74.3587, 31.5204 | 20 | 3 | 18 |
| Quetta | 66.975, 30.1798 | 39 | 3 | 35 |
| Islamabad | 73.0479, 33.6844 | 35 | 5 | 29 |
| Gilgit | 74.3087, 35.9208 | 18 | 3 | 12 |
| Hunza (Karimabad) | 74.662, 36.317 | 36 | 5 | 28 |

- **Sukkur:** Track 041 ascending, frame 015, has ten Provisional GCOV granules on ten different dates, June 17 to October 15. Track 164 descending, frame 075, has 13 granules on nine different dates.
- **Manchar Lake:** Track 092 descending, frame 075, has ten Provisional GCOV granules on ten dates, June 20 to October 18.
- **Karachi and Hunza:** Karachi 092 descending, frame 076, has 15 granules on ten dates. Hunza 055 ascending, frame 020, has 18 granules on ten dates and 16 Provisional GUNW granules with nine distinct first-acquisition dates. The 055 stack matched Karimabad and did not match the chosen Gilgit city point. Multiple products can share an acquisition date, so count dates when planning a timeline.
- **Lahore:** Track 084 ascending, frame 017, has two Validated GCOV granules at the point, October 30 and November 11. This verifies a candidate pair in one release. The images and any change between those dates have yet to be inspected. [Reproduce the Validated GCOV point query](https://cmr.earthdata.nasa.gov/search/granules.umm_json?short_name=NISAR_L2_GCOV_V1&point=74.3587%2C31.5204&page_size=10)

### Documentation corrections and limits

- The summary table now uses the original resource URLs. The numbered entries also link to documentation and redirect destinations used in the review. The Canadian Space Agency's linked access guide explicitly reports about 1.8 million RADARSAT-1 images. [CSA archive access](https://www.asc-csa.gc.ca/eng/satellites/radarsat1/data-access.asp)
- ASF lists Validated soil moisture under its 2027 plans. The permanent outage ran from July 27 at 22:03:25 UTC to August 10 at 00:55:27 UTC. Its known-issues page also describes an incomplete raw-data issue that could cause missing pixels and degrade some Provisional interferograms. ASF lists that processing issue as resolved for P05036. [ASF availability](https://nisar-docs.asf.alaska.edu/availability-overview/) · [ASF known issues](https://nisar-docs.asf.alaska.edu/nisar-known-issues/)
- NASA's water course covers NISAR and OPERA on October 20–27. Its surface-displacement course covers NISAR and OPERA on November 12–19. NASA's indexes list five StoryMaps and 26 application briefs, plus two workshop reports in the applications library. [Water course](https://www.earthdata.nasa.gov/learn/trainings/monitoring-surface-water-sar-water-resource-management) · [Displacement course](https://www.earthdata.nasa.gov/learn/trainings/identifying-disaster-extent-risk-using-nisar-surface-displacement) · [StoryMaps](https://science.nasa.gov/mission/nisar/arcgis-storymaps/) · [Applications library](https://science.nasa.gov/mission/nisar/societal-benefits/)
- For one Sukkur granule, I independently checked that the HDF5 download redirected to Earthdata Login and the browse PNG was accessible without signing in. Catalog metadata establishes availability. No science files were opened or checked for artifacts, and the wire and cable assessments remain judgments based on the instruments and the published research. The gallery and course checks covered the indexes and course descriptions. The monsoon headlines and geographic distribution of the Urgent Response results were outside the verified catalog findings. [ASF data access guide](https://nisar-docs.asf.alaska.edu/access-overview/) · [ASF GCOV product guide](https://nisar-docs.asf.alaska.edu/gcov/)
