# Handoff — state at end of session, 14 Nov 2026

Read this first when resuming. It says what is decided, what is running, and the exact next steps.

**Latest Claude update (supersedes the Codex conclusion below): read `Langtang verification - Claude.md` first.** The published precursor IS visible in the standard 20 m wrapped interferograms: a ~0.06 km² patch in the south-east of the UNOSAT polygon shows no movement 2–14 July, about 5.6 cm line-of-sight in 14–26 July, and more than one fringe in 26 July–19 August. Codex missed it because its coherence ≥ 0.6 / connected-component filter removed the moving ground. Codex's backscatter numbers are confirmed and now have a 97-position control test. Next steps are in the "Path forward" section of that file. Scripts: `scripts/verify_*.py`; images: `previews/lang_verify_*.png`.

Earlier Codex update: read **Langtang local verification - Codex.md** before resuming. All 18 original extracts are complete. Analysis using a downloaded UNOSAT detachment polygon finds increased backscatter change across the collapse, but has not reproduced the published precursor. Explicit processing-version and validity-mask checks are available. Scripts, numerical outputs and review instructions are saved for independent verification. No application has been built.

Key results: HH pixels with absolute change >3 dB increase from 18.55% in July 14–26 to 41.22% in August 19–31 within the mapped polygon, using the same valid pixels. The three old ascending precursor extracts match X05026 exactly over the review crop; P05023 gives nearly identical diagnostic results. Only 19 of 307 source-area pixels meet coherence >=0.6 and component checks across the three benchmark intervals. Descending July 11–23 and August 16–28 have no valid source-area samples after subswath masking; July 23–August 16 has valid coverage. A second-angle acceleration time series is not established.

## Decision
- **Working project: Langtang Lirung collapse, Nepal, 26 Aug 2026.** Question: could NISAR have seen it coming, and where else is a slope doing the same thing now?
- **Quetta subsidence: paused** at the user's request. First test was inconclusive (see below).
- **Fallbacks:** world glacier speed atlas from GOFF; Manchar Lake water extent.

## Proposed project shape (not yet confirmed by results)
1. Reconstruct slope and glacier movement on the north face of Langtang Lirung from the year-long NISAR record up to 19 Aug 2026.
2. Compare with the published precursor: more than one foot of bedrock motion in the month before failure (University of Washington account of **George Brencher**; original “Q. Brencher” attribution corrected).
3. Map the collapse scar, debris path and barrier lakes from the scenes after 26 Aug.
4. Generalise into a watch-list tool that flags accelerating ice and rock faces above rivers, hydropower and border crossings, updated on every pass.

The key pair July 26–August 19 spans 24 days. The local source-area CMR query returns tracks 098 and 048; 149 was not returned. Do not claim a four-day usable monitoring cadence. Actual masks further reduce usable observations. A retrospective surface-change result does not establish warning lead time.

## Historical extraction jobs (complete; table retained for provenance)
Both write to the session scratchpad, which may be cleaned up. Files finished so far were copied to `data/lang/`.

| Job | Script | Finished at handoff | Still to come |
|---|---|---|---|
| Full-resolution GCOV windows (10 m, HHHH and HVHV), track 098 A 016 | `scripts/lang_gcov.py` | 14 Jul, 26 Jul, 19 Aug | 31 Aug, 12 Sep, 24 Sep |
| GUNW phase and GOFF offsets, track 098 A 016 | `scripts/lang_pairs.py` | GUNW pairs starting 2 Jul, 14 Jul, 26 Jul, 19 Aug | GUNW pairs starting 8 Jun, 20 Jun; all six GOFF pairs |

Both scripts skip files that already exist, so re-running them from a folder containing `lang/` completes the set. Window: 85.33–85.62 E, 28.20–28.37 N.

## Next steps, in order
1. Independently reproduce the saved polygon, backscatter, GUNW-mask, provenance and offset checks in `Langtang local verification - Codex.md`.
2. Resolve the precise moving-bedrock footprint and obtain the original precursor processing recipe or an equivalent independent analysis. The broad UNOSAT polygon and automatic 80 m GUNWs do not reproduce the published map.
3. If continuing deformation research, validate terrain visibility, stable reference terrain, atmospheric/tidal corrections, unwrapping and physical phase sign. Existing phase-equivalent rates are diagnostics only.
4. Validate spatially matched controls and additional pre-event comparison intervals for backscatter. July 14–26 is a comparison interval, not known motionless ground.
5. Choose the app scope with the user based on demonstrated capabilities. A retrospective event/change-and-quality explorer is currently better supported than a warning system. Do not turn conditional research results into hazard predictions.

## Access and tooling
- Earthdata Login works through `C:\Users\HP\.netrc` (in the home folder, not in the repo).
- `scripts/nisar_io.py` opens NISAR HDF5 files remotely with range requests; no full downloads needed. A 30 km window takes about 3–4 minutes per file.
- `scripts/utm.py` has UTM and polar stereographic transforms (`ll2xy`). `pyproj`, `rasterio`, `matplotlib`, `xarray`, `earthaccess` and `asf_search` are not usable in this Python install (matplotlib and pandas are broken by a NumPy 2 mismatch). Images are written with PIL.
- Historical Claude plugin note: `gpt-6-sol` worked in that session. Codex successfully queried CMR using network escalation during this continuation; the dated responses and query are saved in `data/lang_sources/cmr_candidates.json`.
- `data/` holds extracted windows (about 700 MB) and is ignored by git.

## Quetta, where it stopped
- Nine GUNW pairs on track 041 A 017 stacked (17 Jun → 15 Oct). Background spread 4.7 cm after ionosphere correction; expected signal about 5 cm. The summed map follows topography (stratified troposphere). No bowl distinguishable.
- Troposphere, tide and geometry cubes for the nine pairs are extracted in `data/atm/`. Applying them needs a terrain model, not yet fetched. Sign convention unverified.

## Verification status
- Catalogue counts and dates: checked by Claude through CMR; Codex confirmed the Pakistan totals earlier in its own app but could not re-check the glacier and Langtang counts.
- Event research now includes the University of Washington account, a published NRSC paper's public abstract/figures, a recent preprint and original UNOSAT/DEM records. Casualty figures were not needed for the numerical tests.
- RGI 7.0 glacier count (274,531): confirmed by Codex.
- A localized backscatter-change result is documented. The published precursor has not been independently reproduced. See the latest Codex note for completed offset and mask tests. No extraction jobs remain running.

## Published artifact
Team brief (private until shared): https://claude.ai/artifact/4VJB2yVSicxijtiRJvZFQ5 — it still describes Quetta as the proposed idea and needs updating once the Langtang tests are in.
