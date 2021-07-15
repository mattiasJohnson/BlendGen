import bpy
import sys
import datetime
import os
import mathutils
import random
import math

def importProp(prop_path):
    # Append objects to blend file's data (not linked to scene)
    with bpy.data.libraries.load(prop_path) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects]
        print('Appended objects: ', data_to.objects)

    # Link objects (objects have to be linked to show up in the scene)
    #for obj in data_to.objects:
    #    bpy.context.collection.objects.link(obj)

    # Delete non-meshes (Cameras, light sources etc)
    bpy.ops.object.select_all(action='DESELECT')
    objs_to_join = []
    for obj in data_to.objects:
        if obj.type == "MESH":
            objs_to_join.append(obj)
        else:
            bpy.context.collection.objects.link(obj) # Link object to select and delete
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
    
class Prop(BlenderObject):
    def __init__(self, name_to_copy):
        # Create copy
        copy_obj = bpy.data.objects[name_to_copy]
        obj = copy_obj.copy()
        obj.data = copy_obj.data.copy()

        # Add to scene
        bpy.context.collection.objects.link(obj)
        
        # Initialise
        BlenderObject.__init__(self, obj)
        self.randomRotate()

    def randomRotate(self):
        x = random.random()*2*math.pi
        y = random.random()*2*math.pi
        z = random.random()*2*math.pi

        self.obj.rotation_mode = "XYZ"
        self.obj.rotation_euler = (x,y,z)



def createCamera():
    obj = bpy.data.objects["Camera"]
    camera = Camera(obj)
    return camera

def getRandomCoordinates(x_range, y_range, z_range):
    x = random.uniform(x_range[0], x_range[1])
    y = random.uniform(y_range[0], y_range[1])
    z = random.uniform(z_range[0], z_range[1])
    return (x, y, z)

def render(render_directory, camera, n_images=1, resolution=[350,350]):

        # Setup camera
        bpy.context.scene.camera = camera.obj # Set camera as render camera
        bpy.context.scene.render.resolution_x = resolution[0] # Set resolution width
        bpy.context.scene.render.resolution_y = resolution[1] # Set resolution height

        for i in range(n_images):
            # Randomize camera position and direction
            camera_coordinates = getRandomCoordinates((-4,4), (-4,4), (4,5))
            look_coordinates = getRandomCoordinates((-2,2), (-2,2), (-4,-1))
            camera.setPos(camera_coordinates)
            camera.lookAt(look_coordinates)

            ## Setup savepath
            filename = f"render{i+1:03}.png"
            filepath = render_directory + "/" + filename
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
        prop_list = []
        for i in range(5):
            prop = Prop(imported_obj.name)
            prop.setPos((i,i,0))

    except OSError:
        print()
        print("FILE NOT FOUND ERROR")
        print(f"File {prop_path_rel} does not exist, quitting.")
        quit()


    # Render
    camera = createCamera()
    render_directory = createRenderDirectory(prop_name=prop_name, folder_name=folder_name)
    render(render_directory, camera, n_images=n_images)
