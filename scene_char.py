import bpy
import math
from mathutils import Vector

bpy.context.scene.cycles.device = 'GPU'

# Clear existing objects
#bpy.ops.wm.read_factory_settings(use_empty=True)

# Import the character (GLB file)
bpy.ops.import_scene.gltf(filepath='/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/kara_-_detroit_become_human.glb')
character = bpy.context.selected_objects[0]  # Assuming the character is the first object imported
character.location = (0, 0, 0)  # Place the character at the center of the scene

# Import the warehouse (GLB file)
bpy.ops.import_scene.gltf(filepath='/Users/kaushikpattanayak/Desktop/KP_Flam/Blender Script/Environments/warehouse_fbx_model_free.glb')
warehouse = bpy.context.selected_objects[0]  # Assuming the warehouse is the first object imported

# Place the character in the center of the warehouse
# Adjust the location if necessary
character.location = (7, 20, 0)

# Set up the camera
bpy.ops.object.camera_add(location=(8, -8, 6))
camera = bpy.context.object
camera.rotation_euler = (1.1, 0, 0.8) 

# Set the camera as the active camera
bpy.context.scene.camera = camera

# Create a sunlight
bpy.ops.object.light_add(type='SUN', location=(5, 0, 5))
sun = bpy.context.object
#sun.data.energy = 2  # Adjust energy as needed
sun.rotation_euler = (0.7854, 0, 1.5708)  # 45 degrees in X and Z axis

# Define parameters
radius = 5  # Distance from origin (where Z = 5)
steps = 1   # Number of steps for rotation (adjust for smoother or finer rotation)
z = 5

# Rotate around the origin in a circle
for i in range(steps):
    angle = 2 * math.pi * i / steps  # Calculate angle in radians
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    
    # Set location
    sun.location = (x, y, z)
    
    # Calculate direction vector and set rotation
    direction =  Vector((x, y, z)) - Vector((0, 0, 0))
    sun.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

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
    file_output.file_slots[0].path = '/tmp/shadow'
    file_output.format.file_format = 'PNG'

    # Link nodes
    links.new(render_layers.outputs['Image'], composite.inputs[0])
    # Correctly identify and link the shadow output after printing available outputs

    # Set the render settings to save the shadow pass
    bpy.context.scene.render.filepath = f'/path/to/output/directory/shadow{i}.png'
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'BW'  # Save as a black and white image

    # Render the scene and save the shadow pass
    bpy.ops.render.render(write_still=True)
