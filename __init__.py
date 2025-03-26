"""Symple (symmetry groups) --- © Martín Torres Valverde 2025. 

Add objects with tetrahedric, octahedric, icosahedric and other forms
of symmetry, as a more general mirror / array modifier. The method
used is to duplicate the objects but not their data.

Usage in Blender:
* Object mode > A(dd) > Symmetry group
* Object mode > Right click > Symmetry group from object

"""
import os as _os

import bpy
import importlib as _importlib

from . import addon_add_object
from . import translations
_importlib.reload(addon_add_object)
_importlib.reload(translations)


ADDON_FOLDER_PATH = _os.path.dirname(__file__)


# Registration

def register():
    #print(f"Enabling {__package__}")
    addon_add_object.register()
    bpy.utils.register_preset_path(ADDON_FOLDER_PATH)
    bpy.app.translations.register(__package__, translations.translations_dict)


def unregister():
    #print(f"Disabling {__package__}")
    addon_add_object.unregister()
    bpy.utils.unregister_preset_path(ADDON_FOLDER_PATH)
    bpy.app.translations.unregister(__package__)


if __name__ == "__main__":
    register()
