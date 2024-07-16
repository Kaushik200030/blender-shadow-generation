# main.py
import os
import sys
import bpy
from mathutils import Vector
import math
import random

def twoChar_noShad(env_path, char1_path, char2_path, save_path, rounds):
    bpy.context.scene.cycles.device = 'GPU'

    # Clear existing objects
    #bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the warehouse (GLB file)
    bpy.ops.import_scene.gltf(filepath = env_path)

    # Find the mesh object (assuming the warehouse is a mesh)
    warehouse = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            warehouse = obj
            break

    # Ensure a mesh object was found
    if warehouse is None:
        raise Exception("No mesh object found in the imported GLB file.")

    # Calculate the bounding box dimensions
    bounding_box = [warehouse.matrix_world @ Vector(corner) for corner in warehouse.bound_box]

    min_x = min([v.x for v in bounding_box])
    max_x = max([v.x for v in bounding_box])
    min_y = min([v.y for v in bounding_box])
    max_y = max([v.y for v in bounding_box])
    min_z = min([v.z for v in bounding_box])
    max_z = max([v.z for v in bounding_box])

    # Calculate the height and breadth
    height = max_z - min_z
    breadth = max_x - min_x
    length = max_y - min_y

    char_x = int((breadth/2))
    char_y = int((length/2))
    char_z = int((height/2))

    # Import the character (GLB file)
    bpy.ops.import_scene.gltf(filepath= char1_path)
    character1 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    character1.location = ( int(char_x-char_x/8), char_y, 0) # Place the character at the center of the scene


    bpy.ops.import_scene.gltf(filepath= char2_path)
    character2 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    character2.location = ( int(char_x+char_x/8), char_y, 0) # Place the character at the center of the scene


    # Create an area light
    bpy.ops.object.light_add(type='AREA', location=(5, 0, 5))
    area_light1 = bpy.context.object
    area_light1.data.energy = 400  # Set strength to 200W
    area_light1.data.cycles.cast_shadow = False

    # Create the second sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light2 = bpy.context.object
    area_light2.data.energy = 400  # Adjust energy as needed
    area_light2.data.cycles.cast_shadow = False

    # Create the third sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light3 = bpy.context.object
    area_light3.data.energy = 600  # Adjust energy as needed
    area_light3.data.cycles.cast_shadow = False
    
    bpy.ops.mesh.primitive_plane_add(size= length*breadth, location=(char_x, char_y, 0))
    plane = bpy.context.object

    # Create a material for the plane and set its color
    plane_material = bpy.data.materials.new(name="PlaneMaterial")
    plane_material.diffuse_color = (0.2, 0.2, 0.2, 1.0)  # Gray color with full opacity
    plane.data.materials.append(plane_material)
#    plane.is_shadow_catcher = True


    # Define parameters
    radius = 5  # Distance from origin (where Z = 5)
    steps = rounds   # Number of steps for rotation (adjust for smoother or finer rotation)
    z = 0

    radius1 = 5  # Distance from origin (where Z = 5)   # Number of steps for rotation (adjust for smoother or finer rotation)
    z1 = 0

    # Set up the camera
    cam_z = (char_z + char_z/2)
    Camera_location = (char_x, char_y/2,  cam_z)
    bpy.ops.object.camera_add(location= Camera_location)
    camera = bpy.context.object


    direction = Vector((char_x, char_y/2,  cam_z)) - Vector((char_x, char_y, 0))
    camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

    # Set the camera as the active camera
    bpy.context.scene.camera = camera

    # Rotate around the origin in a circle
    for i in range(steps):
        rand_no1 = random.uniform(0,1)
        rand_no2 = random.uniform(0,1)
        rand_no3 = random.uniform(0,1)
        
        angle1 = 2 * math.pi * i / steps  # Calculate angle in radians
        angle2 = -(2 * math.pi * i / steps)
        angle3 = (angle2 + math.pi)*(angle1 + (2*math.pi))

        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        
        x3 = radius1 * math.cos(angle3)
        y3 = radius1 * math.sin(angle3)
        
        light_x1 = x1 + char_x
        light_y1 = y1 + char_y
        light_z1 = char_z + char_z/2
        
        light_x2 = x2 + char_x
        light_y2 = y2 + char_y
        light_z2 = char_z  + char_z/2
        
        light_x3 = x3 + char_x
        light_y3 = y3 + char_y
        light_z3 = char_z  + char_z/2
        
         
        
        # Set location
        area_light1.location = (light_x1, light_y1, light_z1)
        area_light2.location = (light_x2, light_y2, light_z2)
        area_light3.location = (light_x3, light_y3, light_z3)
        
        # Calculate direction vector and set rotation
        direction1 = Vector((light_x1, light_y1, light_z1)) - Vector((char_x, char_y, 0)) 
        area_light1.rotation_euler = direction1.to_track_quat('Z', 'Y').to_euler()
        
        direction2 = Vector((light_x2, light_y2, light_z2)) - Vector((char_x, char_y, 0)) 
        area_light2.rotation_euler = direction2.to_track_quat('Z', 'Y').to_euler()
        
        direction3 = Vector((light_x3, light_y3, light_z3)) - Vector((char_x, char_y, 0)) 
        area_light3.rotation_euler = direction3.to_track_quat('Z', 'Y').to_euler()
        

        # Update scene to reflect changes
        bpy.context.view_layer.update()
        
        # Set the render engine to Cycles for better shadow rendering
        bpy.context.scene.render.engine = 'CYCLES'

        # Enable shadow pass
        view_layer = bpy.context.view_layer
        view_layer.use_pass_shadow = True

        # Set up the compositor to isolate the shadow pass
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Create render layers node
        render_layers = nodes.new(type='CompositorNodeRLayers')

        # Print all available outputs to identify the correct shadow pass name
        print("Available outputs for render layers node:")
        for output in render_layers.outputs:
            print(output.name)

        # Create output node
        composite = nodes.new(type='CompositorNodeComposite')

        # Create file output node
        file_output = nodes.new(type='CompositorNodeOutputFile')
        file_output.base_path = ''
        file_output.file_slots[0].path = f'{save_path}/twoChar_noShad/{i}'
        file_output.format.file_format = 'PNG'

        # Link nodes
        links.new(render_layers.outputs['Image'], composite.inputs[0])
        # Correctly identify and link the shadow output after printing available outputs

        # Set the render settings to save the shadow pass
        bpy.context.scene.render.filepath = f'{save_path}/twoChar_noShad/{i}'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # Save as a black and white image

        # Render the scene and save the shadow pass
        bpy.ops.render.render(write_still=True)



