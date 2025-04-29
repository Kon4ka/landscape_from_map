import bpy, bmesh, numpy as np
from mathutils import Matrix, Vector 
from ..core.dem import fetch_dem
from ..operators.op_fetch_tiles import ADDON_ID

BLENDER_SCALE = 100.0          # 1 Bu → 100 реальных метров
SIDE_REAL_M   = 400.0          # реальная высота участка в метрах

class OP_OT_build_height(bpy.types.Operator):
    bl_idname  = "geotg.build_height"
    bl_label   = "Build 3-D terrain"
    bl_options = {'REGISTER', 'UNDO'}

    samples : bpy.props.IntProperty(name="DEM Samples",
                                    default=120, min=30, max=512)

    exaggeration : bpy.props.FloatProperty(name="Z exaggeration",
                                           default=3.0, min=0.5, max=10,
                                           description="Multiply terrain relief")

    def execute(self, context):
        lat = context.scene.get("geotg_lat")
        lon = context.scene.get("geotg_lon")
        ratio = context.scene.get("geotg_ratio", 650/450)

        side_y = SIDE_REAL_M                    # 400 м
        side_x = side_y * ratio
        bu_x   = side_x / BLENDER_SCALE         # 4 Bu × 2.8 Bu ≈ 14 × 10
        bu_y   = side_y / BLENDER_SCALE

        dem = fetch_dem(lat, lon, side_m=side_y, samples=self.samples)
        core = dem.copy()
        core[1:-1, 1:-1] = (
                dem[ :-2, 1:-1] + dem[2:, 1:-1] +     # север-юг
                dem[1:-1,  :-2] + dem[1:-1, 2:]) * 0.25
        dem = core
        z_min, z_max = dem.min(), dem.max()
        z_scale = self.exaggeration * (z_max - z_min) / BLENDER_SCALE

        bm = bmesh.new()
        bmesh.ops.create_grid(
            bm, x_segments=self.samples-1, y_segments=self.samples-1,
            size=0.5, matrix=Matrix.Identity(4))
        bm.verts.ensure_lookup_table()

        step_x = bu_x / (self.samples-1)
        step_y = bu_y / (self.samples-1)

        for idx, v in enumerate(bm.verts):
            xi = idx % self.samples
            yi = idx // self.samples
            v.co.x = (xi - 0.5*(self.samples-1)) * step_x
            v.co.y = (yi - 0.5*(self.samples-1)) * step_y
            v.co.z = (dem[yi, xi] - z_min) / (z_max - z_min) * z_scale

        mesh = bpy.data.meshes.new("GeoTG_Terrain")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("GeoTerrain", mesh)
        context.collection.objects.link(obj)

        # 3 — UV и материал ---------------------------
        img = bpy.data.images.get("GeoTG_Ortho")
        if img:
            # Упрощённый planar-UV на XY
            uv_lay = mesh.uv_layers.new(name="GeoTG_UV")
            w, h   = size_x, size_y
            for loop in mesh.loops:
                v = mesh.vertices[loop.vertex_index].co
                uv.data[loop.index].uv = ((v.x/bu_x)+0.5, (v.y/bu_y)+0.5)

            mat = bpy.data.materials.new("GeoTG_Mat")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            tex  = mat.node_tree.nodes.new("ShaderNodeTexImage")
            tex.image = img
            mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            obj.data.materials.append(mat)

        self.report({'INFO'}, f"Terrain {size_x:.0f}×{size_y:.0f} m created")
        return {'FINISHED'}
