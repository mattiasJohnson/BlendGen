import bpy
import sys
import datetime
import os
import mathutils
import random
import math
from math import sin, cos
import numpy as np

def importProp(prop_path):
    # Append objects to blend file's data (not linked to scene)
    with bpy.data.libraries.load(prop_path) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects]
        #print('Appended objects: ', data_to.objects)

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
        
    def moveRandomSphere(self, center, r_min, r_max):
        theta = random.random()*math.pi
        phi = random.random()*2*math.pi
        r = random.uniform(r_min, r_max)
        random_coordinate = np.array((r*sin(phi)*cos(theta), r*sin(phi)*sin(theta), r*cos(phi)))
        new_coordinate = random_coordinate + np.array(center)
        
        self.setPos(new_coordinate)

    
class Prop(BlenderObject):
    def __init__(self, name_to_copy, pass_index):
        # Create copy
        copy_obj = bpy.data.objects[name_to_copy]
        obj = copy_obj.copy()
        obj.data = copy_obj.data.copy()
        obj.pass_index = pass_index

        # Add to scene
        bpy.context.collection.objects.link(obj)
        
        # Center origin
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.ops.object.select_all(action='DESELECT')
        
        # Initialise
        BlenderObject.__init__(self, obj)
        self.randomRotate()

    def randomRotate(self):
        x = random.random()*2*math.pi
        y = random.random()*2*math.pi
        z = random.random()*2*math.pi

        self.obj.rotation_mode = "XYZ"
        self.obj.rotation_euler = (x,y,z)
        
    def setMaterial(self, material_name):
        for idx, mat in enumerate(self.obj.data.materials):
            self.obj.data.materials[idx] = bpy.data.materials.get(material_name)

class Grid:
    def __init__(self, n_spots):
        self.n_spots = n_spots
        self.side_length = 2
        self.distance_to_edge = math.sqrt(3)/2 * self.side_length

        # Get number of spots per side 
        n_per_side = 1
        while n_spots > n_per_side**3:
            n_per_side += 1 
            
        # Create coordinate_list
        center_coordinate = ((n_per_side-1)*self.side_length/2)
        center = (center_coordinate, center_coordinate, center_coordinate)
        coordinate_list = []
        for i in range(n_per_side):
            for j in range(n_per_side):
                for k in range(n_per_side):
                    coordinate =  (self.side_length * i, self.side_length* j, self.side_length * k)
                    coordinate_list.append(coordinate)
        
        self.coordinate_list = coordinate_list
        self.center = center
        
    def populate(self, obj_name_list, n_instances):
        for idx in range(n_instances):
            obj_name = random.choice(obj_name_list)
            coordinate = self.coordinate_list[idx]
            prop = Prop(obj_name, idx)
            prop.setMaterial("segmentation_material")
            prop.setPos(coordinate)
            
                
                
def createMaterial(n_instances):
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

def createCamera():
    obj = bpy.data.objects["Camera"]
    camera = Camera(obj)
    return camera

def getRandomCoordinates(x_range, y_range, z_range):
    x = random.uniform(x_range[0], x_range[1])
    y = random.uniform(y_range[0], y_range[1])
    z = random.uniform(z_range[0], z_range[1])
    return (x, y, z)

def render(render_directory, camera, grid, n_images=1, resolution=[350,350]):

        # Setup camera
        bpy.context.scene.camera = camera.obj # Set camera as render camera
        bpy.context.scene.render.resolution_x = resolution[0] # Set resolution width
        bpy.context.scene.render.resolution_y = resolution[1] # Set resolution height

        for i in range(n_images):
            # Randomize camera position and direction
            camera.moveRandomSphere(grid.center, grid.distance_to_edge*1.5, grid.distance_to_edge*2)
            camera.lookAt(grid.center)

            ## Setup savepath
            filename = f"render{i+1:03}.png"
            filepath = render_directory + "/" + filename
            bpy.context.scene.render.filepath = filepath

            # Render image
            bpy.ops.render.render(write_still=True)

def run(prop_name, n_images, n_instances, folder_name):
    # Fix prop path for import
    prop_path_rel = "props/" + prop_name
    if prop_path_rel[-6:] != ".blend":
        prop_path_rel = prop_path_rel + ".blend"
    dir_path = bpy.path.abspath("//../")
    prop_path = dir_path + prop_path_rel

    # Import prop
    imported_obj = None
    try:
        imported_obj = importProp(prop_path)
    except OSError:
        print()
        print("FILE NOT FOUND ERROR")
        print(f"File {prop_path_rel} does not exist, quitting.")
        quit()

    material = createMaterial(n_instances)

    # Create grid of objects
    grid = Grid(n_instances)
    grid.populate([imported_obj.name], n_instances)

    # Render
    camera = createCamera()
    render_directory = createRenderDirectory(prop_name=prop_name, folder_name=folder_name)
    render(render_directory, camera, grid, n_images=n_images)

if __name__ == "__main__":
    # Get all arguments after --
    argv = sys.argv[sys.argv.index("--") + 1:]
    prop_name = argv[0]
    n_images = int(argv[1])
    n_instances = int(argv[2])
    folder_name = argv[3] if len(argv) >=4 else None
    
    run(prop_name, n_images, n_instances, folder_name)