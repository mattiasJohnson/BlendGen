import bpy
import sys
import datetime
import os
import mathutils

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

def createRenderDirectory(prop_name="", folder_name=None):

        # Create /renders base directory
        render_base_path = bpy.path.abspath("//../renders/")
        if not os.path.exists(render_base_path):
            os.makedirs(render_base_path)
        
        # Create render directory
        render_directory = ""
        if folder_name:
            render_directory = f"{render_base_path}{folder_name}"
        else:
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
            render_directory = f"{render_base_path}render{render_num:03d}_{prop_name}_{current_date}"
        
        # Confirm overwrite if directory already exists
        if os.path.exists(render_directory):
            while (answer :=input(f"Directory {folder_name}/ already exists, continue and overwrite? (Y/n): ").lower() ) not in {"y", "n", ""}: pass
            if answer == 'n':
                print("Quitting.")
                sys.exit(1)
        else:
            os.mkdir(render_directory)
            
        return render_directory

class BlenderObject:
    def __init__(self, obj):
        self.obj = obj

    def getPos(self):
        return self.obj.location
    
    def setPos(self, new_location):
        self.obj.location = new_location

class Camera(BlenderObject):
    def __init__(self, obj):
        BlenderObject.__init__(self, obj)

    def lookAt(self, position):
        position = mathutils.Vector(position)  
        look_direction = self.getPos() - position

        self.obj.rotation_mode = 'QUATERNION'
        self.obj.rotation_quaternion = look_direction.to_track_quat('Z', 'Y')

def createCamera():
    obj = bpy.data.objects["Camera"]
    camera = Camera(obj)
    return camera



def render(render_directory, camera, n_images=1, resolution=[350,350]):

        # Setup camera
        bpy.context.scene.camera = camera.obj # Set camera as render camera
        bpy.context.scene.render.resolution_x = resolution[0] # Set resolution width
        bpy.context.scene.render.resolution_y = resolution[1] # Set resolution height

        for i in range(n_images):
            camera.lookAt((0,0,-1+0.5*i))
            ## Generate filepath
            filename = f"render{i+1:03}.png"
            filepath = render_directory + "/" + filename
            ## Set savepath
            bpy.context.scene.render.filepath = filepath
            # Render image
            bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    # Get all arguments after --
    argv = sys.argv[sys.argv.index("--") + 1:]
    prop_name = argv[0]
    n_images = int(argv[1])
    folder_name = argv[2] if len(argv) >=3 else None

    # Fix prop path for import
    prop_path_rel = "props/" + prop_name
    if prop_path_rel[-6:] != ".blend":
        prop_path_rel = prop_path_rel + ".blend"
    dir_path = bpy.path.abspath("//../")
    prop_path = dir_path + prop_path_rel

    # Import prop
    try:
        imported_obj = importProp(prop_path)
    except OSError:
        print()
        print("FILE NOT FOUND ERROR")
        print(f"File {prop_path_rel} does not exist, quitting.")
        quit()


    # Render
    camera = createCamera()
    render_directory = createRenderDirectory(prop_name=prop_name, folder_name=folder_name)
    render(render_directory, camera, n_images=n_images)
