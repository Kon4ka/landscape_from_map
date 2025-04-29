# geoterrain_generator/operators/op_build_height.py
import bpy, bmesh, numpy as np
from mathutils import Matrix
from ..core.dem import fetch_dem
from ..operators.op_fetch_tiles import ADDON_ID

class OP_OT_build_height(bpy.types.Operator):
    bl_idname  = "geotg.build_height"
    bl_label   = "Build 3-D terrain"
    bl_options = {'REGISTER', 'UNDO'}

    samples : bpy.props.IntProperty(name="DEM Samples",
                                    default=100, min=20, max=512)

    def execute(self, context):
        lat = context.scene.get("geotg_lat", 55.75)
        lon = context.scene.get("geotg_lon", 37.62)

        dem = fetch_dem(lat, lon, side_m=1000, samples=self.samples)
        z_min, z_max = float(dem.min()), float(dem.max())
        z_range = (z_max - z_min) or 1.0

        bm = bmesh.new()
        bmesh.ops.create_grid(
            bm,
            x_segments=self.samples - 1,
            y_segments=self.samples - 1,
            size=0.5,
            matrix=Matrix.Identity(4))

        bm.verts.ensure_lookup_table()               # ← ВАЖНО

        for idx, v in enumerate(bm.verts):
            x = idx % self.samples
            y = idx // self.samples
            v.co.x *= 1000
            v.co.y *= 1000
            v.co.z = (dem[y, x] - z_min) / z_range * 100

        mesh = bpy.data.meshes.new("GeoTG_Terrain")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("GeoTerrain", mesh)
        context.collection.objects.link(obj)

        img = bpy.data.images.get("GeoTG_Ortho")
        if img:
            mat = bpy.data.materials.new("GeoTG_Mat")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            tex  = mat.node_tree.nodes.new("ShaderNodeTexImage")
            tex.image = img
            mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            obj.data.materials.append(mat)

        self.report({'INFO'}, "Terrain created")
        return {'FINISHED'}
