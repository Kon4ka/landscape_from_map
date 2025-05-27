import bpy
from urllib.parse import quote
from geoterrain_generator.core.geo_utils import fetch_geojson_by_bbox

ADDON_ID = __name__.split('.')[0]

class GEOTG_OT_fetch_osm_roads_rivers(bpy.types.Operator):
    bl_idname = "geotg.fetch_osm_roads_rivers"
    bl_label = "Load OSM Roads/Rivers as Curves"
    bl_description = "Load OSM roads or rivers and create curves on the terrain"
    bl_options = {'REGISTER', 'UNDO'}

    osm_type: bpy.props.EnumProperty(
        name="OSM Type",
        description="Type of OSM feature to fetch",
        items=[('highway', 'Road', ''), ('waterway', 'River', '')],
        default='highway'
    )

    def execute(self, context):
        from mathutils import Vector
        prefs = context.preferences.addons[ADDON_ID].preferences
        lat1, lat2 = sorted([prefs.lat1, prefs.lat2])
        lon1, lon2 = sorted([prefs.lon1, prefs.lon2])
        bbox_str = f"{lat1},{lon1},{lat2},{lon2}"
        key = self.osm_type
        query = (
            f'[out:json][timeout:25];'
            f'(way["{key}"]({bbox_str});relation["{key}"]({bbox_str}););out geom;'
        )
        encoded_query = quote(query, safe='')
        overpass_url = f"https://overpass-api.de/api/interpreter?data={encoded_query}"
        try:
            geojson = fetch_geojson_by_bbox(None, overpass_url)
        except Exception as e:
            self.report({'ERROR'}, f"GeoJSON fetch error: {e}")
            return {'CANCELLED'}

        # Find terrain object
        terrain = context.active_object
        if not terrain or terrain.type != 'MESH' or not terrain.name.startswith('GeoTerrainGrid'):
            self.report({'ERROR'}, "Select a grid object (terrain) to project curves onto")
            return {'CANCELLED'}
        mesh = terrain.data
        verts_world = [terrain.matrix_world @ v.co for v in mesh.vertices]
        min_x = min(v.x for v in verts_world)
        max_x = max(v.x for v in verts_world)
        min_y = min(v.y for v in verts_world)
        max_y = max(v.y for v in verts_world)

        # Create material if not exists
        mat_name = "GeoTG_RoadRiver"
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(mat_name)
            mat.diffuse_color = (0.5, 0.5, 0.5, 1.0)
        
        # Helper: lon/lat to XY in terrain local
        def lonlat_to_xy(lon, lat):
            x = min_x + (max_x - min_x) * (lon - lon1) / (lon2 - lon1) if lon2 - lon1 > 1e-8 else min_x
            y = min_y + (max_y - min_y) * (lat - lat1) / (lat2 - lat1) if lat2 - lat1 > 1e-8 else min_y
            return x, y

        # Helper: project to terrain Z
        def get_z(x, y):
            # Raycast from above
            origin = Vector((x, y, 1e4))
            direction = Vector((0, 0, -1))
            result, loc, normal, index, obj, matrix = terrain.ray_cast(origin, direction)
            if result:
                return loc.z
            else:
                # fallback: min Z
                return min(v.z for v in verts_world)

        count = 0
        for feat in geojson.get('elements', []):
            if 'geometry' in feat and len(feat['geometry']) > 1:
                points = []
                for pt in feat['geometry']:
                    lon, lat = pt['lon'], pt['lat']
                    x, y = lonlat_to_xy(lon, lat)
                    z = get_z(x, y)
                    points.append((x, y, z))
                # Create curve
                curve_data = bpy.data.curves.new(f"{key}_curve_{count}", type='CURVE')
                curve_data.dimensions = '3D'
                spline = curve_data.splines.new('POLY')
                spline.points.add(len(points) - 1)
                for i, co in enumerate(points):
                    spline.points[i].co = (*co, 1)
                curve_obj = bpy.data.objects.new(f"{key}_curve_{count}", curve_data)
                context.collection.objects.link(curve_obj)
                # Assign material
                if curve_obj.data.materials:
                    curve_obj.data.materials[0] = mat
                else:
                    curve_obj.data.materials.append(mat)
                # Bevel
                curve_data.bevel_depth = 1.0
                curve_data.bevel_resolution = 3
                curve_data.fill_mode = 'FULL'
                count += 1
        self.report({'INFO'}, f"Created {count} curves for {key}")
        return {'FINISHED'}
