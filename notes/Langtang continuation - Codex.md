# Langtang continuation, November 14, 2026

Read HANDOFF.md and the Langtang and glacier research notes before this record. The working direction is Langtang. The existing Quetta research remains paused.

All 18 requested extracts are present in data/lang and opened successfully with NumPy. There are six GCOV dates, six GUNW pairs, and six GOFF pairs. The pending extraction step in HANDOFF.md is now complete as judged from local file presence and readable arrays. I did not independently re-extract them or verify their source granule provenance.

I added scripts/lang_check.py and ran it successfully with C:/Users/HP/anaconda3/python.exe. The default Python lacks NumPy. The script resolves paths relative to the repository and can be rerun from any working directory.

Outputs are data/lang_check/checks.json, quiet_change.npz, and event_change.npz. The JSON inventories every file and its arrays. Both comparisons passed exact x, y and EPSG grid equality checks. Change is 10 times log10(after/before), computed only for positive finite power values. The quiet interval is July 14–26 and the event interval is August 19–31. No smoothing or threshold tuning was performed.

Across the whole extracted window, HH pixels changing by more than 3 dB in either direction comprise 18.30% of the quiet pair and 18.50% of the event pair. HV figures are 19.56% and 19.91%. About 97.09% of pixels have positive finite power in both observations. These similar window-wide statistics cannot identify or exclude a small localized collapse. They establish a baseline against which a mapped scar should be tested. The 3 dB threshold is descriptive and has not been calibrated as a detection rule.

GUNW median coherence ranges from 0.413 to 0.620 across the six windows. July 26–August 19 has median 0.559 and 43.49% of window pixels at or above 0.6. Those statistics apply to the entire crop. The source slope's coherence remains to be checked. Valid numeric coherence includes zeros and does not establish usable phase at those pixels.

Next, independently locate the collapse scar from a cited map or original analysis and use its footprint to evaluate both change maps and the source-area coherence. Interpret the GCOV mask codes before excluding terrain-affected pixels, apply common masks, and compare with nearby stable control areas. Check phase sign, connected components, reference stability and correction conventions before estimating motion. GOFF needs quality screening, time-interval normalization and stable-ground referencing before interpreting acceleration. No displacement or warning capability has been established by this run.

For Claude's independent review, rerun scripts/lang_check.py, verify the stored file inventory and grid checks, and recompute the statistics using its own code. Check the expected source footprint against the extracted bounds before drawing conclusions. The event descriptions, reported 30 cm precursor, source geometry and casualty figures were inherited from the research notes and were not independently verified in this continuation. No product UI was built in this step.
