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
# Strike and foot targets ending in _s are in SCREEN space: (across to the right toward the opponent, depth away from
# the camera, height). A strike aimed "forward" from a three-quarter view mostly travels toward the camera and reads
# as nothing on screen; the painted sprites aim every strike straight across the screen, so these do too.
GROUND = .15
def stance(**kw):
    p = dict(pelvis=(0, 0, -.32), pelvisRot=(6, 0, 0), spine=(4, 0, 0), chest=(0, 0, 0), head=(4, 0, 6),
             footL_s=(.8, .14, GROUND), footR_s=(-.78, -.12, GROUND), footLRot=(0, 0, 12), footRRot=(0, 0, -28),
             handL=(.28, -.56, .26), handR=(-.3, -.52, .12), eyes='open', mouth='smile', ears=0, ties=0, yaw=28, spin=0)
    p.update(kw); return p
FOCUS = dict(eyes='focus')
MOVES = {}
# Combo 1 - lead jab (kizami-zuki): the far fist snaps straight across at chin height, shoulders turn a little in.
MOVES['punch1'] = [stance(**FOCUS, chest=(0, 0, 8), handL=(.32, -.4, .22)),
                   stance(**FOCUS, chest=(4, 0, -10), head=(4, 0, 12), handL_s=(1.55, .05, 1.42), handR=(-.3, -.45, .14), mouth='open', ties=-8),
                   stance(**FOCUS, chest=(4, 0, -9), head=(4, 0, 11), handL_s=(1.45, .05, 1.4), handR=(-.3, -.45, .14), ties=-4),
                   stance(chest=(0, 0, -3))]
# Combo 2 - reverse punch (gyaku-zuki): the near fist chambers at the hip, then drives across the body at full reach
# as the hips turn; the other fist pulls back to the hip (hikite); back leg straight; kiai.
MOVES['punch2'] = [stance(**FOCUS, chest=(0, 0, -8), handR=(-.38, -.18, -.12), handL=(.3, -.62, .3)),
                   stance(**FOCUS, pelvis=(0, 0, -.3), pelvisRot=(8, 0, 10), chest=(6, 0, 12), head=(-14, 0, -6), handR_s=(1.75, -.2, 1.38),
                          handL=(.38, -.12, -.12), footR_s=(-.95, -.12, GROUND), mouth='shout', ties=-12),
                   stance(**FOCUS, pelvis=(0, 0, -.3), pelvisRot=(8, 0, 9), chest=(6, 0, 11), head=(-14, 0, -5), handR_s=(1.65, -.2, 1.38),
                          handL=(.38, -.12, -.12), footR_s=(-.95, -.12, GROUND), mouth='open', ties=-7),
                   stance(chest=(0, 0, 3))]
def kick(chamber, target, footRot, lean=-14, low=False, arms_out=False):
    base = dict(**FOCUS, pelvis=(0, 0, -.42 if low else -.06), footR_s=(-.42, -.1, GROUND), footRRot=(0, 0, -35))
    out = dict(handL=(.55, -.2, .4), handR=(-.55, -.1, .45)) if arms_out else {}
    return [stance(**base, footL_s=chamber, footLRot=(-30, 0, 0), spine=(lean * .4, 0, 0), handL=(.3, -.5, .3)),
            stance(**base, footL_s=target, footLRot=footRot, spine=(lean, 0, 0), chest=(lean * .3, 0, 0), head=(-lean * .6, 0, 10),
                   mouth='shout', ties=-14, **out),
            stance(**base, footL_s=(target[0] - .08, target[1], target[2] - .04), footLRot=footRot, spine=(lean * .9, 0, 0), chest=(lean * .3, 0, 0),
                   head=(-lean * .6, 0, 10), mouth='open', ties=-8, **out),
            stance(pelvis=(0, 0, -.34), handL=(.28, -.55, .24))]
