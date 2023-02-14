import bpy
import os
import sys
from .utils import redirectOutputStart, redirectOutputEnd, printProgressBar


def render(render_directory, camera, grid, n_images=1, resolution=[350, 350]):

    # Setup camera
    bpy.context.scene.camera = camera.object  # Set camera as render camera
    bpy.context.scene.render.resolution_x = resolution[0]  # Set resolution width
    bpy.context.scene.render.resolution_y = resolution[1]  # Set resolution height

    print()
    print(f"Generating {n_images} renders in {render_directory}.")
    printProgressBar(0, n_images, prefix="Progress:", suffix="Complete", length=50)

    for i in range(n_images):
        # Randomize camera position and direction

        #         camera.moveRandomSphere(grid.center, grid.distance_to_edge, grid.distance_to_edge*1.1)
        camera.move_abs_spherical_random(grid.center, grid.distance_to_edge * 1.8, grid.distance_to_edge * 2.2)
        camera.look_at(grid.center)

        ## Setup savepath
        filename = f"render{i+1:03}.png"
        filepath = render_directory + "/" + filename
        bpy.context.scene.render.filepath = filepath

        # Redirect output to log file
        old = redirectOutputStart()

        # Render image
        bpy.ops.render.render(write_still=True)

        # Segmentation
        for prop in grid.prop_list:
            prop.setMaterial("segmentation_material")
        segmentation_filename = f"render{i+1:03}_segmentation.png"
        segmentation_filepath = render_directory + "/" + segmentation_filename
        bpy.context.scene.render.filepath = segmentation_filepath
        bpy.ops.render.render(write_still=True)

        # Disable output redirection
        redirectOutputEnd(old)

        # Restore materials
        for prop in grid.prop_list:
            prop.restoreMaterial()

        printProgressBar(i + 1, n_images, prefix="Progress:", suffix="Complete", length=50)
