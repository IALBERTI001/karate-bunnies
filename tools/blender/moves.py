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
def stance(**kw):
    p = dict(root=(0, 0, 0), spin=0, pelvis=(0, 0, -.3), pelvisRot=(4, 0, -58), spine=(4, 0, -4), chest=(0, 0, -8), head=(4, 0, 14),
             footL=(.12, -.7, GROUND), footR=(-.16, .7, GROUND), footLRot=(0, 0, -8), footRRot=(0, 0, -60),
             handL=(.1, -.62, .22), handR=(-.12, -.32, .24), eyes='open', mouth='smile', ears=0, ties=0, yaw=90)
    p.update(kw); return p
FOCUS = dict(eyes='focus')
MOVES = {}
# Combo 1 - jab (kizami-zuki): the lead foot slides in, the lead hip and shoulder push forward (turning even more
# side-on), the lead fist drives straight to chin height; the head stays level; slide back to stance.
MOVES['punch1'] = [stance(**FOCUS, pelvis=(0, 0, -.26), handL=(.12, -.5, .2)),
                   stance(**FOCUS, root=(0, -.28, 0), footL=(.12, -.8, GROUND), pelvisRot=(6, 0, -72), chest=(2, 0, -14), head=(4, 0, 32),
                          handL=(.12, -1.55, .3), handR=(-.12, -.3, .26), mouth='open', ties=-8),
                   stance(**FOCUS, root=(0, -.3, 0), footL=(.12, -.8, GROUND), pelvisRot=(6, 0, -74), chest=(2, 0, -14), head=(4, 0, 32),
                          handL=(.12, -1.52, .3), handR=(-.12, -.3, .26), ties=-4),
                   stance(root=(0, -.1, 0))]
# Combo 2 - reverse punch (gyaku-zuki): from side-on, the rear heel drives and the back leg straightens, the hips
# turn square to the target, the shoulders follow, the rear fist drives straight out as the lead fist pulls back
# to the hip (hikite); the front knee bends over the foot; head level; kiai.
MOVES['punch2'] = [stance(**FOCUS, handR=(-.22, -.05, -.28), handL=(.1, -.66, .22)),
                   stance(**FOCUS, root=(0, -.15, 0), pelvis=(0, 0, -.34), pelvisRot=(8, 0, -32), spine=(6, 0, 2), chest=(2, 0, 4), head=(2, 0, 4),
                          footL=(.12, -.85, GROUND), footR=(-.16, .9, GROUND), footRRot=(0, 0, -25),
                          handR=(-.02, -1.25, .24), handL=(.24, .02, -.26), mouth='shout', ties=-12),
                   stance(**FOCUS, root=(0, -.15, 0), pelvis=(0, 0, -.34), pelvisRot=(8, 0, -33), spine=(6, 0, 2), chest=(2, 0, 4), head=(2, 0, 4),
                          footL=(.12, -.85, GROUND), footR=(-.16, .9, GROUND), footRRot=(0, 0, -25),
                          handR=(-.02, -1.22, .24), handL=(.24, .02, -.26), mouth='open', ties=-7),
                   stance(root=(0, -.05, 0))]
