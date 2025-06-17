import bpy
from bpy.props import StringProperty

class OP_OT_import_dem_geotiff(bpy.types.Operator):
    bl_idname = "geotg.import_dem_geotiff"
    bl_label = "Import DEM from GeoTIFF"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        path = context.scene.geotg_dem_geotiff_path
        if not path or not path.lower().endswith(('.tif', '.tiff')):
            self.report({'ERROR'}, "Please select a valid GeoTIFF file.")
            return {'CANCELLED'}
        # TODO: Реализовать чтение DEM из GeoTIFF и применение к плоскости
        self.report({'INFO'}, f"Selected GeoTIFF: {path}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OP_OT_import_dem_geotiff)

def unregister():
    bpy.utils.unregister_class(OP_OT_import_dem_geotiff)
