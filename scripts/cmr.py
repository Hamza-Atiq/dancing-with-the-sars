import json, urllib.request, urllib.parse, sys
B="https://cmr.earthdata.nasa.gov/search/granules.umm_json"
def q(**p):
    url=B+"?"+urllib.parse.urlencode(p)
    with urllib.request.urlopen(url,timeout=60) as r:
        hits=int(r.headers.get('CMR-Hits',-1)); d=json.load(r)
    return hits,d
PK="60.8,23.6,77.9,37.1"
names=["NISAR_L2_GCOV_V1","NISAR_L2_GCOV_PROVISIONAL_V1","NISAR_L2_GCOV_BETA_V1","NISAR_L2_GUNW_V1","NISAR_L2_GUNW_PROVISIONAL_V1","NISAR_L2_GUNW_BETA_V1","NISAR_L2_GSLC_V1","NISAR_L2_GSLC_PROVISIONAL_V1","NISAR_L2_GOFF_V1","NISAR_L2_GOFF_PROVISIONAL_V1","NISAR_L1_RSLC_V1","NISAR_L1_RSLC_PROVISIONAL_V1","NISAR_L3_SME2_PROVISIONAL_V1","NISAR_L3_SME2_BETA_V1","NISAR_UR_L1","NISAR_UR_L2","NISAR_UR_L0B_RRSD","NISAR_VWC","NISAR_WATERMASK","OPERA_L3_DISP-S1_V1","OPERA_L3_DSWX-S1_V1"]
def rng(sn,**extra):
    out=[]
    for s in ("start_date","-start_date"):
        try:
            h,d=q(short_name=sn,page_size=1,sort_key=s,**extra)
            t=d['items'][0]['umm']['TemporalExtent']['RangeDateTime']['BeginningDateTime'][:10] if d['items'] else '-'
        except Exception as e:
            h,t=-1,'ERR '+str(e)[:40]
        out.append(t)
    return h,out
print("collection | global hits | first | last || PK hits | first | last")
for n in names:
    h,(a,b)=rng(n)
    hp,(c,e)=rng(n,bounding_box=PK)
    print(f"{n} | {h} | {a} | {b} || {hp} | {c} | {e}")
