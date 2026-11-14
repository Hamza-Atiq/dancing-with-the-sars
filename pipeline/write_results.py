"""Regenerates sections 2, 4, 5 and 6 of project/results.md from docs/data/*.json.
Sections 1 (calibration) and 3 (negative controls) are hand-written records and are kept as they are.
Usage: python pipeline/write_results.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def d(n):
    return f"{int(n[6:8])} {MONTHS[int(n[4:6]) - 1]}"


def pr(n):
    return f"{d(n[:8])}–{d(n[9:])}"


def main():
    f = ROOT / 'project/results.md'
    s = f.read_text(encoding='utf-8')
    i = s.index('## 2. Langtang patch time series')
    j = s.index('## 3. Negative controls')
    k = s.index('## 4. Collapse backscatter')
    data = ROOT / 'docs/data'
    t = json.loads((data / 'series.json').read_text())
    e = json.loads((data / 'evaluation.json').read_text())
    sv = json.loads((data / 'sensitivity.json').read_text())
    c = json.loads((data / 'collapse.json').read_text())
    k2c = t['rad_to_cm']

    rows = []
    for r in t['rows']:
        w = r['refs']['west block']
        so = r['refs']['ring south']
        cr = t['control_ranks'].get(r['pair'])
        ver = r['source'].split('_')[15] if r['source'].startswith('NISAR') else '?'
        if r['resolved']:
            rows.append(f"| {pr(r['pair'])} | {ver} | {r['patch_median_coherence']:.2f} | {w['los_cm']:+.1f} | {w['consistency']:.2f} | "
                        f"{so['los_cm']:+.1f} ({so['reference_consistency']:.2f}) | {cr['control_p95'] * k2c:.1f} | {cr['controls_at_or_above_langtang']} of {cr['n_controls']} |")
        else:
            rows.append(f"| {pr(r['pair'])} | {ver} | {r['patch_median_coherence']:.2f} | not readable (consistency {w['consistency']:.2f}) | | | | |")
    key = t['control_ranks']['20260714_20260726']
    sec2 = f"""## 2. Langtang patch time series — full year (26 ascending pairs)

Patch {t['patch_pixels']} pixels ({t['patch_area_km2']:.3f} km²), fixed. "Readable" = patch and west-block consistency ≥ 0.6. Values are wrapped-phase line-of-sight equivalents in cm (the sign is the raw phase sign; physical direction unverified). "Controls p95" is the level 95% of other comparable slopes stay below in that pair; the last column counts controls at or above the Langtang value.

| Pair | Version | Patch coherence | West block, cm | Consistency | South ring, cm (its steadiness) | Controls p95, cm | Controls ≥ Langtang |
|---|---|---:|---:|---:|---:|---:|---:|
""" + "\n".join(rows) + f"""

Findings:
- **14–26 Jul is the only pair in which the patch exceeds every control slope** (0 of {key['n_controls']}). All five references agree (4.7–5.6 cm).
- **Unexpected: the patch was readable in nine winter pairs (28 Nov – 16 Mar) and is not at zero.** Steps of 0.2–2.3 cm against the west block; the first five are all negative (−1.7, −1.1, −1.6, −0.6, −2.3 cm) and the steady south ring broadly agrees. In four of the nine pairs the patch is above the 95% level of the controls, in none above all of them. This could be slow movement months before the collapse, seasonal snow on this slope, or residual topographic phase. It is recorded as an open observation, not a finding. "No movement before July" is therefore too strong; correct is "no step in 2–14 Jul; small steps of uncertain origin in winter".
- Mid-March to June: not readable (patch coherence 0.22–0.26), consistent with snow and melt.
- The north, east and west rings (selected by July coherence) are not steady in winter (steadiness 0.1–0.5) and are not used for those pairs. The east ring disagrees in 2–14 Jul (−4.5 cm, steadiness 0.70); unexplained.
- **Unwrapping check.** 14–26 Jul: two quality-guided paths both give +3.19 rad (6.1 cm), the same wrapped value as −2.91 rad taken the other way round, so the sign is ambiguous. 26 Jul–19 Aug: both paths returned −0.30 rad with a spread of −1.3 to +2.1 rad inside the patch. This is not reported as a value: the pair is not readable by the consistency rule, path-following cannot detect aliasing across an incoherent patch edge, and the two paths differ only by a quality threshold. The reporting rule was tightened to require a readable pair (conservative change made after seeing this output). Status: **spatially mixed phase, magnitude unresolved**.
- **Descending track 048 (8 pairs):** the product has valid data over the patch in one pair only (23 Jul–16 Aug, 24 days; 221 of 672 box pixels coherent, median coherence 0.39). The patch is not readable in it (consistency below 0.6). The other seven pairs are masked invalid over the patch. No second viewing angle is available from standard products.

