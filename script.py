import bpy
import bmesh
import os
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_svg(svg_path):
    bpy.ops.import_curve.svg(filepath=svg_path)

def convert_curves_to_mesh():
    # Ensure we are in Object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select all curves
    curves = [obj for obj in bpy.context.scene.objects if obj.type == 'CURVE']
    bpy.ops.object.select_all(action='DESELECT')
    for curve in curves:
        curve.select_set(True)
        bpy.context.view_layer.objects.active = curve
        # Convert each curve to mesh individually to ensure the context is correct
        bpy.ops.object.convert(target='MESH')
        curve.select_set(False)

    # Return all mesh objects
    return [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

def scale_object_group(scale_factor=(1, 1, 1)):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None

    # Select all mesh objects
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Scale all selected objects together
    bpy.ops.transform.resize(value=scale_factor)

def extrude_walls(joined_mesh, height=3.0):
    # Get the mesh data
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.3), "orient_type":'NORMAL', "orient_matrix":((-0.252587, -0.967574, 0), (0.967574, -0.252587, 0), (0, 0, 1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "use_duplicated_keyframes":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "alt_navigation":True, "use_automerge_and_split":False})
    bpy.ops.object.editmode_toggle()

def apply_material(mesh_object, material_name="WallMaterial", color=(0.8, 0.8, 0.8, 1)):
    # Create a new material
    mat = bpy.data.materials.new(name=material_name)
    mat.diffuse_color = color
    
    # Check if the mesh object has any material slots
    if mesh_object.data.materials:
        # If it does, assign the new material to the first slot
        mesh_object.data.materials[0] = mat
    else:
        # Otherwise, append the new material to the mesh object
        mesh_object.data.materials.append(mat)


def join_meshes(mesh_objects):
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select mesh objects to join
    for obj in mesh_objects:
        obj.select_set(True)

    # Set the active object to the last selected object
    bpy.context.view_layer.objects.active = mesh_objects[-1]

    # Join selected objects into one
    bpy.ops.object.join()

    # Deselect all objects
    #bpy.ops.object.select_all(action='DESELECT')
    return bpy.context.active_object

def add_light(location=(10, -10, 10)):
    bpy.ops.object.light_add(type='SUN', location=location)

def add_camera(location=(10, -10, 10), rotation=(1.1, 0, 0.9)):
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    bpy.context.scene.camera = bpy.context.object

def render_image(filepath='render.png', engine='CYCLES', samples=100):
    bpy.context.scene.render.engine = engine
    bpy.context.scene.cycles.samples = samples
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

def save_fbx(obj_name):
    # Get the directory of the blend file
    blend_file_path = bpy.data.filepath
    blend_file_dir = os.path.dirname(blend_file_path)
    
    # Create the 'objects' directory if it doesn't exist
    objects_dir = os.path.join(blend_file_dir, 'objects')
    if not os.path.exists(objects_dir):
        os.makedirs(objects_dir)
    
    # Check if there is an active object
    if bpy.context.active_object:
        # Set the filepath for the OBJ export
        filepath = os.path.join(objects_dir, obj_name + '.fbx')
        
        # Export the active object as an OBJ file
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.active_object.select_set(True)
        bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
    else:
        print("No active object found.")

# Main script
clear_scene()
svg_file_path = "RgdM3.svg"  # Update this path
import_svg(svg_file_path)
mesh_objects = convert_curves_to_mesh()
scale_object_group((30, 30, 30))
merged = join_meshes(mesh_objects)
extrude_walls(merged)
apply_material(merged)
save_fbx("floor_plan")
#add_light()
#add_camera()
#render_image()
