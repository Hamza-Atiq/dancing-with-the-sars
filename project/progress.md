# Progress log — SlopeWatch build

Newest entries at the bottom. A new session should read `HANDOFF.md`, then `project/spec.md`, `project/plan.md`, then this file, and continue from the last entry.

## 14–15 Nov 2026 (Claude session 2)

- Verified Codex's continuation; found the precursor in the 20 m wrapped phase. Record: `Langtang verification - Claude.md`. Pushed (commit af6649e).
- User instructions for this phase: write spec → plan → have Codex review both → build without stopping; keep records current so another session can continue.
- Started `scripts/series_fetch.py` in the background: 34 GUNW pairs (26 ascending track 098, 8 descending track 048) → `data/series/`. Log in `data/series_fetch.log`. If the session dies, rerun `cd scripts; C:/Users/HP/anaconda3/python.exe -u series_fetch.py`; it skips finished files.
- Detector prototype on the six old pairs (scratch only): single-pair anomaly rule gives 23–130 blobs per pair, mostly glaciers; in 14–26 Jul the Langtang patch is the 2nd largest blob (292 px) and has the highest mean anomaly (2.81 rad). Conclusion: rule needs a "quiet history" condition. This set the thresholds in the spec before the year-long run.
- Wrote `project/spec.md` v1 and `project/plan.md`.
- Codex reviewed spec v1 and plan (read-only). It reproduced the patch numbers with its own code and agreed the earlier negative result came from the 80 m filter. Five must-fix points applied → spec v2. Record: `project/review-codex-spec.md`.
- Built and tested (15 tests pass, `python -m pytest tests -q`): `pipeline/geo.py` (UTM transforms, reprojection, polygon mask), `pipeline/anomaly.py` (spec 4.1), `pipeline/detect.py` (spec 4.2), `pipeline/collapse.py` (spec 4.5), `pipeline/calibrate.py` (plan step 3b). Parameters in `pipeline/params.json` are provisional until calibration is recorded.
- Series files carry a mask on the wrapped grid (values seen: 11 valid, 111 water). Old `data/lang` extracts do not.
- Fetch rate about 200 s per pair; newest pairs first.
- Shell note: bash heredocs fail on some file contents in this environment; write files with the Write tool instead.
