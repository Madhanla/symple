"""Rotate the mesh 60º around the Z axis"""
import bpy
from math import pi
op = bpy.context.active_operator

op.signature = '332'
op.extra_rotation = (0,0,pi/3)

