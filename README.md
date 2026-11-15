# Dancing with the SARs — NASA Space Apps 2026

Research notes and scripts for our entry in the NASA Space Apps 2026 challenge "Dancing with the SARs": build an interactive application that uses NISAR radar data to track and visualise surface change.

## Where we are (15 Nov 2026)

- **Project: SlopeWatch.** A reproducible analysis and a static web app about the Langtang Lirung ice-rock collapse (Nepal, 26 Aug 2026): what NISAR recorded on the slope beforehand, and what a simple "new movement" rule flags across the surrounding 30 km window.
- **Main result:** the 20 m wrapped interferogram in the standard GUNW product shows a phase step equivalent to about 5 cm along the line of sight on a small patch of the slope between 14 and 26 July, with none in the pass before and none on 289 comparable slopes nearby. An earlier conclusion that the precursor could not be reproduced was wrong (a quality filter had removed the patch); see `Langtang verification - Claude.md`. Limits are stated in the app and in `project/results.md`.
- **Fallbacks:** glacier speed atlas; Manchar Lake.

**Start with `HANDOFF.md`**, then `project/spec.md`, `project/plan.md`, `project/progress.md`, `project/results.md`.

## Run the app

```
cd docs
python -m http.server 8765
```
Open http://127.0.0.1:8765/ . The app is static (`docs/`), so it can also be served by GitHub Pages from the `docs` folder.

## Rebuild the results

Needs Python with numpy, scipy, Pillow, h5py, fsspec, requests, pytest, and an Earthdata Login (below).

```
cd scripts && python series_fetch.py        # 34 interferogram windows into data/series (about 1 hour)
cd .. && python pipeline/build.py           # everything in docs/data
python -m pytest tests -q
```
The backscatter part also needs the six GCOV windows from `scripts/lang_gcov.py` and the UNOSAT polygon from `scripts/lang_export_unosat.py` in `data/`.

| Folder | What it is |
|---|---|
| `project/` | Specification, plan, progress log, results, Codex review records |
| `pipeline/` | Analysis code: phase anomaly, detector, slope time series, collapse statistics, image rendering, build |
| `tests/` | Unit tests on synthetic data and checks on the real extracts |
| `docs/` | The web app and its generated data |

## Files

| File | What it is |
|---|---|
| `HANDOFF.md` | Current decision, running jobs, next steps, tooling notes |
| `Langtang verification - Claude.md` | Independent check of the Codex continuation; where the precursor was found |
| `Langtang local verification - Codex.md` | Independent boundary, local results, version and mask audit, reproducible checks and remaining limits |
| `Langtang continuation - Codex.md` | Initial extraction inventory and whole-window baseline |
| `Langtang collapse - Claude.md` | Event facts, reported precursors, NISAR coverage at the site, tests under way |
| `Glacier research - Claude.md` | Coverage at 16 glaciers worldwide, first ice-motion numbers, 2026 glacier events, Codex's verification |
| `Independent verification - Claude.md` | Check of the 14 challenge resources and NISAR coverage over Pakistan |
| `Dancing with the SARs - resource review.md` | Codex's original resource review |
| `NISAR beginner notes.md` | Short primer on the NISAR products |
| `previews/` | Images cut from public browse files and first processing outputs |
| `scripts/` | The Python behind the numbers and images |

## Scripts

Catalogue scripts use only public endpoints. Scripts marked "login" read NISAR science files and need an Earthdata Login.

| Script | Purpose |
|---|---|
| `cmr.py`, `pk.py` | Granule counts and repeat stacks: global, Pakistan |
| `glac.py`, `events.py` | Coverage at 16 glaciers; coverage around the Langtang and Juneau events |
| `gcovsheet.py`, `glacbrowse.py` | Contact sheets from public browse images |
| `nisar_io.py`, `utm.py` | Remote HDF5 reads over HTTPS; UTM and polar stereographic transforms |
| `goffread.py` | Read ice-motion offsets and compute speed for a glacier (login) |
| `lang_gcov.py`, `lang_pairs.py` | Langtang: full-resolution backscatter windows; interferogram and offset windows (login) |
| `series_fetch.py` | Langtang: 20 m wrapped interferogram and coherence for every pair on two tracks (login) |
| `lang_*.py` (others), `verify_*.py` | Codex's local checks; Claude's independent verification |

They were written as working scripts and run from one folder; paths are relative.

### Earthdata Login

1. Create an account at https://urs.earthdata.nasa.gov
2. Put one line in a file named `.netrc` in your home folder (not in this repository):
   ```
   machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD
   ```

Never commit credentials. `.netrc` and the top-level `data/` folder are listed in `.gitignore`.

## Key facts established so far

- Pakistan has 1,978 Provisional GCOV scenes and 1,676 Provisional GUNW pairs; dense 12-day imaging starts mid-June 2026.
- Validated collections start on 21 Oct 2026 and have almost no interferometric pairs; use the Provisional collections for anything earlier.
- A permanent instrument gap runs from 27 Jul to 10 Aug 2026.
- 15 of 16 well-known glaciers tested have the GOFF ice-motion product.
- Langtang has a year-long record on track 098 A 016 (27 dates, Nov 2025 – Oct 2026), passes on 19 Aug and 31 Aug bracketing the collapse, and Urgent Response scenes from 28 Aug.
- Reported by ICIMOD and the University of Washington: satellite radar showed accelerating slope movement in the weeks before the collapse. Our reading of the standard products is consistent with it for 14–26 July; the final 24 days are unresolved in our analysis.
