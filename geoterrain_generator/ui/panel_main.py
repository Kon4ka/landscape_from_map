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
        lay.separator()
        lay.operator("geotg.load_area")
        lay.operator("geotg.displace_area")
        lay.separator()
        lay.operator("geotg.fetch_trees")  # Новая кнопка для загрузки деревьев
