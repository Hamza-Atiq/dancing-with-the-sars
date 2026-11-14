# Dancing with the SARs — NASA Space Apps 2026

Research notes and scripts for our entry in the NASA Space Apps 2026 challenge "Dancing with the SARs": build an interactive application that uses NISAR radar data to track and visualise surface change.

## Where we are (14 Nov 2026)

- **Proposed idea, not final:** an interactive map of how fast Quetta is sinking from groundwater over-pumping, measured with NISAR interferograms and linked to the electric and solar tubewells that drive the pumping.
- **Fallback:** surface-water extent at Manchar Lake and along the Indus.
- **Data test in progress:** stacking nine 12-day interferograms on track 041 to see whether the Quetta sinking bowl appears. No result yet.

## Read in this order

| File | What it is |
|---|---|
| `Independent verification - Claude.md` | Check of all 14 challenge resources against the live pages, plus NISAR coverage over Pakistan from NASA's CMR catalogue |
| `Quetta deep dive and alternatives - Claude.md` | Every NISAR product over the Quetta valley, what the preview images show, published ground truth, and the other directions considered |
| `Dancing with the SARs - resource review.md` | Codex's original resource review (some statements are corrected in the file above) |
| `Quetta deep dive - independent verification.md` | Codex's cross-check of the Quetta findings |
| `NISAR beginner notes.md` | Short primer on the NISAR products |
| `previews/` | Contact sheets cut from NASA's public browse images: interferograms around Quetta (`sheet_*`) and backscatter time strips for other sites (`gcovsheet_*`) |
| `scripts/` | The Python used to produce the numbers and images |

## Scripts

All scripts use only public endpoints except `subset.py`, which reads NISAR science files and needs an Earthdata Login.

| Script | Purpose |
|---|---|
| `cmr.py` | Granule counts per NISAR collection, globally and over Pakistan |
| `pk.py` | Monthly coverage and repeat stacks at seven Pakistani sites |
| `quetta.py` | Full product list over the Quetta valley, by track and date |
| `crop2.py`, `gcovsheet.py` | Build the preview contact sheets from public browse images |
| `nisar_io.py`, `utm.py` | Helpers: remote HDF5 reads over HTTPS, lat/lon to UTM |
| `subset.py` | Cut a 100 km window around Quetta out of each interferogram without downloading the full 2.3 GB file |

They were written as working scripts and run from one folder; paths are relative.

### Earthdata Login

1. Create an account at https://urs.earthdata.nasa.gov
2. Put one line in a file named `.netrc` in your home folder (not in this repository):
   ```
   machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD
   ```

Never commit credentials. `.netrc` is listed in `.gitignore` as a safeguard.

## Key facts established so far

- Pakistan has 1,978 Provisional GCOV scenes and 1,676 Provisional GUNW pairs (Oct 2025 – Oct 2026); dense 12-day imaging starts mid-June 2026.
- The Validated GUNW collection has no coverage of Pakistan; use `NISAR_L2_GUNW_PROVISIONAL_V1`.
- Quetta has 52 GUNW pairs on four tracks (041 and 142 ascending, 092 and 020 descending), 17 Jun – 18 Oct 2026.
- A permanent instrument gap runs from 27 Jul to 10 Aug 2026.
- Published rates for central Quetta are 12–16.6 cm per year (Kakar et al. 2024; Natural Hazards 2025). Taken from abstracts.
