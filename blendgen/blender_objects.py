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

    def rotate(self, angles: Tuple[float, float, float]) -> None:
        conv = np.pi / 180
        angles = [angles[0] * conv, angles[1] * conv, angles[2] * conv]
        self.rotate_radians(angles)
        
    def rotate_radians(self, angles: Tuple[float, float, float]) -> None:
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
        self.rotate_radians((x, y, z))

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
        
    def get_parameters(self, resolution):
        
        # Calculate intrinsic matrix
        assert bpy.context.scene.render.resolution_percentage == 100 # assume image is not scaled
        assert self.data.sensor_fit != 'VERTICAL' # assume angles describe the horizontal field of view
        f_in_mm = self.data.lens
        sensor_width_in_mm = self.data.sensor_width
        w = resolution[0]
        h = resolution[1]
        pixel_aspect = bpy.context.scene.render.pixel_aspect_y / bpy.context.scene.render.pixel_aspect_x
        f_x = f_in_mm / (sensor_width_in_mm / w)
        f_y = f_x * pixel_aspect
        c_x = w * (0.5 - self.data.shift_x)
        c_y = h * 0.5 + w * self.data.shift_y
        intrinsic = np.array([[f_x, 0, c_x],[0, f_y, c_y],[0,   0,   1]])
        
        extrinsic = np.array(self.object.matrix_world)

        return extrinsic, intrinsic
    
    def get_visible_quadron(self, min_radius: float, max_radius: float, resolution: Tuple[int, int]) -> np.ndarray:
        extrinsic, intrinsic = self.get_parameters(resolution)
        extrinsic_homogeneous = extrinsic[:3]
        inv_intrinsic_mult_extrinsic = np.linalg.pinv(np.matmul(intrinsic, extrinsic_homogeneous))
        corners_pixel = np.array([[0, 0], [0, resolution[1]], [resolution[0], 0], [resolution[0], resolution[1]]])

        corners = np.array([
            [self.get_3d_projection(inv_intrinsic_mult_extrinsic, corner_pixel, radius) for corner_pixel in corners_pixel]
            for radius in [min_radius, max_radius]
        ])

        return corners

    def get_3d_projection(self, inv_intrinsic_mult_extrinsic: np.ndarray, coo_pixel: np.ndarray, radius: float) -> np.ndarray:
        coo_pixel_homogeneous = np.append(coo_pixel, 1)
        coordinate_cartesian = radius * np.matmul(inv_intrinsic_mult_extrinsic, coo_pixel_homogeneous)[:3]
        return coordinate_cartesian
    
    def get_angles_of_view(self, resolution):
        radius = 10
        extrinsic, intrinsic = self.get_parameters(resolution)
        extrinsic_homogeneous = extrinsic[:3]
        inv_intrinsic_mult_extrinsic = np.linalg.pinv(np.matmul(intrinsic, extrinsic_homogeneous))
        point = self.get_3d_projection(inv_intrinsic_mult_extrinsic, resolution, radius)
        vertical_angle = np.tan(point[0]/radius)
        horizontal_angle = np.tan(point[1]/radius)

        return (vertical_angle, horizontal_angle)
    
    def get_random_visible_point(self, angles_of_view, min_radius, max_radius, resolution) -> np.ndarray:
        angle_vertical = random.uniform(-angles_of_view[0], angles_of_view[0])        
        angle_horizontal = random.uniform(-angles_of_view[1], angles_of_view[1])
        radius = random.uniform(min_radius, max_radius)
        
        coordinate_camera = np.array((
            np.arctan(angle_horizontal)*radius, 
            np.arctan(angle_vertical)*radius, 
            -radius,
        ))
        
        location, rotation = self.object.matrix_world.decompose()[0:2]
        location = np.array(location)
        rotation = -1 * np.array(rotation.to_matrix())
        
        coordinate_rotated = np.matmul(-1*rotation, coordinate_camera)
        coordinate_translated = coordinate_rotated + location

        return coordinate_translated


    


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
        self.data.energy = energy


class Prop(BlenderObject):
    def __init__(self, name: str, segmentation_idx: int = 0) -> None:
        
        BlenderObject.__init__(self, name)
        self.template_object = bpy.data.objects[name] # object to duplicate
        self.object = self.template_object.copy()
        self.object.data= self.template_object.data.copy()
        self.object.pass_index = segmentation_idx

        bpy.context.collection.objects.link(self.object) # was need for adding it to the scene
        
        # Center origin
        bpy.ops.object.select_all(action='DESELECT')
        self.object.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.ops.object.select_all(action='DESELECT')
        
        # Initialise
        self.rotate_random()

    def setMaterial(self, material_name: str) -> None:
        for idx in range(len(self.object.data.materials)):
            self.object.data.materials[idx] = bpy.data.materials.get(material_name) 
            
    def restoreMaterial(self) -> None:
        for idx in range(len(self.object.data.materials)):
            self.object.data.materials[idx] = self.template_object.data.materials[idx] 


class Grid:
    def __init__(self, n_spots: int) -> None:
        self.n_spots = n_spots
        self.side_length = 2
        self.distance_to_edge = math.sqrt(3) / 2 * self.side_length
        self.prop_list = []

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
        
    def populate(self, obj_name_list: List[str], n_instances: int) -> None:
        for idx in range(n_instances):
            coordinate = self.coordinate_list[idx]
            obj_name = random.choice(obj_name_list)
            prop = Prop(obj_name, idx)
            prop.move_abs_cartesian(coordinate)
            self.prop_list.append(prop)