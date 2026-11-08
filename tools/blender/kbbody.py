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

HEAD_C, HEAD_R = Vector((0, 0, 2.08)), Vector((.66, .6, .53))
def face_y(x, z, out=0.0):
    q = 1 - (x / HEAD_R.x) ** 2 - ((z - HEAD_C.z) / HEAD_R.z) ** 2
    return -(HEAD_R.y + out) * math.sqrt(max(q, 0.0))

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
        T[f'upper_arm.{L}'] = ((s * .44, 0, 1.38), (s * .68, .05, 1.1), 'chest', False, True)
        T[f'forearm.{L}'] = ((s * .68, .05, 1.1), (s * .84, 0, .82), f'upper_arm.{L}', True, True)
        T[f'hand.{L}'] = ((s * .84, 0, .82), (s * .88, -.02, .64), f'forearm.{L}', True, True)
        T[f'thigh.{L}'] = ((s * .29, 0, .84), (s * .3, -.05, .5), 'hips', False, True)
        T[f'shin.{L}'] = ((s * .3, -.05, .5), (s * .3, 0, .16), f'thigh.{L}', True, True)
        T[f'foot.{L}'] = ((s * .3, 0, .16), (s * .3, -.34, .07), f'shin.{L}', True, True)
        T[f'foot_ik.{L}'] = ((s * .3, 0, .16), (s * .3, -.34, .16), 'root', False, False)
        T[f'knee_pole.{L}'] = ((s * .3, -1.3, .5), (s * .3, -1.45, .5), f'foot_ik.{L}', False, False)
        T[f'hand_ik.{L}'] = ((s * .84, 0, .82), (s * .84, -.18, .82), 'chest', False, False)
        T[f'elbow_pole.{L}'] = ((s * 1.1, 1.0, 1.05), (s * 1.1, 1.15, 1.05), 'chest', False, False)
        T[f'ear_a.{L}'] = ((s * .2, .06, 2.5), (s * .31, .07, 2.95), 'head', False, True)
        T[f'ear_b.{L}'] = ((s * .31, .07, 2.95), (s * .42, .08, 3.38), f'ear_a.{L}', True, True)
    T['tail'] = ((0, .38, .8), (0, .56, .84), 'hips', False, True)
    knot = (-.46, .42, 2.36)
    T['tie1_a'] = (knot, (-.72, .66, 2.26), 'head', False, True); T['tie1_b'] = ((-.72, .66, 2.26), (-.92, .84, 2.0), 'tie1_a', True, True)
    T['tie2_a'] = (knot, (-.66, .72, 2.12), 'head', False, True); T['tie2_b'] = ((-.66, .72, 2.12), (-.78, .86, 1.82), 'tie2_a', True, True)
    for i, x in ((1, .07), (2, -.07)):
        T[f'bend{i}_a'] = ((x, -.42, .9), (x * 1.6, -.46, .72), 'hips', False, True)
        T[f'bend{i}_b'] = ((x * 1.6, -.46, .72), (x * 2.2, -.48, .52), f'bend{i}_a', True, True)
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
        ik.pole_target = rig; ik.pole_subtarget = f'knee_pole.{L}'; ik.pole_angle = math.radians(-90); ik.chain_count = 2
        cr = pb[f'foot.{L}'].constraints.new('COPY_ROTATION'); cr.target = rig; cr.subtarget = f'foot_ik.{L}'
        ik = pb[f'forearm.{L}'].constraints.new('IK'); ik.target = rig; ik.subtarget = f'hand_ik.{L}'
        ik.pole_target = rig; ik.pole_subtarget = f'elbow_pole.{L}'; ik.pole_angle = math.radians(-90); ik.chain_count = 2
        for b in (f'shin.{L}', f'forearm.{L}'):  # hinge joints: bend about local X only, never backwards
            p = pb[b]; p.lock_ik_y = p.lock_ik_z = True; p.use_ik_limit_x = True
            p.ik_min_x = math.radians(0 if b.startswith('shin') else -150); p.ik_max_x = math.radians(150 if b.startswith('shin') else 0)
    for p in pb: p.rotation_mode = 'QUATERNION'
    bpy.ops.object.mode_set(mode='OBJECT')
    return rig

# ---------------- body: one continuous skinned mesh (the gi) ----------------
def chain(pts, n):  # densify a polyline of (point, (rx, ry)) with n sub-steps per segment (rings at every joint)
    out = []
    for i in range(len(pts) - 1):
        (a, ra), (b, rb) = pts[i], pts[i + 1]
        for k in range(n):
            t = k / n; out.append((Vector(a).lerp(Vector(b), t), (ra[0] + (rb[0] - ra[0]) * t, ra[1] + (rb[1] - ra[1]) * t)))
    out.append((Vector(pts[-1][0]), pts[-1][1])); return out