# Combo 3 - roundhouse (mawashi-geri) with the rear leg, flowing on from the reverse punch: the front (supporting)
# foot pivots out until its heel points at the target, the rear knee chambers high and comes across, the hip turns
# over, the trunk leans away to balance the leg, the kicking-side arm swings back, the other guards the face; the
# shin snaps out flat, instep first; re-chamber and set down.
def rear_kick(chamber, target, foot_aim, lean, roll=0, hips_turn=60, pivot=100, low=False, step=0, arms_back=True):
    sup = dict(footL=(.1, -.6, GROUND), footLRot=(0, 0, pivot), pelvis=(0, 0, -.42 if low else -.12))
    back = dict(handR=(-.35, .3, -.05), handL=(.12, -.45, .3)) if arms_back else {}
    return [stance(**FOCUS, **sup, footR=chamber, footRRot=foot_aim, pelvisRot=(lean * .4, roll * .4, hips_turn * .4 - 30), spine=(lean * .3, 0, 0), chest=(0, 0, -hips_turn * .3),
                   handR=(-.2, -.1, .1)),
            stance(**FOCUS, **sup, root=(0, -step, 0), footR=target, footRRot=foot_aim, pelvisRot=(lean, roll, hips_turn - 30), spine=(lean * .5, roll * .5, 0),
                   chest=(0, 0, -hips_turn * .55), head=(0, 0, 10), mouth='shout', ties=-16, **back),
            stance(**FOCUS, **sup, root=(0, -step, 0), footR=(target[0], target[1] + .05, target[2] - .05), footRRot=foot_aim, pelvisRot=(lean * .95, roll, hips_turn - 30),
                   spine=(lean * .5, roll * .5, 0), chest=(0, 0, -hips_turn * .55), head=(0, 0, 10), mouth='open', ties=-10, **back),
            stance(root=(0, -step * .6, 0))]
MOVES['combo_kick'] = rear_kick((-.15, -.3, 1.0), (-.02, -1.35, 1.2), 'point', -24, roll=14, hips_turn=75, pivot=120, step=.15)
# Combo 4 / back - spinning back kick (ushiro-geri): turn on the front foot until the back faces the target, knee to
# the chest, trunk hunched forward; drive the heel straight back at the target, the hips pushing back behind it;
# land while the back still faces it, then turn back into stance. Frame 1 is the back view the game uses.
MOVES['spin_kick'] = [stance(**FOCUS, spin=95, pelvisRot=(14, 0, 0), spine=(14, 0, 0), chest=(0, 0, 0), head=(0, 0, -35),
                             footL=(.0, -.2, GROUND), footR=(-.25, -.15, .7), footRRot='point', handL=(.15, -.35, .2), handR=(-.15, -.35, .2), ties=-14),
                      stance(**FOCUS, spin=180, root=(0, -.25, 0), pelvisRot=(30, 0, -50), spine=(22, 0, -10), chest=(0, 0, -10), head=(-10, 0, 30),
                             footL=(.08, -.3, GROUND), footR=(-.05, 1.2, 1.05), footRRot='sole', handL=(.2, -.35, .1), handR=(-.2, -.35, .1), mouth='shout', ties=-20),
                      stance(**FOCUS, spin=180, root=(0, -.25, 0), pelvisRot=(28, 0, -50), spine=(20, 0, -10), chest=(0, 0, -10), head=(-10, 0, 30),
                             footL=(.08, -.3, GROUND), footR=(-.05, 1.17, 1.0), footRRot='sole', handL=(.2, -.35, .1), handR=(-.2, -.35, .1), mouth='open', ties=-12),
                      stance(root=(0, -.15, 0))]
# W - high kick with the rear leg: knee chambers high, then the straight leg rises past the head as the trunk leans
# back to balance it (the lower the trunk, the higher the leg) and the hips push forward; arms keep guard.
MOVES['high_kick'] = rear_kick((-.12, -.4, 1.35), (-.06, -.85, 2.5), 'sole', -36, hips_turn=20, pivot=40, step=.1, arms_back=False)
# S - low kick: sink on the bent supporting leg, the front foot pivots, the hip turns over and the rear shin
# sweeps low at the opponent's legs; the trunk stays upright.
MOVES['low_kick'] = rear_kick((-.15, -.25, .45), (-.02, -1.35, .3), 'point', -6, hips_turn=55, pivot=110, low=True, step=.1)
# Forward - front push kick (mae-geri) with the rear leg: knee up to the chest, toes pulled back, then the hips thrust
# forward behind the ball of the foot at chest height, upper body upright; retract to the chamber and set down.
MOVES['front_kick'] = rear_kick((-.12, -.3, 1.1), (-.05, -1.3, 1.35), 'sole', -12, hips_turn=15, pivot=30, step=.2, arms_back=False)
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
scene, root_empty, decals = kbpuppet.setup_scene(RES, 7.4, (0, 2.5), 2.0 * RES / 512)
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
