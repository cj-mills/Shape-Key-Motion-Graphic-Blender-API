# Create a Shape Key Motion Graphic with the Blender Python API

> [!NOTE]
> **Retired from [christianjmills.com](https://christianjmills.com) on 2026-10-09.** This post was first published on 2021-03-24 at <https://christianjmills.com/posts/shape-key-motion-graphic-bpy/>, which now redirects here. It is kept as it was written; its tools and steps may be out of date.
>
> Source: [`posts/shape-key-motion-graphic-bpy/index.md@8229e99`](https://github.com/cj-mills/christianjmills/blob/8229e991c0be7f8c78a909f0d8a2ca74390dc1e6/posts/shape-key-motion-graphic-bpy/index.md) · Comments: <https://github.com/cj-mills/christianjmills/issues/31>

*This post covers how to create a simple shape-key motion graphic in Blender using the Python API.*

- [Introduction](#introduction)
- [Import Dependencies](#import-dependencies)
- [Define Helper Functions](#define-helper-functions)
- [Set up Scene](#set-up-scene)
- [Create and Position Camera](#create-and-position-camera)
- [Create Material With Emission Shader](#create-material-with-emission-shader)
- [Create a Plane With the Material](#create-a-plane-with-the-material)
- [Cut Out Center From Plane](#cut-out-center-from-plane)
- [Add Shape Keys](#add-shape-keys)
- [Add Keyframes](#add-keyframes)
- [Conclusion](#conclusion)

## Introduction

I decided to recreate this [short tutorial](https://www.youtube.com/watch?v=N3FZcFk-dZA&list=PLGKIkAXk1OeTti1rRVTJF_9_JCC3zY0bh&index=11) from YouTube to practice using the Blender Python API. This post goes through the code I came up with to replicate the tutorial plus some small additions.

<img src="./images/shape_key_mg_2.gif" data-fig-align="center" />

## Import Dependencies

The only dependencies strictly required for this tutorial are `bpy` and `bmesh`. The `bpy` package is the base API for Blender and the `bmesh` module provides access to Blender’s internal mesh editing API. I also used the `math` module from the Python Standard Library for one of my helper functions.

``` python
# The Blender Python API
import bpy
# Gives access to Blender's internal mesh editing API
import bmesh
# Provides access to mathematical functions
import math
```

## Define Helper Functions

I made some wrapper functions for the standard location, rotation, and scale transformations as well as getting the name of the active object.

You can get the name of the active object with `bpy.context.active_object.name`.

The three standard transformations can be accessed for individual objects with the following:

- `bpy.data.objects["object_name"].location`
- `bpy.data.objects["object_name"].rotation_euler`
- `bpy.data.objects["object_name"].scale`

I also made a function to empty the default collection so that nothing gets duplicated. Collections can be accessed with `bpy.data.collections["collection_name"]` or `bpy.data.collections[index]`.

Lastly, I made a function to easily add sequences of keyframes to a given object. The function uses the built-in `setattr()` method to set the desired value for the target object and uses the `object.keyframe_insert()` method to add the keyframe.

``` python
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
```

## Set up Scene

The first thing I do is set the Color Management property, View Transform, from the default value of `Filmic` to `Standard`. This setting can be accessed at `bpy.data.scenes["Scene"].view_settings.view_transform`.

Next, I set the background to the desired color. In my case, it’s pure black. The background color is stored in `bpy.data.worlds['World'].node_tree.nodes["Background"].inputs[0].default_value`.

The last setup step is to clear any objects added from the last time the script was run with the `clear_collection()` function.

``` python
"""Set up the scene"""
# Set View Transform to Standard
bpy.data.scenes["Scene"].view_settings.view_transform = "Standard"
# Set the Background color to pure black
bpy.data.worlds['World'].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
# Clear Collection
clear_collection(bpy.data.collections[0])
```

## Create and Position Camera

Cameras can be added using the `bpy.ops.object.camera_add()` method. I then positioned the camera using the wrapper functions I defined earlier.

``` python
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
```

## Create Material With Emission Shader

I decided to add some color to the motion graphic so I needed to create a new material. It is recommended to check if the material exists before trying to create it. This can be done in one line as shown below.

`material = bpy.data.materials.get(material_name) or bpy.data.materials.new(material_name)`

Since there’s is no light, I’ll add an `Emission` shader. This requires enabling nodes for the material with `material.use_nodes = True`.

Next, I remove the default `Principled_BSDF` node as well as any `Emission` nodes from earlier runs. Nodes can be removed using the `material.node_tree.nodes.remove()` method.

The `Emission` node needs to be linked to the first slot in the `Material Output` node. Nodes are linked using the `material.node_tree.links.new()` method.

``` python
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
```

## Create a Plane With the Material

The object in the above motion graphic is a plain. Plains can be added using the `bpy.ops.mesh.primitive_plane_add()` method.

I then assign the previously created material to the plane. Materials can be added to an object with `object.data.materials.append(material)`.

``` python
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
```

## Cut Out Center From Plane

The next step is to make a square hole in the plane like in the above Gif. This requires modifying the mesh for the plane.

Mesh data for the currently selected object is stored at `bpy.context.object.data`.

To edit the mesh, we need to get a BMesh representation. We first create an empty BMesh with `bm = bmesh.new()` and then fill it with the mesh using `bm.from_mesh(mesh)`.

We can make the square by adding a new inset to the plane using the `bmesh.ops.inset_individual()` method. Then, we delete the new face that gets created with `bmesh.ops.delete()`.

The mesh then needs to be updated with these alterations using `bm.to_mesh(mesh)`. Finally, we need to free the BMesh representation we created with `bm.free()`.

``` python
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
```

## Add Shape Keys

We can add shape keys with the `bpy.ops.object.shape_key_add()` method. To deform the plane, we need to access its vertices. We can do this in edit mode with the `bmesh` module.

We first enter edit mode for the plane with `bpy.ops.object.mode_set(mode="EDIT")`. We can then create a new BMesh representation for the current mesh in edit mode using `bm = bmesh.from_edit_mesh(mesh)`.

The vertices are stored in `bm.verts`, but we need to create our own list since we can’t index it directly.

Unlike the tutorial video, I just set the positions for the inner vertices directly. It took some trial and error to determine the correct indices for the inner vertices.

After freeing the BMesh representation, we can enter object mode with `bpy.ops.object.mode_set(mode="OBJECT")`.

#### First Shape Key

``` python
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
```

### Second Shape Key

The process for the second shape key is identical except it only moves two of the inner vertices.

``` python

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
```

## Add Keyframes

Before adding the keyframes, I set the render frame rate as well the start and end frames for the scene. The frame rate is stored at `bpy.context.scene.render.fps`.

The start and end frames are stored in `bpy.data.scenes['Scene'].frame_start` and `bpy.data.scenes['Scene'].frame_end` respectively.

``` python
"""Set up for animation"""
# Set the render frame rate to 60
bpy.context.scene.render.fps = 60

# Set the start frame to 0
bpy.data.scenes['Scene'].frame_start = 0
# Set the end frame to 200
bpy.data.scenes['Scene'].frame_end = 175
# Set the current frame to 0
bpy.data.scenes['Scene'].frame_current = 0
```

### Shape Keys

The shape keys for the plane are stored in `bpy.context.selected_objects[0].data.shape_keys`. Individual shape keys can be accessed with `bpy.context.selected_objects[0].data.shape_keys.key_blocks[index]`.

#### First Shape Key

``` python
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
```

#### Second Shape Key

``` python
"""Add keyframes to animate the second shape key"""
# Get a reference to the second shape key
zoomy_2 = shape_keys.key_blocks[2]
# Set values for keyframes
values = [0.0, 0.265, 0.95, 0.0]
# Set the frames for keyframes
frames = [100, 110, 132, 142]
# Add keyframes for the value of the second shape key
add_keyframe_sequence(zoomy_2, 'value', values, frames)
```

### Plane Rotation

``` python
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
```

### Material Color

The color for the Emision shader can be accessed at `material.node_tree.nodes["Emission"].inputs["Color"].default_value`.

``` python
"""Add keyframes to animate the material color"""
# Get a reference to the Emission shader
mat_node = mat.node_tree.nodes["Emission"]
# Set values for keyframes
values = [(0, 0.5, 1, 1), (0.96, 0.42, 0, 1), (0.96, 0.42, 0, 1), (0, 0.5, 1, 1)]
# Set the frames for keyframes
frames = [100, 125, 132, 142]
# Add keyframes for the color of the Emission shader
add_keyframe_sequence(mat_node.inputs['Color'], 'default_value', values, frames)
```

## Conclusion

I feel like this exercise was worthwhile as it forced me to learn about multiple parts of the API. Although, it took quite a bit longer than the nine minute length of the tutorial video to track down all the required parts of the API. Finding out how to properly add the Emission shader was particularly time consuming. I did not realize that the name used to create the Emission shader was different than the name used to reference it. Fortunately, Blender has been around for a while and someone on the internet had already asked how to do most of the individual steps.

**Tutorial Resources:** [GitHub Repository](https://github.com/cj-mills/Shape-Key-Motion-Graphic-Blender-API)
