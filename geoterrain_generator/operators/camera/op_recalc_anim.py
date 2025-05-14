import bpy

class OP_OT_recalc_camera_anim(bpy.types.Operator):
    bl_idname = "geotg.recalc_camera_anim"
    bl_label = "Recalculate Camera Animation"
    bl_description = "Пересчитать анимацию камеры по траектории и ограничить таймлайн"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cam = context.active_object
        if not cam or cam.type != 'CAMERA':
            self.report({'ERROR'}, "Выделите объект-камеру!")
            return {'CANCELLED'}
        # Найти Follow Path constraint
        follow = next((c for c in cam.constraints if c.type == 'FOLLOW_PATH'), None)
        if not follow or not follow.target:
            self.report({'ERROR'}, "Камера не привязана к кривой!")
            return {'CANCELLED'}
        curve = follow.target
        frames = context.scene.geotg_camera_frames
        # Ограничить таймлайн
        context.scene.frame_start = 1
        context.scene.frame_end = frames
        # Анимировать offset (старый способ, для совместимости)
        if hasattr(follow, 'offset_factor'):
            follow.use_fixed_location = True
            cam.data.animation_data_clear()
            follow.offset_factor = 0.0
            follow.keyframe_insert(data_path="offset_factor", frame=1)
            follow.offset_factor = 1.0
            follow.keyframe_insert(data_path="offset_factor", frame=frames)
        else:
            # Для старых версий Blender используем offset
            follow.offset = 0
            follow.keyframe_insert(data_path="offset", frame=1)
            follow.offset = 100
            follow.keyframe_insert(data_path="offset", frame=frames)
        # Применить Follow Path animation
        if hasattr(curve.data, 'use_path'):  # Для NURBS/Path
            curve.data.use_path = True
            curve.data.path_duration = frames
        # Не трогаем rotation_euler (поворот камеры)
        self.report({'INFO'}, f"Анимация камеры пересчитана на {frames} кадров и привязана к кривой")
        return {'FINISHED'}
