"""Sentinel-1 burst interferograms over the Langtang source through ASF HyP3 (on demand).

Uses the Earthdata Login in ~/.netrc (never printed). Burst list comes from
data/s1_bursts_at_source.json (written by the survey step).

  python scripts/s1_hyp3.py user       # account and remaining credits
  python scripts/s1_hyp3.py plan       # list the pairs that would be submitted
  python scripts/s1_hyp3.py submit     # submit them (20 m, wrapped phase kept)
  python scripts/s1_hyp3.py status     # job states
  python scripts/s1_hyp3.py download   # fetch finished zips into data/s1/
"""
import json
import netrc
import os
import sys
import requests

API = "https://hyp3-api.asf.alaska.edu"
AUTH = ("https://urs.earthdata.nasa.gov/oauth/authorize?response_type=code"
        "&client_id=BO_n7nTIlMljdvU6kRRB3g&redirect_uri=https://auth.asf.alaska.edu/login&app_type=401")
PROJECT = "langtang-s1"
START, END = "2026-06-01", "2026-09-10"
MAX_GAP_DAYS = 12
OUT = "data/s1"


def session():
    s = requests.Session()
    s.trust_env = False
    login, _, password = netrc.netrc(os.path.expanduser("~/.netrc")).authenticators("urs.earthdata.nasa.gov")
    r = s.get(AUTH, auth=(login, password), timeout=120)
    r.raise_for_status()
    if "asf-urs" not in s.cookies.get_dict():
        raise SystemExit("login did not return an ASF session cookie")
    return s


def pairs():
    from datetime import date
    b = json.load(open("data/s1_bursts_at_source.json"))
    out = []
    for key, rows in b.items():
        rows = [r for r in rows if START <= r[0] <= END]
        for a, c in zip(rows, rows[1:]):
            gap = (date.fromisoformat(c[0]) - date.fromisoformat(a[0])).days
            if gap <= MAX_GAP_DAYS:
                out.append({"burst": key.split("|")[1], "ref": a[0], "sec": c[0], "days": gap,
                            "granules": [a[2], c[2]]})
    return out


def all_jobs(s):
    jobs, url, params = [], API + "/jobs", {"name": PROJECT}
    while url:
        r = s.get(url, params=params, timeout=120)
        r.raise_for_status()
        j = r.json()
        jobs += j["jobs"]
        url, params = j.get("next"), None
    return jobs


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        for p in pairs():
            print(p["burst"], p["ref"], "->", p["sec"], f"{p['days']} d")
        print(len(pairs()), "pairs")
        return
    s = session()
    if cmd == "user":
        u = s.get(API + "/user", timeout=120).json()
        print({k: v for k, v in u.items() if k in ("remaining_credits", "application_status", "job_names")})
    elif cmd == "submit":
        done = {tuple(j["job_parameters"]["granules"]) for j in all_jobs(s)}
        body = {"jobs": [{"name": PROJECT, "job_type": "INSAR_ISCE_BURST",
                          "job_parameters": {"granules": p["granules"], "looks": "5x1",
                                             "apply_water_mask": False}}
                         for p in pairs() if tuple(p["granules"]) not in done]}
        if not body["jobs"]:
            print("nothing new to submit")
            return
        r = s.post(API + "/jobs", json=body, timeout=300)
        print(r.status_code, r.text[:600])
    elif cmd == "status":
        for j in sorted(all_jobs(s), key=lambda j: j["job_parameters"]["granules"][0]):
            g = j["job_parameters"]["granules"]
            print(j["status_code"], g[0][3:27], g[1][10:18], j.get("credit_cost"))
    elif cmd == "download":
        os.makedirs(OUT, exist_ok=True)
        for j in all_jobs(s):
            if j["status_code"] != "SUCCEEDED":
                continue
            for f in j["files"]:
                path = os.path.join(OUT, f["filename"])
                if os.path.exists(path) and os.path.getsize(path) == f["size"]:
                    continue
                print("get", f["filename"], f["size"] // 1_000_000, "MB", flush=True)
                with requests.get(f["url"], stream=True, timeout=600) as r:
                    r.raise_for_status()
                    with open(path + ".part", "wb") as fh:
                        for chunk in r.iter_content(1 << 20):
                            fh.write(chunk)
                os.replace(path + ".part", path)


if __name__ == "__main__":
    main()
