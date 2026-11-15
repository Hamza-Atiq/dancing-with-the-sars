# Handoff — state on 15 Nov 2026 (session 5)

Read this first when resuming, starting with "Session 5 update", then "Session 4 update".

## Session 5 update (15 Nov 2026, evening) — START HERE

**Website (item 1 of the old pending list): done and pushed** (commit `be3abcb`). Checked in Chrome on desktop and at phone width: brightness chart in part 7 matches `data/rtc/rtc_patch.json`; shorter text throughout. Fixed two bugs: the 361-slope dot chart drew its tallest column over the headline (height now follows the tallest column); the two Sentinel-1 charts were cut off on phones (now scroll inside their box). README has three charts from `scripts/readme_figures.py` (SVGs in `previews/readme_*.svg`). `previews/story_*.png` are old screenshots, still untracked. The live Vercel site was not re-opened after the push.

**Four research checks done** (the first four "suggested next steps"). Each one's rules were committed before its data was opened; results appended below the rules. Plain summary:

1. **Independent test, Budhi Gandaki rock slope failure, 11 Oct 2026** (`project/independent_test.md`; data `data/indep_bg/`, 42 pairs, 3 tracks). Rule outcome "HIT" only because of one winter flag 8 months early (27 Jan–8 Feb); 42% of random same-size spots also get a flag (post-hoc check). No flag at the source in the 19 later ascending pairs or on the two descending tracks, including a pair ending ~9 h before the flood. **Not an independent detection.** Hanjia (17 Jul 2026, China) rejected: too few pairs before the event.
2. **Flag check** (`project/flag_check.md`; data `data/flagcheck/`): 65 of 268 flags classable through cloud with HLS Fmask; 28 snow, 32 snow-free (shortlist), 5 mixed. Eye check of 20 random flags: 11 snow/glacier, 6 steep bare rock, 1 vegetation, 1 debris-flow valley floor, 1 unclear; none on a fresh scar.
3. **Winter steps** (`project/winter_check.md`; data `data/winter/`, DEM `data/dem/`): patch 5,075 m vs west block 4,300 m. Air delay explains 3 of 9 winter steps by two independent methods (fit across controls; GUNW weather-model layers), which agree closely. Height-model error: no. Snow: not testable (no clear winter images of this face). **Post-hoc: the July step is not air delay** (predicted +0.12 / +0.01 cm against −5.6 cm).
4. **Blind 24 days at 5 m** (`project/gap_check.md`; data `data/gap/`, GSLC crops): GSLC reproduces the July step (−2.78 vs −2.91 rad). 26 Jul–19 Aug still unreadable; offsets show no patch shift above noise (~0.4 m), upper bound ~0.5 m; a preprint quotes 0.96 m (tension recorded, not resolved).

