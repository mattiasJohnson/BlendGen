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


def generate(prop_path, n_images, n_instances, render_directory):
    
    newScene() 
    
    light = Light("test_light")

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