"""
    ev = e['summary']
    erows = "\n".join(
        f"| {pr(r['pair'])} | {r['days']} | {r['measurable_km2']:.0f} | {r['eligible_km2']:.0f} | "
        f"{r['flags'] if r['has_history'] else '—'} | {r['flags_at_langtang'] if r['has_history'] else '—'} |" for r in e['rows'])
    lab = {'flag_abs_anomaly_rad': 'flag threshold (rad)', 'quiet_abs_anomaly_rad': 'quiet limit (rad)',
           'min_blob_pixels': 'smallest flag (pixels)', 'min_history_measurable': 'quiet earlier pairs required',
           'history_pairs': 'earlier pairs examined', 'background_box': 'background box (pixels)'}
    srows = "\n".join(
        f"| {lab[v['parameter']]} = {v['value']} | {v['total_flags']} | {v['flags_at_langtang_total']} | "
        f"{', '.join(pr(p) for p in v['pairs_with_langtang_flag']) or 'none'} |" for v in sv['variants'])
    h, hv = c['channels']['HHHH'], c['channels']['HVHV']
    sec4 = f"""## 4. Collapse backscatter (`pipeline/collapse.py`)

Inside the UNOSAT polygon ({h['valid_pixels']} valid 10 m pixels), pixels changing by more than 3 dB: HH {h['quiet_pct']:.2f}% (14–26 Jul) → {h['event_pct']:.2f}% (19–31 Aug); HV {hv['quiet_pct']:.2f}% → {hv['event_pct']:.2f}%. {h['controls_n']} shifted control polygons: largest increase {h['control_event_minus_quiet_max']:.1f} points (HH), against {h['event_minus_quiet']:.1f} at the collapse. The verification script, with a different rasteriser, gave 18.54 / 41.11 and 8.7; the difference is edge pixels.

## 5. Year-long detector evaluation (frozen rule, run once)

Window {e['window_km2']:.0f} km². The first four pairs have no history.

| Pair | Days | Measurable km² | Eligible km² | Flags | On Langtang slope |
|---|---:|---:|---:|---:|---:|
{erows}

- {ev['pairs_with_history']} pairs with history, **{ev['total_flags']} flags**, median {ev['median_flags_per_pair']} per pair, most {ev['max_flags_per_pair']}.
- **Langtang is flagged in one pair only, 14–26 Jul** (2 flags; the larger is 2nd of 4 by area and 1st by mean anomaly). It is not flagged in any earlier pair, including winter, and not in 26 Jul–19 Aug (history no longer quiet).
- Before the collapse: {ev['pre_collapse_pairs_with_history']} pairs, {ev['pre_collapse_flags_not_at_langtang']} flags elsewhere. Overall about {ev['mean_unverified_flags_per_100km2_eligible_per_pass']:.1f} **unverified** flags per 100 km² of eligible ground per pass.
- Flag counts rise in spring (28 Mar–9 Apr: 35; 15 May–8 Jun: 25 and 33) and autumn (Sep–Oct: 19–32), when snow cover changes. This suggests many flags are seasonal surface effects. None was checked.
- The rule was adjusted on Langtang (section 1), so the Langtang flag is not an independent detection.

### Sensitivity (one setting changed at a time; base = {sv['base']['total_flags']} flags, {sv['base']['flags_at_langtang_total']} on Langtang)

| Setting | All flags | On Langtang | Langtang flagged in |
|---|---:|---:|---|
{srows}

The Langtang flag survives every variant except a larger minimum flag size (80 pixels) and the original requirement of two quiet earlier pairs. It never appears in another pair.

## 6. What changed after seeing data (complete list)

1. `min_history_measurable` 2 → 1, during calibration, before the year-long run (section 1).
2. Unwrap reporting rule tightened to require a readable pair (section 2). Conservative.
3. Anomaly image opacity and resolution, for display only. No effect on numbers.
4. Per-pair control ranking added after the winter values appeared (section 2), to put them in context. No detector setting was changed after the year-long run.

Provenance of item 1 and of "no change after the year-long run": this is the project's own record. The shipped JSON files hold only the final settings, and git does not prove the order either: the commit intended to capture the freeze did not include `pipeline/params.json`, so the frozen file first appears in commit `4eb4ad5` together with the year-long results. What can be checked: section 1 lists the calibration trials with their outputs, the sensitivity table in section 5 shows what the original setting (two quiet earlier pairs) gives on the full year (184 flags, none on Langtang), and Codex's independent recomputation used the frozen file.
"""
    s = s[:i] + sec2 + s[j:k] + sec4
    s = s.replace("Sections marked PRELIMINARY will be replaced when the year-long series is complete.",
                  "Sections 2, 4, 5 and 6 are generated by `pipeline/write_results.py` from the 34-pair data set fetched on 14–15 Nov 2026.")
    f.write_text(s, encoding='utf-8')
    print('written', len(s))


if __name__ == '__main__':
    main()