def twoChar_withShad(env_path, char1_path, char2_path, save_path, rounds):

    bpy.context.scene.cycles.device = 'GPU'

    # Clear existing objects
    #bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the warehouse (GLB file)
    bpy.ops.import_scene.gltf(filepath=env_path)

    # Find the mesh object (assuming the warehouse is a mesh)
    warehouse = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            warehouse = obj
            break

    # Ensure a mesh object was found
    if warehouse is None:
        raise Exception("No mesh object found in the imported GLB file.")

    # Calculate the bounding box dimensions
    bounding_box = [warehouse.matrix_world @ Vector(corner) for corner in warehouse.bound_box]

    min_x = min([v.x for v in bounding_box])
    max_x = max([v.x for v in bounding_box])
    min_y = min([v.y for v in bounding_box])
    max_y = max([v.y for v in bounding_box])
    min_z = min([v.z for v in bounding_box])
    max_z = max([v.z for v in bounding_box])

    # Calculate the height and breadth
    height = max_z - min_z
    breadth = max_x - min_x
    length = max_y - min_y

    char_x = int((breadth/2))
    char_y = int((length/2))
    char_z = int((height/2))

    # Create a plane
    bpy.ops.mesh.primitive_plane_add(size= length*breadth, location=(char_x, char_y, 0))
    plane = bpy.context.object

    # Create a material for the plane and set its color
    plane_material = bpy.data.materials.new(name="PlaneMaterial")
    plane_material.diffuse_color = (0.2, 0.2, 0.2, 1.0)  # Gray color with full opacity
    plane.data.materials.append(plane_material)
    #plane.is_shadow_catcher = True

    # Import the character (GLB file)
    bpy.ops.import_scene.gltf(filepath=char1_path)
    character1 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    character1.location = ( int(char_x-char_x/8), char_y, 0) # Place the character at the center of the scene


    bpy.ops.import_scene.gltf(filepath=char2_path)
    character2 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    character2.location = ( int(char_x+char_x/8), char_y, 0) # Place the character at the center of the scene


    # Create an area light
    bpy.ops.object.light_add(type='AREA', location=(5, 0, 5))
    area_light1 = bpy.context.object
    area_light1.data.energy = 400  # Set strength to 200W


    # Create the second sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light2 = bpy.context.object
    area_light2.data.energy = 400  # Adjust energy as needed


    # Create the third sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light3 = bpy.context.object
    area_light3.data.energy = 600  # Adjust energy as needed



    # Define parameters
    radius = 5  # Distance from origin (where Z = 5)
    steps = rounds   # Number of steps for rotation (adjust for smoother or finer rotation)
    z = 0

    radius1 = 5  # Distance from origin (where Z = 5)   # Number of steps for rotation (adjust for smoother or finer rotation)
    z1 = 0

    # Set up the camera
    cam_z = (char_z + char_z/2)
    Camera_location = (char_x, char_y/2,  cam_z)
    bpy.ops.object.camera_add(location= Camera_location)
    camera = bpy.context.object


    direction = Vector((char_x, char_y/2,  cam_z)) - Vector((char_x, char_y, 0))
    camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

    # Set the camera as the active camera
    bpy.context.scene.camera = camera

    # Rotate around the origin in a circle
    for i in range(steps):
        rand_no1 = random.uniform(0,1)
        rand_no2 = random.uniform(0,1)
        rand_no3 = random.uniform(0,1)
        
        angle1 = 2 * math.pi * i / steps  # Calculate angle in radians
        angle2 = -(2 * math.pi * i / steps)
        angle3 = (angle2 + math.pi)*(angle1 + (2*math.pi))

        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        
        x3 = radius1 * math.cos(angle3)
        y3 = radius1 * math.sin(angle3)
        
        light_x1 = x1 + char_x
        light_y1 = y1 + char_y
        light_z1 = char_z + char_z/2
        
        light_x2 = x2 + char_x
        light_y2 = y2 + char_y
        light_z2 = char_z  + char_z/2
        
        light_x3 = x3 + char_x
        light_y3 = y3 + char_y
        light_z3 = char_z  + char_z/2
        
         
        
        # Set location
        area_light1.location = (light_x1, light_y1, light_z1)
        area_light2.location = (light_x2, light_y2, light_z2)
        area_light3.location = (light_x3, light_y3, light_z3)
        
        # Calculate direction vector and set rotation
        direction1 = Vector((light_x1, light_y1, light_z1)) - Vector((char_x, char_y, 0)) 
        area_light1.rotation_euler = direction1.to_track_quat('Z', 'Y').to_euler()
        
        direction2 = Vector((light_x2, light_y2, light_z2)) - Vector((char_x, char_y, 0)) 
        area_light2.rotation_euler = direction2.to_track_quat('Z', 'Y').to_euler()
        
        direction3 = Vector((light_x3, light_y3, light_z3)) - Vector((char_x, char_y, 0)) 
        area_light3.rotation_euler = direction3.to_track_quat('Z', 'Y').to_euler()
        

        # Update scene to reflect changes
        bpy.context.view_layer.update()
        
        # Set the render engine to Cycles for better shadow rendering
        bpy.context.scene.render.engine = 'CYCLES'

        # Enable shadow pass
        view_layer = bpy.context.view_layer
        view_layer.use_pass_shadow = True

        # Set up the compositor to isolate the shadow pass
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Create render layers node
        render_layers = nodes.new(type='CompositorNodeRLayers')

        # Print all available outputs to identify the correct shadow pass name
        print("Available outputs for render layers node:")
        for output in render_layers.outputs:
            print(output.name)

        # Create output node
        composite = nodes.new(type='CompositorNodeComposite')

        # Create file output node
        file_output = nodes.new(type='CompositorNodeOutputFile')
        file_output.base_path = ''
        file_output.file_slots[0].path = f'{save_path}/twoChar_withShad/{i}'
        file_output.format.file_format = 'PNG'

        # Link nodes
        links.new(render_layers.outputs['Image'], composite.inputs[0])
        # Correctly identify and link the shadow output after printing available outputs

        # Set the render settings to save the shadow pass
        bpy.context.scene.render.filepath = f'{save_path}/twoChar_withShad/{i}'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # Save as a black and white image

        # Render the scene and save the shadow pass
        bpy.ops.render.render(write_still=True)
        
        

