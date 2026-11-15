# Langtang data hunt — location check and archive survey

15 Nov 2026, Claude session 3. Question from the user: is our location exact, and is there data the earlier sessions missed (other satellites, newer dates)?

Method: (1) read what others published about where the source is; (2) query the archives directly at that position (NASA CMR, ASF search API). Scripts: `scripts/archive_survey.py`, `scripts/s1_hyp3.py`. Raw output: `data/archive_survey.log`, `data/s1_bursts_at_source.json` (not in git).

## 1. Location

Three published positions for the source:

| Source | Lat N, Lon E | Distance from the centre of our patch |
|---|---|---|
| Li (2026), preferred centroid, quoted in Sah's preprint | 28.28858, 85.52701 | **44 m** (inside our patch box) |
| HiRISK rapid hazard assessment, quoted in Sah's preprint | 28.288708, 85.528159 | 147 m (inside our patch box) |
| Bethan Davies reconnaissance point (used by Sah and by Codex's early circle) | 28.2853, 85.5252 | 361 m (outside) |
| Point used for catalogue queries in sessions 1–2 | 28.25, 85.52 | 4,290 m |

Our patch (355250–355800 E, 3129780–3130250 N, UTM 45N; centre 28.28826 N, 85.52675 E) was found from the radar phase alone. It lands on the two independent mapped centroids. The Li and HiRISK values were read from Sah's preprint, not from the original documents.

Other descriptions agree: north/west-north-west face of Langtang Lirung, head scarp about 5,120–5,150 m, source area 0.75–0.99 km² (Zhao; Roy), drop about 1,300 m into the Lhende Khola. Sah gives slope aspect 273–281° (west-facing), slope 33°.

The old catalogue point was 4 km south. Re-running the NISAR queries at the correct point returns the same tracks and the same granule counts, so nothing was missed because of it.

## 2. What others have measured (context for our claims)

| Who | Data | Result |
|---|---|---|
| ICIMOD preliminary synthesis (13 Oct 2026) | Sentinel-1 InSAR | Up to 40 cm line of sight, 7 Jul – 24 Aug (48 days). Volume about 132 million m³ |
| Shirzaei (interview) | Sentinel-1 stack, 8 Jan – 18 Aug | About 10 mm/month, accelerating. Not peer reviewed |
| Kutoglu, Softa, Akgün, *Remote Sensing* 18(21):3727 | NISAR | Opposite-sign rock and ice displacement before failure; 20 Jun – 19 Aug. Full text not read (403) |
| Research Square rs-11022365 (preprint) | NISAR offsets | Source moved 0.96 m in 24 days; 101 other zones also moved (93 glaciers), so the source did not stand out. Read only through a secondary summary |
| Wang, Sassa, Yang et al., *Landslides* | Sentinel-2 pixel tracking, 2018 on | Hanging glacier sped up from 7.4 to 55 m/yr from late 2025 |
| Sah (EarthArXiv, two preprints; Zenodo 10.5281/zenodo.22676918) | Sentinel-1 amplitude, coherence, unwrapped phase on a 500 m disc, 120 controls | No precursor distinguishable from controls; last pass 24 Aug 00:18 UTC, 50.6 h before failure |
| Petley (Landslide Blog) | Planet, 12 and 25 Aug | Minor visible change only |
| ShreyaJari (GitHub) | Sentinel-1 cross-pol ratio | Dip on 17 May 2026; two events at one site |

Two points matter for us. Sah's null used a 500 m disc centred 361 m from the patch, at 40 m pixels and unwrapped phase; our session-2 finding was that exactly this kind of averaging hides the patch. And the "many other zones also move" result matches our own 268 unverified flags.

## 3. Archive survey at 28.28858 N, 85.52701 E

### NISAR (CMR, 15 Nov)

Only two tracks cover the source: 098 ascending (frame 016) and 048 descending (frame 074). Same as before.

New since session 2:
- Validated `NISAR_L2_GCOV_V1` and `NISAR_L2_GSLC_V1`: 27 Oct and 8 Nov (track 048), 30 Oct and 11 Nov (track 098). Also `RSLC_V1`.
- Urgent Response L1/L2 now runs to 11 Nov (track 098: 18 Oct, 30 Oct, 11 Nov).
- Provisional GUNW and GOFF still end with the pair starting 6 Oct. No validated GUNW or GOFF yet.

Not used so far and available: full-resolution `GSLC` (34 dates on track 098, 9 on track 048), `RSLC`, and radar-geometry `RIFG`/`RUNW`/`ROFF`. These are what step 4 of the handoff (the 26 Jul – 19 Aug interval) needs.

The 27 Jul – 10 Aug NISAR gap is real; no product type fills it.

### Sentinel-1 (ASF) — the missed source

Three tracks cover the source, each every 12 days (Sentinel-1A to 25 Jun, Sentinel-1D after):

| Track | Direction | Burst | Dates, late Jun – early Sep 2026 |
|---|---|---|---|
| 19 | descending | 019_039570_IW1 | 25 Jun, 7 Jul, 19 Jul, **31 Jul, 12 Aug**, 24 Aug, 5 Sep |
| 121 | descending | 121_258660_IW3 | 2 Jul, 14 Jul, 26 Jul, **7 Aug**, 19 Aug, 31 Aug |
| 85 | ascending | 085_180590_IW2 | 29 Jun, 11 Jul, 23 Jul, **4 Aug, 16 Aug**, 28 Aug |

Bold dates fall inside NISAR's gap. 24 Aug is five days after NISAR's last pass and 50.6 h before the collapse. About 30 dates per track exist for the past year (92 bursts).

Expectations, not results: Sah reports track 19 sees 44% of a 500 m disc at 71° local incidence and track 121 sees 14%. Sentinel-1's wavelength is 5.5 cm against NISAR's 24 cm, so the same movement gives about four times as many fringes and loses coherence sooner. Sentinel-1 may confirm the July movement and show where coherence is lost in August; it may also show nothing.

**Blocked:** burst downloads and on-demand interferograms (ASF HyP3) return "pre-authorization required" for the user's Earthdata account. The user must approve the ASF application once at `https://urs.earthdata.nasa.gov/approve_app?client_id=BO_n7nTIlMljdvU6kRRB3g`. After that: `python scripts/s1_hyp3.py submit` (24 pairs, 1 Jun – 9 Sep, 20 m pixels), then `status`, `download`.

### Other archives at the point

| Dataset | Result |
|---|---|
| ALOS-2 (L-band, ASF) | 242 scenes, latest 28 Mar 2025. Nothing in 2026 |
| ALOS PALSAR | 2007–2010 only |
| ARIA Sentinel-1 interferograms (ready-made) | End 2020–2024 depending on track |
| OPERA RTC-S1 (ready-made Sentinel-1 backscatter, 30 m) | 51 granules, 1 May – 11 Nov 2026 |
| OPERA DSWx-S1 / DSWx-HLS (water maps) | 61 / 156 granules; useful for the barrier lakes downstream, not the slope |
| HLS (Sentinel-2 and Landsat, 30 m optical) | 91 + 21 granules, May – Nov 2026. Cloud not checked |
| ASTER L1T | 7 scenes, 16 Jun – 22 Sep |
| UAVSAR, RADARSAT-1, ERS, JERS-1, SIR-C | None |
| SWOT HR SLC | 36 granules; not suitable for slope movement |

### Partner resources in the challenge list

- **RADARSAT-1** ended in 2013; ASF holds none at this point.
- **RCM**: open data is mainly over Canada through EODMS, which needs its own account. Not searched for Nepal.
- **SAOCOM** (L-band): open registration covers archive images over Argentina. The catalogue was not searched for Nepal; it needs a CONAE login.
- Commercial data named by others (Planet, Pléiades, WorldView, PowerChina-1) is not open. Post-event WorldView DEMs are on Zenodo (record 22842746).

## 4. What this changes

1. The location is settled and independently confirmed.
2. NISAR had nothing more to give by track or date before the collapse. Its unused products (GSLC) are the route to the last 24 days.
3. Sentinel-1 is a second satellite with five passes inside NISAR's gap and one 50 h before failure. It is the best chance of new data points and is waiting on one approval click.
4. Our wording should cite the other studies: the precursor is known; the published Sentinel-1 "no precursor" test averaged over a disc that mostly misses the patch.

## 5. Not checked

Li (2026), HiRISK and the Research Square preprint at first hand; the MDPI paper's full text; the ICIMOD report PDF; Sentinel-1 data itself; cloud cover in HLS; RCM and SAOCOM catalogues; Copernicus EMSR927 products.

## Sources

- Sah, EarthArXiv preprint: https://eartharxiv.org/repository/object/14902/download/25905/ and Zenodo https://zenodo.org/doi/10.5281/zenodo.22676918
- ICIMOD press release: https://www.icimod.org/press-releases/second-major-himalayan-flood-in-seven-weeks-raises-new-questions-about-mountain-risk/
- ICIMOD event page: https://www.icimod.org/kyirong-rasuwa-flood-2026-nepal-china-border/
- Himalayan Geographic summary of the papers: https://himalayangeographic.com/2026-himalayan-disaster/
- MDPI paper: https://www.mdpi.com/2072-4292/18/21/3727
- Research Square preprint: https://www.researchsquare.com/article/rs-11022365/v1
- EarthArXiv reconstruction: https://eartharxiv.org/repository/view/14717/
- Landslide Blog: https://eos.org/thelandslideblog/nepal-landslide-precursory-behaviour and https://eos.org/thelandslideblog/langtang-lirung-1
- GitHub cross-pol study: https://github.com/ShreyaJari/langtang-polsar-precursor
- HyP3 burst InSAR guide: https://hyp3-docs.asf.alaska.edu/guides/burst_insar_product_guide/
