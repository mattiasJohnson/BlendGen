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
    
    
    resolution = (400, 400)
    bpy.context.scene.render.resolution_x = resolution[0] # Set resolution width
    bpy.context.scene.render.resolution_y = resolution[1] # Set resolution height

    
    
    
    light = Light("test_light")
    light.data.energy = 80

    light2 = Light("test_light_2")
    light2.data.energy = 80
    light2.move_rel_cartesian((3,1,0))

    # Import prop
#     imported_obj = None
#     try:
    imported_obj = importProp(prop_path)
#     except OSError:
#         print()
#         print("FILE NOT FOUND ERROR")
#         print(f"File {prop_path} does not exist, quitting.")
#         quit()

    # Create grid of objects
    createSegmentationMaterial(n_instances)
    grid = Grid(n_instances)
    grid.populate([imported_obj.name], n_instances)

    # Render
    camera = Camera("test_camera")
    
    render(render_directory, camera, grid, n_images=n_images, resolution=resolution)

    
    
    
# def setup_scene(prop_templates, num_props):

#     print("\n--------------------")
#     bg.newScene()
#     resolution = (400, 400)
    
#     # Setup camera
#     camera = bg.Camera("my_camera")
#     camera.rotate((90,0,0))
#     camera.move_abs_cartesian((0,-5,0))
    
    
#     angles_of_view = camera.get_angles_of_view(resolution)

 
#     for i in range(num_props):
#         prop_name = random.choice(list(prop_templates.values())) 
#         prop = bg.Prop(prop_name)
#         point = camera.get_random_visible_point(angles_of_view, 5, 8, resolution)
#         prop.move_abs_cartesian(point)
#         #prop.rotate_random()
