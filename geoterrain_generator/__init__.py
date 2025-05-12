bl_info = {
    "name": "Geo-Terrain Generator",
    "author": "Your Name",
    "version": (0, 1, 0.002),
    "blender": (4, 0, 0),
    "location": "File > Import > Geo-Terrain",
    "description": "Generate small-area terrain from satellite imagery",
    "category": "Import-Export",
}

# ──────────────────────────────────────────────
# 1.  Импорт нужных классов напрямую
# ──────────────────────────────────────────────
import bpy
from .prefs                  import GeoTG_Preferences
from .operators.op_fetch_tiles import OP_OT_fetch_tiles
from .ui.panel_main            import GEOTG_PT_main_panel
from .operators.op_build_height  import OP_OT_build_height
from .operators.op_area_load     import OP_OT_load_area
from .operators.op_area_displace import OP_OT_displace_area
from .operators.op_fetch_trees import OP_OT_fetch_trees

import os, sys
sys.dont_write_bytecode = True 
lib_dir = os.path.join(os.path.dirname(__file__), "libs")
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

# ──────────────────────────────────────────────
# 2.  Список классов для регистрации
# ──────────────────────────────────────────────

classes = (GeoTG_Preferences,
           OP_OT_fetch_tiles,
           OP_OT_load_area,
           OP_OT_displace_area,
           OP_OT_fetch_trees,
           GEOTG_PT_main_panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
