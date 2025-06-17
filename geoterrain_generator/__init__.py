bl_info = {
    "name": "Geo-Terrain Generator",
    "author": "Kon4ka",
    "version": (0, 1, 0, 2),
    "blender": (4, 0, 0),
    "location": "File > Import > Geo-Terrain",
    "description": "Generate small-area terrain from satellite imagery, including terrain generation, tree placement, and flight path creation.",
    "doc_url": "https://github.com/Kon4ka/landscape_from_map/tree/main/geoterrain_generator",
    "tracker_url": "https://github.com/Kon4ka/landscape_from_map/issues",
    "category": "Import-Export",
}

# Удаление кэшированных файлов .pyc
import os
import sys
import pathlib

addon_dir = pathlib.Path(__file__).parent
pycache_dir = addon_dir / "__pycache__"

if pycache_dir.exists():
    for pyc_file in pycache_dir.glob("*.pyc"):
        try:
            pyc_file.unlink()
        except Exception as e:
            print(f"Не удалось удалить {pyc_file}: {e}")

# Чистим кеш .pyc для camera подпакета
camera_dir = addon_dir / "operators" / "camera"
camera_pycache = camera_dir / "__pycache__"
if camera_pycache.exists():
    for pyc_file in camera_pycache.glob("*.pyc"):
        try:
            pyc_file.unlink()
        except Exception as e:
            print(f"[Geo-Terrain Generator] Could not delete camera cache {pyc_file}: {e}")

# Перезагрузка всех вложенных модулей
if "bpy" in locals():
    import importlib
    modules = [
        "geoterrain_generator.operators.op_fetch_tiles",
        "geoterrain_generator.operators.op_build_height",
        "geoterrain_generator.operators.op_area_load",
        "geoterrain_generator.operators.op_area_displace",
        "geoterrain_generator.operators.op_fetch_trees",
        "geoterrain_generator.operators.op_create_flight_curve",
        "geoterrain_generator.operators.op_camera_tools",
        "geoterrain_generator.operators.camera.op_spawn_camera",
        "geoterrain_generator.operators.camera.op_recalc_anim",
        "geoterrain_generator.operators.camera.presets",
        "geoterrain_generator.ui.panel_main",
        "geoterrain_generator.ui.panel_settings",
        "geoterrain_generator.prefs",
        "geoterrain_generator.core.dem",
        "geoterrain_generator.core.geo_utils",
        "geoterrain_generator.core.textures",
        "geoterrain_generator.core.tiles",
        "geoterrain_generator.vendor.gdal_wrapper"
    ]
    for m in modules:
        if m in sys.modules:
            importlib.reload(sys.modules[m])


import bpy
from .prefs                  import GeoTG_Preferences
from .operators.op_fetch_tiles import OP_OT_fetch_tiles
from .ui.panel_main            import GEOTG_PT_main_panel
from .operators.op_build_height  import OP_OT_build_height
from .operators.op_area_load     import OP_OT_load_area
from .operators.op_area_displace import OP_OT_displace_area
from .operators.op_fetch_trees import OP_OT_fetch_trees
from .operators.op_create_flight_curve import OP_OT_create_flight_curve
from .operators.op_camera_tools import OP_OT_spawn_camera, OP_OT_recalc_camera_anim
from .operators.op_osm_load_classes import GEOTG_OT_load_osm_classes
from .operators.op_osm_fetch_class import GEOTG_OT_fetch_osm_class
from .operators.op_osm_roads_rivers import GEOTG_OT_fetch_osm_roads_rivers
from .operators.op_import_dem_geotiff import OP_OT_import_dem_geotiff

import os, sys
sys.dont_write_bytecode = True 
lib_dir = os.path.join(os.path.dirname(__file__), "libs")
if (lib_dir not in sys.path):
    sys.path.append(lib_dir)

# ──────────────────────────────────────────────
# 2.  Список классов для регистрации
# ──────────────────────────────────────────────

classes = (GeoTG_Preferences,
           OP_OT_fetch_tiles,
           OP_OT_load_area,
           OP_OT_displace_area,
           OP_OT_fetch_trees,
           OP_OT_create_flight_curve,
           OP_OT_spawn_camera,
           OP_OT_recalc_camera_anim,
           GEOTG_PT_main_panel,
           GEOTG_OT_load_osm_classes,
           GEOTG_OT_fetch_osm_class,
           GEOTG_OT_fetch_osm_roads_rivers,
           OP_OT_import_dem_geotiff,
)


