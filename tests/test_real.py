"""Checks on the real extracts. Skipped when data/ is absent (it is not in git)."""
import sys
from pathlib import Path
import numpy as np
import pytest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline')]
import anomaly as an
import detect as dt
import series

NEED = ['20260620_20260702', '20260702_20260714', '20260714_20260726']
have = all((ROOT / f'data/series/098_A_016_{n}.npz').exists() or (ROOT / f'data/lang/GUNW_098_A_016_{n}.npz').exists() for n in NEED)
pytestmark = pytest.mark.skipif(not have, reason='real extracts not present')


@pytest.fixture(scope='module')
def pairs():
    return series.load_all()


def test_patch_numbers_match_verification_record(pairs):
    ts = {r['pair']: r for r in series.time_series(pairs)['rows']}
    before, key, last = ts['20260702_20260714'], ts['20260714_20260726'], ts['20260726_20260819']
    assert before['resolved'] and key['resolved'] and not last['resolved']
    assert abs(before['refs']['west block']['los_cm'] - 0.6) < 0.2
    assert abs(abs(key['refs']['west block']['los_cm']) - 5.6) < 0.2
    for name, v in key['refs'].items():                       # every reference sees the step
        assert 4.5 < abs(v['los_cm']) < 5.8, name


def test_patch_region_anomalous_in_key_pair_and_quiet_before(pairs):
    p = pairs['20260714_20260726']
    X, Y = np.meshgrid(p['x'], p['y'])
    b = series.box(X, Y, series.PATCH)
    r = an.anomaly(p['wrapped'], p['coh'], p['mask'])
    m = b & r['measurable']
    assert m.sum() > 100 and (np.abs(r['a'][m]) > 1.5).mean() > 0.8
    q = pairs['20260702_20260714']
    r0 = an.anomaly(q['wrapped'], q['coh'], q['mask'])
    m0 = b & r0['measurable']
    assert m0.sum() > 50 and np.median(np.abs(r0['a'][m0])) < 0.4


def test_frozen_rule_flags_langtang_in_key_pair_only(pairs):
    names = [n for n in pairs if '20260527' <= n[:8] <= '20260726']
    if len(names) < 6:
        pytest.skip('need the pairs from 27 May for a four-pair history')
    x, y = pairs[names[0]]['x'], pairs[names[0]]['y']
    R = [an.anomaly(pairs[n]['wrapped'], pairs[n]['coh'], pairs[n]['mask']) for n in names]
    res = dt.detect([r['a'] for r in R], [r['measurable'] for r in R], x, y)
    b = series.PATCH
    near = lambda f: b[0] - 300 <= f['x'] <= b[1] + 300 and b[2] - 300 <= f['y'] <= b[3] + 300
    by = dict(zip(names, res))
    assert sum(near(f) for f in by['20260714_20260726']['flags']) >= 1
    assert sum(near(f) for f in by['20260702_20260714']['flags']) == 0
    assert sum(near(f) for f in by['20260726_20260819']['flags']) == 0


def test_invalid_mask_pixels_excluded(pairs):
    p = next(q for q in pairs.values() if q['mask'] is not None)
    bad = ~an.mask_valid_land(p['mask'])
    if not bad.any():
        pytest.skip('no invalid mask pixels in this crop')
    assert not an.valid_pixels(p['wrapped'], p['coh'], p['mask'])[bad].any()
