# Langtang event reconstruction: independent research

Research date: 15 November 2026. This is an initial source audit and NASA optical availability/quality investigation, not a completed reconstruction or a new precursor discovery. Website and scientific detector are unchanged.

## Main findings

1. Same-day satellite data exist. A fresh NASA CMR query returned `HLS.L30.T45RUM.2026238T044748.v2.0`, acquired 26 August 2026 at 04:47:48.916 UTC. Relative to the reported 02:52 UTC collapse, this is about 1 h 56 min afterward, not a view of the collapse in progress.
2. The old 18–19-hour reservoir explanation is not the current wording of the report publisher. PreventionWeb retains that explanation, while IRDR's current page and linked updated PDF describe a rapid mass-failure/debris-flow cascade with smaller temporary dams remaining afterward. Preserve both versions as provenance; do not present the older summary as settled chronology.
3. The current project's optical script selects autumn 2025 and October–November 2026 scenes. This is useful for persistent landscape change, but cannot resolve a lake forming or draining during 25–26 August.
4. Existing work already uses NISAR and Sentinel-1. The missing dimension is an event-centred, source-to-river reconstruction, not simply adding a second radar name.
5. An openly published WorldView-derived terrain dataset offers an additional analysis route. Its post-event composite is not an image of a single moment.

## Source provenance and chronology

