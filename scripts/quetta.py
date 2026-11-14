import json, urllib.request, urllib.parse, collections
B="https://cmr.earthdata.nasa.gov/search/granules.umm_json"
def allg(**p):
    items=[]; sa=None
    while True:
        req=urllib.request.Request(B+"?"+urllib.parse.urlencode(dict(p,page_size=2000)))
        if sa: req.add_header('CMR-Search-After',sa)
        with urllib.request.urlopen(req,timeout=120) as r:
            sa=r.headers.get('CMR-Search-After'); d=json.load(r)
        items+=d['items']
        if not d['items'] or not sa: break
    return items
BB="66.80,30.00,67.20,30.45"   # Quetta valley
cols=["NISAR_L2_GUNW_PROVISIONAL_V1","NISAR_L2_GUNW_BETA_V1","NISAR_L2_GUNW_V1","NISAR_L2_GCOV_PROVISIONAL_V1","NISAR_L2_GCOV_BETA_V1","NISAR_L2_GCOV_V1","NISAR_L2_GSLC_PROVISIONAL_V1","NISAR_L2_GSLC_V1","NISAR_L2_GOFF_PROVISIONAL_V1","NISAR_L3_SME2_PROVISIONAL_V1","NISAR_L1_RSLC_PROVISIONAL_V1","NISAR_L1_RIFG_PROVISIONAL_V1","NISAR_L1_RUNW_PROVISIONAL_V1","NISAR_UR_L2","NISAR_UR_L1","OPERA_L3_DISP-S1_V1"]
out={}
for sn in cols:
    it=allg(short_name=sn,bounding_box=BB)
    out[sn]=it
    print("\n==",sn,len(it))
    if not it: continue
    g=collections.defaultdict(list)
    for i in it:
        n=i['umm']['GranuleUR']; p=n.split('_')
        g['_'.join(p[5:8])].append(n)
    for k,v in sorted(g.items()):
        print("  ",k,"n=",len(v))
        if 'GUNW' in sn or 'GOFF' in sn:
            for n in sorted(v, key=lambda s:s.split('_')[11]):
                p=n.split('_'); print("      ",p[11][:8],"->",p[13][:8],"mode",p[9],p[10],"crid",p[15],"acc",p[16],"cov",p[17])
        else:
            ds=sorted(n.split('_')[11][:8]+":"+n.split('_')[8]+n.split('_')[9]+":"+n.split('_')[15] for n in v)
            print("      ",' '.join(ds))
json.dump({k:[i['umm'] for i in v] for k,v in out.items() if 'GUNW' in k or 'GCOV_PROV' in k},open("quetta_meta.json","w"))