# Combo 3 - roundhouse (mawashi-geri): knee chambers high, the leg snaps out flat at chest height, instep first.
MOVES['combo_kick'] = kick((.6, -.1, .85), (1.75, .05, 1.1), 'point', lean=-20)
# Combo 4 / back - spinning back kick (ushiro-geri): turn the back to the opponent and drive the heel across the
# screen, then come round facing them with the leg still out (as in the painted frames), and settle.
MOVES['spin_kick'] = [stance(**FOCUS, spin=110, chest=(0, 0, 8), ties=-12),
                      stance(**FOCUS, spin=180, pelvis=(0, 0, -.06), footL_s=(1.7, .1, .95), footLRot='point', footR_s=(-.2, 0, GROUND),
                             spine=(24, 0, 0), chest=(6, 0, 0), head=(-18, 0, 0), mouth='shout', ties=-20),
                      stance(**FOCUS, spin=360, pelvis=(0, 0, -.06), footL_s=(1.7, .05, 1.05), footLRot='point', footR_s=(-.3, -.1, GROUND),
                             spine=(-18, 0, 0), chest=(-4, 0, 0), head=(10, 0, 10), mouth='open', ties=-12),
                      stance(pelvis=(0, 0, -.34))]
# W - high kick: chamber, then the leg straight up past the head; standing leg straight, arms out for balance.
MOVES['high_kick'] = kick((.55, -.3, 1.15), (.95, -.35, 2.45), 'sole', lean=-32, arms_out=True)
# S - low sweep: drop low, the leg sweeps out flat along the floor.
MOVES['low_kick'] = kick((.55, -.1, .35), (1.8, .05, .22), 'point', lean=8, low=True)
# Forward - front push kick (mae-geri): knee up, then the sole drives across at chest height.
MOVES['front_kick'] = kick((.55, -.15, .95), (1.65, .05, 1.3), 'sole', lean=-18)
MOVES['idle'] = [stance()]

# ---------- posing ----------
def upd(): bpy.context.view_layer.update()
def set_bone(rig, name, R, pos=None):
    pb = rig.pose.bones[name]; pb.matrix_basis = Matrix.Identity(4); upd()
    head = Vector(pos) if pos is not None else pb.head.copy()
    pb.matrix = Matrix.Translation(head) @ (R @ pb.bone.matrix_local.to_3x3()).to_4x4(); upd()

def reach(rig, upper, lower, target, slack=.97):
    # Cartoon reach: lengthen a two-bone limb along its bones only (the lower bone inherits it, aligned) so IK can
    # land the paw or foot on a far target without the limb getting thicker.
    pu = rig.pose.bones[upper]; total = pu.bone.length + rig.pose.bones[lower].bone.length
    k = max(1.0, (Vector(target) - pu.head).length / (total * slack)); pu.scale = (1, k, 1); upd()

def apply_pose(rig, P):
    for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    upd()
    Rs = rotm((0, 0, P['spin']))
    set_bone(rig, 'root', Rs, (0, 0, 0))
    Rp = Rs @ rotm(P['pelvisRot']); set_bone(rig, 'pelvis', Rp, Rs @ (Vector((0, 0, 1.0)) + Vector(P['pelvis'])))
    Rsp = Rp @ rotm(P['spine']); set_bone(rig, 'spine', Rsp)
    Rc = Rsp @ rotm(P['chest']); set_bone(rig, 'chest', Rc)
    Rh = Rc @ rotm(P['head']); set_bone(rig, 'head', Rh)
    for s, L in ((1, 'L'), (-1, 'R')):
        Re = Rh @ rotm((-P['ears'], 0, 0)); set_bone(rig, f'ear_a.{L}', Re); set_bone(rig, f'ear_b.{L}', Re @ rotm((-P['ears'] * .6, 0, 0)))
        chest_head = rig.pose.bones['chest'].head.copy(); toscreen = rotm((0, 0, -P['yaw']))  # screen space -> model space
        hand = toscreen @ Vector(P['hand' + L + '_s']) if 'hand' + L + '_s' in P else chest_head + Rc @ Vector(P['hand' + L])
        reach(rig, f'upper_arm.{L}', f'forearm.{L}', hand)
        set_bone(rig, f'hand_ik.{L}', Rc, hand)
        foot = toscreen @ Vector(P['foot' + L + '_s']) if 'foot' + L + '_s' in P else Rs @ Vector(P['foot' + L])
        reach(rig, f'thigh.{L}', f'shin.{L}', foot)
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
scene, root_empty, decals = kbpuppet.setup_scene(RES, 6.8, (0, 2.3), 2.0 * RES / 512)
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
