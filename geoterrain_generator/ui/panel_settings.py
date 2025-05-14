import bpy

class GEOTG_PT_render_outputs(bpy.types.Panel):
    bl_label = "GeoTG Render Outputs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GeoTerrain"
    bl_parent_id = "GEOTG_PT_main_panel"

    def draw(self, context):
        lay = self.layout
        box = lay.box()
        box.prop(context.scene, "geotg_render_object_index", text="Рендерить Object Index")
        box.prop(context.scene, "geotg_render_material_index", text="Рендерить Material Index")
        box.prop(context.scene, "geotg_render_depth", text="Рендерить depth")
        box.operator("geotg.render_object_index", text="Render Object Index")
        box.operator("geotg.render_material_index", text="Render Material Index")
        box.operator("geotg.render_depth", text="Render Depth")

# Для регистрации панели из __init__.py
GEOTG_PT_render_outputs.__module__ = __name__
