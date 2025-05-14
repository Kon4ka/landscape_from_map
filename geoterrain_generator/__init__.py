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
           GEOTG_PT_main_panel)


def register():
    print("[Geo-Terrain Generator] Аддон перезагружен")
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.geotg_flight_curve_type = bpy.props.EnumProperty(
        name="Тип кривой",
        description="Тип траектории пролёта",
        items=[
            ('STRAIGHT', "Прямолинейный проход", ""),
            ('CIRCLE', "Круговой облёт", ""),
            ('SNAKE', "Змейка (серпантин)", ""),
            ('SPIRAL', "Спираль", ""),
            ('CUSTOM', "Произвольная кривая", "")
        ],
        default='STRAIGHT'
    )
    bpy.types.Scene.geotg_flight_height = bpy.props.FloatProperty(
        name="Высота (м)",
        description="Высота пролёта камеры в метрах",
        default=50.0,
        min=1.0,
        max=1000.0
    )
    bpy.types.Scene.geotg_camera_preset = bpy.props.EnumProperty(
        name="Camera Preset",
        description="Тип камеры для пролёта",
        items=[
            ("DJI_X7", "DJI X7 (APS-C)", ""),
            ("SONY_RX0", "Sony RX0 II (1.0\")", ""),
            ("CUSTOM", "Custom", "")
        ],
        default='DJI_X7'
    )
    bpy.types.Scene.geotg_camera_frames = bpy.props.IntProperty(
        name="Frames",
        description="Количество кадров анимации",
        default=200,
        min=10,
        max=10000
    )
    bpy.types.Scene.geotg_camera_pitch = bpy.props.FloatProperty(
        name="Pitch (deg)",
        description="Угол наклона камеры (градусы от вертикали)",
        default=0.0,
        min=-90.0,
        max=90.0
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.geotg_flight_curve_type
    del bpy.types.Scene.geotg_flight_height
    del bpy.types.Scene.geotg_camera_preset
    del bpy.types.Scene.geotg_camera_frames
    del bpy.types.Scene.geotg_camera_pitch
