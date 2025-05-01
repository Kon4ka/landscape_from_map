import bpy, os
from ..core.tiles import fetch_image

ADDON_ID = __name__.split('.')[0]

class OP_OT_fetch_tiles(bpy.types.Operator):
    bl_idname = "geotg.fetch_tile"
    bl_label  = "Fetch satellite tile"

    lat : bpy.props.FloatProperty(name="Latitude",  default=55.75)
    lon : bpy.props.FloatProperty(name="Longitude", default=37.62)
    zoom: bpy.props.IntProperty   (name="Zoom",     default=18, min=14, max=19)

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_ID].preferences
        cache_dir = bpy.path.abspath(prefs.cache_dir)
        try:
            os.makedirs(cache_dir, exist_ok=True)     # ← может бросить PermissionError
        except PermissionError as e:
            self.report({'ERROR'},
                        f"No write access to '{cache_dir}'. "
                        f"Choose another Cache Folder in Add-on Preferences.")
            return {'CANCELLED'}

        out_file = os.path.join(
            cache_dir, f"tile_{self.lat}_{self.lon}_{self.zoom}.jpg")

        try:
            fetch_image(self.lat, self.lon, self.zoom,
                        prefs.provider, prefs.api_key, out_file)
        except Exception as e:
            self.report({'ERROR'}, f"Tile download failed: {e}")
            return {'CANCELLED'}

        img = bpy.data.images.load(out_file, check_existing=True)
        img.name = "GeoTG_Ortho"          # ← добавьте
        context.scene["geotg_lat"] = self.lat
        context.scene["geotg_lon"] = self.lon
        context.scene["geotg_ratio"] = img.size[0]/img.size[1]
        if context.area.type == 'IMAGE_EDITOR':
            context.area.spaces.active.image = img
        self.report({'INFO'}, f"Saved {out_file}")
        return {'FINISHED'}
