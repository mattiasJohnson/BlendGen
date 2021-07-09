import bpy
import sys
import datetime
import os

def importProp(prop_path):
    # Append objects to blend file's data (not linked to scene)
    with bpy.data.libraries.load(prop_path) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects]
        print('Appended objects: ', data_to.objects)

    # Link objects (objects have to be linked to show up in the scene)
    for obj in data_to.objects:
        bpy.context.collection.objects.link(obj)

    # Delete non-meshes (Cameras, light sources etc)
    bpy.ops.object.select_all(action='DESELECT')
    objs_to_join = []
    for obj in data_to.objects:
        if obj.type == "MESH":
            objs_to_join.append(obj)
        else:
            obj.select_set(True)
    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')

    # JOIN OBJECTS  
    ## Get a context
    ctx = bpy.context.copy()
    ## One of the objects to join (have to have a active selection)
    ctx['active_object'] = objs_to_join[0]
    ## Select all objects to join
    ctx['selected_editable_objects'] = objs_to_join

    # Join
    bpy.ops.object.join(ctx)

    # Rename and get reference to joined object
    imported_obj = bpy.data.objects[objs_to_join[0].name] # Has inherited active obj's name
    imported_obj.name = "imported_obj"

    # Resize prop
    imported_obj.dimensions = imported_obj.dimensions/max(imported_obj.dimensions)

    return imported_obj

def render(resolution=[512,512]):

        # Setup camera
        bpy.context.scene.camera = bpy.data.objects["Camera"] # Set camera as render camera
        bpy.context.scene.render.resolution_x = resolution[0] # Set resolution width
        bpy.context.scene.render.resolution_y = resolution[1] # Set resolution height

        # Save path
        render_base_path = bpy.path.abspath("//../renders/")

        ## Create render directory -> e.g: render023_current_datetime
        subfolders = [ f.name for f in os.scandir(render_base_path) if f.is_dir() ]
        max_num = 0
        for folder in subfolders:
            if folder[0:6] == "render":
                num_string = folder[6:9].lstrip('0')
                num = int(num_string)
                if num > max_num:
                    max_num = num
        render_num = max_num + 1
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        render_path = f"{render_base_path}render{render_num:03d}_{current_date}"
        os.mkdir(render_path)

        ## Generate savepath
        filepath = render_path + "/" + "test.png"

        ## Set savepath
        bpy.context.scene.render.filepath = filepath
 

        # Render image
        bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    # Get all arguments after --
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]

    # Get prop path
    dir_path = bpy.path.abspath("//../")
    prop_path_rel = argv[0]
    prop_path = dir_path + prop_path_rel

    # Import prop
    imported_obj = importProp(prop_path)

    # Render
    render()