def twoChar_1mask(env_path, char1_path, char2_path, save_path, rounds):
    
    bpy.context.scene.cycles.device = 'GPU'

    # Clear existing objects
    #bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the warehouse (GLB file)
    bpy.ops.import_scene.gltf(filepath=env_path)

    # Find the mesh object (assuming the warehouse is a mesh)
    warehouse = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            warehouse = obj
            break

    # Ensure a mesh object was found
    if warehouse is None:
        raise Exception("No mesh object found in the imported GLB file.")

    # Calculate the bounding box dimensions
    bounding_box = [warehouse.matrix_world @ Vector(corner) for corner in warehouse.bound_box]

    min_x = min([v.x for v in bounding_box])
    max_x = max([v.x for v in bounding_box])
    min_y = min([v.y for v in bounding_box])
    max_y = max([v.y for v in bounding_box])
    min_z = min([v.z for v in bounding_box])
    max_z = max([v.z for v in bounding_box])

    # Calculate the height and breadth
    height = max_z - min_z
    breadth = max_x - min_x
    length = max_y - min_y

    char_x = int((breadth/2))
    char_y = int((length/2))
    char_z = int((height/2))

    ## Enable shadow catcher
    #warehouse.select_set(True)
    #bpy.context.view_layer.objects.active = warehouse
    #bpy.context.object.is_shadow_catcher = True

    # Apply shadow catcher to all mesh objects within the warehouse
    def apply_shadow_catcher(obj):
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.context.object.is_shadow_catcher = True
        for child in obj.children:
            apply_shadow_catcher(child)

    apply_shadow_catcher(warehouse)

    # Create a plane
    bpy.ops.mesh.primitive_plane_add(size= length*breadth, location=(char_x, char_y, 0))
    plane = bpy.context.object

    # Create a material for the plane and set its color
    plane_material = bpy.data.materials.new(name="PlaneMaterial")
    plane_material.diffuse_color = (0.2, 0.2, 0.2, 1.0)  # Gray color with full opacity
    plane.data.materials.append(plane_material)
    plane.is_shadow_catcher = True


    ## Import the character (GLB file)
    #bpy.ops.import_scene.gltf(filepath='/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/kara_-_detroit_become_human.glb')
    #character1 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    #character1.location = ( int(char_x-char_x/8), char_y, 0) # Place the character at the center of the scene


    bpy.ops.import_scene.gltf(filepath=char2_path)
    character2 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    character2.location = ( int(char_x+char_x/8), char_y, 0) # Place the character at the center of the scene


    # Create an area light
    bpy.ops.object.light_add(type='AREA', location=(5, 0, 5))
    area_light1 = bpy.context.object
    area_light1.data.energy = 400  # Set strength to 200W
    area_light1.data.cycles.cast_shadow = False

    # Create the second sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light2 = bpy.context.object
    area_light2.data.energy = 400  # Adjust energy as needed
    area_light2.data.cycles.cast_shadow = False

    # Create the third sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light3 = bpy.context.object
    area_light3.data.energy = 600  # Adjust energy as needed
    area_light3.data.cycles.cast_shadow = False


    # Define parameters
    radius = 5  # Distance from origin (where Z = 5)
    steps = rounds   # Number of steps for rotation (adjust for smoother or finer rotation)
    z = 0

    radius1 = 5  # Distance from origin (where Z = 5)   # Number of steps for rotation (adjust for smoother or finer rotation)
    z1 = 0

    # Set up the camera
    cam_z = (char_z + char_z/2)
    Camera_location = (char_x, char_y/2,  cam_z)
    bpy.ops.object.camera_add(location= Camera_location)
    camera = bpy.context.object


    direction = Vector((char_x, char_y/2,  cam_z)) - Vector((char_x, char_y, 0))
    camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

    # Set the camera as the active camera
    bpy.context.scene.camera = camera

    # Rotate around the origin in a circle
    for i in range(steps):
        rand_no1 = random.uniform(0,1)
        rand_no2 = random.uniform(0,1)
        rand_no3 = random.uniform(0,1)
        
        angle1 = 2 * math.pi * i / steps  # Calculate angle in radians
        angle2 = -(2 * math.pi * i / steps)
        angle3 = (angle2 + math.pi)*(angle1 + (2*math.pi))
        
        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        
        x3 = radius1 * math.cos(angle3)
        y3 = radius1 * math.sin(angle3)
        
        light_x1 = x1 + char_x
        light_y1 = y1 + char_y
        light_z1 = char_z + char_z/2
        
        light_x2 = x2 + char_x
        light_y2 = y2 + char_y
        light_z2 = char_z  + char_z/2
        
        light_x3 = x3 + char_x
        light_y3 = y3 + char_y
        light_z3 = char_z  + char_z/2
        
         
        
        # Set location
        area_light1.location = (light_x1, light_y1, light_z1)
        area_light2.location = (light_x2, light_y2, light_z2)
        area_light3.location = (light_x3, light_y3, light_z3)
        
        # Calculate direction vector and set rotation
        direction1 = Vector((light_x1, light_y1, light_z1)) - Vector((char_x, char_y, 0)) 
        area_light1.rotation_euler = direction1.to_track_quat('Z', 'Y').to_euler()
        
        direction2 = Vector((light_x2, light_y2, light_z2)) - Vector((char_x, char_y, 0)) 
        area_light2.rotation_euler = direction2.to_track_quat('Z', 'Y').to_euler()
        
        direction3 = Vector((light_x3, light_y3, light_z3)) - Vector((char_x, char_y, 0)) 
        area_light3.rotation_euler = direction3.to_track_quat('Z', 'Y').to_euler()
        

        # Update scene to reflect changes
        bpy.context.view_layer.update()
        
        # Set the render engine to Cycles for better shadow rendering
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.film_transparent = True


        # Enable shadow pass
        view_layer = bpy.context.view_layer
        view_layer.use_pass_shadow = True

        # Set up the compositor to isolate the shadow pass
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Create render layers node
        render_layers = nodes.new(type='CompositorNodeRLayers')

        # Print all available outputs to identify the correct shadow pass name
        print("Available outputs for render layers node:")
        for output in render_layers.outputs:
            print(output.name)

        # Create output node
        composite = nodes.new(type='CompositorNodeComposite')

        # Create file output node
        file_output = nodes.new(type='CompositorNodeOutputFile')
        file_output.base_path = ''
        file_output.file_slots[0].path = f'{save_path}/twoChar_1mask/{i}'
        file_output.format.file_format = 'PNG'

        # Link nodes
        links.new(render_layers.outputs['Image'], composite.inputs[0])
     
        # Correctly identify and link the shadow output after printing available outputs

        # Set the render settings to save the shadow pass
        bpy.context.scene.render.filepath = f'{save_path}/twoChar_1mask/{i}'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # Save as a black and white image

        # Render the scene and save the shadow pass
        bpy.ops.render.render(write_still=True)
        
           
        
