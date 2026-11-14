"""One-off calibration trials: python pipeline/calibrate_try.py old|series key=value [key=value ...]"""
import sys
import copy
import anomaly as an
from calibrate import load, run

mode = sys.argv[1]
p = copy.deepcopy(an.PARAMS)
if mode == 'old':
    p['history_pairs'] = 3
for kv in sys.argv[2:]:
    k, v = kv.split('=')
    p[k] = float(v) if '.' in v else int(v)
print({k: p[k] for k in p if k != 'status'})
rows, res = run(load(mode), p, verbose=False)
for r in rows:
    print(r['pair'], 'hist' if r['has_history'] else 'nohist', 'meas_frac %.2f' % r['window_measurable_frac'],
          'patch meas', r['patch_box_measurable'], 'med|a|', None if r['patch_median_abs_a'] is None else round(r['patch_median_abs_a'], 2),
          '| eligible', r['eligible_px'], 'flags', r['flags'], 'at patch', r['flags_at_patch'], 'rank', r['rank_by_pixels'])
for r, d in zip(rows, res):
    if d['flags']:
        print('  ', r['pair'], sorted([(f['pixels'], round(f['x']), round(f['y']), round(f['mean_abs_rad'], 2)) for f in d['flags']], reverse=True)[:8])
