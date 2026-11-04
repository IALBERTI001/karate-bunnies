# Teaches the rigged bunny its moves and renders them:
#   blender -b --factory-startup -P moves.py -- <out dir> [only moves, comma separated] [res]
# Every move is 4 game frames keyed on one timeline (a marker names each move); the .blend is saved beside the renders
# so a person can open it, scrub the moves and pose the bunny by hand.
# Poses follow the painted sprites: wide bent-knee stance, fists up; strikes reach out toward the opponent (screen
# right), the body leans into punches and back from kicks, the active pose is the extreme, recovery settles low.
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, kbpuppet, kbrig
importlib.reload(kbpuppet); importlib.reload(kbrig)
from mathutils import Vector, Matrix
from kbrig import rotm

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moves-out')
ONLY = set(argv[1].split(',')) if len(argv) > 1 and argv[1] else None
RES = int(argv[2]) if len(argv) > 2 else 512

# ---------- the moves ----------
# Real karate body mechanics (see the karate-body-mechanics skill), not stretchy limbs: reach comes from the stance,
# a step, the hips and shoulders turning and the trunk leaning. Arms and legs keep their length.
# The fighter stands on the line toward the opponent: model -Y is toward the opponent (screen right, yaw 90), +X is
# its left = away from the camera. Orthodox stance: left foot and left fist lead; the hips and chest turn side-on
# (hanmi) to their right, which is what shows the chest to the camera.
# Hands are offsets from the chest bone's head and feet are positions on the ground, both in body space (they turn
# with a spin, not with the hips); `root` steps the whole fighter.
GROUND = .15
# Poses below are read from side-on reference sheets of a real karate athlete (design/karate-refs, generated with
# ChatGPT on Nov 3 2026): long low stance, upright torso turned ~55 degrees toward the camera; punches keep the head
# at one height and the torso upright while the stance lengthens; kick chambers stand tall on a straight supporting
# leg; kick impacts lean the trunk back just enough to balance the leg (about 30 degrees for a head kick).
def stance(**kw):
    p = dict(root=(0, 0, 0), spin=0, pelvis=(0, 0, -.28), pelvisRot=(0, 0, -55), spine=(2, 0, 0), chest=(0, 0, -5), head=(0, 0, 10),
             footL=(.1, -.82, GROUND), footR=(-.15, .78, GROUND), footLRot=(0, 0, -5), footRRot=(0, 0, -60),
             handL=(.14, -.72, .18), handR=(-.08, -.28, .28), eyes='open', mouth='smile', ears=0, ties=0, yaw=90)
    p.update(kw); return p
FOCUS = dict(eyes='focus')
MOVES = {}
# Combo 1 - jab (kizami-zuki): the front foot slides on and the stance lengthens, the lead hip and shoulder drive,
# the body turns more side-on, the lead arm extends level at chin height, rear fist at the chin, head level.
MOVES['punch1'] = [stance(**FOCUS, pelvis=(0, 0, -.3)),
                   stance(**FOCUS, root=(0, -.18, 0), footL=(.1, -1.02, GROUND), pelvis=(0, 0, -.33), pelvisRot=(0, 0, -66), chest=(0, 0, -9),
                          handL=(.12, -1.0, .24), ties=-6),
                   stance(**FOCUS, root=(0, -.24, 0), footL=(.1, -1.08, GROUND), pelvis=(0, 0, -.34), pelvisRot=(0, 0, -72), chest=(0, 0, -12),
                          handL=(.1, -1.6, .3), mouth='open', ties=-10),
                   stance(root=(0, -.08, 0))]
# Combo 2 - reverse punch (gyaku-zuki): rear fist to the hip; then the rear heel drives, the back leg straightens and
# the stance lengthens and lowers, the hips turn toward square while the torso stays upright, the rear arm drives out
# level at shoulder height and the lead fist pulls back to the hip; head level.
MOVES['punch2'] = [stance(**FOCUS, handR=(-.2, -.05, -.3), handL=(.12, -.78, .18)),
                   stance(**FOCUS, root=(0, -.1, 0), pelvis=(0, 0, -.36), pelvisRot=(0, 0, -38), chest=(0, 0, 0), footL=(.1, -.98, GROUND),
                          footR=(-.15, .98, GROUND), footRRot=(0, 0, -35), handR=(-.05, -.85, .2), handL=(.24, -.1, -.22), ties=-6),
                   stance(**FOCUS, root=(0, -.14, 0), pelvis=(0, 0, -.38), pelvisRot=(0, 0, -30), chest=(0, 0, 4), footL=(.1, -1.02, GROUND),
                          footR=(-.15, 1.02, GROUND), footRRot=(0, 0, -30), handR=(-.02, -1.6, .3), handL=(.26, .05, -.28), mouth='shout', ties=-12),
                   stance(root=(0, -.05, 0))]
