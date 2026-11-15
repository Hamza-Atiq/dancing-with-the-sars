"""Survey public SAR archives at the published Langtang source coordinates.

Queries NASA CMR (all collections with granules at the point) and the ASF
search API (Sentinel-1, NISAR, ARIA, OPERA). No login needed; nothing is downloaded.
Output: data/archive_survey.json and a printed summary.

Run: C:/Users/HP/anaconda3/python.exe scripts/archive_survey.py
"""
import json
import os
import sys
import collections
import requests

# Published source coordinates (lon, lat). See "Langtang data hunt - Claude.md".
POINTS = {
    "Li2026_centroid": (85.52701, 28.28858),
    "HiRISK": (85.528159, 28.288708),
    "Davies_recon": (85.5252, 28.2853),
    "old_session_point": (85.52, 28.25),
}
MAIN = POINTS["Li2026_centroid"]
START, END = "2026-05-01T00:00:00Z", "2026-11-16T00:00:00Z"
CMR = "https://cmr.earthdata.nasa.gov/search"
ASF = "https://api.daac.asf.alaska.edu/services/search/param"
S = requests.Session()
S.trust_env = False  # do not send .netrc credentials; these endpoints are public
S.headers["User-Agent"] = "archive-survey-script"


def cmr_collections(lon, lat):
    out, page = [], 1
    while True:
        r = S.get(CMR + "/collections.json", params={
            "point": f"{lon},{lat}", "temporal": f"{START},{END}",
            "has_granules": "true", "page_size": 2000, "page_num": page,
        }, timeout=120)
        r.raise_for_status()
        e = r.json()["feed"]["entry"]
        out += e
        if len(e) < 2000:
            return out
        page += 1


def cmr_granules(concept_id, lon, lat):
    out, page = [], 1
    while True:
        r = S.get(CMR + "/granules.json", params={
            "collection_concept_id": concept_id, "point": f"{lon},{lat}",
            "temporal": f"{START},{END}", "page_size": 2000, "page_num": page,
            "sort_key": "start_date",
        }, timeout=120)
        r.raise_for_status()
        e = r.json()["feed"]["entry"]
        out += e
        if len(e) < 2000:
            return out
        page += 1


def asf(params):
    p = {"intersectsWith": f"POINT({MAIN[0]} {MAIN[1]})", "start": START, "end": END,
         "output": "jsonlite", "maxResults": 5000}
    p.update(params)
    r = S.get(ASF, params=p, timeout=180)
    r.raise_for_status()
    return r.json().get("results", [])


def main():
    res = {"points": POINTS, "window": [START, END]}
    kw = ("SAR", "NISAR", "SENTINEL-1", "OPERA", "ALOS", "RADARSAT", "UAVSAR", "ARIA",
          "INSAR", "RTC", "DISP", "DIST", "ITS_LIVE", "HLS", "LANDSAT", "ICESAT", "GEDI",
          "ECOSTRESS", "ASTER", "SWOT", "EMIT", "VELOCITY")
    cols = cmr_collections(*MAIN)
    print("CMR collections with granules at point, in window:", len(cols))
    keep = []
    for c in cols:
        text = (c.get("short_name", "") + " " + c.get("title", "") + " " +
                " ".join(c.get("platforms", []) if isinstance(c.get("platforms"), list) else [])).upper()
        if any(k in text for k in kw):
            keep.append(c)
    res["cmr"] = []
    for c in sorted(keep, key=lambda c: c.get("short_name", "")):
        try:
            g = cmr_granules(c["id"], *MAIN)
        except Exception as ex:  # noqa
            print("  fail", c.get("short_name"), ex)
            continue
        if not g:
            continue
        dates = sorted(x["time_start"][:10] for x in g if x.get("time_start"))
        row = {"short_name": c.get("short_name"), "version": c.get("version_id"),
               "id": c["id"], "provider": c.get("data_center"), "n": len(g),
               "first": dates[0] if dates else None, "last": dates[-1] if dates else None,
               "dates": sorted(set(dates))}
        res["cmr"].append(row)
        print(f"  {row['short_name']:<40} v{row['version']:<6} n={row['n']:<5} {row['first']} -> {row['last']}")

    print("\nASF Sentinel-1 SLC at point:")
    s1 = asf({"dataset": "SENTINEL-1", "processingLevel": "SLC"})
    by = collections.defaultdict(list)
    for x in s1:
        by[(x.get("platform"), x.get("flightDirection"), x.get("track"), x.get("frame"))].append(x["startTime"][:16])
    res["s1_slc"] = {"|".join(map(str, k)): sorted(v) for k, v in by.items()}
    for k, v in sorted(by.items(), key=lambda kv: str(kv[0])):
        print("  ", k, len(v), sorted(v)[0], "->", sorted(v)[-1])

    print("\nASF Sentinel-1 bursts at point:")
    try:
        b = asf({"dataset": "SLC-BURST", "polarization": "VV"})
        byb = collections.defaultdict(list)
        for x in b:
            bid = (x.get("burst") or {}).get("fullBurstID") or x.get("fullBurstID")
            byb[(x.get("flightDirection"), x.get("track"), bid)].append(x["startTime"][:10])
        res["s1_burst"] = {"|".join(map(str, k)): sorted(v) for k, v in byb.items()}
        for k, v in sorted(byb.items(), key=lambda kv: str(kv[0])):
            print("  ", k, len(v), sorted(v)[0], "->", sorted(v)[-1])
    except Exception as ex:  # noqa
        print("  burst query failed:", ex)

    for ds in ("NISAR", "ARIA S1 GUNW", "OPERA-S1", "ALOS-2", "ALOS PALSAR"):
        try:
            r = asf({"dataset": ds})
        except Exception as ex:  # noqa
            print(f"\nASF {ds}: query failed: {ex}")
            continue
        by = collections.defaultdict(list)
        for x in r:
            by[(x.get("processingLevel"), x.get("flightDirection"), x.get("track"), x.get("frame"))].append((x.get("startTime") or "unknown")[:10])
        res["asf_" + ds] = {"|".join(map(str, k)): sorted(set(v)) for k, v in by.items()}
        print(f"\nASF {ds}: {len(r)} results")
        for k, v in sorted(by.items(), key=lambda kv: str(kv[0])):
            print("  ", k, len(v), min(v), "->", max(v))

    os.makedirs("data", exist_ok=True)
    with open("data/archive_survey.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print("\nwrote data/archive_survey.json")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