def register():
    print("[Geo-Terrain Generator] Аддон перезагружен")
    from .ui.panel_settings import GEOTG_PT_render_outputs
    from .operators.op_render_outputs import (
        GEOTG_OT_render_object_index,
        GEOTG_OT_render_material_index,
        GEOTG_OT_render_depth,
    )
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(GEOTG_PT_render_outputs)
    bpy.utils.register_class(GEOTG_OT_render_object_index)
    bpy.utils.register_class(GEOTG_OT_render_material_index)
    bpy.utils.register_class(GEOTG_OT_render_depth)
    bpy.types.Scene.geotg_flight_curve_type = bpy.props.EnumProperty(
        name="Curve Type",
        description="Type of flight trajectory",
        items=[
            ('STRAIGHT', "Straight Path", ""),
            ('CIRCLE', "Circular Path", ""),
            ('SNAKE', "Snake (serpentine)", ""),
            ('SPIRAL', "Spiral", ""),
            ('CUSTOM', "Custom Curve", "")
        ],
        default='STRAIGHT'
    )
    bpy.types.Scene.geotg_flight_height = bpy.props.FloatProperty(
        name="Flight Height (m)",
        description="Camera flight height in meters",
        default=50.0,
        min=1.0,
        max=1000.0
    )
    bpy.types.Scene.geotg_camera_preset = bpy.props.EnumProperty(
        name="Camera Preset",
        description="Type of camera for the flight",
        items=[
            ("DJI_X7", "DJI X7 (APS-C)", ""),
            ("SONY_RX0", "Sony RX0 II (1.0\")", ""),
            ("CUSTOM", "Custom", "")
        ],
        default='DJI_X7'
    )
    bpy.types.Scene.geotg_camera_frames = bpy.props.IntProperty(
        name="Frames",
        description="Number of animation frames",
        default=200,
        min=10,
        max=10000
    )
    bpy.types.Scene.geotg_camera_pitch = bpy.props.FloatProperty(
        name="Pitch (deg)",
        description="Camera tilt angle (degrees from vertical)",
        default=0.0,
        min=-90.0,
        max=90.0
    )
    # Свойства для OSM классов
    bpy.types.Scene.geotg_selected_osm_class = bpy.props.StringProperty(
        name="OSM Class",
        description="Selected OSM class for loading",
        default=""
    )
    # geotg_osm_classes хранится как список в scene['geotg_osm_classes']
    # Для EnumProperty используем динамический items
    def osm_classes_items(self, context):
        items = []
        classes = context.scene.get('geotg_osm_classes', [])
        for i, c in enumerate(classes):
            items.append((c, c, "", i))
        return items or [("", "(нет)", "", 0)]
    bpy.types.Scene.geotg_selected_osm_class = bpy.props.EnumProperty(
        name="OSM Class",
        description="Selected OSM class for loading",
        items=osm_classes_items
    )
    bpy.types.Scene.geotg_render_object_index = bpy.props.BoolProperty(
        name="Render Object Index", default=False)
    bpy.types.Scene.geotg_render_material_index = bpy.props.BoolProperty(
        name="Render Material Index", default=False)
    bpy.types.Scene.geotg_render_depth = bpy.props.BoolProperty(
        name="Render Depth", default=False)
    bpy.types.Scene.geotg_dem_source = bpy.props.EnumProperty(
        name="DEM Source",
        description="Source of elevation data",
        items=[
            ("API", "Online API", "Use online elevation API"),
            ("GEOTIFF", "GeoTIFF file", "Use local GeoTIFF file")
        ],
        default="API"
    )
    bpy.types.Scene.geotg_dem_geotiff_path = bpy.props.StringProperty(
        name="GeoTIFF Path",
        description="Path to GeoTIFF DEM file",
        subtype='FILE_PATH',
        default=""
    )

def unregister():
    from .ui.panel_settings import GEOTG_PT_render_outputs
    from .operators.op_render_outputs import (
        GEOTG_OT_render_object_index,
        GEOTG_OT_render_material_index,
        GEOTG_OT_render_depth,
    )
    bpy.utils.unregister_class(GEOTG_PT_render_outputs)
    bpy.utils.unregister_class(GEOTG_OT_render_object_index)
    bpy.utils.unregister_class(GEOTG_OT_render_material_index)
    bpy.utils.unregister_class(GEOTG_OT_render_depth)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.geotg_flight_curve_type
    del bpy.types.Scene.geotg_flight_height
    del bpy.types.Scene.geotg_camera_preset
    del bpy.types.Scene.geotg_camera_frames
    del bpy.types.Scene.geotg_camera_pitch
    if hasattr(bpy.types.Scene, 'geotg_selected_osm_class'):
        del bpy.types.Scene.geotg_selected_osm_class
    del bpy.types.Scene.geotg_render_object_index
    del bpy.types.Scene.geotg_render_material_index
    del bpy.types.Scene.geotg_render_depth
    del bpy.types.Scene.geotg_dem_source
    del bpy.types.Scene.geotg_dem_geotiff_path