def chamber_pose(foot, pivot, **kw):  # stand tall on the front leg, rear knee up, supporting foot pivoting
    return stance(**FOCUS, pelvis=(0, 0, -.02), pelvisRot=(-3, 0, -35), spine=(-3, 0, 0), chest=(0, 0, -12),
                  footL=(.06, -.62, GROUND), footLRot=(0, 0, pivot), footR=foot, **kw)
def kick(chamber, chamber_aim, target, aim, lean, pivot, hips=10, chest=-35, support_bend=0, arm_back=True, step=.1):
    sup = dict(footL=(.06, -.62, GROUND), footLRot=(0, 0, pivot), pelvis=(0, 0, -.02 - support_bend))
    arms = dict(handR=(-.32, .38, -.18), handL=(.1, -.42, .34)) if arm_back else dict(handL=(.14, -.55, .26), handR=(-.1, -.3, .3))
    hit = lambda d, m: stance(**FOCUS, **sup, root=(0, -step, 0), footR=(target[0], target[1] + d, target[2] - d), footRRot=aim,
                             pelvisRot=(lean, 0, hips), spine=(lean * .25, 0, 0), chest=(0, 0, chest), head=(0, 0, 12), mouth=m, ties=-16, **arms)
    return [chamber_pose(chamber, pivot * .6, footRRot=chamber_aim, handL=(.14, -.55, .26), handR=(-.1, -.3, .3)),
            hit(0, 'shout'), hit(.05, 'open'), stance(root=(0, -step * .5, 0))]
# Combo 3 - roundhouse to the head (rear leg): chamber tall with the knee at the belt; at impact the supporting foot
# has pivoted ~135 degrees, the hip has turned over, the leg is flat at head height, the trunk leans back ~30 degrees,
# the kicking-side arm swings back and the other guards the face.
MOVES['combo_kick'] = kick((-.12, -.38, .95), 'point', (-.05, -1.45, 2.2), 'point', lean=-30, pivot=135, hips=10, chest=-38)
# Combo 4 / back - spinning back kick (ushiro-geri): pivot on the front foot and look over the shoulder as the rear
# knee draws up to the chest; at impact the back faces the camera and the target, the trunk leans away and the heel
# drives out flat at chest height; land and turn back into stance. Frame 1 is the back view the game uses.
MOVES['spin_kick'] = [stance(**FOCUS, spin=110, pelvis=(0, 0, -.04), pelvisRot=(12, 0, 0), spine=(8, 0, 0), chest=(0, 0, 0), head=(0, 0, -50),
                             footL=(.0, -.25, GROUND), footR=(-.2, -.2, .9), footRRot='point', handL=(.15, -.35, .2), handR=(-.15, -.35, .2), ties=-14),
                      stance(**FOCUS, spin=180, root=(0, -.2, 0), pelvis=(0, 0, -.02), pelvisRot=(28, 0, -70), spine=(14, 0, -10), chest=(0, 0, -10), head=(-6, 0, 40),
                             footL=(.05, -.3, GROUND), footR=(-.05, 1.45, 1.45), footRRot='sole', handL=(.2, -.35, .1), handR=(-.2, -.35, .1), mouth='shout', ties=-20),
                      stance(**FOCUS, spin=180, root=(0, -.2, 0), pelvis=(0, 0, -.02), pelvisRot=(26, 0, -70), spine=(13, 0, -10), chest=(0, 0, -10), head=(-6, 0, 40),
                             footL=(.05, -.3, GROUND), footR=(-.05, 1.4, 1.4), footRRot='sole', handL=(.2, -.35, .1), handR=(-.2, -.35, .1), mouth='open', ties=-12),
                      stance(root=(0, -.1, 0))]
