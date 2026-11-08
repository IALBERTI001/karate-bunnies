# Karate Bunny v2: a body that bends and a clean rig, built the way professional character artists and riggers do
# (blender-character-rig skill, Nov 7 2026). Proportions come from the painted turnaround sheet (kb-turnaround-v2.png):
# floor to crown 2.6 units, head chin 1.56 to crown 2.6 (40% of the height, wider than tall), ears 0.8 above the crown,
# shoulders 1.45, belt 0.92, trouser hems 0.3, hip joints 0.84, a leg about 0.7 long, big oval feet.
#  - Body: ONE continuous mesh (skin modifier + subsurf) through hips, knees, shoulders and elbows, with extra rings at
#    every joint, so limbs fold instead of opening a seam. It is the gi; head, fists, feet, ears are rigid parts.
#  - Rig: torso control (centre of gravity), hips, spine, chest, neck, head; IK legs with a knee pole parented to the
#    foot control (a knee always points where its foot points); IK arms with elbow poles; knees and elbows hinge only.
#  - Weights: automatic (bone heat) on the body = smooth gradients across every joint.
#  - Outlines: an inverted ink hull on every solid part (kbrig.ink_material).
# Faces -Y, +X is the character's left, feet on z=0.
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix
D = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else r'C:\Users\Ultim\Downloads\KarateBunnies3D'
if D not in sys.path: sys.path.insert(0, D)
import importlib, kbpuppet, kbrig
from kbpuppet import _toon, _flat

INK_T = .028
# v3 proportions (user, Nov 8 2026: "legs are usually longer anyways"; reference: a 2D karate fighter whose legs are about
# half her height). Thigh and shin are each LEG long, so every kick shows a thigh, a knee and a shin with air around them.
# Everything above the hips is the v2 body lifted by DZ; legs are slim and set under the body.
LEG = .52                      # thigh = shin (v2: .34, shorter than the belly was deep, so a raised knee vanished into it)
ANKLE_Z = .16
HIP_Z = ANKLE_Z + 2 * LEG      # 1.2 (v2 .84)
DZ = HIP_Z - .84               # the v2 upper body sits this much higher
HIP_X = .21                    # hip joints under the body (v2 .29: legs hung off the belly's sides)
KNEE_Z = ANKLE_Z + LEG
def up(v): return (v[0], v[1], v[2] + DZ)

HEAD_C, HEAD_R = Vector((0, 0, 2.08 + DZ)), Vector((.66, .6, .53))
def face_y(x, z, out=0.0):
    q = 1 - (x / HEAD_R.x) ** 2 - ((z + DZ - HEAD_C.z) / HEAD_R.z) ** 2  # z in v2 coordinates (the face is placed before the lift)
    return -(HEAD_R.y + out) * math.sqrt(max(q, 0.0))

BELT = False   # user, Nov 8 2026: "remove the belt" (ring, knot and hanging ends); the bend bones stay so old actions still load

def split_off(body, groups, suffix):
    # A sleeve that is part of the one continuous body has no outline where it lies against the jacket, so a guarding
    # arm melts into the chest ("the arms are sucked into the body", Nov 8 2026). Faces that belong to the arm become
    # their own object (same weights, same armature; the shared seam vertices stay welded in place), so each arm gets
    # its own ink line wherever it crosses the body.
    import bmesh
    gi = {body.vertex_groups[n].index for n in groups if n in body.vertex_groups}
    w = [sum(g.weight for g in v.groups if g.group in gi) for v in body.data.vertices]
    keep = {p.index for p in body.data.polygons if min(w[i] for i in p.vertices) > .5}
    part = body.copy(); part.data = body.data.copy(); part.name = body.name + suffix
    for c in body.users_collection: c.objects.link(part)
    for ob, inside in ((part, False), (body, True)):
        bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if (f.index in keep) == inside], context='FACES')
        bm.to_mesh(ob.data); bm.free()
    return part

def mats(tag, belt, gear):
    M = {}
    M['GI'] = _toon(f'{tag}_gi', '#f4f3ee', '#c4c8d2', '#ffffff')
    M['FUR'] = _toon(f'{tag}_fur', '#f8e7d8', '#e0c0ab', '#fff6ee')
    M['PINK'] = _toon(f'{tag}_pink', '#f7a596', '#e5877b')
    M['BELT'] = _toon(f'{tag}_belt', belt[0], belt[1])
    M['GEAR'] = _toon(f'{tag}_gear', gear[0], gear[1])
    M['EYE'] = _toon(f'{tag}_eye', '#3a1d10', '#24110a'); M['IRIS'] = _toon(f'{tag}_iris', '#8a4a24', '#6b3519')
    M['WHITE'] = _flat(f'{tag}_shine', '#ffffff'); M['INK'] = _flat(f'{tag}_inkline', '#4a3226')
    M['BLUSH'] = _flat(f'{tag}_blush', '#f9c4bd'); M['NOSE'] = _toon(f'{tag}_nose', '#f08f8f', '#d9706f')
    return M

def hull(ob, t=INK_T):
    ob.data.materials.append(kbrig.ink_material())
    h = ob.modifiers.new('ink', 'SOLIDIFY'); h.thickness = t; h.offset = 1; h.use_even_offset = False
    h.use_flip_normals = True; h.use_rim = False; h.material_offset = len(ob.data.materials) - 1

