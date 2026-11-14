"""Local phase anomaly of a 20 m wrapped interferogram (spec 4.1)."""
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import uniform_filter

ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((Path(__file__).parent / 'params.json').read_text())
WAVELENGTH_CM = 299792458 / 1.239e9 * 100
RAD_TO_CM = WAVELENGTH_CM / (4 * np.pi)


def mask_valid_land(mask):
    """GUNW mask: low byte = water*100 + reference subswath*10 + secondary subswath;
    bits 8-23 are anomaly flags. Valid = both subswaths 1-5, no water, no anomaly bits."""
    m = np.asarray(mask, dtype=np.uint32)
    low = m & 255
    ref = (low // 10) % 10
    sec = low % 10
    return ((low != 255) & (ref >= 1) & (ref <= 5) & (sec >= 1) & (sec <= 5)
            & (low // 100 == 0) & (((m >> 8) & 65535) == 0))


def valid_pixels(wrapped, coh, mask=None):
    v = np.isfinite(wrapped) & (np.abs(wrapped) > 0) & np.isfinite(coh) & (coh > 0) & (coh <= 1)
    if mask is not None:
        v &= mask_valid_land(mask)
    return v


def _boxsum(a, n):
    return uniform_filter(a, n, mode='constant', cval=0.0) * (n * n)


def _cboxsum(a, n):
    return _boxsum(a.real, n) + 1j * _boxsum(a.imag, n)


def anomaly(wrapped, coh, mask=None, params=PARAMS):
    """Returns dict: a (rad, nan where undefined), consistency, local_coherence,
    background_strength, measurable (bool), valid (bool)."""
    p = params
    v = valid_pixels(wrapped, coh, mask)
    c = np.where(v, coh, 0.0).astype(float)
    ph = np.zeros(wrapped.shape, complex)
    ph[v] = wrapped[v] / np.abs(wrapped[v])
    cp = c * ph
    nl, nb = p['local_box'], p['background_box']
    S5, C5, N5 = _cboxsum(cp, nl), _boxsum(c, nl), _boxsum(v.astype(float), nl)
    Sb, Cb, Nb = _cboxsum(cp, nb) - S5, _boxsum(c, nb) - C5, _boxsum(v.astype(float), nb) - N5
    with np.errstate(all='ignore'):
        s = S5 / C5
        b = Sb / Cb
        lcoh = C5 / N5
    enough = (N5 >= p['min_local_valid'] - 1e-6) & (Nb >= p['min_background_valid_fraction'] * (nb * nb - nl * nl))
    with np.errstate(all='ignore'):
        a = np.angle(s * np.conj(b))
        cons = np.abs(s)
        bg = np.abs(b)
    a[~enough | ~np.isfinite(a)] = np.nan
    meas = (enough & np.isfinite(a) & (cons >= p['min_consistency'])
            & (lcoh >= p['min_local_coherence']) & (bg >= p['min_background_strength']))
    return {'a': a, 'consistency': np.nan_to_num(cons), 'local_coherence': np.nan_to_num(lcoh),
            'background_strength': np.nan_to_num(bg), 'measurable': meas, 'valid': v}


def load_series_pair(path):
    d = np.load(path)
    return {'x': d['x'], 'y': d['y'], 'epsg': int(d['epsg']), 'wrapped': d['wrapped'], 'coh': d['wcoh'],
            'mask': d['mask'] if 'mask' in d.files else None}


def load_old_pair(path):
    """Old extracts in data/lang (no wrapped-grid mask stored)."""
    d = np.load(path)
    return {'x': d['xw'], 'y': d['yw'], 'epsg': int(d['epsg']), 'wrapped': d['wrapped'], 'coh': d['wcoh'],
            'mask': None}
