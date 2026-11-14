import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline')]
import anomaly as an
import detect as dt

N = 200
X = np.arange(N) * 20.0
Y = (N - np.arange(N)) * 20.0


def synth(step=0.0, patch=None, coh=0.8, noise=0.25, seed=0, lowcoh=None):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[:N, :N]
    ph = 0.004 * xx + 0.002 * yy + 1.0 + rng.normal(0, noise, (N, N))      # ramp + noise
    c = np.full((N, N), coh)
    if patch is not None:
        ph[patch] += step
    if lowcoh is not None:
        ph[lowcoh] = rng.uniform(-np.pi, np.pi, int(lowcoh.sum()))
        c[lowcoh] = 0.1
    return np.exp(1j * ph).astype(np.complex64) * 3.0, c


def patch_mask(r0=85, c0=85, n=30):
    m = np.zeros((N, N), bool)
    m[r0:r0 + n, c0:c0 + n] = True
    return m


def test_flat_scene_has_no_anomaly():
    w, c = synth()
    r = an.anomaly(w, c)
    inner = np.zeros((N, N), bool)
    inner[40:-40, 40:-40] = True
    assert r['measurable'][inner].mean() > 0.99
    assert np.nanmax(np.abs(r['a'][inner])) < 0.3


def test_patch_step_recovered_and_sign_kept():
    pm = patch_mask()
    core = patch_mask(92, 92, 16)
    for step in (2.5, -2.5):
        w, c = synth(step, pm)
        r = an.anomaly(w, c)
        assert abs(np.nanmedian(r['a'][core]) - step) < 0.3


def test_step_near_pi_gives_large_abs_everywhere():
    w, c = synth(np.pi, patch_mask())
    r = an.anomaly(w, c)
    core = patch_mask(92, 92, 16)
    assert np.nanmin(np.abs(r['a'][core])) > 2.4          # +pi/-pi flips do not reduce |a|


def test_low_coherence_and_invalid_not_measurable():
    w, c = synth(lowcoh=patch_mask(20, 20, 40))
    r = an.anomaly(w, c)
    assert r['measurable'][28:52, 28:52].mean() < 0.02
    w, c = synth()
    mask = np.full((N, N), 11, np.uint32)
    mask[100:140, 100:140] = 111                         # water
    r = an.anomaly(w, c, mask)
    assert not r['valid'][100:140, 100:140].any() and not r['measurable'][108:132, 108:132].any()
    w[60:70, 60:70] = np.nan
    assert not an.anomaly(w, c)['valid'][60:70, 60:70].any()


def test_mask_decoder():
    v = np.array([0, 1, 10, 11, 12, 55, 111, 255, 267, 65547, 16777227], np.uint32)
    assert an.mask_valid_land(v).tolist() == [False, False, False, True, True, True, False, False, False, False, True]


def _stack(steps_by_pair, patch, lowcoh_pairs=()):
    A, M = [], []
    for k, s in enumerate(steps_by_pair):
        w, c = synth(s, patch, seed=k, lowcoh=patch if k in lowcoh_pairs else None)
        r = an.anomaly(w, c)
        A.append(r['a'])
        M.append(r['measurable'])
    return A, M


def test_new_patch_flagged_once_after_quiet_history():
    A, M = _stack([0, 0, 0, 0, 2.5], patch_mask())
    res = dt.detect(A, M, X, Y)
    assert [len(r['flags']) for r in res] == [0, 0, 0, 0, 1]
    f = res[4]['flags'][0]
    assert abs(f['x'] - X[99:101].mean()) < 60 and abs(f['y'] - Y[99:101].mean()) < 60 and f['pixels'] > 300


def test_persistent_glacier_like_patch_never_flagged():
    A, M = _stack([2.5] * 6, patch_mask())
    assert sum(len(r['flags']) for r in dt.detect(A, M, X, Y)) == 0


def test_no_measurable_history_not_flagged():
    A, M = _stack([0, 0, 0, 0, 2.5], patch_mask(), lowcoh_pairs=(0, 1, 2, 3))
    res = dt.detect(A, M, X, Y)
    assert not (res[4]['labels'][patch_mask(92, 92, 16)] > 0).any()


def test_small_blob_not_flagged():
    A, M = _stack([0, 0, 0, 0, 2.5], patch_mask(95, 95, 5))
    assert sum(len(r['flags']) for r in dt.detect(A, M, X, Y)) == 0


def test_second_moving_pair_not_reflagged():
    A, M = _stack([0, 0, 0, 0, 2.5, 2.5], patch_mask())
    res = dt.detect(A, M, X, Y)
    assert len(res[4]['flags']) == 1 and len(res[5]['flags']) == 0
