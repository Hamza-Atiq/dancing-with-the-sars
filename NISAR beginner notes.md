# Dancing with the SARs

The challenge asks our team to build an interactive app that uses NISAR radar data to help people see how Earth's surface changes. NISAR sends radio waves toward Earth and measures the echoes. Comparing observations of the same place over time can reveal changes.

## The two search pages

- **Earthdata Search** is the data catalog. The pasted search for NISAR showed 52 matching collections. A collection is like an album. A granule is one item inside it, often covering a particular area and one observation date or a pair of dates. [Earthdata Search](https://search.earthdata.nasa.gov/search)
- **The NASA Earthdata website search** showed 102 results, including dataset descriptions, news, events, and training. The Spanish flood-monitoring result is a lesson on using NISAR and OPERA to map water.

## Four NISAR collections we found

| Product | What it gives us | What it might help us see |
| --- | --- | --- |
| **GCOV — Geocoded Polarimetric Covariance** | A map of how strongly radar echoes came back. Processing reduces brightness differences caused by hills and slopes. | Where surface conditions may have changed, such as fields that may have flooded. |
| **GUNW — Geocoded Unwrapped Interferogram** | A map made by comparing detailed radar measurements from two dates. | How the ground may have moved, for example after an earthquake. |
| **GSLC — Geocoded Single Look Complex** | Radar measurements lined up with a map, keeping both signal strength and phase. Phase is the position within a wave's repeating cycle. | More advanced comparisons that need the extra detail from the radar wave. |
| **RSLC — Range Doppler Single Look Complex** | Detailed radar measurements arranged in the satellite's viewing geometry. | A starting point for processing radar data and making products such as GCOV and GSLC. |

**Geocoded** means the data is lined up with a map grid. The four results shown were **Provisional**, meaning partially validated and still undergoing quality checks. Beta, Provisional, and Validated are release maturity labels. [NISAR Data Products Guide](https://nisar-docs.asf.alaska.edu/products-overview/)

The results also included **OPERA Dynamic Surface Water Extent**, a product that already labels areas of surface water using **Sentinel-1** radar observations. It may provide context for a water example. The challenge calls for NISAR as the basis of the app.

## First practice search

Try the exact catalog name `NISAR_L2_GCOV_PROVISIONAL_V1`. Open the collection, choose one place on the map, and see which dates cover it. For a first comparison, look for two observations of the same area from different dates with similar radar settings and viewing geometry. A brightness change is a clue. For example, calm water often appears dark, and other surfaces can appear dark too. [ASF guide to finding NISAR data](https://nisar-docs.asf.alaska.edu/earthdata-search/) · [NASA guide to interpreting SAR](https://nisar.jpl.nasa.gov/mission/get-to-know-sar/overview/)

## Reading a GCOV granule

The first ten pasted granules are all from October 21, 2026. Start and End describe the seconds during which the radar collected data for each granule. For example, `033_139_D_091` means cycle 033, track 139, descending direction, frame 091. A track is the satellite's route, and a frame is one section along it. The first row covers only part of frame 091, so check the actual outline of coverage on the map, called the footprint. A browse image is a quick preview. [ASF guide to GCOV filenames](https://nisar-docs.asf.alaska.edu/gcov/)

To practice finding a repeat observation, choose a small area on the map and look for two different dates. Matching track, direction, frame, and radar settings is a useful starting point. Confirm that both footprints cover the area you want to compare. [ASF guide to searching by place and time](https://nisar-docs.asf.alaska.edu/earthdata-search/)
