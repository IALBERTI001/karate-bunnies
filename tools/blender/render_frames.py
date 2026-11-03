# Renders a list of puppet poses: blender -b --factory-startup -P render_frames.py -- poses.json outdir [res ortho centerZ line]
# For every frame writes outdir/color/<id>.png (the sprite) and outdir/mask/<id>.png (red belt, green headband, blue trousers).
import bpy, sys, os, json, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbpuppet; importlib.reload(kbpuppet)
argv = sys.argv[sys.argv.index('--') + 1:]
frames = json.load(open(argv[0])); out = argv[1]
res = int(argv[2]) if len(argv) > 2 else 512; ortho = float(argv[3]) if len(argv) > 3 else 5.0
cz = float(argv[4]) if len(argv) > 4 else 2.15; line = float(argv[5]) if len(argv) > 5 else 2.2
only = set(argv[6].split(',')) if len(argv) > 6 and argv[6] else None
bpy.ops.wm.read_factory_settings(use_empty=True)
scene, root, decals = kbpuppet.setup_scene(res, ortho, (0, cz), line)
os.makedirs(os.path.join(out, 'color'), exist_ok=True); os.makedirs(os.path.join(out, 'mask'), exist_ok=True)
for f in frames:
    if only and f['id'] not in only and f['id'].rsplit('-', 1)[0] not in only: continue
    objs = kbpuppet.build(root, f.get('pose'), decals); kbpuppet.place_root(root, f.get('pose'), f.get('yaw', 0))
    scene.render.use_freestyle = True; scene.render.filepath = os.path.join(out, 'color', f['id'] + '.png')
    bpy.ops.render.render(write_still=True)
    kbpuppet.to_mask(objs); scene.render.use_freestyle = False
    scene.render.filepath = os.path.join(out, 'mask', f['id'] + '.png'); bpy.ops.render.render(write_still=True)
    kbpuppet.clear(objs); print('KB-FRAME', f['id'], flush=True)
print('KB-DONE', len(frames), flush=True)
