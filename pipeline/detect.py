"""New-movement detector on a time-ordered stack of anomaly maps (spec 4.2)."""
import numpy as np
from scipy.ndimage import label, center_of_mass
from anomaly import PARAMS


def flag_pixels(A, M, k, params=PARAMS):
    """A, M: lists of anomaly (rad) and measurable arrays in acquisition order.
    Returns (flagged, eligible) boolean arrays for pair k."""
    h = params['history_pairs']
    if k < h:
        z = np.zeros(A[k].shape, bool)
        return z, z
    n_meas = np.zeros(A[k].shape, int)
    loud = np.zeros(A[k].shape, bool)
    for j in range(k - h, k):
        n_meas += M[j]
        loud |= M[j] & (np.abs(np.nan_to_num(A[j])) >= params['quiet_abs_anomaly_rad'])
    eligible = (n_meas >= params['min_history_measurable']) & ~loud & M[k]
    flagged = eligible & (np.abs(np.nan_to_num(A[k])) >= params['flag_abs_anomaly_rad'])
    return flagged, eligible


def blobs(flagged, absa, x, y, params=PARAMS):
    """4-connected groups of flagged pixels of at least min_blob_pixels."""
    lab, n = label(flagged)
    out = []
    if n == 0:
        return out, lab
    sizes = np.bincount(lab.ravel())
    cell = abs(x[1] - x[0]) * abs(y[1] - y[0])
    small = np.flatnonzero(sizes < params['min_blob_pixels'])
    lab[np.isin(lab, small)] = 0
    for i in range(1, n + 1):
        if sizes[i] < params['min_blob_pixels']:
            continue
        m = lab == i
        r, c = center_of_mass(m)
        out.append({'label': int(i), 'pixels': int(sizes[i]), 'area_km2': float(sizes[i] * cell / 1e6),
                    'x': float(np.interp(c, np.arange(len(x)), x)), 'y': float(np.interp(r, np.arange(len(y)), y)),
                    'mean_abs_rad': float(absa[m].mean()), 'max_abs_rad': float(absa[m].max())})
    return out, lab


def detect(A, M, x, y, params=PARAMS):
    """Runs every pair. Returns a list (per pair) of dicts:
    flags, eligible_pixels, measurable_pixels, has_history, labels."""
    res = []
    prev = None
    for k in range(len(A)):
        fl, el = flag_pixels(A, M, k, params)
        bl, lab = blobs(fl, np.abs(np.nan_to_num(A[k])), x, y, params)
        for b in bl:
            b['continuing'] = bool(prev is not None and (prev[lab == b['label']] > 0).any())
        res.append({'flags': bl, 'eligible_pixels': int(el.sum()), 'measurable_pixels': int(M[k].sum()),
                    'has_history': k >= params['history_pairs'], 'labels': lab})
        prev = lab
    return res
