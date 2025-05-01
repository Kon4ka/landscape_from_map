import bpy, os, urllib.request, math
from mathutils import Vector
ADDON_ID = __name__.split('.')[0]

class OP_OT_load_area(bpy.types.Operator):
    bl_idname  = "geotg.load_area"
    bl_label   = "Load Area"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_ID].preferences

        # ─ координаты (SW-NE) ───────────────────────────────────────────────
        lat1, lon1 = min(prefs.lat1, prefs.lat2), min(prefs.lon1, prefs.lon2)
        lat2, lon2 = max(prefs.lat1, prefs.lat2), max(prefs.lon1, prefs.lon2)

        # ─ скачиваем ортофото в кеш ─────────────────────────────────────────
        cache = bpy.path.abspath(prefs.cache_dir)
        os.makedirs(cache, exist_ok=True)
        out_img = os.path.join(cache, "area.jpg")
        bbox = f"{lon1},{lat1}~{lon2},{lat2}"
        url  = f"https://static-maps.yandex.ru/1.x/?bbox={bbox}&l=sat&size=650,450"
        urllib.request.urlretrieve(url, out_img)

        img = bpy.data.images.load(out_img, check_existing=True)
        img.name = "GeoTG_Ortho"

        # ─ реальные размеры участка (в метрах) ──────────────────────────────
        meters_lat = 111_320
        lat_mid    = 0.5 * (lat1 + lat2)
        meters_lon = meters_lat * math.cos(math.radians(lat_mid))
        side_x = max((lon2 - lon1) * meters_lon, 1.0)   # ≥1 м
        side_y = max((lat2 - lat1) * meters_lat, 1.0)

        # ─ создаём квадратную Grid и растягиваем её под нужные стороны ─────
        n = prefs.grid_n
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=n, y_subdivisions=n,
                                        size=0.5, enter_editmode=False)
        obj = context.active_object
        obj.name = "GeoTerrainGrid"

        # коэффициент: 1 BU = 100 м
        obj.scale = Vector((side_x / 100.0,
                            side_y / 100.0,
                            1.0))

        # применяем масштаб к геометрии, чтобы obj.scale снова стал 1,1,1
        bpy.ops.object.transform_apply(scale=True)

        # ─ материал с текстурой ─────────────────────────────────────────────
        mat = (bpy.data.materials.get("GeoTG_Mat")
               or bpy.data.materials.new("GeoTG_Mat"))
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        tex   = nodes.get("GeoTG_Tex") or nodes.new("ShaderNodeTexImage")
        tex.name, tex.image = "GeoTG_Tex", img
        bsdf = nodes["Principled BSDF"]
        if not tex.outputs["Color"].is_linked:
            mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

        obj.data.materials.clear()
        obj.data.materials.append(mat)

        # ─ сохраняем усреднённую сторону для DEM ───────────────────────────
        context.scene["geotg_side_m_avg"] = 0.5 * (side_x + side_y)

        self.report({'INFO'},
                    f"Area loaded: {side_x:.0f} × {side_y:.0f} m, "
                    f"Grid {n}×{n}")
        return {'FINISHED'}