- [PreventionWeb summary](https://www.preventionweb.net/publication/documents-and-publications/rapid-analysis-report-scientific-anatomy-26-august-2026): retains a likely temporary dam lasting 18–19 hours. This describes a secondary-source rapid analysis, not direct observations throughout the proposed impoundment interval.
- [IRDR current publication page](https://www.irdrinternational.org/knowledge_pool/publications/142) and [updated PDF](https://www.irdrinternational.org/upload/20260917/Rapid%20Situation%20Report_%20The%2026%20August%202026%20Bhotekoshi%20Flash%20Flood%20in%20Nepal-updated.pdf): describe failure, interaction with river water, entrainment, and rapid downstream propagation. PDF pages 2–4 show Planet comparisons dated 25/26 August, snow/water-index illustrations, and the revised chronology. These figures are not a measured reservoir-level time series. The filename is “updated”; its URL contains a September directory, although the cover still carries an event-day report status. Do not assign an exact revision date from the URL alone.
- [ICIMOD preliminary synthesis record, 13 October](https://lib.icimod.org/records/qdvc1-tc123): identifies a cascading rock-and-ice disaster rather than a conventional GLOF, with initiation details unresolved. The landing-page description was read; the full PDF redirect failed in this session.
- [ICIMOD event compilation](https://www.icimod.org/kyirong-rasuwa-flood-2026-nepal-china-border/): distinguishes the August 2026 collapse from the July 2025 Purepu glacial-lake flood. Its mixed reports and interviews should not be treated as one uniform primary measurement.
- [Li preprint v2](https://arxiv.org/html/2609.04563v2): gives source-area mapping near 28.289 N, 85.530 E and identifies optical views from 24, 26 and 27 August. Cloud-limited source mapping does not establish a precursor lake or initiation mechanism. Its revised source outline is a different object from the small radar patch used here.

## Location: several different objects must be mapped

The current catalog query point is **28.28858 N, 85.52701 E**, inherited from the earlier project location audit. It is a source-sector reference point, not a verified dam coordinate. Earlier notes attribute its precise centroid to Li via Sah; this session directly checked the newer Li paper's approximate source location, not the original precise-centroid provenance.

Keep distinct geometries for:

- the detached rock/ice source and the existing radar patch;
- the downslope deposition/river-entry zone;
- each proposed blockage and its upstream water polygon;
- the affected downstream corridor and damaged assets.

No exact pre-event dam location has been independently verified in this session. Do not relabel the slope centroid as that location. Existing source polygon files and UNOSAT data are already in `data/lang_sources/` for later geospatial validation.

## Fresh NASA catalog and quality results

Reproduce with `scripts/event_optical_inventory.py`, then `scripts/event_optical_quality.py`.
The first uses public metadata without credentials; the second downloads Fmask using the existing Earthdata login without logging credentials.

Saved raw inventory: `data/event_reconstruction/hls_inventory.json`. Saved pixel counts and rules: `data/event_reconstruction/patch_quality.json`. Raw Fmask GeoTIFFs are retained beside them.

Search: HLSL30 and HLSS30, 20 August–2 September, point 85.52701 E / 28.28858 N. These products combine Landsat and Sentinel-2 observations at 30 m; HLS is not another independent satellite.

| UTC acquisition | Product | Tile cloud % | Patch pixels passing cloud/shadow/adjacency filter |
|---|---|---:|---:|
| 22 Aug 05:10:45 | HLS S30 | 86 | 0/288 |
| 24 Aug 05:00:49 | HLS S30 | 56 | 288/288 |
| 24 Aug 05:11:03 | HLS S30 | 69 | 288/288 |
| 26 Aug 04:47:48 | HLS L30 | 82 | 223/288 |
| 27 Aug 05:10:45 | HLS S30 | 92 | 0/288 |
| 29 Aug 05:00:50 | HLS S30 | 94 | 0/288 |
| 1 Sep 05:10:46 | HLS S30 | 97 | 0/288 |

The screening region is the existing rectangular radar patch box (UTM 45N: E 355250–355800, N 3129780–3130250), not its 0.056 km² irregular selected-pixel area and not the full failure or river. The pixel-centre selection contains 288 pixels.

Rule: exclude fill 255, cloud bit 1, adjacency bit 2, shadow bit 3. Snow/ice is retained and separately counted. Critically, **all 288 passing pixels in each 24 August scene have high-aerosol flags**. On 26 August, 217 of 223 passing pixels have that flag; only six also pass a high-aerosol exclusion. The other 65 pixels are fill. Thus this is a candidate-visibility screen, not validation of reflectance change. Fmask water flags on steep snow-covered terrain are not independently validated water polygons.

[NASA HLS bit definitions](https://github.com/nasa/HLS-Data-Resources/blob/main/r/HLS_Tutorial.Rmd) document the flags. Local fractions matter more than tile-wide cloud percentages, but they still require visual inspection and terrain-shadow assessment. No RGB, snow-loss area, melt volume, lake area, lake elevation, or flood discharge was measured in this session.

## Additional independently verified dataset

[Shean and Bhushan, post-event WorldView stereo DEMs](https://zenodo.org/records/22842746), published 18 September, provides 2 m terrain products from WorldView-2/3 and Legion imagery acquired 27 August–8 September. The record includes composites and elevation-change products, in UTM 45N with ellipsoidal heights, under CC BY-NC 4.0. Metadata were already present locally and the public record was independently opened.

Possible use: map erosion and deposition after checking registration, source dates, voids, stable-terrain errors and vertical datum. A surface-elevation difference is not automatically glacier melt, and post-event topography alone cannot reconstruct a pre-event lake level. Preserve per-pixel source dates when displaying a composite. Raw commercial imagery has separate rights.

## Why many satellites do not guarantee continuous evidence

Different measurements answer different questions. Optical images can show surface appearance if visible; radar phase needs compatible observations and coherent returns; radar amplitude can show a changed surface without measuring displacement. Geometric coverage is not usable visibility in a steep valley. A reported result may rely on commercial imagery, raw-data processing, a long time series, or a different spatial footprint. Reconstruction after an event does not prove that an actionable product was available beforehand.

Consequently replace broad wording such as “the last 24 days are blind” with the specific limitation: the present NISAR patch displacement analysis is unresolved over its 24-day pair. Optical snapshots and other radar observations exist within that period, with different capabilities and limitations.

## Next analysis sequence and evidence gates

1. Inspect native Sentinel-2 and Landsat RGB/SWIR/QA around 24–26 August over the entire source-to-river corridor. Use fixed georeferencing and comparable display scales; mark gaps and high-aerosol areas. Native Sentinel-2 may preserve finer detail than HLS.
2. Trace the Planet 25/26 August figure to original scene identifiers, acquisition times and usable imagery. A published illustration establishes an observation lead, not possession of analysis-ready pixels or permission to republish them.
3. Delineate candidate deposits, blockages and water only where observations support them. Search backward and forward independently. Date any lake as first observed, not assumed formation time.
4. Compare NISAR and Sentinel-1 amplitude/coherence along the valley, with layover/shadow masks and same-season controls. Keep this separate from the frozen precursor detector.
5. Use DEM differences to assess material loss/deposition with stable-ground uncertainty. Do not convert all material loss into meltwater.
6. Obtain original river-gauge time series and station metadata for water-level rise and flood arrival. A satellite water-area polygon does not directly give water depth or reservoir volume. Test any storage estimate against terrain and inflow constraints.
7. Overlay UNOSAT/Copernicus damage data with their observation dates and damage categories. Distinguish mapped exposure, interpreted damage and field confirmation.

The website can eventually connect these stages with each scene's timestamp, sensor, measurement, uncertainty and source. Animate observed frames explicitly; any motion between observations must be labelled a reconstruction. A distinctive result is possible, but uniqueness or a missed warning cannot be promised before these tests.

## Access and verification limits

The live Vercel HTML was retrieved successfully and saved locally. The challenge URL failed through web retrieval and through Python certificate validation; the existing resource-review note was consulted instead, not claimed as a fresh full resource-page review. RCM/SAOCOM were not freshly queried. Full ICIMOD PDF, original Planet pixels, terrain rasters, and gauge measurements remain unprocessed. No website deployment or detector modification occurred.
