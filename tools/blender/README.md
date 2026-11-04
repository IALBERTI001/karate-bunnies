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

## The weighted rig (Nov 3): `kbrig.py` + `moves.py`

The bunny is built once in sections (head, torso, pelvis, two-part arms and legs, paws, feet, two-part ears,
two-part ribbons). Each section is weighted to its own bone, with blends only at the elbows, knees, waist and mid-ear.
Arms and legs use IK. Faces are keyed parts (open, focus, happy, hurt; smile, open, shout).

`moves.py` keys the 4-hit combo (jab, reverse punch, roundhouse, spinning back kick) and the WASD kicks (high, low,
front push, spinning back kick), 4 frames each, on one timeline with a marker per move. It renders colour and mask
passes and saves `bunny-rig.blend`, so you can open it, scrub the moves and pose the bunny by hand.

```
blender -b --factory-startup -P tools/blender/moves.py -- out [moves] [res]
```

Lessons learned:
- Aim strikes in screen space. From a three-quarter view, a strike aimed "forward" mostly travels toward the camera.
- Don't use Blender's IK stretch: it scales bones in every direction, so stretched limbs get fat. `moves.py` lengthens limbs along their bones only.
- Turn Preserve Volume off on stretched limbs.

## Movement rules (Nov 3): `kbmove.py`
Every pose goes through a governor (see the `natural-movement-rules` skill): the centre of gravity is kept over the
declared support (hips travel on two feet, the trunk leans away from the reaching limb on one), planted feet stay down
(the body sinks instead), knees and elbows are placed by rule (standing knees track the toes, lifted knees lead) with an
exact two-bone solve (Blender's IK constraints are muted), the standing foot pivots with the hips, and kicks name the
striking surface and target so the impact is centred on it. Each frame prints a `KB-GOV` line and each move a `KB-MOVE`
line with any broken rule; `python3 govsheet.py <out> <log> sheet.png` draws the rules on the frames.
`python3 tools/blender/kbmove_test.py` unit-tests the rule math.
