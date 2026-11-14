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
sites={"Baltoro (Karakoram, PK)":(76.40,35.74),"Batura (Hunza, PK)":(74.60,36.55),"Hispar (PK)":(75.30,36.10),"Siachen":(77.10,35.40),"Shishper (PK)":(74.60,36.38),
"Khumbu (Everest)":(86.82,27.98),"Jakobshavn (Greenland)":(-49.60,69.17),"Pine Island (Antarctica)":(-100.5,-75.10),"Thwaites (Antarctica)":(-106.8,-75.4),
"Hubbard (Alaska)":(-139.45,60.05),"Malaspina (Alaska)":(-140.5,59.9),"Columbia (Alaska)":(-147.0,61.15),"Upsala (Patagonia)":(-73.30,-49.90),"Vatnajokull (Iceland)":(-16.80,64.40),"Fedchenko (Pamir)":(72.25,38.80),"Kronebreen (Svalbard)":(12.9,78.87)}
out={}
for name,(lon,lat) in sites.items():
    row=[]
    for sn in ["NISAR_L2_GOFF_PROVISIONAL_V1","NISAR_L2_GUNW_PROVISIONAL_V1","NISAR_L2_GCOV_PROVISIONAL_V1"]:
        it=allg(short_name=sn,point=f"{lon},{lat}")
        tf=collections.defaultdict(set)
        for i in it:
            p=i['umm']['GranuleUR'].split('_'); tf['_'.join(p[5:8])].add(p[11][:8])
        dates=sorted(set().union(*tf.values())) if tf else []
        best=max(tf.items(),key=lambda kv:len(kv[1])) if tf else ("-",[])
        row.append(f"{sn.split('_')[2]}: {len(it)} gran, {len(tf)} tracks, best {best[0]} n={len(best[1])}, {dates[0] if dates else '-'}..{dates[-1] if dates else '-'}")
        if sn.startswith("NISAR_L2_GOFF"): out[name]=[i['umm'] for i in it]
    print(f"\n## {name}\n   "+"\n   ".join(row),flush=True)
json.dump(out,open("glac_goff.json","w"))
