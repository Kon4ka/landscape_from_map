import bpy
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

class GEOTG_OT_load_osm_classes(bpy.types.Operator):
    bl_idname = "geotg.load_osm_classes"
    bl_label = "Load OSM Classes"
    bl_description = "Load the list of OSM classes for the selected bbox"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_ID].preferences
        lat1, lat2 = sorted([prefs.lat1, prefs.lat2])
        lon1, lon2 = sorted([prefs.lon1, prefs.lon2])
        bbox_str = f"{lat1},{lon1},{lat2},{lon2}"

        query = (
            f'[out:json][timeout:25];'
            f'(way({bbox_str});relation({bbox_str}););out tags;'
        )
        encoded_query = quote(query, safe='')
        overpass_url = f"https://overpass-api.de/api/interpreter?data={encoded_query}"

        try:
            geojson = fetch_geojson_by_bbox((lat1, lon1, lat2, lon2), overpass_url)
        except Exception as e:
            self.report({'ERROR'}, f"GeoJSON fetch error: {e}")
            return {'CANCELLED'}

        classes = extract_osm_classes(geojson)
        scene = context.scene
        scene['geotg_osm_classes'] = classes
        scene.geotg_selected_osm_class = classes[0] if classes else ""

        self.report({'INFO'}, f"Found classes: {len(classes)}")
        return {'FINISHED'}