# W - high front kick (jodan mae-geri, rear leg): knee to the chest with the foot hanging under it; then the leg rises
# nearly vertical with the sole above head height, the trunk leans back ~20 degrees, the supporting leg stays straight.
MOVES['high_kick'] = kick((-.12, -.5, .9), 'point', (-.08, -1.45, 2.65), 'sole', lean=-30, pivot=40, hips=-40, chest=-8, arm_back=False)
# S - low roundhouse (gedan mawashi-geri, rear leg): the knee lifts low and comes across, the supporting knee bends,
# the hip turns over and the shin swings flat at knee height; trunk upright.
MOVES['low_kick'] = kick((-.08, -.3, .62), 'point', (-.05, -1.5, .72), 'point', lean=-6, pivot=110, hips=0, chest=-30, support_bend=.16, arm_back=False)
# Forward - front push kick (chudan mae-geri, rear leg): same tall chamber, then the hips thrust forward behind the
# sole at stomach height with the upper body nearly upright.
MOVES['front_kick'] = kick((-.12, -.42, .85), 'point', (-.08, -1.8, 1.55), 'sole', lean=-14, pivot=60, hips=-55, chest=-8, arm_back=False, step=.18)
MOVES['idle'] = [stance()]

# ---------- posing ----------
def upd(): bpy.context.view_layer.update()
def set_bone(rig, name, R, pos=None):
    pb = rig.pose.bones[name]; pb.matrix_basis = Matrix.Identity(4); upd()
    head = Vector(pos) if pos is not None else pb.head.copy()
    pb.matrix = Matrix.Translation(head) @ (R @ pb.bone.matrix_local.to_3x3()).to_4x4(); upd()

def clamp_reach(rig, upper, lower, target, slack=.985):
    # Limbs never stretch: a target out of reach is pulled in along the limb, so reach has to come from the body.
    pu = rig.pose.bones[upper]; total = pu.bone.length + rig.pose.bones[lower].bone.length
    base = pu.head.copy(); d = Vector(target) - base
    return base + d.normalized() * min(d.length, total * slack) if d.length > 1e-6 else Vector(target)

def apply_pose(rig, P):
    for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    upd()
    Rs = rotm((0, 0, P['spin'])); R0 = Vector(P['root'])
    set_bone(rig, 'root', Rs, R0)
    Rp = Rs @ rotm(P['pelvisRot']); set_bone(rig, 'pelvis', Rp, R0 + Rs @ (kbrig.warp((0, 0, 1.0)) + Vector(P['pelvis'])))
    Rsp = Rp @ rotm(P['spine']); set_bone(rig, 'spine', Rsp)
    Rc = Rsp @ rotm(P['chest']); set_bone(rig, 'chest', Rc)
    # Karate keeps the head level: the head takes the body's turn but not its lean, plus its own nod, tilt and turn.
    turn = P['spin'] + P['pelvisRot'][2] + P['spine'][2] + P['chest'][2]
    Rh = rotm((0, 0, turn)) @ rotm(P['head']); set_bone(rig, 'head', Rh)
    for s, L in ((1, 'L'), (-1, 'R')):
        Re = Rh @ rotm((-P['ears'], 0, 0)); set_bone(rig, f'ear_a.{L}', Re); set_bone(rig, f'ear_b.{L}', Re @ rotm((-P['ears'] * .6, 0, 0)))
        chest_head = rig.pose.bones['chest'].head.copy()
        hand = clamp_reach(rig, f'upper_arm.{L}', f'forearm.{L}', chest_head + Rs @ Vector(P['hand' + L]))
        set_bone(rig, f'hand_ik.{L}', Rc, hand)
        foot = clamp_reach(rig, f'thigh.{L}', f'shin.{L}', R0 + Rs @ Vector(P['foot' + L]))
        fr = P['foot' + L + 'Rot']
        if isinstance(fr, str):  # aim the foot from the hip along the leg: toes pointed ('point') or sole to the target ('sole')
            hipj = rig.pose.bones[f'thigh.{L}'].head.copy(); d = (foot - hipj).normalized()
            up = Vector((0, 0, 1)); side = d.cross(up).normalized() if abs(d.z) < .95 else Vector((1, 0, 0))
            if fr == 'point': ax_y, ax_z = -d, side.cross(d).normalized()          # foot's -Y (toes) along the leg
            else: ax_z, ax_y = -d, -(up - d * up.dot(d)).normalized() if abs(d.z) < .95 else Vector((0, 1, 0))  # sole (-Z) to target, toes up
            ax_x = ax_y.cross(ax_z).normalized(); Rf = Matrix((ax_x, ax_y, ax_z)).transposed()
            set_bone(rig, f'foot_ik.{L}', Rf, foot)  # Rf turns the rest foot (toes -Y, top +Z) to the new axes
        else:
            set_bone(rig, f'foot_ik.{L}', Rs @ rotm(fr), foot)

    for t in ('tie1', 'tie2'):
        set_bone(rig, f'{t}_a', Rh @ rotm((0, 0, P['ties']))); set_bone(rig, f'{t}_b', Rh @ rotm((0, 0, P['ties'] * 1.6)))

