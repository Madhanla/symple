import bpy
import bpy.types
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from .simetrias import SymGrp, BadSymGrpError
from .utils import Vector


MODES = (
    ('TILE', "Tile",
     "Fundamental tile that makes a sphere when the group acts on it.",
     "MESH_ICOSPHERE", 0),
    ('AXES', "Axes",
     "Axes having each group element as rotation.",
     "EMPTY_AXIS", 1),
    ('OBJECT', "Object",
     "Active object.",
     "OBJECT_DATA", 2))
SIGNATURES =  (
        "", "1", "*", "x",
        "2*", "3*", "4*", "5*", "6*",
        "2x", "3x", "4x", "5x", "6x",
        "*532", "532",
        "*432", "432",
        "*332", "332",
        "*622", "622",
        "*522", "522",
        "*422", "422",
        "*322", "322",
        "*222", "222",
        "*22",  "22",
        "*33",  "33",
        "*44",  "44",
        "*55",  "55",
        "*66",  "66",
        "3*2",
        "2*2", "2*3", "2*4", "2*5", "2*6",
)


def add_symgrp(operator, context):
    """Add a fundamental tile with a specified symmetry group"""
    try:
        grp = SymGrp(operator.signature)
    except (BadSymGrpError, NotImplementedError) as e:
        operator.report(
            {'ERROR_INVALID_INPUT'},
            ": ".join((str(type(e).__name__), *e.args)))
        return
    
    match operator.mode:
        case 'TILE':
            verts, faces = grp.tile
            data = bpy.data.meshes.new('Tile')
            data.from_pydata(verts, (), faces)
            object_add_command = lambda: bpy.data.objects.new('Tile', data)
        case 'AXES':
            object_add_command = lambda: bpy.data.objects.new('Axis', None)
        case 'OBJECT':
            ao = context.active_object
            object_add_command = lambda: ao.copy()
            
    empty = object_data_add(context, None,
                            name = f"SymGrp {grp.signature}",
                            operator=operator)
    for axis, scale in grp:
        tile = object_add_command()
        context.collection.objects.link(tile)
        tile.empty_display_type = 'SINGLE_ARROW'
        tile.rotation_mode = 'QUATERNION'
        tile.rotation_quaternion = axis
        tile.location = Vector()
        tile.parent = empty
        tile.scale *= scale
        if operator.lock:
            for transform in "location", "rotation", "scale":
                setattr(tile, f"lock_{transform}", (True, True, True))
            tile.lock_rotation_w = True

    for obj in context.selected_objects:
        obj.select_set(False)
    empty.select_set(True)
    context.view_layer.objects.active = empty
        

def search_signature(operator, context, value):
    return (s for s in SIGNATURES
            if s.startswith(value))

# Class definitions

class SymGrpAdder(bpy.types.Operator, AddObjectHelper):
    """Create a new symmetry group"""
    signature: StringProperty(
        name = "Signature",
        default = "*432",
        description = "Orbifold signature",
        maxlen = 7,
        search = search_signature,
        #search_options = {"SORT"}, 
        translation_context = "SymGrp button",
    )
    lock : BoolProperty(
        name = "Lock transforms",
        description = "Lock position, scale and rotation to avoid breaking the symmetry",
        default = True,
        translation_context = "SymGrp button",
    )

    def execute(self, context):
        add_symgrp(self, context)
        return {'FINISHED'}


class OBJECT_OT_add_symgrp(SymGrpAdder):
    """Create a new symmetry group"""
    bl_idname = "object.add_symgrp"
    bl_label = "Symmetry group"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    mode : EnumProperty(
        name = "Mode",
        #default = 'TILE',
        translation_context = "SymGrp button",
        items = MODES[:-1],
    )


class OBJECT_OT_symgrp_from_object(SymGrpAdder):
    """Create a new symmetry group from the active object"""
    bl_idname = "object.symgrp_from_object"
    bl_label = "Symmetry group"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    mode : EnumProperty(
        name = "Mode",
        #default = 'TILE',
        translation_context = "SymGrp button",
        items = MODES
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

# Menus

def add_symgrp_menu(self, context):
    self.layout.operator_menu_enum(
        "object.add_symgrp", "mode",
        text="Symmetry group",
        icon='MOD_MIRROR',
    )


def symgrp_from_object_menu(self, context):
    self.layout.operator(
        "object.symgrp_from_object",
        text="Symmetry group from object",
        icon='MOD_MIRROR',
    ).mode = 'OBJECT'

# Registration
        
def register():
    bpy.utils.register_class(OBJECT_OT_add_symgrp)
    bpy.utils.register_class(OBJECT_OT_symgrp_from_object)
    bpy.types.VIEW3D_MT_add.append(add_symgrp_menu)
    bpy.types.VIEW3D_MT_object.append(symgrp_from_object_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(symgrp_from_object_menu)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_symgrp)
    bpy.utils.unregister_class(OBJECT_OT_symgrp_from_object)
    bpy.types.VIEW3D_MT_add.remove(add_symgrp_menu)
    bpy.types.VIEW3D_MT_object.remove(symgrp_from_object_menu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(symgrp_from_object_menu)


if __name__ == "__main__":
    register()
