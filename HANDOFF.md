# Handoff — state at end of session, 14 Nov 2026

Read this first when resuming. It says what is decided, what is running, and the exact next steps.

## Decision
- **Working project: Langtang Lirung collapse, Nepal, 26 Aug 2026.** Question: could NISAR have seen it coming, and where else is a slope doing the same thing now?
- **Quetta subsidence: paused** at the user's request. First test was inconclusive (see below).
- **Fallbacks:** world glacier speed atlas from GOFF; Manchar Lake water extent.

## Proposed project shape (not yet confirmed by results)
1. Reconstruct slope and glacier movement on the north face of Langtang Lirung from the year-long NISAR record up to 19 Aug 2026.
2. Compare with the published precursor: up to 30 cm of slope movement in the 3–4 weeks before failure (ICIMOD, citing Q. Brencher).
3. Map the collapse scar, debris path and barrier lakes from the scenes after 26 Aug.
4. Generalise into a watch-list tool that flags accelerating ice and rock faces above rivers, hydropower and border crossings, updated on every pass.

Limits already established: NISAR revisits a track every 12 days (about 4 days with three tracks), so no daily monitoring; the flood arrived within about 7 minutes, so only pre-failure movement gives warning; the instrument gap (27 Jul – 10 Aug 2026) sits inside the precursor window, making the key pair 26 Jul → 19 Aug span 24 days.

## Background jobs at handoff
Both write to the session scratchpad, which may be cleaned up. Files finished so far were copied to `data/lang/`.

| Job | Script | Finished at handoff | Still to come |
|---|---|---|---|
| Full-resolution GCOV windows (10 m, HHHH and HVHV), track 098 A 016 | `scripts/lang_gcov.py` | 14 Jul, 26 Jul, 19 Aug | 31 Aug, 12 Sep, 24 Sep |
| GUNW phase and GOFF offsets, track 098 A 016 | `scripts/lang_pairs.py` | GUNW pairs starting 2 Jul, 14 Jul, 26 Jul, 19 Aug | GUNW pairs starting 8 Jun, 20 Jun; all six GOFF pairs |

Both scripts skip files that already exist, so re-running them from a folder containing `lang/` completes the set. Window: 85.33–85.62 E, 28.20–28.37 N.

## Next steps, in order
1. Finish the two extractions (re-run the scripts if the session ended).
2. **Event change map:** log-ratio of HHHH and HVHV, 19 Aug → 31 Aug, compared with the quiet interval 14 Jul → 26 Jul. Expect the scar, debris path and any lake to stand out.
3. **Precursor test:** in the GUNW pairs before 19 Aug, look for a localised phase signal on the north face near 28.3 N, 85.5 E, 5,000–5,500 m. Check coherence first; steep ice may be decorrelated, in which case use the GOFF offsets.
4. Confirm the phase sign convention from the GUNW product specification before stating direction of motion.
5. Bring in descending tracks 048 D 074 and 149 D 074 for a second look angle.
6. Read the rest of the Wikipedia article (only the first 100,000 characters were read) and find the original Brencher and Adhikari analyses.
7. Only then design the app.

## Access and tooling
- Earthdata Login works through `C:\Users\HP\.netrc` (in the home folder, not in the repo).
- `scripts/nisar_io.py` opens NISAR HDF5 files remotely with range requests; no full downloads needed. A 30 km window takes about 3–4 minutes per file.
- `scripts/utm.py` has UTM and polar stereographic transforms (`ll2xy`). `pyproj`, `rasterio`, `matplotlib`, `xarray`, `earthaccess` and `asf_search` are not usable in this Python install (matplotlib and pandas are broken by a NumPy 2 mismatch). Images are written with PIL.
- Codex plugin: the model name that works is `gpt-6-sol`. `gpt-6.1-sol` fails. Codex's sandbox cannot reach the CMR endpoint, so it cannot verify catalogue counts.
- `data/` holds extracted windows (about 700 MB) and is ignored by git.

## Quetta, where it stopped
- Nine GUNW pairs on track 041 A 017 stacked (17 Jun → 15 Oct). Background spread 4.7 cm after ionosphere correction; expected signal about 5 cm. The summed map follows topography (stratified troposphere). No bowl distinguishable.
- Troposphere, tide and geometry cubes for the nine pairs are extracted in `data/atm/`. Applying them needs a terrain model, not yet fetched. Sign convention unverified.

## Verification status
- Catalogue counts and dates: checked by Claude through CMR; Codex confirmed the Pakistan totals earlier in its own app but could not re-check the glacier and Langtang counts.
- Event facts: ICIMOD and Wikipedia, both secondary. Casualty figures differ by source and date.
- RGI 7.0 glacier count (274,531): confirmed by Codex.
- No result yet shows the Langtang collapse or its precursor in NISAR data.

## Published artifact
Team brief (private until shared): https://claude.ai/artifact/4VJB2yVSicxijtiRJvZFQ5 — it still describes Quetta as the proposed idea and needs updating once the Langtang tests are in.
