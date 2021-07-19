import bpy
import random
import os



def deleteScene():
    for obj in bpy.context.scene.objects: 
        if obj.name[-1].isdigit() == True: 
            obj.select_set(True)
        else: 
            obj.select_set(False)

    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')
    
    
def getRandomCoordinates(x_range, y_range, z_range):
    x = random.uniform(x_range[0], x_range[1])
    y = random.uniform(y_range[0], y_range[1])
    z = random.uniform(z_range[0], z_range[1])
    return (x, y, z)


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
    
    
