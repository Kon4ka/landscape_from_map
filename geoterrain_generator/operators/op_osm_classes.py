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

class GEOTG_OT_fetch_osm_class(bpy.types.Operator):
    bl_idname = "geotg.fetch_osm_class"
    bl_label = "Load GeoJSON Class"
    bl_description = "Load and set weights for the selected OSM class"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_ID].preferences
        lat1, lat2 = sorted([prefs.lat1, prefs.lat2])
        lon1, lon2 = sorted([prefs.lon1, prefs.lon2])
        bbox_str = f"{lat1},{lon1},{lat2},{lon2}"
        selected = context.scene.geotg_selected_osm_class

        if not selected or '=' not in selected:
            self.report({'ERROR'}, "No OSM class selected")
            return {'CANCELLED'}

        key, value = selected.split('=', 1)
        query = (
            f'[out:json][timeout:25];'
            f'(way["{key}"="{value}"]({bbox_str});'
            f'relation["{key}"="{value}"]({bbox_str}););out geom;'
        )
        encoded_query = quote(query, safe='')
        overpass_url = f"https://overpass-api.de/api/interpreter?data={encoded_query}"

        try:
            from geoterrain_generator.core.geo_utils import point_in_polygon
            geojson = fetch_geojson_by_bbox(None, overpass_url)
        except Exception as e:
            self.report({'ERROR'}, f"GeoJSON fetch error: {e}")
            return {'CANCELLED'}

        obj = context.active_object
        if not obj or obj.type != 'MESH' or not obj.name.startswith('GeoTerrainGrid'):
            self.report({'ERROR'}, "Select a grid object to set weights")
            return {'CANCELLED'}

        mesh = obj.data
        vgroup = obj.vertex_groups.get(value) or obj.vertex_groups.new(name=value)
        polygons = []
        for feat in geojson.get('elements', []):
            if 'geometry' in feat:
                poly = [(pt['lon'], pt['lat']) for pt in feat['geometry']]
                if len(poly) > 2:
                    polygons.append(poly)

        verts_world = [obj.matrix_world @ v.co for v in mesh.vertices]
        min_x = min(v.x for v in verts_world)
        max_x = max(v.x for v in verts_world)
        min_y = min(v.y for v in verts_world)
        max_y = max(v.y for v in verts_world)

        for v in mesh.vertices:
            co = obj.matrix_world @ v.co
            if max_x - min_x > 1e-8 and max_y - min_y > 1e-8:
                lon = lon1 + (lon2 - lon1) * (co.x - min_x) / (max_x - min_x)
                lat = lat1 + (lat2 - lat1) * (co.y - min_y) / (max_y - min_y)
            else:
                lon = lon1
                lat = lat1
            inside = any(point_in_polygon(lon, lat, poly) for poly in polygons)
            vgroup.add([v.index], 1.0 if inside else 0.0, 'REPLACE')

        self.report({'INFO'}, f"Weights for '{value}' set on grid ({len(polygons)} polygons)")
        return {'FINISHED'}
