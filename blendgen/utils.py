import bpy
import random
import os
import datetime
import sys


def newScene():
    bpy.ops.scene.new(type="EMPTY") 


def deleteScene():
    for obj in bpy.context.scene.objects: 
        obj.select_set(True)

    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')
    
    
def getRandomCoordinates(x_range, y_range, z_range):
    x = random.uniform(x_range[0], x_range[1])
    y = random.uniform(y_range[0], y_range[1])
    z = random.uniform(z_range[0], z_range[1])
    return (x, y, z)


def importProp(prop_path):
    old = redirectOutputStart()
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
    
    redirectOutputEnd(old)

    return imported_obj

def createSegmentationMaterial(n_instances: int) -> bpy.types.Material:
    
    if n_instances >= 32:
        print("ERROR: Colorband cannot have 32 or more classes, setting to 31")
        n_instances = 31

    # Create material
    material = bpy.data.materials.new("segmentation_material")
    material["is_auto"] = True
    material.use_nodes = True

    # Nodes
    nodes = material.node_tree.nodes
    nodes.clear()
    step_size = 1/n_instances
    sep = 3 # Visual separation

    # Object Info node
    node_info = material.node_tree.nodes.new("ShaderNodeObjectInfo")
    node_info.location = (-300 * sep, 100)

    # Value node
    node_value = material.node_tree.nodes.new("ShaderNodeValue")
    node_value.location = (-300 * sep, -100)
    node_value.outputs[0].default_value = step_size

    # Math node
    node_math = material.node_tree.nodes.new("ShaderNodeMath")
    node_math.location = (-200 * sep, 0)
    node_math.operation = 'MULTIPLY_ADD'
    node_math.inputs[2].default_value = step_size/2

    # ColorRamp node
    node_ramp = material.node_tree.nodes.new("ShaderNodeValToRGB")
    node_ramp.location = (-100 * sep, 0)
    node_ramp.color_ramp.color_mode = 'RGB'
    node_ramp.color_ramp.interpolation = 'CONSTANT'
    # Split ColorRamp
    step_size = 1/n_instances
    for i in range(1,n_instances): # For three objects **two** splits are needed
        node_ramp.color_ramp.elements.new(step_size*i)
        
    for i in range(0,n_instances):
        node_ramp.color_ramp.elements[i].color = (random.random(), random.random(), random.random(), 1)

    # Shader node
    node_shader = nodes.new('ShaderNodeEmission')
    node_shader.location = (0,0)

    # Material Output node
    node_output = nodes.new("ShaderNodeOutputMaterial")
    node_output.location = (100*sep,0)

    # Create connections between nodes
    material.node_tree.links.new(node_info.outputs['Object Index'], node_math.inputs[0] )
    material.node_tree.links.new(node_value.outputs['Value'], node_math.inputs[1] )
    material.node_tree.links.new(node_math.outputs['Value'], node_ramp.inputs['Fac'])
    material.node_tree.links.new(node_ramp.outputs['Color'], node_shader.inputs['Color'])
    material.node_tree.links.new(node_shader.outputs['Emission'], node_output.inputs['Surface'])
    
    return material

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
    
    
# Redirect output (https://blender.stackexchange.com/a/44563/69661)
def redirectOutputStart():
    logfile = '.blenderlog'
    open(logfile, 'a').close()
    old = os.dup(1)
    sys.stdout.flush()
    os.close(1)
    os.open(logfile, os.O_WRONLY)
    return old

def redirectOutputEnd(old) -> None:
    os.close(1)
    os.dup(old)
    os.close(old)
    
# Print iterations progress (https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)
def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()