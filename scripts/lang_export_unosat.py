"""Run with Python 3.13 and project-local data/lang_tools Fiona install."""
from pathlib import Path
import sys
import json
import hashlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'data/lang_tools'))
import fiona
from fiona.transform import transform_geom
from fiona.model import to_dict

folder=ROOT/'data/lang_sources'
path=folder/'unosat/FL20260826NPL.gdb'
layer='UNOSAT_Landsat9_20260826_DetachmentZone'
with fiona.open(path,layer=layer) as source:
    records=list(source)
    for epsg,name in [('EPSG:4326','detachment.geojson'),('EPSG:32645','detachment_utm.geojson')]:
        features=[{'type':'Feature','properties':dict(f.properties),
                   'geometry':to_dict(transform_geom(source.crs,epsg,f.geometry))} for f in records]
        result={'type':'FeatureCollection','source':'https://unosat.org/products/4260',
                'layer':layer,'source_crs':str(source.crs),'output_crs':epsg,
                'source_zip_sha256':hashlib.sha256((folder/'UNOSAT.gdb.zip').read_bytes()).hexdigest(),
                'features':features}
        (folder/name).write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(name,len(features),'features')
