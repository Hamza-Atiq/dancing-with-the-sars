# Langtang local verification, 14 November 2026

This continues `Langtang continuation - Codex.md`. The objective is to test the Langtang project scientifically before designing the application. Results below distinguish published evidence from our own calculations. All local paths are relative to this repository. The versioned extracts and checks have finished; no background extraction job remains running.

## Findings from primary sources

- [University of Washington, 19 October](https://www.ce.washington.edu/news/article/2026-10-19/tracking-mountainside-centimeters-time) identifies the researcher as **George Brencher**, correcting “Q. Brencher” in the earlier handoff. It reports accelerating bedrock motion exceeding one foot in the month before failure. Its figure compares July 2–14, July 14–26, and July 26–August 19. The color scale is **cm/day**, not cumulative displacement. The figure is saved as `data/lang_sources/brencher.jpg`. This is an institutional account of his analysis, not a reproducible processing release. We have not independently reproduced it.
- [Roy et al., published 16 October](https://doi.org/10.1007/s12524-026-02611-x) report precursory NISAR SBAS and offset signals. Public figures 1 and 4 were downloaded and inspected. Figure 4 shows displacement intervals of unequal duration. The full article is subscription restricted; its complete processing choices were not read. Its reported failure footprint and volume are about 0.99 km² and 99 ± 10 million m³. Different outlines and methods must not be conflated with these estimates.
- [Pramanik et al., preprint dated 12 November](https://doi.org/10.5194/egusphere-2026-6868) models the remnant glacier's **post-collapse** response under two scenarios. It identifies glacier 15.05732 and references optical elevation models. Its simulated speed changes are not measured precursor velocities. Figure 1 was rendered and inspected. The paper promises model code and outputs upon publication; it does not supply a ready-to-use source shapefile in its availability statement.
- [Shean and Bhushan's optical DEM archive](https://zenodo.org/records/22842746) provides 2 m products in EPSG:32645, ellipsoidal heights, under CC BY-NC 4.0. Its preview includes an approximate outline, but lacks coordinates sufficient to digitize it directly. The `dh.zip` directory contains post-event versus post-event differences, not the required pre/post-collapse scar layer. A slow full download was stopped and renamed `.zip.partial`; it is not usable data. The ZIP central directory was inspected with a 64 KB range request. No full DEM was extracted.
- [Berthier's pre-event terrain archive](https://zenodo.org/records/22147118) provides 2019 elevation models. Its gap-filled Copernicus product is explicitly unsuitable for elevation-change mapping. No terrain raster from this archive has been downloaded yet.

## Independent detachment boundary

[UNOSAT product 4260](https://unosat.org/products/4260) links a public event geodatabase. We downloaded `FL20260826NPL.gdb.zip` and inspected its layers. `UNOSAT_Landsat9_20260826_DetachmentZone` contains one polygon with projected area **1,956,822.82 m²**. It is a preliminary interpretation, not field validated, and is broader than a precise moving-bedrock patch.

The polygon spans 85.510878–85.529932 E and 28.282191–28.295798 N. Original CRS is EPSG:9707. Fiona/GDAL exported horizontal coordinates to EPSG:4326 and EPSG:32645. The repository's hand-written UTM conversion agrees with GDAL at the vertices to about 0.00002 m. This checks the coordinate transformation, not the accuracy of the boundary.

**Metadata inconsistency preserved:** the layer name identifies August 26, but its `SensorDate` field contains September 26. `FieldValidation` is 0. Do not silently correct the attribute or imply that the polygon is surveyed ground truth.

Files: `data/lang_sources/UNOSAT.gdb.zip`, `unosat/FL20260826NPL.gdb`, `detachment.geojson`, `detachment_utm.geojson`. The exported files preserve attributes and ZIP SHA-256. `scripts/lang_export_unosat.py` reproduces the exports using Python 3.13 and Fiona 1.10.1 installed locally under `data/lang_tools`; the global environment was not changed.

An earlier exploratory circle uses the [reconnaissance coordinate published by Bethan Davies](https://www.antarcticglaciers.org/2026/08/august-2026-nepal-tibet-floods/), rounded to 85.5252 E, 28.2853 N. It misses much of the western detachment. Results from this circle are retained to show location sensitivity, not presented as source-wide measurements.

## Local backscatter result

`scripts/lang_local.py` compares July 14–26 with August 19–31 on exactly matching GCOV grids. Both use the **same pixels** with finite positive power and masks 1–5 on all four dates. Change is `10*log10(after/before)`. No smoothing was used. The July interval is a comparison period; the published precursor means it cannot be assumed motionless.

Within the UNOSAT polygon, 17,626 pixels pass these checks, about 90.10% of the rasterized polygon.

| Channel | July comparison: fraction changing by >3 dB in either direction | Collapse interval |
|---|---:|---:|
| HH | 18.55% | 41.22% |
| HV | 18.60% | 36.57% |

This is evidence of localized radar backscatter change coincident with the collapse interval. It is not a calibrated landslide detector, a significance test, a volume estimate, or evidence of advance warning. Pixels are spatially correlated. Weather, viewing geometry, and surface changes affect radar brightness. The polygon is broad, and no stable terrain-matched control has been validated.

The [GCOV specification linked by ASF](https://nisar-docs.asf.alaska.edu/gcov/) was downloaded and checked: mask 0 denotes invalid/partly focused samples, 1–5 valid subswaths, and 255 fill. This mask is **not a layover/shadow classification**. Terrain visibility remains an additional check.

Outputs: `data/lang_check/local_checks.json` and `local_backscatter.png`. In the figure, green is the UNOSAT boundary, black is the exploratory 500 m circle, grey is excluded, blue is decreased power and red increased power. The display uses nearest-neighbor reduction and is for orientation; statistics use native pixels.

## Phase diagnostics and pitfalls

The published three intervals have 12, 12, and 24 days. Any velocity comparison must divide by these durations. The script converts reference-subtracted phase to **phase-equivalent cm/day** with positive factor `wavelength/(4*pi)`. It intentionally does not label the sign as physical motion. No vertical displacement is estimated.

In the existing ascending extracts, 19 of 307 polygon pixels have coherence >=0.6, component 1, and finite phase/ionosphere across the three benchmark intervals. The whole-polygon median coherence is about 0.231, 0.248, and 0.206; it falls to 0.086 across the collapse. All polygon connected components are 0 in the collapse pair. The 20 m wrapped coherence also has limited usable coverage. Requiring post-collapse phase survival would wrongly discard the destroyed surface; the precursor selection uses pre-event pairs only.

**These old-extract phase results are provisional:** the original extraction omitted the GUNW validity mask and source granule IDs. Coherence and connected components alone are insufficient. `scripts/lang_sensitivity.py` sweeps coherence 0.3–0.7 and four reference directions, preserving all results rather than selecting the result closest to the publication. The source-pixel counts are 79, 57, 35, 19, and 9 before the missing mask is applied. Reference choice substantially changes the early-July result. The initial result does not establish the published acceleration.

The [ASF GUNW guide](https://nisar-docs.asf.alaska.edu/gunw/) states that supplied ionospheric and external phase corrections are not applied by default. Subtracting the ionosphere is retained as an explicit diagnostic, with raw results alongside. Troposphere, tides, elevation dependence, reference stability, phase unwrapping and product-specific conventions remain to be resolved.

The official [ISCE3 Crossmul source](https://raw.githubusercontent.com/isce-framework/isce3/develop/cxx/isce3/signal/Crossmul.cpp) forms reference times conjugate-secondary. This establishes the algebra in that code, but the physical interpretation still needs the focused-SLC sign, product reference order and processing provenance. Do not copy the sign from an unrelated Sentinel-1 tutorial.

## Catalogue and quality audit

`scripts/lang_catalogue.py` saved complete paginated CMR responses for a local bounding box and June 1–September 2 overlap search in `data/lang_sources/cmr_candidates.json`. It found tracks 098 A 016 and 048 D 074; track 149 was not returned for this source-area query. This does not support a three-track/four-day source-monitoring claim. Counts are product records, not distinct dates, because multiple processing versions exist.

Several ascending GUNW pairs have both P05023 and X05026 products. The original script overwrites dictionary entries with the same pair start date and does not preserve version selection. `scripts/lang_fetch_review.py` fetches explicitly named products into `data/lang_review` and saves source URLs, attributes, processing metadata and file hashes without overwriting the old extracts.

The first descending file, July 11–23, contains large zero-valued phase areas. Inspection of its **actual HDF5 mask description**, specification version 1.5.0, explains why a numeric value alone is insufficient. The mask is uint32: low byte encodes water/reference/secondary subswaths, bits 8–23 encode anomalies, and bit 24 indicates interpolated ionosphere. Mask value 1 has an invalid reference sample. All 7,155 zero-phase pixels in that crop have mask 1. Coherence >0.6 still occurs at 557 of those zero-phase pixels. Correcting these invalid zeros could manufacture apparent motion.

The older Rev E PDF linked by the guide describes a byte mask and is not a complete description of this newer file. `scripts/lang_quality.py` decodes the actual mask description and has passing checks for invalid subswaths, water, anomalies and interpolated-ionosphere flags. Do not assume all nonzero mask values are valid or use the GCOV mask rule for GUNW.

## Reproduction and independent review

1. Read the source URLs and distinguish reported, modeled, and locally measured evidence.
2. Run `python scripts/lang_export_unosat.py` in the workspace (Python 3.13). Verify original attributes and the date inconsistency.
3. Run `C:/Users/HP/anaconda3/python.exe scripts/lang_local.py` for native-grid backscatter and preliminary old-extract phase summaries.
4. Run `C:/Users/HP/anaconda3/python.exe scripts/lang_quality.py` and `scripts/lang_sensitivity.py` for mask checks and sensitivity results.
5. Inspect the explicit source metadata in `data/lang_review`. Confirm reference/secondary dates, grid coordinates, mask interpretation and version matches before reusing any phase estimate.
6. Recompute polygon statistics independently; do not accept agreement between scripts that share the same assumptions as scientific validation.

## Completed version and second-angle checks

Nine new GUNW extracts are saved with metadata and hashes: the three ascending benchmark intervals in each of P05023 and X05026, plus descending July 11–23, July 23–August 16 and August 16–28. `scripts/lang_review_check.py` verifies hashes and grids. All four checked arrays in each old ascending precursor crop match X05026 exactly; they do not all match P05023. This identifies matching content over the crop rather than proving the original request URL.

Both versions retain 19 common source pixels at coherence >=0.6 after masking, and their median diagnostics differ negligibly. With the polygon-centered 1.5–3 km reference annulus, X05026's ionosphere-subtracted phase-equivalent rates are approximately **−0.0223, +0.0410, +0.0191 cm/day**. These differ from the circle-centered reference results in `local_checks.json`; reference definition matters. Neither reproduces the published acceleration. These are not validated physical velocities.

**Processing time matters:** X05026 was processed September 18, after the collapse. The three P05023 pairs were processed August 12, August 13 and August 24. Public availability on those dates is unverified. Acquisition date is not availability date; retrospective processing does not establish historical warning capability.

| Descending pair | Valid land-mask pixels out of 307 | Also coherence >=0.6 and component 1 |
|---|---:|---:|
| July 11–23 | 0 | 0 |
| July 23–August 16 | 307 | 21 |
| August 16–28 | 0 | 0 |

There are no common usable source pixels across the two pre-event descending pairs even at coherence 0.3. Catalogue overlap is insufficient evidence of usable coverage. Invalid pairs involve narrower/mixed bandwidth pairing, but the exact acquisition/processing cause is unresolved. Do not call it terrain shadow or a software bug without further evidence.

Results are in `data/lang_check/review_checks.json`. The searched ISCE3 issue 284 concerns zero correlation peaks in a different layer and was not accepted as an explanation for zero phase.

## Completed offset checks

Three X05026 GOFF extracts now contain all three offset layers, variances, cross-covariance, correlation peaks, SNR and the parent-grid validity mask. They are in `data/lang_review_goff`. Attributes confirm meters for offsets and meters squared for variances. Every one of the twelve original offset/SNR/correlation arrays matches its new cropped counterpart exactly. Layer grids were checked.

The GOFF parent mask shares subswath/anomaly encoding but reserves bits 24–31; it does not use GUNW's ionosphere flag. `scripts/lang_quality.py` tests both decoders. `scripts/lang_fetch_goff_masks.py` fetches this mask outside the per-layer groups.

`scripts/lang_goff_check.py` requires common pixels across the three intervals, valid land masks, finite offsets, positive variances, positive-semidefinite covariance, SNR >=5, and correlation peaks >=0.3, 0.5 or 0.7. These are sensitivity tests, not calibrated detection criteria. Rates use actual interval duration and candidate-reference medians separately for along-track and slant-range axes. No vertical or 3D motion is estimated.

| Layer | Common pixels at peak >=0.3 | >=0.5 | >=0.7 |
|---|---:|---:|---:|
| 1 | 128 | 52 | 7 |
| 2 | 133 | 69 | 12 |
| 3 | 120 | 45 | 0 |

For example, layer 2 at peak >=0.5 gives relative slant-range rates of +0.065, +0.138 and −0.141 cm/day against the full annulus. Median per-pixel formal range sigmas are about 6.9, 7.1 and 8.0 cm. These sigmas omit systematic error and are not uncertainty on the spatial median. Along-track estimates vary substantially with reference direction. One seven-pixel layer-1 selection has increasing values, but this is not consistent across layers/selections. Reporting that selection alone would overstate the evidence. The tested broad-area offsets do not establish robust acceleration.

The [ASF GOFF guide](https://nisar-docs.asf.alaska.edu/goff/) notes that distributed offsets are unfiltered and may contain outliers. Original raw offsets must not be read directly as glacier speeds. Results are in `data/lang_check/goff_checks.json`.

## What remains and recommended decision

The local diagnostic stage is complete: independent boundary, before/after comparison, source coherence, provenance, masks, reference sensitivity, descending samples and offset sensitivity. It supports a reproducible surface-change result. A precursor or warning system has not been validated.

Further deformation research needs an independently mapped moving-bedrock subset, original published processing details or an equivalent higher-resolution workflow, terrain visibility, atmosphere/tide handling, unwrapping and physical sign validation. Agreement between the published map and off-the-shelf GUNWs has not been established. These tasks should be weighed against the project deadline before committing to warning functionality.

Backscatter detector performance still needs additional comparison intervals and terrain-matched stable controls. Lake outlines and debris paths have not been quantitatively validated. No model, warning service, public deployment or application UI was built.

My recommendation is to discuss a **retrospective change-and-data-quality explorer** as the immediately supportable product, with precursor recovery retained as a labeled research track. This is a recommendation for the user's decision, not an adopted scope change.

Claude should rerun the export, local, quality, sensitivity, review-check and GOFF-check scripts, inspect source attributes and independently recompute the statistics. Data and local dependencies remain ignored by Git, so a repository clone alone will not include the extracts.
