"""Symple (symmetry groups) --- © Martín Torres Valverde 2025. 

Add objects with tetrahedric, hexaedric, icosahedric and other forms
of symmetry.

Usage in Blender:
* Object mode > A(dd) > Symmetry group
* Object mode > Right click > Symmetry group from object

"""
import sys as _sys
import os as _os
import warnings as _warnings

import bpy.utils
import importlib as _importlib

from . import addon_add_object
_importlib.reload(addon_add_object)


ADDON_FOLDER_PATH = _os.path.dirname(__file__)
VERSION = (0, 0, 3)
MODULE_NAME = "symple"
ADDON_NAME = "Symple (symmetry groups) v{}.{}.{}".format(*VERSION)


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
