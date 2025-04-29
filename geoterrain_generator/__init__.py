bl_info = {
    "name": "Geo-Terrain Generator",
    "author": "Your Name",
    "version": (0, 1, 0.001),
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

# ──────────────────────────────────────────────
# 2.  Список классов для регистрации
# ──────────────────────────────────────────────
...
classes = (GeoTG_Preferences,
           OP_OT_fetch_tiles,
           OP_OT_build_height,      # ← новая строка
           GEOTG_PT_main_panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