def twoChar_2mask(env_path, char1_path, char2_path, save_path, rounds):
    

    bpy.context.scene.cycles.device = 'GPU'

    # Clear existing objects
    #bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the warehouse (GLB file)
    bpy.ops.import_scene.gltf(filepath=env_path)

    # Find the mesh object (assuming the warehouse is a mesh)
    warehouse = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            warehouse = obj
            break

    # Ensure a mesh object was found
    if warehouse is None:
        raise Exception("No mesh object found in the imported GLB file.")

    # Calculate the bounding box dimensions
    bounding_box = [warehouse.matrix_world @ Vector(corner) for corner in warehouse.bound_box]

    min_x = min([v.x for v in bounding_box])
    max_x = max([v.x for v in bounding_box])
    min_y = min([v.y for v in bounding_box])
    max_y = max([v.y for v in bounding_box])
    min_z = min([v.z for v in bounding_box])
    max_z = max([v.z for v in bounding_box])

    # Calculate the height and breadth
    height = max_z - min_z
    breadth = max_x - min_x
    length = max_y - min_y

    char_x = int((breadth/2))
    char_y = int((length/2))
    char_z = int((height/2))

    ## Enable shadow catcher
    #warehouse.select_set(True)
    #bpy.context.view_layer.objects.active = warehouse
    #bpy.context.object.is_shadow_catcher = True

    # Apply shadow catcher to all mesh objects within the warehouse
    def apply_shadow_catcher(obj):
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.context.object.is_shadow_catcher = True
        for child in obj.children:
            apply_shadow_catcher(child)

    apply_shadow_catcher(warehouse)

    # Create a plane
    bpy.ops.mesh.primitive_plane_add(size= length*breadth, location=(char_x, char_y, 0))
    plane = bpy.context.object

    # Create a material for the plane and set its color
    plane_material = bpy.data.materials.new(name="PlaneMaterial")
    plane_material.diffuse_color = (0.2, 0.2, 0.2, 1.0)  # Gray color with full opacity
    plane.data.materials.append(plane_material)
    plane.is_shadow_catcher = True


    # Import the character (GLB file)
    bpy.ops.import_scene.gltf(filepath=char1_path)
    character1 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    character1.location = ( int(char_x-char_x/8), char_y, 0) # Place the character at the center of the scene


    #bpy.ops.import_scene.gltf(filepath='/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/kara_-_detroit_become_human.glb')
    #character2 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    #character2.location = ( int(char_x+char_x/8), char_y, 0) # Place the character at the center of the scene


    # Create an area light
    bpy.ops.object.light_add(type='AREA', location=(5, 0, 5))
    area_light1 = bpy.context.object
    area_light1.data.energy = 400  # Set strength to 200W
    area_light1.data.cycles.cast_shadow = False

    # Create the second sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light2 = bpy.context.object
    area_light2.data.energy = 400  # Adjust energy as needed
    area_light2.data.cycles.cast_shadow = False

    # Create the third sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light3 = bpy.context.object
    area_light3.data.energy = 600  # Adjust energy as needed
    area_light3.data.cycles.cast_shadow = False


    # Define parameters
    radius = 5  # Distance from origin (where Z = 5)
    steps = rounds   # Number of steps for rotation (adjust for smoother or finer rotation)
    z = 0

    radius1 = 5  # Distance from origin (where Z = 5)   # Number of steps for rotation (adjust for smoother or finer rotation)
    z1 = 0

    # Set up the camera
    cam_z = (char_z + char_z/2)
    Camera_location = (char_x, char_y/2,  cam_z)
    bpy.ops.object.camera_add(location= Camera_location)
    camera = bpy.context.object


    direction = Vector((char_x, char_y/2,  cam_z)) - Vector((char_x, char_y, 0))
    camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

    # Set the camera as the active camera
    bpy.context.scene.camera = camera

    # Rotate around the origin in a circle
    for i in range(steps):
        rand_no1 = random.uniform(0,1)
        rand_no2 = random.uniform(0,1)
        rand_no3 = random.uniform(0,1)
        
        angle1 = 2 * math.pi * i / steps  # Calculate angle in radians
        angle2 = -(2 * math.pi * i / steps)
        angle3 = (angle2 + math.pi)*(angle1 + (2*math.pi))

        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        
        x3 = radius1 * math.cos(angle3)
        y3 = radius1 * math.sin(angle3)
        
        light_x1 = x1 + char_x
        light_y1 = y1 + char_y
        light_z1 = char_z + char_z/2
        
        light_x2 = x2 + char_x
        light_y2 = y2 + char_y
        light_z2 = char_z  + char_z/2
        
        light_x3 = x3 + char_x
        light_y3 = y3 + char_y
        light_z3 = char_z  + char_z/2
        
         
        
        # Set location
        area_light1.location = (light_x1, light_y1, light_z1)
        area_light2.location = (light_x2, light_y2, light_z2)
        area_light3.location = (light_x3, light_y3, light_z3)
        
        # Calculate direction vector and set rotation
        direction1 = Vector((light_x1, light_y1, light_z1)) - Vector((char_x, char_y, 0)) 
        area_light1.rotation_euler = direction1.to_track_quat('Z', 'Y').to_euler()
        
        direction2 = Vector((light_x2, light_y2, light_z2)) - Vector((char_x, char_y, 0)) 
        area_light2.rotation_euler = direction2.to_track_quat('Z', 'Y').to_euler()
        
        direction3 = Vector((light_x3, light_y3, light_z3)) - Vector((char_x, char_y, 0)) 
        area_light3.rotation_euler = direction3.to_track_quat('Z', 'Y').to_euler()
        

        # Update scene to reflect changes
        bpy.context.view_layer.update()
        
        # Set the render engine to Cycles for better shadow rendering
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.film_transparent = True


        # Enable shadow pass
        view_layer = bpy.context.view_layer
        view_layer.use_pass_shadow = True

        # Set up the compositor to isolate the shadow pass
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Create render layers node
        render_layers = nodes.new(type='CompositorNodeRLayers')

        # Print all available outputs to identify the correct shadow pass name
        print("Available outputs for render layers node:")
        for output in render_layers.outputs:
            print(output.name)

        # Create output node
        composite = nodes.new(type='CompositorNodeComposite')

        # Create file output node
        file_output = nodes.new(type='CompositorNodeOutputFile')
        file_output.base_path = ''
        file_output.file_slots[0].path = f'{save_path}/twoChar_2mask/{i}'
        file_output.format.file_format = 'PNG'

        # Link nodes
        links.new(render_layers.outputs['Image'], composite.inputs[0])
     
        # Correctly identify and link the shadow output after printing available outputs

        # Set the render settings to save the shadow pass
        bpy.context.scene.render.filepath = f'{save_path}/twoChar_2mask/{i}'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # Save as a black and white image

        # Render the scene and save the shadow pass
        bpy.ops.render.render(write_still=True)



