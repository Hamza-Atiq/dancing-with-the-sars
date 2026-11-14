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
PK="60.8,23.6,77.9,37.1"
for sn in ["NISAR_L2_GCOV_PROVISIONAL_V1","NISAR_L2_GCOV_V1","NISAR_L2_GUNW_PROVISIONAL_V1","NISAR_UR_L2"]:
    it=allg(short_name=sn,bounding_box=PK)
    mon=collections.Counter(i['umm']['TemporalExtent']['RangeDateTime']['BeginningDateTime'][:7] for i in it)
    print("\n==",sn,len(it)); print(' '.join(f"{k}:{v}" for k,v in sorted(mon.items())))
    print("sample:",it[0]['umm']['GranuleUR']); print("sample:",it[-1]['umm']['GranuleUR'])
    if sn=="NISAR_UR_L2":
        typ=collections.Counter(i['umm']['GranuleUR'].split('_')[3] if len(i['umm']['GranuleUR'].split('_'))>3 else '?' for i in it); print(typ)
    json.dump([i['umm']['GranuleUR'] for i in it],open(sn+"_pk.json","w"))
# point tests
pts={"Sukkur/Indus (27.70N,68.85E)":"68.85,27.70","Lahore (31.52N,74.35E)":"74.35,31.52","Karachi (24.86N,67.01E)":"67.01,24.86","Manchar Lake (26.42N,67.67E)":"67.67,26.42","Quetta (30.18N,66.99E)":"66.99,30.18","Islamabad (33.69N,73.05E)":"73.05,33.69","Gilgit/Hunza (36.32N,74.65E)":"74.65,36.32"}
for name,pt in pts.items():
    print("\n##",name)
    for sn in ["NISAR_L2_GCOV_PROVISIONAL_V1","NISAR_L2_GCOV_V1","NISAR_L2_GUNW_PROVISIONAL_V1"]:
        it=allg(short_name=sn,point=pt)
        tf=collections.defaultdict(list)
        for i in it:
            u=i['umm']['GranuleUR'].split('_')
            tf['_'.join(u[5:8])].append(i['umm']['TemporalExtent']['RangeDateTime']['BeginningDateTime'][:10])
        print(" ",sn,len(it))
        for k,v in sorted(tf.items()): print("    track_dir_frame",k,"n=",len(v),sorted(set(v))[0],"->",sorted(set(v))[-1])
