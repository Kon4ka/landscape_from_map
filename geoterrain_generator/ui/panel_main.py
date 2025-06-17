import bpy
ADDON_ID = __name__.split('.')[0]

class GEOTG_PT_main_panel(bpy.types.Panel):
    bl_label       = "Geo-Terrain Generator"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "GeoTerrain"

    def draw(self, context):
        lay  = self.layout
        p    = context.preferences.addons[ADDON_ID].preferences

        lay.label(text="Lat/Lon 1 (SW):")
        lay.prop(p, "lat1"); lay.prop(p, "lon1")
        lay.label(text="Lat/Lon 2 (NE):")
        lay.prop(p, "lat2"); lay.prop(p, "lon2")
        lay.prop(p, "grid_n")
        lay.operator("geotg.load_area", text="Load Area")
        lay.separator()
        lay.prop(context.scene, "geotg_dem_source", text="DEM Source")
        if context.scene.geotg_dem_source == 'GEOTIFF':
            lay.prop(context.scene, "geotg_dem_geotiff_path", text="GeoTIFF File")
            lay.operator("geotg.import_dem_geotiff", text="Import DEM from GeoTIFF")
        if context.scene.geotg_dem_source == 'API':
            lay.operator("geotg.displace_area", text="Displace Area")
        lay.separator()
        # --- New block: load OSM classes ---
        lay.operator("geotg.load_osm_classes", text="Load class info")
        lay.prop(context.scene, "geotg_selected_osm_class", text="OSM Class")
        lay.operator("geotg.fetch_osm_class", text="Load GeoJSON Class")
        lay.separator()
        lay.operator("geotg.fetch_trees")
        lay.separator()
        lay.label(text="Flight curve:")
        lay.prop(context.scene, "geotg_flight_curve_type", text="Curve type")
        lay.prop(context.scene, "geotg_flight_height", text="Height (m)")
        lay.operator("geotg.create_flight_curve", text="Create flight curve")

        # --- Camera animation block ---
        cam_anim_box = lay.box()
        cam_anim_box.label(text="Camera Animation:")
        cam_anim_box.prop(context.scene, "geotg_camera_frames", text="Frames")
        cam_anim_box.operator("geotg.recalc_camera_anim", text="Recalculate")

        # --- Camera tools block (only if curve selected) ---
        obj = context.active_object
        if obj and obj.type == 'CURVE':
            cam_tools_box = lay.box()
            cam_tools_box.label(text="Camera Tools:")
            cam_tools_box.prop(context.scene, "geotg_camera_preset", text="Camera preset")
            cam_tools_box.prop(context.scene, "geotg_camera_pitch", text="Pitch (deg)")
            cam_tools_box.operator("geotg.spawn_camera", text="Spawn Camera")

