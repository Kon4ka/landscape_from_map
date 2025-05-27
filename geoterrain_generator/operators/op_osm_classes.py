import bpy
import math
from urllib.parse import quote
from geoterrain_generator.core.geo_utils import fetch_geojson_by_bbox

ADDON_ID = __name__.split('.')[0]

def extract_osm_classes(geojson):
    classes = set()
    for feat in geojson.get('elements', []):
        tags = feat.get('tags', {})
        for k, v in tags.items():
            if k in ("landuse", "natural", "amenity", "leisure", "building", "highway", "waterway"):
                classes.add(f"{k}={v}")
    return sorted(classes)

# Класс перенесён в op_osm_load_classes.py

# Класс перенесён в op_osm_fetch_class.py

# Класс перенесён в op_osm_roads_rivers.py
