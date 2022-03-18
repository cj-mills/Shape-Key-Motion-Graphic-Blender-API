# The Blender Python API
import bpy
# Gives access to Blender's internal mesh editing API
import bmesh

# Provides access to mathematical functions
import math

def get_name():
    """Get the name for the currently active object"""
    return bpy.context.active_object.name

def degToRadian(angle):
    """Convert angle from degrees to radians"""
    return angle*(math.pi/180)

def move_obj(name, coords):
    """Set object location to the specified coordinates"""
    bpy.data.objects[name].location = coords

def rotate_obj(name, angles):
    """Set object rotation to the specified angles"""
    rotation = [degToRadian(angle) for angle in angles]
    bpy.data.objects[name].rotation_euler = rotation

def scale_obj(name, scale):
    """Set object scale"""
    bpy.data.objects[name].scale = scale

def clear_collection(collection):
    """Remove everything from the specified collection"""
    for obj in collection.objects:
        bpy.data.objects.remove(obj)
        
def add_keyframe_sequence(obj, attribute, values, frames):
    """Add a sequence of keyframes for an object"""
    for v, f in zip(values, frames):
        setattr(obj, attribute, v)
        obj.keyframe_insert(data_path=attribute, frame=f)
  



"""Set up the scene"""
# Set View Transform to Standard
bpy.data.scenes["Scene"].view_settings.view_transform = "Standard"
# Set the Background color to pure black
bpy.data.worlds['World'].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
# Clear Collection
clear_collection(bpy.data.collections[0])



"""Create and position a new camera"""
# Create a new camera
bpy.ops.object.camera_add()
# Get the name of the current object, the camera
name = get_name()
# Move the camera
move_obj(name, [0, -8, 0])
# Rotate the camera
rotate_obj(name, [90, 0, 0])
# Set camera to orthographic
bpy.context.active_object.data.type = "ORTHO"

"""Create a material with an Emission Shader"""
# Create a material named "Material" if it does not exist
mat_name = "Material"
mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)

# Enable nodes for the material
mat.use_nodes = True
# Get a reference to the material's node tree
nodes = mat.node_tree.nodes

# Remove the 'Principled BSDF' node if there is one
if (nodes.get('Principled BSDF') is not None):
    nodes.remove(nodes.get('Principled BSDF'))
    
# Remove the 'Emission' node if there is one
if (nodes.get('Emission') is not None):
    nodes.remove(nodes.get('Emission'))

# Get a reference to the material's output node
mat_output = nodes.get('Material Output')
# Create a new Emission shader
emission = nodes.new('ShaderNodeEmission')
# Link the Emission shader to the Surface value of the output node
mat.node_tree.links.new(mat_output.inputs[0], emission.outputs[0])


"""Create a new plane with the Emission material"""
# Create a new plane
bpy.ops.mesh.primitive_plane_add()
# Get the name of the new plane
name = get_name()
# Rotate the plane
rotate_obj(name, [90, 0, 0])
# Reduce the size of the plance by half
plane_scale = 0.5
scale_obj(name, [plane_scale]*3)

# Get a reference to the plane
plane = bpy.context.active_object
# Attach the material with the Emission shader to the plane
if plane.data.materials:
    plane.data.materials[0] = mat
else:
    plane.data.materials.append(mat)



"""Cut out a center square from the plane"""
# Get the mesh for the plane object
mesh = bpy.context.object.data

# Get a BMesh representation of the plane mesh
bm = bmesh.new()
bm.from_mesh(mesh)

# Create a list of the plane faces
faces_copy = [f for f in bm.faces]
# Create a new inset for the selected face
bmesh.ops.inset_individual(bm, faces = [faces_copy[0]], thickness=0.3, depth=0.0) 

# Get a list of faces
faces_select = [f for f in bm.faces]
# Delete the middle face
bmesh.ops.delete(bm, geom=[faces_select[0]], context='FACES_ONLY')
# Update the mesh
bm.to_mesh(mesh)
# Free the Bmesh representation and prevent further access
bm.free()



"""Add first shape key to deform the plane"""
# Add a Basis shape key 
bpy.ops.object.shape_key_add()
# Add a new shape key
bpy.ops.object.shape_key_add()

