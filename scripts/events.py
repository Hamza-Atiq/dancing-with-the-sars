import json, urllib.request, urllib.parse, collections
B="https://cmr.earthdata.nasa.gov/search/granules.umm_json"
def allg(**p):
    with urllib.request.urlopen(B+"?"+urllib.parse.urlencode(dict(p,page_size=2000)),timeout=120) as r: return json.load(r)['items']
sites={"Langtang Lirung, Nepal (collapse 26 Aug 2026)":(85.52,28.25),"Langtang valley downstream (Lhende Khola/Kyirong side)":(85.35,28.30),"Suicide Basin / Mendenhall, Juneau (flood ~11 Aug 2026)":(-134.50,58.46)}
for name,(lon,lat) in sites.items():
    print("\n##",name)
    for sn in ["NISAR_L2_GCOV_PROVISIONAL_V1","NISAR_L2_GUNW_PROVISIONAL_V1","NISAR_L2_GOFF_PROVISIONAL_V1","NISAR_L2_GCOV_V1","NISAR_UR_L2"]:
        it=allg(short_name=sn,point=f"{lon},{lat}")
        tf=collections.defaultdict(set)
        for i in it:
            p=i['umm']['GranuleUR'].split('_'); 
            key='_'.join(p[5:8])+("" if 'GCOV' in p[3] or 'GSLC' in p[3] else "")
            tf[p[3]+" "+'_'.join(p[5:8])].add(p[11][4:8] + (">"+p[13][4:8] if p[3] in('GUNW','GOFF') else ":"+p[9]))
        print("  ",sn.replace("NISAR_",""),len(it))
        for k,v in sorted(tf.items()): print("      ",k,' '.join(sorted(v)))
