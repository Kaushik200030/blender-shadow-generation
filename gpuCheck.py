import bpy
bpy.context.scene.cycles.device = 'GPU'
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'

# List of available devices
devices = bpy.context.preferences.addons['cycles'].preferences.get_devices()

# Enable all available CUDA devices
for device in devices:
    for d in device:
        d.use = True