# Enter edit mode
bpy.ops.object.mode_set(mode="EDIT")
# Create a BMesh representation from the current mesh in edit mode
bm = bmesh.from_edit_mesh(mesh)

# Create a list of the vertices
vertices = [v for v in bm.verts]

# Set the location for the inner four corners to the same as the outer corners 
vertices[4].co.x = vertices[0].co.x
vertices[4].co.y = vertices[0].co.y

vertices[5].co.x = vertices[1].co.x
vertices[5].co.y = vertices[1].co.y

vertices[7].co.x = vertices[2].co.x
vertices[7].co.y = vertices[2].co.y

vertices[6].co.x = vertices[3].co.x
vertices[6].co.y = vertices[3].co.y

# Update the mesh
bmesh.update_edit_mesh(mesh, True)
# Free the BMesh representation and prevent further access
bm.free()

# Enter object mode
bpy.ops.object.mode_set(mode="OBJECT")

"""Add second shape key to deform the plane"""
# Add a new shape key
bpy.ops.object.shape_key_add()
# Enter edit mode
bpy.ops.object.mode_set(mode="EDIT")
# Create a BMesh representation from the current mesh in edit mode
bm = bmesh.from_edit_mesh(mesh)

# Create a list of vertices
vertices = [v for v in bm.verts]

# Move the bottom inner left corner to the bottom outer left corner 
vertices[4].co.x = vertices[0].co.x
vertices[4].co.y = vertices[0].co.y
# Move the top inner right corner to the top right outer corner
vertices[6].co.x = vertices[3].co.x
vertices[6].co.y = vertices[3].co.y

# Update the mesh
bmesh.update_edit_mesh(mesh, True)
# Free the BMesh representation and prevent further access
bm.free()

# Enter object mode
bpy.ops.object.mode_set(mode="OBJECT")




"""Set up for animation"""
# Set the render frame rate to 60
bpy.context.scene.render.fps = 60

# Set the start frame to 0
bpy.data.scenes['Scene'].frame_start = 0
# Set the end frame to 200
bpy.data.scenes['Scene'].frame_end = 175
# Set the current frame to 0
bpy.data.scenes['Scene'].frame_current = 0


"""Add keyframes to the first shape key"""
# Get a reference to the list of shape keys
shape_keys = bpy.context.selected_objects[0].data.shape_keys

# Get a reference to the first shape key
zoomy = shape_keys.key_blocks[1]
# Set values for keyframes
values = [1.0, 0.2, 0.0, 0.0, 0.75, 1.0]
# Set the frames for keyframes
frames = [0, 10, 40, 135, 145, 170]
# Add keyframes for the value of the first shape key
add_keyframe_sequence(zoomy, 'value', values, frames)


"""Add keyframes to animate the second shape key"""
# Get a reference to the second shape key
zoomy_2 = shape_keys.key_blocks[2]
# Set values for keyframes
values = [0.0, 0.265, 0.95, 0.0]
# Set the frames for keyframes
frames = [100, 110, 132, 142]
# Add keyframes for the value of the second shape key
add_keyframe_sequence(zoomy_2, 'value', values, frames)


"""Add keyframes to rotato the plane"""
# Get a reference to the planey
plane = bpy.context.selected_objects[0]
# Set values for keyframes
values = [[degToRadian(angle) for angle in [90, 0, 0]],
          [degToRadian(angle) for angle in [90, 85, 0]],
          [degToRadian(angle) for angle in [90, 90, 0]]]
# Set the frames for keyframes
frames = [0, 10, 50]
# Add keyframes
add_keyframe_sequence(plane, 'rotation_euler', values, frames)

"""Add keyframes to animate the material color"""
# Get a reference to the Emission shader
mat_node = mat.node_tree.nodes["Emission"]
# Set values for keyframes
values = [(0, 0.5, 1, 1), (0.96, 0.42, 0, 1), (0.96, 0.42, 0, 1), (0, 0.5, 1, 1)]
# Set the frames for keyframes
frames = [100, 125, 132, 142]
# Add keyframes for the color of the Emission shader
add_keyframe_sequence(mat_node.inputs['Color'], 'default_value', values, frames)