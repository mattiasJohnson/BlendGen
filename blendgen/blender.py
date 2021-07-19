import bpy
import sys
import datetime
import os
import mathutils
import random
import math
from math import sin, cos
import importlib


import sys, os
print("--------------",os.path.dirname(sys.executable))


import numpy



# dir = os.path.dirname(bpy.data.filepath)
# if not dir in sys.path:
#     sys.path.append(dir)

import utils
import blender_objects
import render

importlib.reload(utils)
importlib.reload(blender_objects)

from blender_objects import Camera, Prop, Grid
from utils import deleteScene, importProp, createRenderDirectory
from render import render


def run(prop_name, n_images, n_instances, folder_name):
    
    deleteScene()
    # Fix prop path for import
    prop_path_rel = "props/" + prop_name
    if prop_path_rel[-6:] != ".blend":
        prop_path_rel = prop_path_rel + ".blend"
    dir_path = bpy.path.abspath("//../")
    prop_path = dir_path + prop_path_rel

    # Import prop
    imported_obj = None
    try:
        imported_obj = importProp(prop_path)
    except OSError:
        print()
        print("FILE NOT FOUND ERROR")
        print(f"File {prop_path_rel} does not exist, quitting.")
        quit()

    # Create grid of objects
    grid = Grid(n_instances)
    grid.populate([imported_obj.name], 1)

    # Render
    camera = Camera("test_camera")
    
#     camera = createCamera()
    render_directory = createRenderDirectory(prop_name=prop_name, folder_name=folder_name)
    render(render_directory, camera, grid, n_images=n_images)

if __name__ == "__main__":
    # Get all arguments after --
    argv = sys.argv[sys.argv.index("--") + 1:]
    prop_name = argv[0]
    n_images = int(argv[1])
    n_instances = int(argv[2])
    folder_name = argv[3] if len(argv) >=4 else None
    
    run(prop_name, n_images, n_instances, folder_name)