def build_body(name, coll, M):
    trunk = chain([((0, 0, .7), (.43, .37)), ((0, 0, .86), (.45, .38)), ((0, 0, 1.0), (.41, .34)), ((0, 0, 1.2), (.45, .37)),
                   ((0, 0, 1.38), (.41, .33)), ((0, 0, 1.55), (.22, .2))], 3)
    verts, rad, edges = [], [], []
    def add_chain(ch, start=None):
        prev = start
        for p, r in ch:
            verts.append(p); rad.append(r); i = len(verts) - 1
            if prev is not None: edges.append((prev, i))
            prev = i
    add_chain(trunk)
    i_chest = min(range(len(verts)), key=lambda i: (verts[i] - Vector((0, 0, 1.36))).length)
    i_pelvis = min(range(len(verts)), key=lambda i: (verts[i] - Vector((0, 0, .86))).length)
    for s in (1, -1):
        arm = chain([((s * .3, 0, 1.38), (.22, .22)), ((s * .46, 0, 1.38), (.23, .23)), ((s * .68, .05, 1.1), (.2, .2)),
                     ((s * .82, .01, .86), (.22, .22))], 3)
        add_chain(arm, i_chest)
        leg = chain([((s * .2, 0, .82), (.27, .27)), ((s * .3, 0, .8), (.27, .27)), ((s * .3, -.05, .5), (.235, .235)),
                     ((s * .3, 0, .24), (.255, .255)), ((s * .3, 0, .2), (.25, .25))], 3)
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

CORE = ('hips', 'spine', 'chest', 'neck', 'thigh.', 'shin.', 'upper_arm.', 'forearm.', 'hand.')
def bind_auto(rig, ob):  # bone heat from the body's own skeleton only (not ears, ribbons or belt ends)
    saved = {b.name: b.use_deform for b in rig.data.bones}
    for b in rig.data.bones: b.use_deform = b.use_deform and b.name.startswith(CORE)
    for o in bpy.context.view_layer.objects: o.select_set(False)
    ob.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for b in rig.data.bones: b.use_deform = saved[b.name]

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
    body = build_body(name, coll, M); bind_auto(rig, body); hull(body)
    E, C = kbrig.ellipsoid, kbrig.capsule
    def part(nm, bm, mat, bone=None, groups=None, ink=True):
        ob = mesh_obj(f'{name}_{nm}', bm, mat, coll)
        if bone: bind_bone(rig, ob, bone)
        if groups: bind_groups(rig, ob, groups)
        if ink: hull(ob)
        return ob
    part('head', E(HEAD_C, HEAD_R, segs=40), M['FUR'], 'head')
    for s, L in ((1, 'L'), (-1, 'R')):
        a, t = Vector((s * .2, .06, 2.45)), Vector((s * .42, .08, 3.4)); d = t - a
        R = d.to_track_quat('Z', 'Y').to_matrix()
        w = lambda p, L=L: {f'ear_a.{L}': 1 - ss01(2.85, 3.05, p.z), f'ear_b.{L}': ss01(2.85, 3.05, p.z)}
        part(f'ear.{L}', E((a + t) / 2, (.17, .07, d.length / 2 + .04), R), M['FUR'], groups=w)
        part(f'inner.{L}', E((a + t) / 2 + Vector((0, -.055, .05)), (.1, .03, d.length / 2 - .1), R), M['PINK'], groups=w, ink=False)
        part(f'fist.{L}', E((s * .88, -.03, .7), (.19, .2, .18)), M['GEAR'], f'hand.{L}')
        part(f'foot.{L}', E((s * .3, -.17, .1), (.21, .36, .12)), M['FUR'], f'foot.{L}')
        part(f'pad.{L}', E((s * .3, -.2, .13), (.2, .3, .1)), M['GEAR'], f'foot.{L}')  # WKF foot protector over the instep
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
    zb = 2.36; k = math.sqrt(max(0, 1 - ((zb - HEAD_C.z) / HEAD_R.z) ** 2))
    part('headband', kbrig.ring((0, 0, zb), HEAD_R.x * k + .015, HEAD_R.y * k + .015, 1.3, .06), BAND, 'head')
    part('bandknot', E((-.46, .42, 2.36), (.09, .09, .1)), BAND, 'head')
    for t, pts, wd in (('tie1', [(-.46, .42, 2.36), (-.72, .66, 2.26), (-.92, .84, 2.0)], .1), ('tie2', [(-.46, .42, 2.36), (-.66, .72, 2.12), (-.78, .86, 1.82)], .09)):
        a1 = Vector(pts[1])
        part(t, kbrig.strip(pts, wd), BAND, groups=lambda p, t=t, a1=a1: {f'{t}_a': 1 - ss01(-.1, .1, (Vector(p) - a1).dot(Vector((-.6, .5, -.4)).normalized())),
                                                                       f'{t}_b': ss01(-.1, .1, (Vector(p) - a1).dot(Vector((-.6, .5, -.4)).normalized()))}, ink=False)
    # belt with a front knot and two hanging ends
    part('belt', kbrig.ring((0, 0, .93), .45, .385, .7, .09), M['BELT'], 'hips')
    part('knot', E((0, -.38, .93), (.08, .05, .07)), M['BELT'], 'hips')
    for i, x in ((1, .07), (2, -.07)):
        pts = [(x, -.42, .9), (x * 1.6, -.46, .72), (x * 2.2, -.48, .52)]
        part(f'beltend{i}', kbrig.strip(pts, .07, up=(1, 0, 0)), M['BELT'],
             groups=lambda p, i=i: {f'bend{i}_a': 1 - ss01(.66, .78, p.z), f'bend{i}_b': ss01(.66, .78, p.z)}, ink=False)
    # gi lapels: two ink folds forming the V of the jacket
    for s in (1, -1):
        lap = [(s * .2, -.33, 1.47), (s * .08, -.39, 1.22), (-s * .05, -.39, 1.0)]
        part(f'lapel{s}', kbrig.tube_curve(lap, .012), M['INK'], 'chest', ink=False)
    rig['fighter'] = name
    return rig, coll
