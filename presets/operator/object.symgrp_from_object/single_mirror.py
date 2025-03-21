import bpy
op = bpy.context.active_operator

op.signature = '*'
op.extra_rotation = (0,0,0)

