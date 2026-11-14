# Dancing with the SARs — NASA Space Apps 2026

Research notes and scripts for our entry in the NASA Space Apps 2026 challenge "Dancing with the SARs": build an interactive application that uses NISAR radar data to track and visualise surface change.

## Where we are (14 Nov 2026)

- **Working project:** the Langtang Lirung ice-rock collapse in Nepal on 26 Aug 2026. Question: could NISAR have seen the slope moving beforehand, and can the same method flag other slopes?
- **Status:** all 18 original extracts are complete. Local backscatter changes increase across the collapse within a UNOSAT-mapped detachment boundary. Processing-version, phase-quality, descending-view and offset tests are documented; the published precursor has not been independently reproduced. See `Langtang local verification - Codex.md`.
- **Paused:** Quetta groundwater subsidence. The first nine-pair stack was dominated by atmospheric noise as large as the expected signal.
- **Fallbacks:** a world glacier speed atlas; water extent at Manchar Lake.

**Start with `HANDOFF.md`** for the current state and next steps.

## Files

| File | What it is |
|---|---|
| `HANDOFF.md` | Current decision, running jobs, next steps, tooling notes |
| `Langtang local verification - Codex.md` | Independent boundary, local results, version and mask audit, reproducible checks and remaining limits |
| `Langtang continuation - Codex.md` | Initial extraction inventory and whole-window baseline |
| `Langtang collapse - Claude.md` | Event facts, reported precursors, NISAR coverage at the site, tests under way |
| `Glacier research - Claude.md` | Coverage at 16 glaciers worldwide, first ice-motion numbers, 2026 glacier events, Codex's verification |
| `Quetta deep dive and alternatives - Claude.md` | Every NISAR product over Quetta, preview findings, published ground truth, other directions considered |
| `Independent verification - Claude.md` | Check of the 14 challenge resources and NISAR coverage over Pakistan |
| `Dancing with the SARs - resource review.md` | Codex's original resource review |
| `Quetta deep dive - independent verification.md` | Codex's cross-check of the Quetta findings |
| `NISAR beginner notes.md` | Short primer on the NISAR products |
| `previews/` | Images cut from public browse files and first processing outputs |
| `scripts/` | The Python behind the numbers and images |

## Scripts

Catalogue scripts use only public endpoints. Scripts marked "login" read NISAR science files and need an Earthdata Login.

| Script | Purpose |
|---|---|
| `cmr.py`, `pk.py`, `quetta.py` | Granule counts and repeat stacks: global, Pakistan, Quetta |
| `glac.py`, `events.py` | Coverage at 16 glaciers; coverage around the Langtang and Juneau events |
| `crop2.py`, `gcovsheet.py`, `glacbrowse.py` | Contact sheets from public browse images |
| `nisar_io.py`, `utm.py` | Remote HDF5 reads over HTTPS; UTM and polar stereographic transforms |
| `subset.py`, `subset_atm.py`, `stack.py` | Quetta: cut interferogram windows and correction cubes, stack them (login) |
| `goffread.py` | Read ice-motion offsets and compute speed for a glacier (login) |
| `lang_gcov.py`, `lang_pairs.py` | Langtang: full-resolution backscatter windows; interferogram and offset windows (login) |

They were written as working scripts and run from one folder; paths are relative.

### Earthdata Login

1. Create an account at https://urs.earthdata.nasa.gov
2. Put one line in a file named `.netrc` in your home folder (not in this repository):
   ```
   machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD
   ```

Never commit credentials. `.netrc` and `data/` are listed in `.gitignore`.

## Key facts established so far

- Pakistan has 1,978 Provisional GCOV scenes and 1,676 Provisional GUNW pairs; dense 12-day imaging starts mid-June 2026.
- Validated collections start on 21 Oct 2026 and have almost no interferometric pairs; use the Provisional collections for anything earlier.
- A permanent instrument gap runs from 27 Jul to 10 Aug 2026.
- 15 of 16 well-known glaciers tested have the GOFF ice-motion product.
- Langtang has a year-long record on track 098 A 016 (27 dates, Nov 2025 – Oct 2026), passes on 19 Aug and 31 Aug bracketing the collapse, and Urgent Response scenes from 28 Aug.
- Reported by ICIMOD: satellite radar showed up to 30 cm of slope movement in the 3–4 weeks before the collapse. Not yet reproduced by us.
