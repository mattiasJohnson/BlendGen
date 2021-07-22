from typing import Tuple, List
import bpy
import mathutils
import random
import math
import numpy as np


class BlenderObject:
    """A superclass with utility functions for blender objects for use in more specific subclasses"""

    def __init__(self, name: str) -> None:
        self.name = name

    def get_loc(self):
        return self.object.location

    def set_loc(self, coo_cartesian: mathutils.Vector) -> None:
        self.object.location = coo_cartesian

    def move_rel_cartesian(self, coo_cartesian: Tuple[float]) -> None:
        self.set_loc(self.get_loc() + mathutils.Vector(coo_cartesian))

    def move_abs_cartesian(self, coo_cartesian: Tuple[float]) -> None:
        self.set_loc(mathutils.Vector(coo_cartesian))

    def move_rel_spherical(self, coo_spherical: Tuple[float]) -> None:
            r_diff, theta_diff, phi_diff = coo_spherical
            theta_diff = radians(theta_diff)
            phi_diff = radians(phi_diff)
            x, y, z = self.get_loc()
            r_prev = (x**2 + y**2 + z**2)**0.5
            r = r_prev + r_diff
            theta = atan2(y,x) + theta_diff
            phi = acos(z/r_prev) + phi_diff
            self.set_loc((r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)))

    def move_abs_spherical(self, coo_spherical: Tuple[float]) -> None:
            r, theta, phi = coo_spherical
            theta = radians(theta)
            phi = radians(phi)
            self.set_loc((r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)))

    def rotate(self, angles: Tuple[float]) -> None:
        self.object.rotation_mode = "XYZ"
        x, y, z = angles
        self.object.rotation_euler = (x, y, z)

    def move_abs_spherical_random(self, center, r_min, r_max) -> None:
        theta = random.random()*math.pi
        phi = random.random()*2*math.pi
        r = random.uniform(r_min, r_max)
        random_coordinate = np.array((r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)))
        new_coordinate = random_coordinate + np.array(center)
        self.move_abs_cartesian(new_coordinate)

    def rotate_random(self) -> None:
        x = random.random() * 2 * math.pi
        y = random.random() * 2 * math.pi
        z = random.random() * 2 * math.pi
        self.rotate((x, y, z))

    def look_at(self, point: Tuple[float]) -> None:
        point = mathutils.Vector(point)  
        look_direction = self.get_loc() - point
        self.object.rotation_mode = 'QUATERNION'
        self.object.rotation_quaternion = look_direction.to_track_quat('Z', 'Y')


class Camera(BlenderObject):
    def __init__(self, name: str, lens: float = 50) -> None:
        assert 1 <= lens <= float("inf")
        BlenderObject.__init__(self, name)

        self.data = bpy.data.cameras.new(self.name)
        self.object = bpy.data.objects.new(self.name, self.data)
        self.data.lens = lens
        self.move_abs_cartesian((0, 0, 0))
        bpy.context.scene.collection.objects.link(self.object) 
 
    def random_lens(self, span: float) -> None:
        length = random.uniform(span[0], span[1])
        self.setLens(length)        


class Light(BlenderObject):
    def __init__(self, name: str, position: Tuple[float] = (0,0,0), energy: float = 30) -> None:
        BlenderObject.__init__(self, name)

        self.data = bpy.data.lights.new(name=self.name, type='POINT')
        self.object = bpy.data.objects.new(self.name, self.data)

        self.data.energy = energy
        self.move_abs_cartesian(position)
        bpy.context.scene.collection.objects.link(self.object) 

    def random_energy(self, span: Tuple[float]) -> None:
        energy = np.random.rand() * (span[1] - span[0]) + span[0]
        self.setEnergy(energy)


class Prop(BlenderObject):
    def __init__(self, name: str) -> None:
        
        BlenderObject.__init__(self, name)
        template_object = bpy.data.objects[name] # object to duplicate
        self.object = template_object.copy()
        self.object.data= template_object.data.copy()
        bpy.context.collection.objects.link(self.object) # was need for adding it to the scene
        
        # Center origin
        bpy.ops.object.select_all(action='DESELECT')
        self.object.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.ops.object.select_all(action='DESELECT')
        
        # Initialise
        self.rotate_random()


class Grid:
    def __init__(self, n_spots: int) -> None:
        self.n_spots = n_spots
        self.side_length = 2
        self.distance_to_edge = math.sqrt(3) / 2 * self.side_length

        # Get number of spots per side 
        n_per_side = 1
        while n_spots > n_per_side**3:
            n_per_side += 1 
            
        # Create coordinate_list
        center_coordinate = ((n_per_side - 1) * self.side_length / 2)
        center = (center_coordinate, center_coordinate, center_coordinate)
        coordinate_list = []
        for i in range(n_per_side):
            for j in range(n_per_side):
                for k in range(n_per_side):
                    coordinate =  (self.side_length * i, self.side_length * j, self.side_length * k)
                    coordinate_list.append(coordinate)
        
        self.coordinate_list = coordinate_list
        self.center = center
        
    def populate(self, obj_name_list: List[str], density: float) -> None:
        for coordinate in self.coordinate_list:
            if random.random() < density:
                obj_name = random.choice(obj_name_list)
                prop = Prop(obj_name)
                prop.move_abs_cartesian(coordinate)
