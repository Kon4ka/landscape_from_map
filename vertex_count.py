import bpy
import bmesh
import blf

handler = None

def get_unity_vertex_count(obj):
    if obj.type != 'MESH':
        return 0

    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.active

    seen = set()

    for face in bm.faces:
        for loop in face.loops:
            key = [loop.vert.index]

            if not face.smooth:
                key.append(face.index)

            if uv_layer:
                uv = loop[uv_layer].uv
                key.append(round(uv.x, 6))
                key.append(round(uv.y, 6))

            seen.add(tuple(key))

    return len(seen)

def draw_callback():
    context = bpy.context
    obj = context.active_object

    if not obj or context.mode != 'EDIT_MESH':
        return

    count = get_unity_vertex_count(obj)
    msg = f"Unity Vertex Count: {count}"

    font_id = 0
    blf.size(font_id, 16)

    text_width, text_height = blf.dimensions(font_id, msg)
    region = context.region

    if not region:
        return

    x = region.width - text_width - 20
    y = 20

    blf.position(font_id, x, y, 0)
    blf.color(font_id, 1, 1, 1, 1)
    blf.draw(font_id, msg)

def tag_redraw_all_view3d():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

def timer_redraw():
    tag_redraw_all_view3d()
    return 1.0

def register():
    global handler
    handler = bpy.types.SpaceView3D.draw_handler_add(draw_callback, (), 'WINDOW', 'POST_PIXEL')
    bpy.app.timers.register(timer_redraw)

def unregister():
    global handler
    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        handler = None
    bpy.app.timers.unregister(timer_redraw)
