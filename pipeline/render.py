"""Image overlays for the app: UTM rasters -> lon/lat RGBA images."""
import colorsys
import numpy as np
from PIL import Image
import geo

BOUNDS = (85.33, 28.20, 85.62, 28.37)        # west, south, east, north
SHAPE = (944, 1420)                          # rows, cols (about 20 m)
_HSV = (np.array([colorsys.hsv_to_rgb(i / 256, 1, 1) for i in range(256)]) * 255).astype(np.uint8)


def diverging(z):
    """z in [-1, 1] -> blue-white-red RGB (uint8)."""
    z = np.clip(np.nan_to_num(z), -1, 1)
    r = 255 * (1 + np.minimum(z, 0) * 0.85)
    g = 255 * (1 - np.abs(z) * 0.85)
    b = 255 * (1 - np.maximum(z, 0) * 0.85)
    return np.stack([r, g, b], -1).astype(np.uint8)


def to_lonlat(a, x, y, epsg, fill):
    return geo.reproject(a, x, y, epsg, BOUNDS, SHAPE, fill=fill)


def save(rgba, path, quality):
    """quality None = lossless WebP; otherwise lossy WebP at that quality (alpha kept)."""
    im = Image.fromarray(rgba, 'RGBA')
    if quality is None:
        im.save(path, 'WEBP', lossless=True, method=4)
    else:
        im.save(path, 'WEBP', quality=quality, alpha_quality=90, method=4)
    return path.stat().st_size


def anomaly_image(a, measurable, x, y, epsg, path):
    z = to_lonlat(np.where(measurable, a, np.nan), x, y, epsg, np.nan)
    rgb = diverging(z / np.pi)
    # near-zero anomaly is drawn faintly so the basemap stays readable; strong anomaly is opaque
    alpha = np.where(np.isfinite(z), 80 + 160 * np.clip(np.abs(np.nan_to_num(z)) / 1.0, 0, 1), 0).astype(np.uint8)
    # the anomaly is a 100 m average, so a 40 m image loses nothing visible and is a quarter of the size
    return save(np.dstack([rgb, alpha])[::2, ::2], path, 82)


def phase_image(wrapped, coh, valid, x, y, epsg, path):
    ph = to_lonlat(np.where(valid, np.angle(wrapped), np.nan), x, y, epsg, np.nan)
    c = to_lonlat(np.where(valid, coh, 0.0).astype(float), x, y, epsg, np.nan)
    ok = np.isfinite(ph)
    idx = ((np.nan_to_num(ph) + np.pi) / (2 * np.pi) * 255).astype(int) % 256
    rgb = (_HSV[idx] * np.clip(np.nan_to_num(c) / 0.5, 0.2, 1)[..., None]).astype(np.uint8)
    return save(np.dstack([rgb, np.where(ok, 255, 0).astype(np.uint8)]), path, 50)


def coherence_image(coh, valid, x, y, epsg, path):
    c = to_lonlat(np.where(valid, coh, np.nan).astype(float), x, y, epsg, np.nan)
    g = (np.clip(np.nan_to_num(c), 0, 1) * 255).astype(np.uint8)
    return save(np.dstack([g, g, g, np.where(np.isfinite(c), 255, 0).astype(np.uint8)])[::2, ::2], path, 50)


def flag_image(labels, x, y, epsg, path):
    m = to_lonlat((labels > 0), x, y, epsg, np.nan)
    rgba = np.zeros(SHAPE + (4,), np.uint8)
    rgba[m] = (255, 0, 200, 255)
    return save(rgba, path, None)


def change_image(db, x, y, epsg, path, limit=6.0):
    z = to_lonlat(db, x, y, epsg, np.nan)
    rgb = diverging(z / limit)
    return save(np.dstack([rgb, np.where(np.isfinite(z), 235, 0).astype(np.uint8)]), path, 80)
