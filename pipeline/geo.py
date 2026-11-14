"""Coordinate transforms and reprojection without pyproj (WGS84 UTM only)."""
import numpy as np

A = 6378137.0
F = 1 / 298.257223563
K0 = 0.9996
E2 = F * (2 - F)
EP2 = E2 / (1 - E2)


def _zone(epsg):
    if 32600 < epsg < 32661:
        return epsg - 32600, 0.0
    if 32700 < epsg < 32761:
        return epsg - 32700, 10_000_000.0
    raise ValueError(f'not a WGS84 UTM code: {epsg}')


def _lon0(zone):
    return np.radians((zone - 1) * 6 - 180 + 3)


def ll2xy(lon, lat, epsg):
    """Vectorised forward UTM. lon/lat in degrees."""
    zone, fn = _zone(int(epsg))
    la = np.radians(np.asarray(lat, float)); lo = np.radians(np.asarray(lon, float))
    N = A / np.sqrt(1 - E2 * np.sin(la) ** 2)
    T = np.tan(la) ** 2
    C = EP2 * np.cos(la) ** 2
    a = np.cos(la) * (lo - _lon0(zone))
    M = A * ((1 - E2 / 4 - 3 * E2 ** 2 / 64 - 5 * E2 ** 3 / 256) * la
             - (3 * E2 / 8 + 3 * E2 ** 2 / 32 + 45 * E2 ** 3 / 1024) * np.sin(2 * la)
             + (15 * E2 ** 2 / 256 + 45 * E2 ** 3 / 1024) * np.sin(4 * la)
             - (35 * E2 ** 3 / 3072) * np.sin(6 * la))
    x = K0 * N * (a + (1 - T + C) * a ** 3 / 6 + (5 - 18 * T + T * T + 72 * C - 58 * EP2) * a ** 5 / 120) + 500000
    y = K0 * (M + N * np.tan(la) * (a * a / 2 + (5 - T + 9 * C + 4 * C * C) * a ** 4 / 24
                                    + (61 - 58 * T + T * T + 600 * C - 330 * EP2) * a ** 6 / 720)) + fn
    return x, y


def xy2ll(x, y, epsg):
    """Inverse UTM by Newton iteration on the forward transform (sub-mm)."""
    zone, fn = _zone(int(epsg))
    x = np.asarray(x, float); y = np.asarray(y, float)
    lat = (y - fn) / K0 / A * 180 / np.pi
    lon = np.degrees(_lon0(zone)) + (x - 500000) / (K0 * A * np.cos(np.radians(lat))) * 180 / np.pi
    for _ in range(8):
        fx, fy = ll2xy(lon, lat, epsg)
        lat = lat + (y - fy) / (K0 * A) * 180 / np.pi * 0.999
        lon = lon + (x - fx) / (K0 * A * np.cos(np.radians(lat))) * 180 / np.pi * 0.999
    return lon, lat


def reproject(a, x, y, epsg, bounds, shape, fill=np.nan):
    """Nearest-neighbour resample of a[y, x] (UTM, regular grid) onto a regular
    lon/lat grid. bounds=(west, south, east, north); shape=(rows, cols); row 0 is north.
    Pixel centres are used on both grids."""
    w, s, e, n = bounds
    rows, cols = shape
    lon = w + (np.arange(cols) + 0.5) * (e - w) / cols
    lat = n - (np.arange(rows) + 0.5) * (n - s) / rows
    LON, LAT = np.meshgrid(lon, lat)
    X, Y = ll2xy(LON, LAT, epsg)
    dx = x[1] - x[0]; dy = y[1] - y[0]
    ix = np.rint((X - x[0]) / dx).astype(int)
    iy = np.rint((Y - y[0]) / dy).astype(int)
    ok = (ix >= 0) & (ix < len(x)) & (iy >= 0) & (iy < len(y))
    out = np.full(shape + a.shape[2:], fill, dtype=a.dtype if not np.isnan(fill) else float) if a.dtype.kind != 'b' \
        else np.zeros(shape, bool)
    out[ok] = a[iy[ok], ix[ok]]
    return out


def inside(x, y, vertices):
    """Boolean mask of grid-cell centres inside a closed polygon (even-odd rule).
    Only the polygon's bounding box is evaluated."""
    v = np.asarray(vertices, float)
    res = np.zeros((len(y), len(x)), bool)
    ix = np.flatnonzero((x >= v[:, 0].min()) & (x <= v[:, 0].max()))
    iy = np.flatnonzero((y >= v[:, 1].min()) & (y <= v[:, 1].max()))
    if not ix.size or not iy.size:
        return res
    X, Y = np.meshgrid(x[ix], y[iy])
    sub = np.zeros(X.shape, bool)
    for (x1, y1), (x2, y2) in zip(v[:-1], v[1:]):
        if y1 != y2:
            sub ^= ((y1 > Y) != (y2 > Y)) & (X < (x2 - x1) * (Y - y1) / (y2 - y1) + x1)
    res[np.ix_(iy, ix)] = sub
    return res
