import bpy
import math
from geoterrain_generator.core.geo_utils import fetch_geojson_by_bbox, point_in_polygon

ADDON_ID = __name__.split('.')[0]

class OP_OT_fetch_trees(bpy.types.Operator):
    bl_idname = "geotg.fetch_trees"
    bl_label = "Load GeoJson"
    bl_description = "Load and place tree data for the selected rectangle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_ID].preferences
        lat1, lat2 = min(prefs.lat1, prefs.lat2), max(prefs.lat1, prefs.lat2)
        lon1, lon2 = min(prefs.lon1, prefs.lon2), max(prefs.lon1, prefs.lon2)
        bbox = (lat1, lon1, lat2, lon2)
        bbox_str = f"{lat1},{lon1},{lat2},{lon2}"
        # By default, class for trees
        key, value = "landuse", "forest"
        overpass_url = (
            "https://overpass-api.de/api/interpreter?data="
            "[out:json][timeout:25];"
            f"(way[\"{key}\"=\"{value}\"]({bbox});way[\"landuse\"=\"wood\"]({bbox});way[\"natural\"=\"wood\"]({bbox});"
            f"relation[\"{key}\"=\"{value}\"]({bbox});relation[\"landuse\"=\"wood\"]({bbox});relation[\"natural\"=\"wood\"]({bbox}););out geom;"
        )
        self.report({'INFO'}, f"BBox: {bbox_str}")
        try:
            geojson = fetch_geojson_by_bbox((lat1, lon1, lat2, lon2), overpass_url)
        except Exception as e:
            self.report({'ERROR'}, f"GeoJSON fetch error: {e}")
            return {'CANCELLED'}
        obj = context.active_object
        if not obj or obj.type != 'MESH' or not obj.name.startswith('GeoTerrainGrid'):
            self.report({'ERROR'}, "Select a grid object to set weights")
            return {'CANCELLED'}
        mesh = obj.data
        vgroup = obj.vertex_groups.get('forest') or obj.vertex_groups.new(name='forest')
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
        self.report({'INFO'}, f"Weights for forest set on grid ({len(polygons)} polygons)")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OP_OT_fetch_trees)

def unregister():
    bpy.utils.unregister_class(OP_OT_fetch_trees)
