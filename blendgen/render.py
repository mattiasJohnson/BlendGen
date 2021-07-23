import bpy

def render(render_directory, camera, grid, n_images=1, resolution=[350,350]):

    # Setup camera
    bpy.context.scene.camera = camera.object # Set camera as render camera
    bpy.context.scene.render.resolution_x = resolution[0] # Set resolution width
    bpy.context.scene.render.resolution_y = resolution[1] # Set resolution height

    for i in range(n_images):
        # Randomize camera position and direction
        
#         camera.moveRandomSphere(grid.center, grid.distance_to_edge, grid.distance_to_edge*1.1)
        camera.move_abs_spherical_random(grid.center, grid.distance_to_edge, grid.distance_to_edge*1.1)
        camera.look_at(grid.center)

        ## Setup savepath
        filename = f"render{i+1:03}.png"
        filepath = render_directory + "/" + filename
        bpy.context.scene.render.filepath = filepath

        # Render image
        bpy.ops.render.render(write_still=True)