def mesh_obj(name, bm, mat, coll, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    me.materials.append(mat); ob = bpy.data.objects.new(name, me); coll.objects.link(ob); return ob

# ---------------- skeleton (rest pose) ----------------
def bone_table():
    T = {}  # name: (head, tail, parent, connect, deform)
    T['root'] = ((0, 0, 0), (0, .7, 0), None, False, False)
    T['torso'] = ((0, 0, .88), (0, .5, .88), 'root', False, False)  # centre of gravity: pivots at the pelvis
    T['hips'] = ((0, 0, .95), (0, 0, .72), 'torso', False, True)
    T['spine'] = ((0, 0, .95), (0, 0, 1.2), 'torso', False, True)
    T['chest'] = ((0, 0, 1.2), (0, 0, 1.48), 'spine', True, True)
    T['neck'] = ((0, 0, 1.48), (0, 0, 1.62), 'chest', True, True)
    T['head'] = ((0, 0, 1.62), (0, 0, 2.6), 'neck', True, True)
    for s, L in ((1, 'L'), (-1, 'R')):
        # v4 rig (Nov 8 2026, "the rig must move like a person"): shoulder (clavicle) between chest and arm, a paw with a
        # palm, a two-segment finger block and a two-segment thumb, and a toe joint at the ball of each foot.
        T[f'shoulder.{L}'] = ((s * .1, 0, 1.42), (s * .42, 0, 1.4), 'chest', False, True)
        T[f'upper_arm.{L}'] = ((s * .44, 0, 1.38), (s * .72, .05, 1.04), f'shoulder.{L}', False, True)   # v3 arms ~15% longer to suit the legs
        T[f'forearm.{L}'] = ((s * .72, .05, 1.04), (s * .9, 0, .7), f'upper_arm.{L}', True, True)
        T[f'hand.{L}'] = ((s * .9, 0, .7), (s * .92, -.01, .52), f'forearm.{L}', True, True)
        T[f'fingers_a.{L}'] = ((s * .92, -.01, .52), (s * .93, -.01, .41), f'hand.{L}', True, True)
        T[f'fingers_b.{L}'] = ((s * .93, -.01, .41), (s * .93, -.01, .31), f'fingers_a.{L}', True, True)
        T[f'thumb_a.{L}'] = ((s * .88, -.1, .6), (s * .89, -.2, .53), f'hand.{L}', False, True)
        T[f'thumb_b.{L}'] = ((s * .89, -.2, .53), (s * .9, -.27, .46), f'thumb_a.{L}', True, True)
        T[f'thigh.{L}'] = ((s * .29, 0, .84), (s * .3, -.05, .5), 'hips', False, True)
        T[f'shin.{L}'] = ((s * .3, -.05, .5), (s * .3, 0, .16), f'thigh.{L}', True, True)
        T[f'foot.{L}'] = ((s * .3, 0, .16), (s * .3, -.34, .07), f'shin.{L}', True, True)
        T[f'foot_ik.{L}'] = ((s * .3, 0, .16), (s * .3, -.34, .16), 'root', False, False)
        T[f'knee_pole.{L}'] = ((s * .3, -1.3, .5), (s * .3, -1.45, .5), f'foot_ik.{L}', False, False)
        T[f'hand_ik.{L}'] = ((s * .9, 0, .7), (s * .9, -.18, .7), 'chest', False, False)
        T[f'elbow_pole.{L}'] = ((s * 1.15, .35, .5), (s * 1.15, .5, .5), 'chest', False, False)   # elbows down and OUT (behind the body they folded the arm into the chest)
        T[f'ear_a.{L}'] = ((s * .2, .06, 2.5), (s * .31, .07, 2.95), 'head', False, True)
        T[f'ear_b.{L}'] = ((s * .31, .07, 2.95), (s * .42, .08, 3.38), f'ear_a.{L}', True, True)
    T['tail'] = ((0, .38, .8), (0, .56, .84), 'hips', False, True)
    knot = (-.46, .42, 2.36)
    T['tie1_a'] = (knot, (-.72, .66, 2.26), 'head', False, True); T['tie1_b'] = ((-.72, .66, 2.26), (-.92, .84, 2.0), 'tie1_a', True, True)
    T['tie2_a'] = (knot, (-.66, .72, 2.12), 'head', False, True); T['tie2_b'] = ((-.66, .72, 2.12), (-.78, .86, 1.82), 'tie2_a', True, True)
    for i, x in (((1, .07), (2, -.07)) if BELT else ()):
        T[f'bend{i}_a'] = ((x, -.42, .9), (x * 1.6, -.46, .72), 'hips', False, True)
        T[f'bend{i}_b'] = ((x * 1.6, -.46, .72), (x * 2.2, -.48, .52), f'bend{i}_a', True, True)
    LEGB = ('root', 'thigh.', 'shin.', 'foot.', 'foot_ik.', 'knee_pole.', 'toe.')
    for n, (h, t, p, c, d) in list(T.items()):
        if not n.startswith(LEGB): T[n] = (up(h), up(t), p, c, d)
    for s, L in ((1, 'L'), (-1, 'R')):
        x = s * HIP_X
        T[f'thigh.{L}'] = ((x, 0, HIP_Z), (x, -.05, KNEE_Z), 'hips', False, True)
        T[f'shin.{L}'] = ((x, -.05, KNEE_Z), (x, 0, ANKLE_Z), f'thigh.{L}', True, True)
        T[f'foot.{L}'] = ((x, 0, ANKLE_Z), (x, -.34, .07), f'shin.{L}', True, True)
        T[f'toe.{L}'] = ((x, -.34, .07), (x, -.54, .07), f'foot.{L}', True, True)     # ball of the foot: toes bend while the heel lifts
        T[f'foot_ik.{L}'] = ((x, 0, ANKLE_Z), (x, -.34, ANKLE_Z), 'root', False, False)
        T[f'knee_pole.{L}'] = ((x, -1.3, KNEE_Z), (x, -1.45, KNEE_Z), f'foot_ik.{L}', False, False)
    T['torso'] = ((0, 0, HIP_Z + .04), (0, .5, HIP_Z + .04), 'root', False, False)  # centre of gravity: pivots at the pelvis
    return T

def build_rig(name, coll):
    arm = bpy.data.armatures.new(name + '_arm'); rig = bpy.data.objects.new(name + '_rig', arm); coll.objects.link(rig)
    arm.display_type = 'STICK'; rig.show_in_front = True
    bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
    T = bone_table(); eb = arm.edit_bones
    for n, (h, t, p, c, d) in T.items():
        b = eb.new(n); b.head = h; b.tail = t; b.use_deform = d
    for n, (h, t, p, c, d) in T.items():
        b = eb[n]
        if p: b.parent = eb[p]; b.use_connect = c
        # limbs: roll so local X is the character's left-right axis (the hinge axis for knees and elbows)
        b.align_roll(Vector((0, 0, 1)) if abs((b.tail - b.head).normalized().z) < .7 else Vector((0, -1, 0)))
    bpy.ops.object.mode_set(mode='POSE')
    pb = rig.pose.bones
    for L in 'LR':
        ik = pb[f'shin.{L}'].constraints.new('IK'); ik.target = rig; ik.subtarget = f'foot_ik.{L}'
        ik.pole_target = rig; ik.pole_subtarget = f'knee_pole.{L}'; ik.pole_angle = math.radians(90); ik.chain_count = 2  # +90: measured Nov 7, -90 bent knees backward
        cr = pb[f'foot.{L}'].constraints.new('COPY_ROTATION'); cr.target = rig; cr.subtarget = f'foot_ik.{L}'
        ik = pb[f'forearm.{L}'].constraints.new('IK'); ik.target = rig; ik.subtarget = f'hand_ik.{L}'
        ik.pole_target = rig; ik.pole_subtarget = f'elbow_pole.{L}'; ik.pole_angle = math.radians(-90); ik.chain_count = 2
        for b in (f'shin.{L}', f'forearm.{L}'):  # hinge joints: bend about local X only, never backwards
            p = pb[b]; p.lock_ik_y = p.lock_ik_z = True; p.use_ik_limit_x = True
            lo, hi = (-150, 0) if b.startswith('shin') else (0, 150)        # knee: negative local X (measured Nov 7); elbow: POSITIVE since the
            p.ik_min_x = math.radians(lo); p.ik_max_x = math.radians(hi)      # v3 arm lengthening (Nov 8: the wrong sign locked the elbows straight)
    for p in pb: p.rotation_mode = 'QUATERNION'
    # IK/FK switch per limb: rig["ik_arm.L"] = 1 IK (place the hand) / 0 FK (rotate joint by joint)
    for L in 'LR':
        for prop, cons in ((f'ik_arm.{L}', [pb[f'forearm.{L}'].constraints[0]]),
                           (f'ik_leg.{L}', [pb[f'shin.{L}'].constraints[0], pb[f'foot.{L}'].constraints[0]])):
            rig[prop] = 1.0
            for c in cons:
                d = c.driver_add('influence').driver; d.type = 'AVERAGE'
                v = d.variables.new(); v.name = 'ik'; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["{prop}"]'
    # curl axis of every finger/thumb segment, measured from the rest pose (which local axis and sign moves the tip
    # toward the palm), so grip/limits never depend on a guessed roll sign again (Nov 8: the elbow limit had the wrong sign)
    for L, s in (('L', 1), ('R', -1)):
        palm = Vector((-s, -.25, 0)).normalized()                 # paws hang palm-in; the thumb wraps across the palm
        for b in (f'fingers_a.{L}', f'fingers_b.{L}', f'thumb_a.{L}', f'thumb_b.{L}'):
            bone = arm.bones[b]; M3 = bone.matrix_local.to_3x3(); tip = Vector((0, bone.length, 0)); best = None
            for ax, axv in ((0, Vector((1, 0, 0))), (2, Vector((0, 0, 1)))):
                for sg in (1, -1):
                    moved = M3 @ (Matrix.Rotation(sg * math.radians(30), 3, axv) @ tip - tip)
                    score = moved.normalized().dot(palm)
                    if best is None or score > best[0]: best = (score, ax, sg)
            bone['curl_axis'] = best[1]; bone['curl_sign'] = best[2]
    # joint limits: a person's range of motion (degrees, bone-local XYZ). Checked by rom_test.py on every build.
    for b in pb:
        lim = rom_for(b.name, arm.bones[b.name])
        if not lim: continue
        c = b.constraints.new('LIMIT_ROTATION'); c.name = 'ROM'; c.owner_space = 'LOCAL'
        c.use_limit_x = c.use_limit_y = c.use_limit_z = True
        (c.min_x, c.max_x), (c.min_y, c.max_y), (c.min_z, c.max_z) = [(math.radians(a), math.radians(z)) for a, z in lim]
    bpy.ops.object.mode_set(mode='OBJECT')
    return rig

ROM = {  # bone prefix: ((min x, max x), (min y, max y), (min z, max z)) in degrees, bone-local (Y runs along the bone)
    'hips': ((-30, 30), (-40, 40), (-25, 25)),
    'spine': ((-35, 45), (-35, 35), (-30, 30)),       # +X flexes forward
    'chest': ((-30, 40), (-35, 35), (-25, 25)),
    'neck': ((-45, 45), (-60, 60), (-35, 35)),
    'head': ((-40, 40), (-60, 60), (-35, 35)),
    'shoulder.': ((-20, 35), (-15, 15), (-30, 30)),   # +X raises (shrug), Z rolls forward/back
    'forearm.': ((0, 150), (0, 0), (0, 0)),          # elbow: a hinge, never backwards (IK limit matches)
    'shin.': ((-150, 0), (0, 0), (0, 0)),            # knee: a hinge, never backwards
    'hand.': ((-75, 75), (-80, 80), (-35, 35)),      # wrist bend, forearm twist carried at the wrist, side bend
    'toe.': ((-40, 60), (-5, 5), (-10, 10)),         # +X lifts the toes
    'thigh.': ((-35, 140), (-45, 45), (-45, 45)),     # +X raises the knee forward (a karateka's hip, 140 for head kicks)
    'foot.': ((-45, 45), (-15, 15), (-25, 25)),      # ankle point/flex, roll
}
def rom_for(name, bone):
    if name.startswith(('fingers_', 'thumb_')):      # curl only toward the palm, a little spread, no twist
        ax, sg = bone['curl_axis'], bone['curl_sign']; rng = 100 if name.startswith('fingers') else 70
        lim = [(-10, 10), (-5, 5), (-10, 10)]; lim[ax] = (0, rng) if sg > 0 else (-rng, 0); return lim
    for k, v in ROM.items():
        if name.startswith(k): return v
    return None

# ---------------- body: one continuous skinned mesh (the gi) ----------------
def chain(pts, n):  # densify a polyline of (point, (rx, ry)) with n sub-steps per segment (rings at every joint)
    out = []
    for i in range(len(pts) - 1):
        (a, ra), (b, rb) = pts[i], pts[i + 1]
        for k in range(n):
            t = k / n; out.append((Vector(a).lerp(Vector(b), t), (ra[0] + (rb[0] - ra[0]) * t, ra[1] + (rb[1] - ra[1]) * t)))
    out.append((Vector(pts[-1][0]), pts[-1][1])); return out

def build_body(name, coll, M):
    trunk = chain([(up((0, 0, .72)), (.36, .3)), (up((0, 0, .86)), (.38, .31)), (up((0, 0, 1.0)), (.35, .29)), (up((0, 0, 1.2)), (.41, .33)),
                   (up((0, 0, 1.38)), (.39, .31)), (up((0, 0, 1.55)), (.22, .2))], 3)  # v3: belly depth .3 (v2 .38), thinner than a thigh is long
    verts, rad, edges = [], [], []
    def add_chain(ch, start=None):
        prev = start
        for p, r in ch:
            verts.append(p); rad.append(r); i = len(verts) - 1
            if prev is not None: edges.append((prev, i))
            prev = i
    add_chain(trunk)
    i_chest = min(range(len(verts)), key=lambda i: (verts[i] - Vector(up((0, 0, 1.36)))).length)
    i_pelvis = min(range(len(verts)), key=lambda i: (verts[i] - Vector(up((0, 0, .86)))).length)
    for s in (1, -1):
        arm = chain([(up((s * .3, 0, 1.38)), (.18, .18)), (up((s * .46, 0, 1.38)), (.165, .165)), (up((s * .72, .05, 1.04)), (.135, .135)),
                     (up((s * .88, .01, .74)), (.155, .155))], 3)   # slimmer sleeves: the arm keeps its shape in a guard
        add_chain(arm, i_chest)
        x = s * HIP_X  # v3: a slim trouser leg that tapers to the knee and flares a little to the hem
        leg = chain([(up((s * .12, 0, .82)), (.22, .22)), ((x, 0, HIP_Z - .02), (.2, .2)), ((x, -.05, KNEE_Z), (.14, .14)),
                     ((x, 0, ANKLE_Z + .1), (.17, .17)), ((x, 0, ANKLE_Z + .05), (.165, .165))], 4)
        add_chain(leg, i_pelvis)
    me = bpy.data.meshes.new(name + '_body_src'); me.from_pydata([tuple(v) for v in verts], edges, [])
    ob = bpy.data.objects.new(name + '_body', me); coll.objects.link(ob)
    sk = ob.modifiers.new('skin', 'SKIN'); sk.branch_smoothing = .6; sk.use_smooth_shade = True
    for i, r in enumerate(rad): me.skin_vertices[0].data[i].radius = r
    me.skin_vertices[0].data[i_pelvis].use_root = True
    ss = ob.modifiers.new('ss', 'SUBSURF'); ss.levels = ss.render_levels = 2
    dg = bpy.context.evaluated_depsgraph_get(); new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.clear(); ob.data = new; bpy.data.meshes.remove(me); new.name = name + '_body'
    for p in new.polygons: p.use_smooth = True
    new.materials.append(M['GI'])
    return ob

CORE = ('hips', 'spine', 'chest', 'neck', 'shoulder.', 'thigh.', 'shin.', 'upper_arm.', 'forearm.', 'hand.')
def bind_auto(rig, ob):  # bone heat from the body's own skeleton only (not ears, ribbons or belt ends)
    saved = {b.name: b.use_deform for b in rig.data.bones}
    for b in rig.data.bones: b.use_deform = b.use_deform and b.name.startswith(CORE)
    for o in bpy.context.view_layer.objects: o.select_set(False)
    ob.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for b in rig.data.bones: b.use_deform = saved[b.name]

def fix_leg_weights(rig, ob):
    # Bone heat left the trouser below the knee on the thigh (Nov 8 2026: the knee never showed). Below the upper thigh,
    # each leg vertex belongs to its thigh or shin only, with a narrow blend band at the knee.
    groups = {g.name: g for g in ob.vertex_groups}
    for v in ob.data.vertices:
        p = v.co; L = 'L' if p.x > 0 else 'R'
        if p.z > HIP_Z - .12 or abs(p.x) < .06: continue
        for g in ob.vertex_groups: g.remove([v.index])
        ws = ss01(KNEE_Z + .06, KNEE_Z - .06, p.z); wh = ss01(HIP_Z - .2, HIP_Z - .12, p.z)  # the whole thigh follows the thigh (a wide hip blend left it in the jacket)
        groups[f'shin.{L}'].add([v.index], ws, 'REPLACE'); groups[f'thigh.{L}'].add([v.index], (1 - ws) * (1 - wh), 'REPLACE')
        if wh > 0: groups['hips'].add([v.index], (1 - ws) * wh, 'REPLACE')

def fix_skirt_weights(rig, ob):
    # Action and reaction (user, Nov 8 2026: "leg up, whats in the way gets shifted, not entered"): the jacket skirt below
    # the belt rides on the thigh in front of it, so a lifted knee pushes the skirt up and out instead of rising inside it.
    groups = {g.name: g for g in ob.vertex_groups}
    belt = .93 + DZ
    for v in ob.data.vertices:
        p = v.co
        if not (HIP_Z - .14 < p.z < belt + .02) or p.y > .12 or abs(p.x) > .45: continue   # the hands hang at skirt height
        L = 'L' if p.x > 0 else 'R'; s = 1 if L == 'L' else -1
        w = .6 * ss01(.02, .16, s * p.x) * ss01(belt + .02, belt - .14, p.z) * ss01(.12, -.12, p.y)
        if w < .01: continue
        for g in ob.vertex_groups:
            try:
                old = g.weight(v.index); g.add([v.index], old * (1 - w), 'REPLACE')
            except RuntimeError: pass
        groups[f'thigh.{L}'].add([v.index], w + (groups[f'thigh.{L}'].weight(v.index) if any(gg.group == groups[f'thigh.{L}'].index for gg in v.groups) else 0), 'REPLACE')

def fix_arm_weights(rig, ob):
    # Bone heat left some sleeve vertices with no arm weight: they stayed at the rest pose and stretched into spikes
    # when the guard came up (Nov 8 2026). Every sleeve vertex now belongs to upper arm / forearm / hand by its place
    # along the arm, with blend bands at the shoulder (chest), elbow and wrist.
    from mathutils.geometry import intersect_point_line
    groups = {g.name: g for g in ob.vertex_groups}
    for v in ob.data.vertices:
        p = v.co; L = 'L' if p.x > 0 else 'R'; s = 1 if L == 'L' else -1
        sh, el, wr = Vector(up((s * .44, 0, 1.38))), Vector(up((s * .72, .05, 1.04))), Vector(up((s * .9, 0, .7)))
        best = None
        for k, (a, b) in enumerate(((sh, el), (el, wr))):
            q, t = intersect_point_line(p, a, b); t = max(0, min(1, t)); q = a.lerp(b, t); d = (p - q).length
            if best is None or d < best[0]: best = (d, k + t)
        d, u = best                                    # u: 0 shoulder, 1 elbow, 2 wrist
        if d > .3 or u < .05 or abs(p.x) < .3: continue
        for g in ob.vertex_groups: g.remove([v.index])
        wc = ss01(.35, .05, u)                         # chest near the shoulder
        we = ss01(.85, 1.15, u)                        # upper arm -> forearm at the elbow
        wh = ss01(1.85, 2.0, u)
        w = {f'shoulder.{L}': wc, f'upper_arm.{L}': (1 - wc) * (1 - we), f'forearm.{L}': (1 - wc) * we * (1 - wh), f'hand.{L}': (1 - wc) * we * wh}
        for n, x in w.items():
            if x > .001: groups[n].add([v.index], x, 'REPLACE')

def fix_shoulder_weights(rig, ob):
    # the top of the jacket over each shoulder rides the shoulder bone (a shrug lifts the cloth, not just the sleeve)
    groups = {g.name: g for g in ob.vertex_groups}
    for L in 'LR':
        if f'shoulder.{L}' not in groups: groups[f'shoulder.{L}'] = ob.vertex_groups.new(name=f'shoulder.{L}')
    for v in ob.data.vertices:
        p = v.co; L = 'L' if p.x > 0 else 'R'; s = 1 if L == 'L' else -1
        if any(groups[n].index == g.group and g.weight > .5 for g in v.groups for n in (f'upper_arm.{L}', f'forearm.{L}')): continue
        w = .75 * ss01(.16, .36, s * p.x) * ss01(1.2 + DZ, 1.38 + DZ, p.z)
        if w < .01: continue
        for g in ob.vertex_groups:
            try: g.add([v.index], g.weight(v.index) * (1 - w), 'REPLACE')
            except RuntimeError: pass
        groups[f'shoulder.{L}'].add([v.index], w, 'ADD')

def paint_body_weights(rig, ob):
    # v4 weights (Nov 8 2026, range-of-motion test): bone heat on this cartoon body put thigh weight at chest height and the
    # old sleeve rule (anything within .3 of the arm line) pulled the side of the jacket along with the arm, so the skin tore
    # at the armpit, crotch and shoulder. A rigger hand-paints a stylised body; this paints the same map from the anatomy:
    #   sleeves      only vertices within the sleeve radius of the arm line; shoulder cap blends trunk -> arm across the joint
    #   trunk        hips -> spine -> chest -> neck by height, each joint a soft band
    #   shoulders    the jacket over each shoulder rides the shoulder (clavicle) bone, so a shrug lifts the cloth
    #   legs         thigh -> shin with a knee band; the inner thigh fades to the hips toward the midline (crotch)
    from mathutils.geometry import intersect_point_line
    for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
    names = [b.name for b in rig.data.bones if b.use_deform and b.name.startswith(CORE)]
    G = {n: ob.vertex_groups.new(name=n) for n in names}
    bh = {b.name: b.head_local.copy() for b in rig.data.bones}
    for v in ob.data.vertices:
        p = v.co; s = 1 if p.x >= 0 else -1; L = 'L' if s > 0 else 'R'; ax = s * p.x
        sh, el, wr = bh[f'upper_arm.{L}'], bh[f'forearm.{L}'], bh[f'hand.{L}']
        q, t0 = intersect_point_line(p, sh, el)
        best = None
        for k, (a, b) in enumerate(((sh, el), (el, wr))):
            q, t = intersect_point_line(p, a, b); tc = max(0, min(1, t)); d = (p - a.lerp(b, tc)).length
            if best is None or d < best[0]: best = (d, k + tc)
        d, u = best
        if t0 < 0: u = t0                                   # before the shoulder joint: negative along-arm coordinate
        # inside the sleeve tube (radius .12-.18). Under the armpit the jacket side is just as close to the arm line, so the
        # surface direction decides: sleeve skin faces away from the arm's axis, the jacket beside it faces toward it.
        q = (sh.lerp(el, max(0, min(1, t0))) if u <= 1 else el.lerp(wr, max(0, min(1, u - 1))))
        rdir = (p - q).normalized() if (p - q).length > 1e-6 else v.normal
        md = ss01(.215, .185, d) * ss01(.2, .3, ax) * ss01(-.25, .25, v.normal.dot(rdir))
        wa = md * ss01(-.12, .12, u)                        # trunk -> arm across the shoulder joint
        w = {}
        if wa > 0:
            we = ss01(.75, 1.25, u); wh = ss01(1.82, 2.0, u)
            w[f'upper_arm.{L}'] = wa * (1 - we); w[f'forearm.{L}'] = wa * we * (1 - wh); w[f'hand.{L}'] = wa * we * wh
        rest = 1 - wa
        # legs
        # the crotch fade toward the midline applies only near the crotch (not to the inner trouser cuff), and never to the
        # hands, which hang at hip height
        mid = ss01(.0, .13, ax) if p.z > HIP_Z - .32 else 1.0
        wl = ss01(HIP_Z + .04, HIP_Z - .2, p.z) * mid * ss01(.55, .45, ax)
        if wl > 0:
            ws = ss01(KNEE_Z + .09, KNEE_Z - .09, p.z)
            w[f'thigh.{L}'] = w.get(f'thigh.{L}', 0) + rest * wl * (1 - ws); w[f'shin.{L}'] = rest * wl * ws
        tr = rest * (1 - wl)
        if tr > 0:
            z = p.z
            a1 = ss01(1.22, 1.42, z); a2 = ss01(1.48, 1.66, z); a3 = ss01(1.74, 1.93, z)
            chain = {'hips': 1 - a1, 'spine': a1 * (1 - a2), 'chest': a2 * (1 - a3), 'neck': a3}
            shf = .8 * ss01(.14, .34, ax) * ss01(1.52, 1.72, z)            # jacket over the shoulder
            shf = max(shf, md * (1 - ss01(-.12, .12, u)) * ss01(.2, .32, ax))  # the shoulder cap just inside the sleeve
            shf = min(shf, 1)
            w[f'shoulder.{L}'] = tr * shf
            for n, x in chain.items(): w[n] = w.get(n, 0) + tr * (1 - shf) * x
        tot = sum(w.values()) or 1
        for n, x in w.items():
            if x / tot > .002: G[n].add([v.index], x / tot, 'REPLACE')
    smooth_weights(ob, 14, .5)
    mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_world = mw
    m = ob.modifiers.new('Armature', 'ARMATURE'); m.object = rig; m.use_vertex_groups = True; m.use_bone_envelopes = False
    m.use_deform_preserve_volume = True                     # dual quaternion: elbows, knees and twists keep their thickness
    ob.modifiers.move(len(ob.modifiers) - 1, 0)

def smooth_weights(ob, iters=14, f=.5):
    # the step a rigger does after painting: blend every vertex's weights with its neighbours' so no two neighbouring
    # vertices disagree sharply (sharp disagreement is what tears skin into slivers and spikes at the armpit and crotch)
    import numpy as np
    me = ob.data; nv = len(me.vertices); gs = list(ob.vertex_groups); W = np.zeros((nv, len(gs)))
    for v in me.vertices:
        for g in v.groups: W[v.index, g.group] = g.weight
    E = np.array([e.vertices[:] for e in me.edges]); deg = np.bincount(E.ravel(), minlength=nv).astype(float)[:, None]
    for _ in range(iters):
        acc = np.zeros_like(W); np.add.at(acc, E[:, 0], W[E[:, 1]]); np.add.at(acc, E[:, 1], W[E[:, 0]])
        W = (1 - f) * W + f * acc / np.maximum(deg, 1)
    W[W < .003] = 0; W /= np.maximum(W.sum(1, keepdims=True), 1e-9)
    for j, g in enumerate(gs):
        g.remove(list(range(nv)))
        idx = np.nonzero(W[:, j])[0]
        for i in idx: g.add([int(i)], float(W[i, j]), 'REPLACE')

def unweighted(ob):
    return sum(1 for v in ob.data.vertices if sum(g.weight for g in v.groups) < .01)

def bind_bone(rig, ob, bone):
    mw = ob.matrix_world.copy(); ob.parent = rig; ob.parent_type = 'BONE'; ob.parent_bone = bone
    bpy.context.view_layer.update(); ob.matrix_world = mw

def bind_groups(rig, ob, weights):  # weights(p) -> {bone: w}
    for v in ob.data.vertices:
        for b, w in weights(v.co).items():
            g = ob.vertex_groups.get(b) or ob.vertex_groups.new(name=b); g.add([v.index], w, 'REPLACE')
    m = ob.modifiers.new('arm', 'ARMATURE'); m.object = rig; ob.parent = rig

def ss01(a, b, x): t = max(0, min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def build_bunny(name, belt, gear, band=None):
    coll = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(coll)
    M = mats(name, belt, gear); band = band or gear
    BAND = _toon(f'{name}_band', band[0], band[1])
    rig = build_rig(name, coll)
    body = build_body(name, coll, M); paint_body_weights(rig, body); fix_skirt_weights(rig, body); rig['unweighted_body_verts'] = unweighted(body)
    arms = [split_off(body, (f'upper_arm.{L}', f'forearm.{L}', f'hand.{L}'), f'_arm.{L}') for L in 'LR']
    hull(body)
    for a in arms: hull(a)
    E, C = kbrig.ellipsoid, kbrig.capsule
    def part(nm, bm, mat, bone=None, groups=None, ink=True):
        lift = not nm.startswith(('foot.', 'pad.', 'toe.'))
        if lift:
            for v in bm.verts: v.co.z += DZ
        else:
            for v in bm.verts: v.co.x *= HIP_X / .3
        ob = mesh_obj(f'{name}_{nm}', bm, mat, coll)
        if bone: bind_bone(rig, ob, bone)
        if groups: bind_groups(rig, ob, (lambda p, g=groups: g(Vector(p) - Vector((0, 0, DZ)))) if lift else groups)
        if ink: hull(ob)
        return ob
    part('head', E(HEAD_C - Vector((0, 0, DZ)), HEAD_R, segs=40), M['FUR'], 'head')
    for s, L in ((1, 'L'), (-1, 'R')):
        a, t = Vector((s * .2, .06, 2.45)), Vector((s * .42, .08, 3.4)); d = t - a
        R = d.to_track_quat('Z', 'Y').to_matrix()
        w = lambda p, L=L: {f'ear_a.{L}': 1 - ss01(2.85, 3.05, p.z), f'ear_b.{L}': ss01(2.85, 3.05, p.z)}
        part(f'ear.{L}', E((a + t) / 2, (.17, .07, d.length / 2 + .04), R), M['FUR'], groups=w)
        part(f'inner.{L}', E((a + t) / 2 + Vector((0, -.055, .05)), (.1, .03, d.length / 2 - .1), R), M['PINK'], groups=w, ink=False)
        # paw (red mitt): palm + two finger segments + two thumb segments, overlapping so a curl never opens a gap;
        # curled (grip 1) the segments close into the round fist of the old one-piece glove
        part(f'palm.{L}', E((s * .91, -.01, .6), (.11, .17, .13)), M['GEAR'], f'hand.{L}')
        part(f'fing_a.{L}', E((s * .925, -.01, .465), (.095, .16, .085)), M['GEAR'], f'fingers_a.{L}')
        part(f'fing_b.{L}', E((s * .93, -.01, .36), (.085, .145, .075)), M['GEAR'], f'fingers_b.{L}')
        part(f'thumb_a.{L}', E((s * .885, -.15, .565), (.065, .075, .07)), M['GEAR'], f'thumb_a.{L}')
        part(f'thumb_b.{L}', E((s * .895, -.235, .495), (.055, .06, .06)), M['GEAR'], f'thumb_b.{L}')
        part(f'foot.{L}', E((s * .3, -.1, .1), (.21, .3, .12)), M['FUR'], f'foot.{L}')     # heel to ball
        part(f'toe.{L}', E((s * .3, -.42, .09), (.2, .14, .1)), M['FUR'], f'toe.{L}')     # toes
        part(f'pad.{L}', E((s * .3, -.16, .13), (.2, .24, .1)), M['GEAR'], f'foot.{L}')  # WKF foot protector over the instep
    part('tail', E((0, .44, .8), (.17, .15, .16)), M['FUR'], 'tail')
    # face (decals ride the head bone, no outline hull)
    for s in (1, -1):
        x, z = s * .27, 2.03
        part(f'eye{s}', E((x, face_y(x, z, -.03), z), (.11, .05, .135)), M['EYE'], 'head', ink=False)
        part(f'iris{s}', E((x, face_y(x, z - .03, -.0), z - .03), (.075, .035, .085)), M['IRIS'], 'head', ink=False)
        part(f'shine{s}', E((x + .03, face_y(x + .03, z + .05, .01), z + .05), (.035, .015, .04)), M['WHITE'], 'head', ink=False)
        part(f'blush{s}', E((s * .44, face_y(s * .44, 1.88, -.02), 1.88), (.09, .03, .05)), M['BLUSH'], 'head', ink=False)
    part('nose', E((0, face_y(0, 1.87, .0), 1.87), (.05, .03, .035)), M['NOSE'], 'head', ink=False)
    mouth = [(x, face_y(x, z, .0), z) for x, z in ((-.09, 1.8), (-.04, 1.77), (0, 1.79), (.04, 1.77), (.09, 1.8))]
    part('mouth', kbrig.tube_curve(mouth, .012), M['INK'], 'head', ink=False)
    # headband (ring around the head at the measured height) and its ribbons
    zb = 2.36; k = math.sqrt(max(0, 1 - ((zb + DZ - HEAD_C.z) / HEAD_R.z) ** 2))
    part('headband', kbrig.ring((0, 0, zb), HEAD_R.x * k + .015, HEAD_R.y * k + .015, 1.3, .06), BAND, 'head')
    part('bandknot', E((-.46, .42, 2.36), (.09, .09, .1)), BAND, 'head')
    for t, pts, wd in (('tie1', [(-.46, .42, 2.36), (-.72, .66, 2.26), (-.92, .84, 2.0)], .1), ('tie2', [(-.46, .42, 2.36), (-.66, .72, 2.12), (-.78, .86, 1.82)], .09)):
        a1 = Vector(pts[1])
        part(t, kbrig.strip(pts, wd), BAND, groups=lambda p, t=t, a1=a1: {f'{t}_a': 1 - ss01(-.1, .1, (Vector(p) - a1).dot(Vector((-.6, .5, -.4)).normalized())),
                                                                       f'{t}_b': ss01(-.1, .1, (Vector(p) - a1).dot(Vector((-.6, .5, -.4)).normalized()))}, ink=False)
    # belt with a front knot and two hanging ends
    for i, x in (((1, .07), (2, -.07)) if BELT else ()):
        if i == 1:
            part('belt', kbrig.ring((0, 0, .93), .45, .385, .7, .09), M['BELT'], 'hips')
            part('knot', E((0, -.38, .93), (.08, .05, .07)), M['BELT'], 'hips')
        pts = [(x, -.42, .9), (x * 1.6, -.46, .72), (x * 2.2, -.48, .52)]
        part(f'beltend{i}', kbrig.strip(pts, .07, up=(1, 0, 0)), M['BELT'],
             groups=lambda p, i=i: {f'bend{i}_a': 1 - ss01(.66, .78, p.z), f'bend{i}_b': ss01(.66, .78, p.z)}, ink=False)
    # gi lapels: two ink folds forming the V of the jacket
    for s in (1, -1):
        lap = [(s * .2, -.33, 1.47), (s * .08, -.39, 1.22), (-s * .05, -.39, 1.0)]
        part(f'lapel{s}', kbrig.tube_curve(lap, .012), M['INK'], 'chest', ink=False)
    rig['fighter'] = name
    return rig, coll
