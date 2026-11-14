import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline'), str(ROOT / 'scripts')]
import geo, utm


def test_forward_matches_scalar_reference():
    rng = np.random.default_rng(0)
    lon = rng.uniform(85.2, 85.8, 50); lat = rng.uniform(28.0, 28.5, 50)
    x, y = geo.ll2xy(lon, lat, 32645)
    ref = np.array([utm.ll2xy(a, b, 32645) for a, b in zip(lon, lat)])
    assert np.max(np.abs(x - ref[:, 0])) < 1e-3 and np.max(np.abs(y - ref[:, 1])) < 1e-3


def test_round_trip():
    x = np.array([336000., 355500., 364800.]); y = np.array([3120000., 3130000., 3139300.])
    lon, lat = geo.xy2ll(x, y, 32645)
    x2, y2 = geo.ll2xy(lon, lat, 32645)
    assert np.max(np.abs(x - x2)) < 1e-3 and np.max(np.abs(y - y2)) < 1e-3


def test_gdal_polygon_agreement():
    src = ROOT / 'data/lang_sources'
    if not (src / 'detachment.geojson').exists():
        import pytest; pytest.skip('source polygon not present')
    ll = np.array(json.loads((src / 'detachment.geojson').read_text())['features'][0]['geometry']['coordinates'][0][0])
    xy = np.array(json.loads((src / 'detachment_utm.geojson').read_text())['features'][0]['geometry']['coordinates'][0][0])
    x, y = geo.ll2xy(ll[:, 0], ll[:, 1], 32645)
    assert np.max(np.hypot(x - xy[:, 0], y - xy[:, 1])) < 0.01
    lon, lat = geo.xy2ll(xy[:, 0], xy[:, 1], 32645)
    assert np.max(np.abs(lon - ll[:, 0])) < 1e-7 and np.max(np.abs(lat - ll[:, 1])) < 1e-7


def test_reproject_places_known_pixel():
    x = np.arange(350000., 360000., 20.); y = np.arange(3135000., 3125000., -20.)
    a = np.zeros((len(y), len(x))); a[250, 275] = 7.0      # x=355500, y=3130000
    lon, lat = geo.xy2ll(355500., 3130000., 32645)
    b = (85.47, 28.24, 85.57, 28.33); shape = (900, 1000)   # ~10 m cells
    out = geo.reproject(a, x, y, 32645, b, shape)
    r, c = np.argwhere(out == 7.0).mean(axis=0)
    assert abs(c - (lon - b[0]) / (b[2] - b[0]) * shape[1]) < 2.5
    assert abs(r - (b[3] - lat) / (b[3] - b[1]) * shape[0]) < 2.5


def test_inside_square():
    x = np.arange(0., 10.); y = np.arange(9., -1., -1.)
    m = geo.inside(x, y, [(2.5, 2.5), (6.5, 2.5), (6.5, 6.5), (2.5, 6.5), (2.5, 2.5)])
    assert m.sum() == 16 and m[9 - 3, 3] and not m[9 - 2, 2]