def twoChar_1Shad(env_path, char1_path, char2_path, save_path, rounds):
    
    bpy.context.scene.cycles.device = 'GPU'

    # Clear existing objects
    #bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the warehouse (GLB file)
    bpy.ops.import_scene.gltf(filepath=env_path)

    # Find the mesh object (assuming the warehouse is a mesh)
    warehouse = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            warehouse = obj
            break

    # Ensure a mesh object was found
    if warehouse is None:
        raise Exception("No mesh object found in the imported GLB file.")

    # Calculate the bounding box dimensions
    bounding_box = [warehouse.matrix_world @ Vector(corner) for corner in warehouse.bound_box]

    min_x = min([v.x for v in bounding_box])
    max_x = max([v.x for v in bounding_box])
    min_y = min([v.y for v in bounding_box])
    max_y = max([v.y for v in bounding_box])
    min_z = min([v.z for v in bounding_box])
    max_z = max([v.z for v in bounding_box])

    # Calculate the height and breadth
    height = max_z - min_z
    breadth = max_x - min_x
    length = max_y - min_y

    char_x = int((breadth/2))
    char_y = int((length/2))
    char_z = int((height/2))

    ## Enable shadow catcher
    #warehouse.select_set(True)
    #bpy.context.view_layer.objects.active = warehouse
    #bpy.context.object.is_shadow_catcher = True

    # Apply shadow catcher to all mesh objects within the warehouse
    def apply_shadow_catcher(obj):
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.context.object.is_shadow_catcher = True
        for child in obj.children:
            apply_shadow_catcher(child)

    apply_shadow_catcher(warehouse)

    # Create a plane
    bpy.ops.mesh.primitive_plane_add(size= length*breadth, location=(char_x, char_y, 0))
    plane = bpy.context.object

    # Create a material for the plane and set its color
    plane_material = bpy.data.materials.new(name="PlaneMaterial")
    plane_material.diffuse_color = (0.2, 0.2, 0.2, 1.0)  # Gray color with full opacity
    plane.data.materials.append(plane_material)
    plane.is_shadow_catcher = True


    ## Import the character (GLB file)
    #bpy.ops.import_scene.gltf(filepath='/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/kara_-_detroit_become_human.glb')
    #character1 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    #character1.location = ( int(char_x-char_x/8), char_y, 0) # Place the character at the center of the scene


    bpy.ops.import_scene.gltf(filepath=char2_path)
    character2 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    character2.location = ( int(char_x+char_x/8), char_y, 0) # Place the character at the center of the scene




    # Create an area light
    bpy.ops.object.light_add(type='AREA', location=(5, 0, 5))
    area_light1 = bpy.context.object
    area_light1.data.energy = 400  # Set strength to 200W
    area_light1.data.cycles.cast_shadow = True

    # Create the second sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light2 = bpy.context.object
    area_light2.data.energy = 400  # Adjust energy as needed
    area_light2.data.cycles.cast_shadow = True

    # Create the third sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light3 = bpy.context.object
    area_light3.data.energy = 600  # Adjust energy as needed
    area_light3.data.cycles.cast_shadow = True


    # Define parameters
    radius = 5  # Distance from origin (where Z = 5)
    steps = rounds   # Number of steps for rotation (adjust for smoother or finer rotation)
    z = 0

    radius1 = 5  # Distance from origin (where Z = 5)   # Number of steps for rotation (adjust for smoother or finer rotation)
    z1 = 0

    # Set up the camera
    cam_z = (char_z + char_z/2)
    Camera_location = (char_x, char_y/2,  cam_z)
    bpy.ops.object.camera_add(location= Camera_location)
    camera = bpy.context.object


    direction = Vector((char_x, char_y/2,  cam_z)) - Vector((char_x, char_y, 0))
    camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

    # Set the camera as the active camera
    bpy.context.scene.camera = camera


    # Function to make an object completely invisible to the camera but still allow it to cast shadows
    def make_invisible_to_camera(obj):
        obj.is_holdout = True
        for child in obj.children:
            make_invisible_to_camera(child)

    make_invisible_to_camera(character2)

    # Rotate around the origin in a circle
    for i in range(steps):
        rand_no1 = random.uniform(0,1)
        rand_no2 = random.uniform(0,1)
        rand_no3 = random.uniform(0,1)
        
        angle1 = 2 * math.pi * i / steps  # Calculate angle in radians
        angle2 = -(2 * math.pi * i / steps)
        angle3 = (angle2 + math.pi)*(angle1 + (2*math.pi))

        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        
        x3 = radius1 * math.cos(angle3)
        y3 = radius1 * math.sin(angle3)
        
        light_x1 = x1 + char_x
        light_y1 = y1 + char_y
        light_z1 = char_z + char_z/2
        
        light_x2 = x2 + char_x
        light_y2 = y2 + char_y
        light_z2 = char_z  + char_z/2
        
        light_x3 = x3 + char_x
        light_y3 = y3 + char_y
        light_z3 = char_z  + char_z/2
        
         
        
        # Set location
        area_light1.location = (light_x1, light_y1, light_z1)
        area_light2.location = (light_x2, light_y2, light_z2)
        area_light3.location = (light_x3, light_y3, light_z3)
        
        # Calculate direction vector and set rotation
        direction1 = Vector((light_x1, light_y1, light_z1)) - Vector((char_x, char_y, 0)) 
        area_light1.rotation_euler = direction1.to_track_quat('Z', 'Y').to_euler()
        
        direction2 = Vector((light_x2, light_y2, light_z2)) - Vector((char_x, char_y, 0)) 
        area_light2.rotation_euler = direction2.to_track_quat('Z', 'Y').to_euler()
        
        direction3 = Vector((light_x3, light_y3, light_z3)) - Vector((char_x, char_y, 0)) 
        area_light3.rotation_euler = direction3.to_track_quat('Z', 'Y').to_euler()
        

        # Update scene to reflect changes
        bpy.context.view_layer.update()
        
        # Set the render engine to Cycles for better shadow rendering
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.film_transparent = True


    #    # Enable shadow pass
    #    view_layer = bpy.context.view_layer
    #    view_layer.use_pass_shadow = True

        # Set up the compositor to isolate the shadow pass
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Create render layers node
        render_layers = nodes.new(type='CompositorNodeRLayers')

        # Print all available outputs to identify the correct shadow pass name
        print("Available outputs for render layers node:")
        for output in render_layers.outputs:
            print(output.name)

        # Create output node
        composite = nodes.new(type='CompositorNodeComposite')

        # Create file output node
        file_output = nodes.new(type='CompositorNodeOutputFile')
        file_output.base_path = ''
        file_output.file_slots[0].path = f'{save_path}/twoChar_1Shad/{i}'
        file_output.format.file_format = 'PNG'

        # Link nodes
        links.new(render_layers.outputs['Image'], composite.inputs[0])
     
        # Correctly identify and link the shadow output after printing available outputs

        # Set the render settings to save the shadow pass
        bpy.context.scene.render.filepath = f'{save_path}/twoChar_1Shad/{i}'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # Save as a black and white image

        # Render the scene and save the shadow pass
        bpy.ops.render.render(write_still=True)



