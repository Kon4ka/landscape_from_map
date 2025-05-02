import bpy, bmesh
import math
from bpy.props import FloatProperty, BoolProperty
from geoterrain_generator.operators.op_build_height import BLENDER_SCALE
from ..core.dem import fetch_dem
ADDON_ID = __name__.split('.')[0]


class OP_OT_displace_area(bpy.types.Operator):
    bl_idname  = "geotg.displace_area"
    bl_label   = "Displace (apply DEM)"
    bl_options = {'REGISTER', 'UNDO'}

    exaggeration : FloatProperty(
        name="Z exaggeration",
        default=2.5, min=0.1, max=20.0,
        description="Во сколько раз усиливать рельеф")

    center_to_zero : BoolProperty(
        name="Уровень моря в ноль Z", default=True,
        description="Минимальная отметка DEM будет на высоте 0")

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.name.split('.')[0] != "GeoTerrainGrid":
            self.report({'ERROR'}, "Select the grid created by 'Load Area'")
            return {'CANCELLED'}

        prefs  = context.preferences.addons[ADDON_ID].preferences
        lat_c  = 0.5 * (prefs.lat1 + prefs.lat2)
        lon_c  = 0.5 * (prefs.lon1 + prefs.lon2)
        side_m = context.scene.get("geotg_side_m_avg", 400.0)

        verts = obj.data.vertices
        xs = sorted({round(v.co.x, 7) for v in verts})
        ys = sorted({round(v.co.y, 7) for v in verts})
        cols, rows = len(xs), len(ys)
        samples = max(cols, rows)      

        try:
            dem   = fetch_dem(lat_c, lon_c,
                  side_m=side_m,
                  samples=samples).astype(float)
        except Exception as e:
            self.report({'ERROR'}, f"DEM download failed: {e}")
            return {'CANCELLED'}

        z_min, z_max = float(dem.min()), float(dem.max())
        if z_max == z_min:
            self.report({'WARNING'}, "DEM returned a flat tile; mesh left unchanged")
            return {'CANCELLED'}

        m2bu = self.exaggeration / BLENDER_SCALE

        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        for vidx, v in enumerate(bm.verts):
            row = vidx // cols
            col = vidx %  cols
            elev = dem[min(row, dem.shape[0]-1),
                    min(col, dem.shape[1]-1)]
            if self.center_to_zero:
                elev -= z_min
            v.co.z = elev * m2bu

        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()                                 

        # switch viewport shading so the texture + relief are visible
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        break

        self.report({'INFO'},
            f"Displace ok (Δ {z_max - z_min:.1f} m, exaggeration ×{self.exaggeration})")
        return {'FINISHED'}
