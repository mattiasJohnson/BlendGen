import bpy

import sys
import os
import mathutils
import random
import math
from math import sin, cos
import importlib

import numpy

from .blender_objects import Camera, Grid, Light
from .utils import createSegmentationMaterial, deleteScene, importProp, createRenderDirectory, newScene
from .render import render


def generate(prop_paths, save_path, n_images, n_instances):
    prop_path = list(prop_paths.values())[0]
    render_directory = os.path.join(save_path, "renders")
    
    newScene() 
    
    light = Light("test_light")
    light.data.energy = 80

    light2 = Light("test_light_2")
    light2.data.energy = 80
    light2.move_rel_cartesian((3,1,0))

    # Import prop
    imported_obj = None
    try:
        imported_obj = importProp(prop_path)
    except OSError:
        print()
        print("FILE NOT FOUND ERROR")
        print(f"File {prop_path} does not exist, quitting.")
        quit()

    # Create grid of objects
    createSegmentationMaterial(n_instances)
    grid = Grid(n_instances)
    grid.populate([imported_obj.name], n_instances)

    # Render
    camera = Camera("test_camera")
    
    render(render_directory, camera, grid, n_images=n_images)