def twoChar_2Shad(env_path, char1_path, char2_path, save_path, rounds):
    
    bpy.context.scene.cycles.device = 'GPU'

    # Clear existing objects
    #bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the warehouse (GLB file)
    bpy.ops.import_scene.gltf(filepath=env_path)

    # Find the mesh object (assuming the warehouse is a mesh)
    warehouse = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            warehouse = obj
            break

    # Ensure a mesh object was found
    if warehouse is None:
        raise Exception("No mesh object found in the imported GLB file.")

    # Calculate the bounding box dimensions
    bounding_box = [warehouse.matrix_world @ Vector(corner) for corner in warehouse.bound_box]

    min_x = min([v.x for v in bounding_box])
    max_x = max([v.x for v in bounding_box])
    min_y = min([v.y for v in bounding_box])
    max_y = max([v.y for v in bounding_box])
    min_z = min([v.z for v in bounding_box])
    max_z = max([v.z for v in bounding_box])

    # Calculate the height and breadth
    height = max_z - min_z
    breadth = max_x - min_x
    length = max_y - min_y

    char_x = int((breadth/2))
    char_y = int((length/2))
    char_z = int((height/2))

    ## Enable shadow catcher
    #warehouse.select_set(True)
    #bpy.context.view_layer.objects.active = warehouse
    #bpy.context.object.is_shadow_catcher = True

    # Apply shadow catcher to all mesh objects within the warehouse
    def apply_shadow_catcher(obj):
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.context.object.is_shadow_catcher = True
        for child in obj.children:
            apply_shadow_catcher(child)

    apply_shadow_catcher(warehouse)

    # Create a plane
    bpy.ops.mesh.primitive_plane_add(size= length*breadth, location=(char_x, char_y, 0))
    plane = bpy.context.object

    # Create a material for the plane and set its color
    plane_material = bpy.data.materials.new(name="PlaneMaterial")
    plane_material.diffuse_color = (0.2, 0.2, 0.2, 1.0)  # Gray color with full opacity
    plane.data.materials.append(plane_material)
    plane.is_shadow_catcher = True


    # Import the character (GLB file)
    bpy.ops.import_scene.gltf(filepath = char1_path)
    character1 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    character1.location = ( int(char_x-char_x/8), char_y, 0) # Place the character at the center of the scene


    #bpy.ops.import_scene.gltf(filepath='/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/kara_-_detroit_become_human.glb')
    #character2 = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
    #character2.location = ( int(char_x+char_x/8), char_y, 0) # Place the character at the center of the scene




    # Create an area light
    bpy.ops.object.light_add(type='AREA', location=(5, 0, 5))
    area_light1 = bpy.context.object
    area_light1.data.energy = 400  # Set strength to 200W
    area_light1.data.cycles.cast_shadow = True

    # Create the second sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light2 = bpy.context.object
    area_light2.data.energy = 400  # Adjust energy as needed
    area_light2.data.cycles.cast_shadow = True

    # Create the third sunlight
    bpy.ops.object.light_add(type='AREA', location=(-5, 0, 5))
    area_light3 = bpy.context.object
    area_light3.data.energy = 600  # Adjust energy as needed
    area_light3.data.cycles.cast_shadow = True


    # Define parameters
    radius = 5  # Distance from origin (where Z = 5)
    steps = rounds   # Number of steps for rotation (adjust for smoother or finer rotation)
    z = 0

    radius1 = 5  # Distance from origin (where Z = 5)   # Number of steps for rotation (adjust for smoother or finer rotation)
    z1 = 0

    # Set up the camera
    cam_z = (char_z + char_z/2)
    Camera_location = (char_x, char_y/2,  cam_z)
    bpy.ops.object.camera_add(location= Camera_location)
    camera = bpy.context.object


    direction = Vector((char_x, char_y/2,  cam_z)) - Vector((char_x, char_y, 0))
    camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

    # Set the camera as the active camera
    bpy.context.scene.camera = camera


    # Function to make an object completely invisible to the camera but still allow it to cast shadows
    def make_invisible_to_camera(obj):
        obj.is_holdout = True
        for child in obj.children:
            make_invisible_to_camera(child)

    make_invisible_to_camera(character1)

    # Rotate around the origin in a circle
    for i in range(steps):
        rand_no1 = random.uniform(0,1)
        rand_no2 = random.uniform(0,1)
        rand_no3 = random.uniform(0,1)
        
        angle1 = 2 * math.pi * i / steps  # Calculate angle in radians
        angle2 = -(2 * math.pi * i / steps)
        angle3 = (angle2 + math.pi)*(angle1 + (2*math.pi))

        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        
        x3 = radius1 * math.cos(angle3)
        y3 = radius1 * math.sin(angle3)
        
        light_x1 = x1 + char_x
        light_y1 = y1 + char_y
        light_z1 = char_z + char_z/2
        
        light_x2 = x2 + char_x
        light_y2 = y2 + char_y
        light_z2 = char_z  + char_z/2
        
        light_x3 = x3 + char_x
        light_y3 = y3 + char_y
        light_z3 = char_z  + char_z/2
        
         
        
        # Set location
        area_light1.location = (light_x1, light_y1, light_z1)
        area_light2.location = (light_x2, light_y2, light_z2)
        area_light3.location = (light_x3, light_y3, light_z3)
        
        # Calculate direction vector and set rotation
        direction1 = Vector((light_x1, light_y1, light_z1)) - Vector((char_x, char_y, 0)) 
        area_light1.rotation_euler = direction1.to_track_quat('Z', 'Y').to_euler()
        
        direction2 = Vector((light_x2, light_y2, light_z2)) - Vector((char_x, char_y, 0)) 
        area_light2.rotation_euler = direction2.to_track_quat('Z', 'Y').to_euler()
        
        direction3 = Vector((light_x3, light_y3, light_z3)) - Vector((char_x, char_y, 0)) 
        area_light3.rotation_euler = direction3.to_track_quat('Z', 'Y').to_euler()
        

        # Update scene to reflect changes
        bpy.context.view_layer.update()
        
        # Set the render engine to Cycles for better shadow rendering
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.film_transparent = True


    #    # Enable shadow pass
    #    view_layer = bpy.context.view_layer
    #    view_layer.use_pass_shadow = True

        # Set up the compositor to isolate the shadow pass
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Create render layers node
        render_layers = nodes.new(type='CompositorNodeRLayers')

        # Print all available outputs to identify the correct shadow pass name
        print("Available outputs for render layers node:")
        for output in render_layers.outputs:
            print(output.name)

        # Create output node
        composite = nodes.new(type='CompositorNodeComposite')

        # Create file output node
        file_output = nodes.new(type='CompositorNodeOutputFile')
        file_output.base_path = ''
        file_output.file_slots[0].path = f'{save_path}/twoChar_2Shad/{i}'
        file_output.format.file_format = 'PNG'

        # Link nodes
        links.new(render_layers.outputs['Image'], composite.inputs[0])
     
        # Correctly identify and link the shadow output after printing available outputs

        # Set the render settings to save the shadow pass
        bpy.context.scene.render.filepath = f'{save_path}/twoChar_2Shad/{i}'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # Save as a black and white image

        # Render the scene and save the shadow pass
        bpy.ops.render.render(write_still=True)

