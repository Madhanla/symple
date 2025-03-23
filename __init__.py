"""Symple (symmetry groups) --- © Martín Torres Valverde 2025. 

Add objects with tetrahedric, hexaedric, icosahedric and other forms
of symmetry, as a more general mirror / array modifier.

Usage in Blender:
* Object mode > A(dd) > Symmetry group
* Object mode > Right click > Symmetry group from object

"""
import os as _os

import bpy.utils
import importlib as _importlib

from . import addon_add_object
_importlib.reload(addon_add_object)


ADDON_FOLDER_PATH = _os.path.dirname(__file__)


# Registration

def register():
    print(f"Enabling {__package__}")
    addon_add_object.register()
    bpy.utils.register_preset_path(ADDON_FOLDER_PATH)


def unregister():
    print(f"Disabling {__package__}")
    addon_add_object.unregister()
    bpy.utils.unregister_preset_path(ADDON_FOLDER_PATH)


if __name__ == "__main__":
    register()