def key_frame(rig, f, P):
    for pb in rig.pose.bones:
        pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f); pb.keyframe_insert('scale', frame=f)
    rig.rotation_euler = (0, 0, math.radians(P['yaw'])); rig.keyframe_insert('rotation_euler', frame=f)
    for key, objs in kbrig.EXPRESSIONS.items():
        on = key in ('eyes_' + P['eyes'], 'mouth_' + P['mouth'])
        for o in objs: o.hide_render = not on; o.keyframe_insert('hide_render', frame=f)

def constant_keys(ids):
    for idb in ids:
        ad = idb.animation_data
        if not ad or not ad.action: continue
        for fc in getattr(ad.action, 'fcurves', []) or []:
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
        for layer in getattr(ad.action, 'layers', []) or []:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# ---------- painterly finish: anisotropic Kuwahara over the colour pass (alpha kept) ----------
def kuwahara(scene, size=4):
    try:
        tree = bpy.data.node_groups.new('Paint', 'CompositorNodeTree'); scene.compositing_node_group = tree
        tree.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = tree.nodes.new('CompositorNodeRLayers'); kw = tree.nodes.new('CompositorNodeKuwahara'); out = tree.nodes.new('NodeGroupOutput')
        sa = tree.nodes.new('CompositorNodeSetAlpha')
        for name, val in (('Size', size), ('Uniformity', 4), ('Sharpness', .6), ('Eccentricity', 1.2)):
            if name in kw.inputs: kw.inputs[name].default_value = val
        if 'Type' in kw.inputs:
            try: kw.inputs['Type'].default_value = 'Anisotropic'
            except Exception: pass
        elif hasattr(kw, 'variation'): kw.variation = 'ANISOTROPIC'
        tree.links.new(rl.outputs['Image'], kw.inputs['Image']); tree.links.new(kw.outputs['Image'], sa.inputs['Image'])
        tree.links.new(rl.outputs['Alpha'], sa.inputs['Alpha']); tree.links.new(sa.outputs['Image'], out.inputs[0])
        print('KB-KUWAHARA on', flush=True); return tree
    except Exception as e:
        print('KB-KUWAHARA off:', e, flush=True); return None

# ---------- build, key, render ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene, root_empty, decals = kbpuppet.setup_scene(RES, 8.0, (0, 2.7), 2.0 * RES / 512)
bpy.data.objects.remove(root_empty)
rig = kbrig.build_armature(scene); parts = kbrig.build_body(rig, decals)
names = [n for n in MOVES if not ONLY or n in ONLY]
frames = []
for k, name in enumerate(names):
    m = scene.timeline_markers.new(name, frame=k * 10 + 1)
    for i, P in enumerate(MOVES[name]):
        f = k * 10 + 1 + i; apply_pose(rig, P); key_frame(rig, f, P); frames.append((f, f'{name}-{i}'))
constant_keys([rig] + [o for objs in kbrig.EXPRESSIONS.values() for o in objs])
scene.frame_start, scene.frame_end = 1, frames[-1][0]
os.makedirs(os.path.join(OUT, 'color'), exist_ok=True); os.makedirs(os.path.join(OUT, 'mask'), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'bunny-rig.blend'))
paint = kuwahara(scene)
for f, fid in frames:
    scene.frame_set(f); scene.render.filepath = os.path.join(OUT, 'color', fid + '.png'); bpy.ops.render.render(write_still=True)
    print('KB-FRAME', fid, flush=True)
if paint is not None: scene.compositing_node_group = None
scene.render.use_freestyle = False; kbpuppet.to_mask(parts.objs)
for f, fid in frames:
    scene.frame_set(f); scene.render.filepath = os.path.join(OUT, 'mask', fid + '.png'); bpy.ops.render.render(write_still=True)
print('KB-DONE', len(frames), flush=True)
