"""Reproducible first checks of the extracted Langtang windows."""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'lang'
OUT = ROOT / 'data' / 'lang_check'
OUT.mkdir(exist_ok=True)
report = {'files': {}, 'comparisons': {}, 'coherence': {}}
for path in sorted(DATA.glob('*.npz')):
    with np.load(path) as data:
        report['files'][path.name] = {
            'epsg': int(data['epsg']),
            'shape': [len(data['y']), len(data['x'])],
            'keys': list(data.files),
        }
        if path.name.startswith('GUNW'):
            coherence = data['coherenceMagnitude']
            valid = np.isfinite(coherence) & (coherence >= 0) & (coherence <= 1)
            report['coherence'][path.name] = {
                'finite_fraction': float(valid.mean()),
                'median': float(np.median(coherence[valid])),
                'fraction_ge_0_6': float(np.mean(valid & (coherence >= 0.6))),
            }
for label, before, after in [('quiet', '20260714', '20260726'), ('event', '20260819', '20260831')]:
    with np.load(DATA / f'098_A_016_{before}.npz') as first, np.load(DATA / f'098_A_016_{after}.npz') as last:
        for key in ('x', 'y', 'epsg'):
            if not np.array_equal(first[key], last[key]):
                raise ValueError(f'{label}: different {key} grids')
        layers = {'x': first['x'], 'y': first['y'], 'epsg': first['epsg']}
        report['comparisons'][label] = {}
        for channel in ('HHHH', 'HVHV'):
            a, b = first[channel], last[channel]
            valid = np.isfinite(a) & np.isfinite(b) & (a > 0) & (b > 0)
            change = np.full(a.shape, np.nan, dtype=np.float32)
            change[valid] = 10 * (np.log10(b[valid]) - np.log10(a[valid]))
            layers[channel + '_change_db'] = change
            report['comparisons'][label][channel] = {
                'valid_fraction': float(valid.mean()),
                'percentiles_5_50_95_db': np.percentile(change[valid], [5, 50, 95]).tolist(),
                'fraction_abs_gt_3db_of_valid': float(np.mean(np.abs(change[valid]) > 3)),
            }
        np.savez_compressed(OUT / f'{label}_change.npz', **layers)
(OUT / 'checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))