def clear_scene():
    # Select all objects
    bpy.ops.object.select_all(action='SELECT')
    
    # Delete all selected objects
    bpy.ops.object.delete()
    
    # Clear out orphan data blocks
    bpy.ops.outliner.orphans_purge(do_recursive=True)

    

def main(env_path, char1_path, char2_path, save_path, rounds):
    
    # Call the functions from the imported scripts
    twoChar_noShad(env_path, char1_path, char2_path, save_path, rounds)
    clear_scene()
    twoChar_withShad(env_path, char1_path, char2_path, save_path, rounds)
    clear_scene()
    twoChar_1mask(env_path, char1_path, char2_path, save_path, rounds)
    clear_scene()
    twoChar_2mask(env_path, char1_path, char2_path, save_path, rounds)
    clear_scene()
    twoChar_1Shad(env_path, char1_path, char2_path, save_path, rounds)
    clear_scene()
    twoChar_2Shad(env_path, char1_path, char2_path, save_path, rounds)

    

if __name__ == "__main__":
    
    #Parameters 
    
    ENV_PATH = f"/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/warehouse3.glb"
    CHAR1_PATH = f"/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/kara_-_detroit_become_human.glb"
    CHAR2_PATH = f"/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/kara_-_detroit_become_human.glb"
    SAVE_PATH = f"/Users/kaushikpattanayak/Desktop/KP_Flam/blender_output/Test"
    ROUNDS = 1
    
    main(ENV_PATH, CHAR1_PATH, CHAR2_PATH, SAVE_PATH, ROUNDS)
