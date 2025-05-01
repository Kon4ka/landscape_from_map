import bpy, bmesh
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
        if not obj or obj.name != "GeoTerrainGrid":
            self.report({'ERROR'},
                        "Выберите сетку, созданную командой Load Area")
            return {'CANCELLED'}

        prefs  = context.preferences.addons[ADDON_ID].preferences
        lat_c  = 0.5 * (prefs.lat1 + prefs.lat2)
        lon_c  = 0.5 * (prefs.lon1 + prefs.lon2)
        side_m = context.scene.get("geotg_side_m_avg", 400.0)

        # число вершин по одной стороне
        verts_side = round(len(obj.data.vertices) ** 0.5)

        # запрашиваем DEM
        dem = fetch_dem(lat_c, lon_c,
                        side_m=side_m,
                        samples=verts_side).astype(float)
        z_min, z_max = dem.min(), dem.max()

        # коэффициент: метры → BU
        m2bu = self.exaggeration / BLENDER_SCALE

        bm = bmesh.new(); bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        for idx, v in enumerate(bm.verts):
            x = idx % verts_side
            y = idx // verts_side

            # абсолютная высота относительно выбранного «нуля»
            elev = dem[y, x] - (z_min if self.center_to_zero else 0.0)
            v.co.z = elev * m2bu

        bm.to_mesh(obj.data); bm.free()

        # переключаем просмотр на Material, чтобы увидеть рельеф с текстурой
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        break

        self.report({'INFO'},
                    f"Displace applied (Δ={z_max - z_min:.1f} m, "
                    f"ex×{self.exaggeration})")
        return {'FINISHED'}