**Not done / next:**
- Website not updated with these four results (only README). Candidate spots: part 8 (flags: "65 checked, 28 snow, 32 snow-free"), part 9/10 (independent test: no detection), part 5 or 10 (July step is not air delay). Ask the user before changing the site.
- Walkthrough of the site for the user: still at part 5 of 10 ("Was it unusual", 361 slopes). 361 vs 289 is confirmed in code: `control_ranks` needs the pair alone, `controls()` needs both July pairs.
- Codex cross-check of the four new records not done (user's standing preference).
- Team names; RCM (user's own EODMS account); submission text; demo video; old team-brief artifact still describes Quetta.

Local data added this session (ignored by git): `data/indep_bg/` (~42 × 2 files), `data/flagcheck/` (205 Fmask npz, chips), `data/gap/` (5 GSLC crops, ~30 MB each), `data/winter/`, `data/dem/cop_N28_E085.tif`.

---

Older notes follow (session 4 and before). Then `project/spec.md`, `project/plan.md`, `project/progress.md` (running log), `project/results.md` (all numbers).

## What exists

**SlopeWatch**: a reproducible analysis plus a static web app about the Langtang Lirung collapse (Nepal, 26 Aug 2026).

- Site: `docs/index.html` is the story page, `docs/explore.html` the map tool (static; `cd docs && python -m http.server 8765`, open http://127.0.0.1:8765/). Data for the app is in `docs/data` and is committed. Could be served by GitHub Pages from `/docs` (not enabled; needs the repo owner).
- Pipeline: `pipeline/build.py` regenerates `docs/data` from `data/` (about 8 minutes). `pipeline/write_results.py` regenerates the numeric sections of `project/results.md`.
- Tests: `python -m pytest tests -q` (19 tests; real-data tests skip if `data/` is absent).
- Raw extracts: `data/` (not in git). `data/series/` holds 34 interferogram windows fetched by `scripts/series_fetch.py`.
- Python: `C:/Users/HP/anaconda3/python.exe` (numpy, scipy, PIL, h5py work; matplotlib, pandas, skimage, rasterio, pyproj do not).

## Results in brief (details and caveats in `project/results.md`)

1. **Precursor present in standard products.** In the 20 m wrapped interferogram, a 0.056 km² patch on the slope shows a phase step equivalent to 4.7–5.6 cm line of sight in 14–26 Jul (five references agree), 0.6 cm in 2–14 Jul. It is the only pair in the year in which the patch exceeds every comparable slope (0 of 361). The 80 m unwrapped layer discards the patch; that caused Codex's earlier negative result. Codex has since reproduced the numbers.
2. **Final 24 days unresolved.** 26 Jul–19 Aug has spatially mixed phase; no value is reported.
3. **Winter observation, open.** The patch was readable in nine pairs from 28 Nov to 16 Mar with steps of 0.2–2.3 cm, mostly one sign, above the controls' 95% level in four pairs but never above all controls. Could be slow movement, snow, or topographic residual. Not claimed as a finding.
4. **Detector.** A "new movement" rule (frozen after calibration on Langtang) run over 22 pairs flags Langtang in exactly one pair (14–26 Jul) and raises 270 flags in total (median 6.5 per pass); the other 268 are unverified and cluster in spring and autumn.
5. **Collapse.** Backscatter change inside the UNOSAT polygon rises from 18.6% to 41.2% of pixels; 97 control areas rise by at most 8.5 points.
6. **No second look direction.** Descending track has valid data over the patch in one of eight pairs, and it is not readable there.

## What is not established

Ground movement as the cause of the phase step; direction and true size; onset date; anything about lead time or availability of products at the time; meaning of the other flags; performance anywhere else. The rule was tuned on Langtang, so its Langtang flag is not an independent detection.

## Session 4 update (15 Nov 2026) — START HERE, then read session 3 below for background

- **Sentinel-1 is done.** All 24 products downloaded; `scripts/s1_patch.py` ran once, unedited. Result: no pair ending after 14 Jul is readable on the patch on any track; the two readable pairs (25 Jun–7 Jul track 19, 2–14 Jul track 121) are 0.1–0.2 cm and ordinary among controls. Sentinel-1 neither confirms nor contradicts the NISAR step and does not fill the gap. Record: `project/results.md` section 7; reading check `scripts/s1_readcheck.py`. Item 1 of session 3 below is finished.
- **Sentinel-1 brightness (OPERA RTC-S1) is done** (`scripts/s1_rtc.py`, `project/results.md` section 8): track 85 has the patch fully in layover; on 24 Aug (50 h before) brightness was normal; across the collapse it dropped 12.0 dB (track 19) and 10.6 dB (track 121) with no control matching; a June–July brightening is seasonal (2025 repeats it). Not yet shown on the website.
- **Website is live on Vercel:** https://dancing-with-the-sars-docs.vercel.app/ (the user deployed it; root directory `docs`, redeploys on every push to `main`). GitHub Pages is not needed. The Sentinel-1 slot is filled from `story.json`; its new wording in `docs/story.js` was not looked at in a browser by Claude.
- **Root tidy:** all note files moved to `notes/` on the user's request; only `README.md` and `HANDOFF.md` stay in the root. Quetta notes are in `notes/` too and still ignored by git.
- **In progress: website walkthrough for the user**, so they can defend it to judges. Format that worked: what the section shows, where each number comes from, then likely judge questions with honest answers, in simple words. The page has ten parts: 1 hero, 2 the event, 3 how radar measures 5 cm, 4 what the satellite saw (four panels), 5 was it unusual (361 slopes), 6 one year 26 frames, 7 the blind 24 days and Sentinel-1, 8 one flag among 270, 9 could this time an alarm, 10 what we do not claim. **Parts 1–4 are done. Resume at part 5** when the user says "next". Worth explaining there: the page says 361 controls (readable in the 14–26 Jul pair alone) while `project/results.md` section 3 says 289 (readable in both July pairs); Claude inferred this difference from the data file and did not confirm it in `scripts/site_assets.py`. Check before telling the user.
- **Waiting on the user:** whether to add the two brightness points (12 dB drop across the collapse with no control matching; normal brightness 50 h before) to part 7 of the website. Offered, not answered. If yes, add them through `scripts/site_assets.py` and `docs/story.js` so the numbers come from `data/rtc/rtc_patch.json`, not typed by hand.
- **Not looked at in a browser by Claude:** the filled Sentinel-1 box and the extra sentence in "More than one satellite" on the live site. Playwright did not connect this session.
- **Challenge resource list re-read:** RCM (EODMS) and SAOCOM (CONAE) are the only listed sources still unsearched; both need the user's own accounts. Offered; the user has not registered.
- **Local data added this session (ignored by git):** `data/s1/` (5.5 GB, 24 zips + results), `data/rtc/` and `data/rtc_2025/` (about 330 MB each). `previews/story_*.png` are untracked and uncommitted.
- **Still open:** team member names; next steps list below (independent test of the frozen rule is the most valuable).

## State at the end of session 3 (15 Nov 2026) — START HERE

**1. Sentinel-1 download is running by itself.** A detached process (`scripts/s1_finish.py`, log `data/s1_finish.log`) downloads the 24 HyP3 burst interferograms into `data/s1/` (about 230 MB each, roughly 5.5 GB) and then runs `scripts/s1_patch.py`, writing `data/s1/s1_patch.json` and `data/s1/s1_patch_table.txt`.
- First thing next session: `ls data/s1/*.zip | wc -l` (want 24) and read `data/s1_finish.log`.
- If it stopped (PC restarted, fewer than 24 zips): check no copy is running, delete any `*.part`, run `C:/Users/HP/anaconda3/python.exe scripts/s1_finish.py` again. Finished files are skipped. HyP3 keeps the products for about two weeks from 15 Nov.
- `scripts/s1_patch.py` has **never been run on real data**. Its rules were fixed before any Sentinel-1 file was opened (same patch pixels, west-block reference, consistency 0.6, same controls as NISAR). Expect to debug reading (GeoTIFF via PIL; grid, EPSG, sign) but do not change the rules after seeing results; if a rule must change, record it.
- Then: read the table, write the result into `project/results.md` (new section) and `notes/Langtang data hunt - Claude.md`, rerun `scripts/site_assets.py` so the website's Sentinel-1 slot fills in, check the page, push. Report the result whatever it is; a null is a result.

**2. Website is built, not yet live.** `docs/index.html` (story page) + `docs/story.css` + `docs/story.js`; images and `story.json` in `docs/story/`, built by `scripts/site_assets.py` (and `scripts/site_optical.py` for two HLS Sentinel-2 scenes). The old map tool is `docs/explore.html`. Preview: `cd docs && python -m http.server 8765`. Screenshots: `previews/story_*.png`.
- Waiting on the user: (a) whether to enable GitHub Pages from `/docs` (not enabled; `gh` works on this machine); (b) team member names for a team section.
- User's aim: presentation that wins attention; cinematic look. Our line: beautiful, but only claims we can prove. Wording rules below still apply.
- Ideas not done: demo video, submission text, a short "how to read this" for judges.

**3. Data hunt results** (record: `notes/Langtang data hunt - Claude.md`).
- Location confirmed: patch centre 44 m from Li (2026)'s centroid, 147 m from HiRISK (both quoted in Sah's preprint).
- NISAR: only tracks 098 A and 048 D; new validated GCOV/GSLC to 11 Nov; nothing fills 27 Jul – 10 Aug. GSLC is unused.
- Sentinel-1: three tracks (19 D, 121 D, 85 A); passes on 31 Jul, 4, 7, 12, 16, 19, 24 Aug between NISAR's 26 Jul pass and the collapse.
- ALOS-2 ends Mar 2025 here. RCM and SAOCOM catalogues not searched (own logins).
- The user approved the ASF application on Earthdata; HyP3 works (7,976 credits left).

**4. Repository.** Quetta and other Pakistan exploration files were removed from the public repo on the user's request (kept locally, in `.gitignore`). They remain in git history; history was not rewritten.

## Suggested next steps (none started)

1. **Independent test of the frozen rule** on a second, unrelated slope failure or a known slow landslide with NISAR coverage. This is what would make the watch-list idea credible.
2. Look at a sample of the 268 other flags against optical imagery to classify them (glacier margin, snow, real movement).
3. Follow up the winter observation: same patch measurement with a terrain model to test elevation-correlated phase; compare with snow data.
4. Quantify 26 Jul–19 Aug with proper unwrapping or offsets from higher-resolution products (RSLC/GSLC).
5. Enable GitHub Pages for `docs/`, update the team brief artifact (https://claude.ai/artifact/4VJB2yVSicxijtiRJvZFQ5 still describes Quetta), prepare the submission text and demo video.

## Decisions on record

- Working project: Langtang. Quetta subsidence paused (nine-pair stack dominated by atmosphere; details in `notes/Quetta deep dive and alternatives - Claude.md`, kept locally and not in the public repository since 15 Nov). Fallbacks: glacier speed atlas; Manchar Lake.
- Wording rules for anything public: "phase step equivalent to X cm along the line of sight", "flag" not "warning", no casualty figures, no claims about what could have been done.
- Detector parameters are frozen (`pipeline/params.json`). Any change must be recorded in `project/results.md` section 6 with before/after numbers.

## Tooling notes

- Earthdata Login is in `C:\Users\HP\.netrc` (never print or commit it). `scripts/nisar_io.py` reads NISAR HDF5 remotely.
- In this environment bash heredocs fail on some content; write scripts to files instead.
- Codex plugin: model `gpt-6-sol` works; ask for read-only reviews and keep it out of `data/` while jobs run.
- Earlier records kept for provenance: `notes/Langtang verification - Claude.md`, `notes/Langtang local verification - Codex.md`, `notes/Langtang continuation - Codex.md`, `notes/Langtang collapse - Claude.md`.
