import bpy

class GEOTG_OT_render_object_index(bpy.types.Operator):
    bl_idname = "geotg.render_object_index"
    bl_label = "Render Object Index"
    bl_description = "Stub: Render Object Index pass"

    def execute(self, context):
        self.report({'INFO'}, "Object Index render stub")
        return {'FINISHED'}

class GEOTG_OT_render_material_index(bpy.types.Operator):
    bl_idname = "geotg.render_material_index"
    bl_label = "Render Material Index"
    bl_description = "Stub: Render Material Index pass"

    def execute(self, context):
        self.report({'INFO'}, "Material Index render stub")
        return {'FINISHED'}

class GEOTG_OT_render_depth(bpy.types.Operator):
    bl_idname = "geotg.render_depth"
    bl_label = "Render Depth"
    bl_description = "Stub: Render Depth pass"

    def execute(self, context):
        self.report({'INFO'}, "Depth render stub")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(GEOTG_OT_render_object_index)
    bpy.utils.register_class(GEOTG_OT_render_material_index)
    bpy.utils.register_class(GEOTG_OT_render_depth)

def unregister():
    bpy.utils.unregister_class(GEOTG_OT_render_object_index)
    bpy.utils.unregister_class(GEOTG_OT_render_material_index)
    bpy.utils.unregister_class(GEOTG_OT_render_depth)
