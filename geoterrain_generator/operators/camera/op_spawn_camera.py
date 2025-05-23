import bpy
import math
from .presets import CAMERA_PRESETS, CAMERA_PRESET_PARAMS

# Камерные пресеты с параметрами
CAMERA_PRESET_PARAMS = {
    "DJI_X7": {
        "resolution": (6016, 4000),
        "sensor_width": 23.5,
        "sensor_height": 15.7,
        "pixel_size": 3.91,
        "focal_length": 24.0,  # по умолчанию
        "shutter_type": 'MECHANICAL',
        "pitch_deg": 0.0,
    },
    "PHASE_ONE_IXM100": {
        "resolution": (11608, 8708),
        "sensor_width": 43.9,
        "sensor_height": 32.9,
        "pixel_size": 3.76,
        "focal_length": 50.0,
        "shutter_type": 'LEAF',
        "pitch_deg": 0.0,
    },
    "SONY_ILX_LR1": {
        "resolution": (9504, 6336),
        "sensor_width": 35.6,
        "sensor_height": 23.8,
        "pixel_size": 3.76,
        "focal_length": 35.0,
        "shutter_type": 'MECHANICAL',
        "pitch_deg": 0.0,
    },
    "CUSTOM": {
        # Пользователь задаёт вручную
    }
}

class OP_OT_spawn_camera(bpy.types.Operator):
    bl_idname = "geotg.spawn_camera"
    bl_label = "Spawn Camera"
    bl_description = "Create a camera at the start of the trajectory with the selected preset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preset = context.scene.geotg_camera_preset
        params = CAMERA_PRESET_PARAMS.get(preset, CAMERA_PRESET_PARAMS["DJI_X7"])
        curve = context.active_object
        if not curve or curve.type != 'CURVE':
            self.report({'ERROR'}, "Select a trajectory curve!")
            return {'CANCELLED'}
        # Создать камеру
        cam_data = bpy.data.cameras.new("GeoTG_Camera")
        cam_obj = bpy.data.objects.new("GeoTG_Camera", cam_data)
        context.collection.objects.link(cam_obj)
        # Параметры камеры
        if 'sensor_width' in params:
            cam_data.sensor_width = params['sensor_width']
        if 'sensor_height' in params:
            cam_data.sensor_height = params['sensor_height']
        if 'focal_length' in params:
            cam_data.lens = params['focal_length']
        # Установить разрешение рендера по пресету (делим на 4)
        if 'resolution' in params:
            res_x, res_y = params['resolution']
            scene = context.scene
            scene.render.resolution_x = int(res_x // 4)
            scene.render.resolution_y = int(res_y // 4)
            scene.render.resolution_percentage = 200
        # Привязка к кривой (Follow Path)
        follow = cam_obj.constraints.new('FOLLOW_PATH')
        follow.target = curve
        follow.use_curve_follow = True  # Включаем автоматический поворот по кривой
        # Ограничение поворота камеры (фиксируем X и Y, разрешаем только Z)
        limit_rot = cam_obj.constraints.new('LIMIT_ROTATION')
        limit_rot.use_limit_x = True
        limit_rot.min_x = cam_obj.rotation_euler.x
        limit_rot.max_x = cam_obj.rotation_euler.x
        limit_rot.use_limit_y = True
        limit_rot.min_y = cam_obj.rotation_euler.y
        limit_rot.max_y = cam_obj.rotation_euler.y
        limit_rot.use_limit_z = False  # Z свободен
        limit_rot.owner_space = 'LOCAL'
        # Ставим в начало кривой
        cam_obj.location = (0.0, 0.0, 0.0)
        # Устанавливаем pitch из свойства сцены
        import math
        pitch_deg = context.scene.geotg_camera_pitch if hasattr(context.scene, 'geotg_camera_pitch') else 0.0
        cam_obj.rotation_euler = (math.radians(90 + pitch_deg), 0, 0)
        # Анимируем движение по кривой (Animate Path)
        # Вручную задаём ключи для offset_factor
        if hasattr(curve.data, 'use_path'):
            curve.data.use_path = True
            follow = next((c for c in cam_obj.constraints if c.type == 'FOLLOW_PATH'), None)
            if follow:
                frame_start = context.scene.frame_start
                frame_end = context.scene.frame_end
                follow.offset_factor = 0.0
                follow.keyframe_insert(data_path="offset_factor", frame=frame_start)
                follow.offset_factor = 1.0
                follow.keyframe_insert(data_path="offset_factor", frame=frame_end)
        # Выделить и сделать активной
        bpy.ops.object.select_all(action='DESELECT')
        cam_obj.select_set(True)
        context.view_layer.objects.active = cam_obj
        self.report({'INFO'}, f"Camera created and linked to curve ({preset}), render: {int(res_x//4)}x{int(res_y//4)} @200%")
        return {'FINISHED'}
