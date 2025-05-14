import bpy

ADDON_ID = __name__.split('.')[0]

# Переадресация классов из подпапки camera
from .camera.op_spawn_camera import OP_OT_spawn_camera
from .camera.op_recalc_anim import OP_OT_recalc_camera_anim
from .camera.presets import CAMERA_PRESETS

# Оставляем только регистрацию

def register():
    bpy.utils.register_class(OP_OT_spawn_camera)
    bpy.utils.register_class(OP_OT_recalc_camera_anim)

def unregister():
    bpy.utils.unregister_class(OP_OT_spawn_camera)
    bpy.utils.unregister_class(OP_OT_recalc_camera_anim)
