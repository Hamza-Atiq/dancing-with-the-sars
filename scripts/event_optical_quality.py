"""Inspect HLS quality flags on the existing radar patch, not the full failure."""
import json
from pathlib import Path
import numpy as np
import requests
from PIL import Image

ROOT = Path("data/event_reconstruction")
BOX = (355250, 355800, 3129780, 3130250)  # Existing patch box, EPSG:32645


def main():
    inventory = json.loads((ROOT / "hls_inventory.json").read_text())
    session = requests.Session()  # Existing Earthdata Login in .netrc, never logged.
    rows = []
    for group in inventory["collections"]:
        for scene in group["scenes"]:
            url = next(x["href"] for x in scene["links"] if x["href"].endswith(".Fmask.tif"))
            path = ROOT / (scene["title"] + ".Fmask.tif")
            if not path.exists():
                response = session.get(url, timeout=90)
                response.raise_for_status()
                path.write_bytes(response.content)
            with Image.open(path) as image:
                keys = image.tag_v2[34735]
                epsg = next(keys[i+3] for i in range(4, len(keys), 4) if keys[i] == 3072)
                assert epsg == 32645, epsg
                sx, sy = image.tag_v2[33550][:2]
                tp = image.tag_v2[33922]
                assert tp[:2] == (0.0, 0.0), tp
                xs = tp[3] + (np.arange(image.width) + 0.5) * sx
                ys = tp[4] - (np.arange(image.height) + 0.5) * sy
                mask = np.asarray(image)[np.ix_((ys >= BOX[2]) & (ys <= BOX[3]),
                                               (xs >= BOX[0]) & (xs <= BOX[1]))]
            assert mask.size > 0
            valid = mask != 255
            clear = valid & ((mask & 14) == 0)
            row = {"title": scene["title"], "time_start": scene["time_start"],
                   "pixels": int(mask.size), "valid_pixels": int(valid.sum()),
                   "cloud_shadow_adjacency_free_pixels": int(clear.sum()),
                   "clear_snow_ice_pixels": int((clear & ((mask & 16) != 0)).sum()),
                   "clear_high_aerosol_pixels": int((clear & ((mask >> 6) == 3)).sum()),
                   "clear_not_high_aerosol_pixels": int((clear & ((mask >> 6) != 3)).sum()),
                   "quality_value_counts": {str(int(v)): int(n) for v, n in
                                            zip(*np.unique(mask, return_counts=True))}}
            rows.append(row)
            print(row["title"], row["cloud_shadow_adjacency_free_pixels"], "/", row["pixels"], "QA-clear pixels", flush=True)
    (ROOT / "patch_quality.json").write_text(json.dumps({
        "box_utm45n": BOX, "scope": "Existing radar patch box, not full collapse or river",
        "rule": "Fmask !=255; bits 1,2,3 unset. Snow retained and separately counted.",
        "caution": "QA-clear does not establish visible fractures, water, or displacement.",
        "scenes": rows}, indent=2))


if __name__ == "__main__":
    main()
