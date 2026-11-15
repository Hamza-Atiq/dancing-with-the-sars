"""Record public NASA HLS metadata around the flood; no image usability claims."""
import concurrent.futures
import datetime
import json
from pathlib import Path
import requests

POINT = "85.52701,28.28858"
WINDOW = "2026-08-20T00:00:00Z,2026-09-02T23:59:59Z"


def query(name):
    session = requests.Session()
    session.trust_env = False  # Public metadata; do not send Earthdata credentials.
    params = dict(short_name=name, point=POINT, temporal=WINDOW,
                  page_size=200, sort_key="start_date")
    response = session.get("https://cmr.earthdata.nasa.gov/search/granules.json",
                           params=params, timeout=60)
    response.raise_for_status()
    entries = response.json()["feed"]["entry"]
    if len(entries) >= 200:
        raise RuntimeError("Pagination required; refusing an incomplete inventory")
    return {"collection": name, "query_url": response.url, "scenes": [
        {"id": e["id"], "title": e["title"], "time_start": e["time_start"],
         "tile_cloud_percent": e.get("cloud_cover"),
         "links": [{"href": link["href"], "rel": link.get("rel")}
                   for link in e.get("links", []) if link.get("href", "").startswith("https://")]}
        for e in entries]}


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(query, ["HLSL30", "HLSS30"]))
    output = {"queried_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "point_lon_lat": POINT, "window": WINDOW,
              "warning": "Catalog presence and tile cloud cover do not establish local visibility.",
              "collections": results}
    path = Path("data/event_reconstruction/hls_inventory.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    for result in results:
        for scene in result["scenes"]:
            print(scene["title"], scene["time_start"], "tile cloud", scene["tile_cloud_percent"])
    print("Saved", path)
