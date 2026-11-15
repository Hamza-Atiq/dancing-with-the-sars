"""Fetch clear-sky HLS (Sentinel-2, 30 m) true-colour windows over Langtang Lirung for the story site.

Picks the clearest scene in an autumn window before the collapse and one after it,
crops to the site window and saves float arrays to data/site/optical_<date>.npz.
Needs Earthdata Login in ~/.netrc.   Run: python scripts/site_optical.py
"""
import io
import os
import sys
import numpy as np
import requests
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pipeline'))
import geo  # noqa: E402

POINT = "85.52701,28.28858"
WINDOWS = {"before": "2025-10-01T00:00:00Z,2025-12-15T00:00:00Z",
           "after": "2026-10-15T00:00:00Z,2026-11-10T00:00:00Z"}
BOX = (346000, 365000, 3121000, 3139000)   # UTM 45N: xmin, xmax, ymin, ymax
OUT = "data/site"


def candidates(temporal):
    s = requests.Session()
    s.trust_env = False
    e = s.get("https://cmr.earthdata.nasa.gov/search/granules.json", params={
        "short_name": "HLSS30", "point": POINT, "temporal": temporal, "page_size": 500}, timeout=120).json()["feed"]["entry"]
    e = [x for x in e if x.get("cloud_cover") not in (None, "")]
    return sorted(e, key=lambda x: (float(x["cloud_cover"]), x["time_start"]))


def band(sess, x, b):
    url = next(l["href"] for l in x["links"] if l["href"].startswith("https") and l["href"].endswith(f".{b}.tif"))
    r = sess.get(url, timeout=600)
    r.raise_for_status()
    im = Image.open(io.BytesIO(r.content))
    a = np.asarray(im).astype(np.float32)
    sx, sy = im.tag_v2[33550][:2]
    tp = im.tag_v2[33922]
    xs = tp[3] + (np.arange(a.shape[1]) + 0.5) * sx
    ys = tp[4] - (np.arange(a.shape[0]) + 0.5) * sy
    return a, xs, ys


def main():
    os.makedirs(OUT, exist_ok=True)
    sess = requests.Session()          # uses ~/.netrc for Earthdata
    for name, temporal in WINDOWS.items():
        c = candidates(temporal)
        for x in c[:4]:
            print(name, "candidate", x["time_start"][:10], x["cloud_cover"], x["title"])
        x = c[0]
        bands = {}
        for b in ("B04", "B03", "B02"):
            a, xs, ys = band(sess, x, b)
            jx = (xs >= BOX[0]) & (xs <= BOX[1])
            iy = (ys >= BOX[2]) & (ys <= BOX[3])
            bands[b] = a[np.ix_(iy, jx)]
            print("  ", b, a.shape, "->", bands[b].shape, flush=True)
        np.savez_compressed(f"{OUT}/optical_{name}.npz", x=xs[jx], y=ys[iy], date=x["time_start"][:10],
                            title=x["title"], cloud=float(x["cloud_cover"]), **bands)
        print("saved", name, x["time_start"][:10])


if __name__ == "__main__":
    main()
