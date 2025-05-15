import bpy

class OP_OT_recalc_camera_anim(bpy.types.Operator):
    bl_idname = "geotg.recalc_camera_anim"
    bl_label = "Recalculate Camera Animation"
    bl_description = "Recalculate camera animation along the trajectory and limit the timeline"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cam = context.active_object
        if not cam or cam.type != 'CAMERA':
            self.report({'ERROR'}, "Select a camera object!")
            return {'CANCELLED'}
        # Find Follow Path constraint
        follow = next((c for c in cam.constraints if c.type == 'FOLLOW_PATH'), None)
        if not follow or not follow.target:
            self.report({'ERROR'}, "Camera is not linked to a curve!")
            return {'CANCELLED'}
        curve = follow.target
        frames = context.scene.geotg_camera_frames
        # Limit the timeline
        context.scene.frame_start = 1
        context.scene.frame_end = frames
        # Animate offset (old method, for compatibility)
        if hasattr(follow, 'offset_factor'):
            follow.use_fixed_location = True
            cam.data.animation_data_clear()
            follow.offset_factor = 0.0
            follow.keyframe_insert(data_path="offset_factor", frame=1)
            follow.offset_factor = 1.0
            follow.keyframe_insert(data_path="offset_factor", frame=frames)
        else:
            # For older versions of Blender, use offset
            follow.offset = 0
            follow.keyframe_insert(data_path="offset", frame=1)
            follow.offset = 100
            follow.keyframe_insert(data_path="offset", frame=frames)
        # Apply Follow Path animation
        if hasattr(curve.data, 'use_path'):  # For NURBS/Path
            curve.data.use_path = True
            curve.data.path_duration = frames
        # Do not touch rotation_euler (camera rotation)
        self.report({'INFO'}, f"Camera animation recalculated for {frames} frames and linked to the curve")
        return {'FINISHED'}
