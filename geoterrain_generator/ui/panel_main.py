import bpy

class GEOTG_PT_main_panel(bpy.types.Panel):
    bl_label = "Geo-Terrain Generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GeoTerrain"

    def draw(self, context):
        layout = self.layout
        layout.operator("geotg.fetch_tile")
        layout.operator("geotg.build_height")

        

# panneau должен быть указан в classes (__init__.py)
