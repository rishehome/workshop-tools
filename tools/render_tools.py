#!/usr/bin/env python3
"""Render workshop CAD in a configurable solid studio finish using Blender."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))


ROOT = Path(__file__).resolve().parents[1]



def step_python():
    configured = os.environ.get("FREECAD_PYTHON")
    if configured:
        return configured
    bundled = Path("/Applications/FreeCAD.app/Contents/Resources/bin/python")
    if bundled.is_file():
        return str(bundled)
    raise RuntimeError("STEP conversion requires FREECAD_PYTHON pointing to a Python with FreeCAD, Part and MeshPart installed.")


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    # Release prior models during large catalogue builds.
    for collection in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)


def cached_cad_mesh(source):
    directory = os.environ.get("RISHE_CAD_CACHE")
    if not directory:
        return None
    import hashlib
    digest = hashlib.sha256(source.read_bytes())
    for script in ("tessellate_step.py", "cad_selection.py"):
        digest.update(Path(__file__).with_name(script).read_bytes())
    return Path(directory) / (digest.hexdigest() + ".stl")


CAD_METADATA = {}


def load_mesh(source: Path):
    if source.suffix.lower() in {".step", ".stp", ".fcstd"}:
        cached = cached_cad_mesh(source)
        if cached is not None and cached.is_file():
            CAD_METADATA[str(source)] = json.loads(cached.with_suffix('.json').read_text())
            return load_mesh(cached)
        with tempfile.TemporaryDirectory(prefix="rishe-step-") as directory:
            mesh = Path(directory) / "body.stl"
            subprocess.run([step_python(), str(Path(__file__).with_name("tessellate_step.py")),
                            str(source), str(mesh)], check=True)
            CAD_METADATA[str(source)] = json.loads(mesh.with_suffix('.json').read_text())
            return load_mesh(mesh)
    if source.suffix.lower() == ".obj":
        bpy.ops.wm.obj_import(filepath=str(source))
    elif source.suffix.lower() == ".stl":
        if bpy.app.version >= (4, 0, 0):
            bpy.ops.wm.stl_import(filepath=str(source))
        else:
            bpy.ops.import_mesh.stl(filepath=str(source))
    else:
        raise ValueError(f"Unsupported mesh source: {source}")
    objects = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if not objects:
        raise ValueError(f"No mesh objects imported: {source}")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return objects


VIEWS = ("front", "side", "top", "back", "three-quarter")


def apply_finish(objects, color):
    material = bpy.data.materials.new("Rishe solid finish")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    # Hex colors are sRGB; Blender shader inputs use linear RGB.
    rgb = [int(color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    bsdf.inputs["Base Color"].default_value = (*linear, 1)
    bsdf.inputs["Roughness"].default_value = .52
    bsdf.inputs["Metallic"].default_value = 0
    for obj in objects:
        obj.data.materials.clear()
        obj.data.materials.append(material)


def render_preview(objects, destination: Path, view="three-quarter", source=None):
    for obj in list(bpy.context.scene.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)
    box = [v for obj in objects for v in (obj.matrix_world @ Vector(c) for c in obj.bound_box)]
    minimum = [min(getattr(v, axis) for v in box) for axis in "xyz"]
    maximum = [max(getattr(v, axis) for v in box) for axis in "xyz"]
    span = max(maximum[i] - minimum[i] for i in range(3)) or 1
    center = [(minimum[i] + maximum[i]) / 2 for i in range(3)]
    # OBJ exports are imported upright by Blender; STEP/STL bodies lie in XY.
    flat = source is not None and source.suffix.lower() in {".step", ".stp", ".stl", ".fcstd"}
    front = Vector((0, 0, 1) if flat else (0, -1, 0))
    up = Vector((0, 1, 0) if flat else (0, 0, 1))
    right = up.cross(front)
    directions = {"front": front, "side": right, "top": up, "back": -front,
                  "three-quarter": (front * 1.8 + right * 1.3 + up * 0.9).normalized()}
    offset = directions[view]
    camera_up = -front if view == "top" else up
    target = Vector(center)
    bpy.ops.object.camera_add(location=target + offset * span * 3)
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    backward = offset.normalized()
    camera_right = camera_up.cross(backward).normalized()
    camera_up = backward.cross(camera_right).normalized()
    from mathutils import Matrix
    camera.rotation_euler = Matrix((camera_right, camera_up, backward)).transposed().to_euler()
    camera.data.type = "ORTHO"
    projected_x = [(v - target).dot(camera_right) for v in box]
    projected_y = [(v - target).dot(camera_up) for v in box]
    camera.data.ortho_scale = max(max(projected_x)-min(projected_x),
                                 (max(projected_y)-min(projected_y)) * 1200 / 900) * 1.15
    camera.data.clip_end = span * 10
    for location, energy, size in (
        (target + (backward * 2 + camera_right + camera_up * 2) * span, 45, 2.2),
        (target + (backward + camera_right * -2 + camera_up) * span, 25, 2.0),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.data.energy = span * span * energy
        light.data.shape = "DISK"
        light.data.size = span * size
        light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.device = "GPU" if USE_GPU else "CPU"
    bpy.context.scene.cycles.samples = 48
    bpy.context.scene.cycles.use_denoising = True
    bpy.context.scene.world.use_nodes = True
    bpy.context.scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
    bpy.context.scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3
    bpy.context.scene.display.shading.light = "STUDIO"
    bpy.context.scene.display.shading.color_type = "MATERIAL"
    bpy.context.scene.display.shading.show_shadows = True
    bpy.context.scene.display.shading.show_cavity = True
    bpy.context.scene.render.resolution_x = 1200
    bpy.context.scene.render.resolution_y = 900
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.filepath = str(destination)
    bpy.context.scene.world.color = (0.62, 0.53, 0.43)
    bpy.context.scene.view_settings.view_transform = "Standard"
    # Composite transparent studio lighting over pure white, independent of exposure.
    scene = bpy.context.scene
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    nodes.clear()
    layers = nodes.new("CompositorNodeRLayers")
    over = nodes.new("CompositorNodeAlphaOver")
    over.inputs[1].default_value = (1, 1, 1, 1)
    composite = nodes.new("CompositorNodeComposite")
    scene.node_tree.links.new(layers.outputs["Image"], over.inputs[2])
    scene.node_tree.links.new(over.outputs["Image"], composite.inputs["Image"])
    bpy.ops.render.render(write_still=True)


def main():
    import argparse
    import hashlib
    import re
    from workshop_models import select
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--path', type=Path, default=ROOT, help='Repository-relative design, export or source')
    cli.add_argument('--color', default='9C9D9F', help='Six-digit sRGB hex; default Nardo-inspired gray')
    cli.add_argument('--dry-run', action='store_true')
    cli.add_argument('--device', choices=('auto', 'cpu'), default='auto')
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    args = cli.parse_args(argv)
    color = args.color.lstrip('#')
    if not re.fullmatch('[0-9a-fA-F]{6}', color):
        cli.error('--color must be a six-digit hex color')
    try:
        models = select(ROOT / args.path)
    except ValueError as exc:
        cli.error(str(exc))
    if not models:
        cli.error('No workshop models matched')
    for source, output in models:
        print(f'{source.relative_to(ROOT)} -> {output.relative_to(ROOT)}/renders', flush=True)
    if args.dry_run:
        return
    global bpy, Vector, USE_GPU
    import bpy
    from mathutils import Vector
    USE_GPU = False
    if args.device == 'auto' and sys.platform == 'darwin':
        try:
            preferences = bpy.context.preferences.addons['cycles'].preferences
            preferences.compute_device_type = 'METAL'
            preferences.get_devices()
            for device in preferences.devices:
                device.use = device.type == 'METAL'
            USE_GPU = any(device.type == 'METAL' for device in preferences.devices)
        except (TypeError, RuntimeError):
            pass
    for source, output in models:
        reset()
        objects = load_mesh(source)
        apply_finish(objects, color)
        renders = output / 'renders'
        renders.mkdir(parents=True, exist_ok=True)
        for view in VIEWS:
            render_preview(objects, renders / f'solid-{view}.png', view, source)
        (renders / 'sources.json').write_text(json.dumps({
            'source': source.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'color_srgb': '#' + color.upper(), 'roughness': .52,
            'blender': bpy.app.version_string, 'views': VIEWS,
            'cad': CAD_METADATA.get(str(source)),
        }, indent=2) + '\n')
    print(f'Rendered {len(models)} workshop models.', flush=True)


if __name__ == '__main__':
    main()
