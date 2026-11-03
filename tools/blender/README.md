# Blender bunny pipeline

One 3D bunny puppet, built from soft shapes, renders every fight frame and the shop 360 views. All views come from one
model, so the bunny looks the same in every pose and from every angle. It loads in the game with `?art=3d` (the painted sprites stay the default until approved).

| File | What it does |
| --- | --- |
| `kbpuppet.py` | The model: cream fur, material-green gi (so the game's recolour, piping, prints and patches still work), black belt, headband with flowing ribbons. It is posed by joint numbers (hips, torso, head, paws, ankles, face) and drawn in the game's painted style with brown brush lines. |
| `poses.py` | All poses: 8 turnaround views plus 18 fight animations x 4 frames. `python3 poses.py > poses.json` |
| `render_frames.py` | Runs inside Blender: renders each pose as a sprite (`color/`) and a mask pass (`mask/`: red belt, green headband, blue trousers). |
| `assemble.py` | Packs frames into sheets (`bunny3d-*.png`), exact masks (`parts-pass-*.png`, `belt-mask-*.png`) and `atlases.json`. Every fight sheet starts with the same standing frame, so fighters keep one size. |
| `install.py` | Copies a packed folder into `assets/` as the 3d set and writes `assets/animations-3d.json`. |

## Make the art (Blender 5.2, about 3 minutes for all 80 frames)

```
python3 tools/blender/poses.py > tools/blender/poses.json
blender -b --factory-startup -P tools/blender/render_frames.py -- tools/blender/poses.json out 512 6.4 2.4 2.0 [ids]
python3 tools/blender/assemble.py out out/atlas
python3 -I tools/blender/install.py out/atlas
python3 tools/soften-belt-masks.py --set 3d && python3 tools/gi-parts.py --set 3d && node refresh-assets.mjs
```

The optional `[ids]` re-renders only some frames, for example `combo_kick,victory` or `idle-0`.

Change a pose by editing `poses.py`, and the look by editing `kbpuppet.py`. Then rerun the steps above.
