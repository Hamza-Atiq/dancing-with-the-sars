import requests, netrc, os, h5py, fsspec
_s=None
def session():
    global _s
    if _s is None:
        _s=requests.Session()   # requests reads ~/.netrc itself for urs.earthdata.nasa.gov
    return _s
def signed_url(url):
    r=session().get(url,headers={"Range":"bytes=0-0"},allow_redirects=True,stream=True,timeout=120)
    r.close()
    if r.status_code not in (200,206): raise RuntimeError(f"HTTP {r.status_code}")
    return r.url
def open_h5(url):
    su=signed_url(url)
    f=fsspec.open(su,mode="rb",block_size=4*1024*1024,cache_type="blockcache").open()
    return h5py.File(f,"r")
def gunw_url(g): return f"https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GUNW_PROVISIONAL_V1/{g}/{g}.h5"
