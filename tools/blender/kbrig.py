# Karate Bunnies rig: the bunny built ONCE in sections, each section weighted to its own bone (blends only at the
# elbows, knees, waist and mid-ear), IK arms and legs with a little cartoon stretch, face expressions as keyed parts.
# Proportions measured from the painted sprites: ears ~30% of height, head ~30%, body and legs ~40%.
# Used by moves.py (poses, keys, render) inside Blender 5.x. Model space: faces -Y, +X is its left, feet on z=0.
import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion
import kbpuppet  # materials and colour helpers

LEG = .62  # extra leg length: real kicks need legs that reach past the round body
def warp(v):
    v = Vector(v); t = min(max((v.z - .15) / (.92 - .15), 0.0), 1.0); return Vector((v.x, v.y, v.z + LEG * t))

def ss(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0); return t * t * (3 - 2 * t)

def rotm(deg):  # (pitch: top toward -Y +, roll: toward its left +, yaw: turn to its left +), degrees -> 3x3
    p, r, y = [math.radians(a) for a in deg]
    return Matrix.Rotation(y, 3, 'Z') @ Matrix.Rotation(r, 3, 'Y') @ Matrix.Rotation(p, 3, 'X')
# Sign checks: a forward lean tips the top toward -Y, a roll to its left tips it toward +X, a turn to its left faces +X.
assert (rotm((90, 0, 0)) @ Vector((0, 0, 1))).y < -.99 and (rotm((0, 90, 0)) @ Vector((0, 0, 1))).x > .99
assert (rotm((0, 0, 90)) @ Vector((0, -1, 0))).x > .99

HEAD_C, HEAD_S = Vector((0, 0, 2.32)), Vector((.92, .78, .66))
def face_y(x, z, out=0.0):  # y of the head's front surface at (x, z), pushed out by `out`
    q = 1 - (x / HEAD_S.x) ** 2 - ((z - HEAD_C.z) / HEAD_S.z) ** 2
    return -HEAD_S.y * math.sqrt(max(q, .02)) - out

# name: (head, tail, parent, deform, connect)
def bone_table():
    T = {'root': ((0, 0, 0), (0, .4, 0), None, False, False),
         'pelvis': ((0, 0, 1.0), (0, 0, 1.18), 'root', True, False),
         'spine': ((0, 0, 1.18), (0, 0, 1.42), 'pelvis', True, True),
         'chest': ((0, 0, 1.42), (0, 0, 1.7), 'spine', True, True),
         'head': ((0, 0, 1.7), (0, 0, 2.5), 'chest', True, True),
         'tail': ((0, .55, 1.0), (0, .8, 1.05), 'pelvis', True, False)}
    for s, L in ((1, 'L'), (-1, 'R')):
        T[f'ear_a.{L}'] = ((s * .34, .04, 2.82), (s * .43, .04, 3.45), 'head', True, False)
        T[f'ear_b.{L}'] = ((s * .43, .04, 3.45), (s * .5, .04, 4.15), f'ear_a.{L}', True, True)
        T[f'upper_arm.{L}'] = ((s * .52, 0, 1.58), (s * .86, .08, 1.0), 'chest', True, False)
        T[f'forearm.{L}'] = ((s * .86, .08, 1.0), (s * .96, -.04, .42), f'upper_arm.{L}', True, True)
        T[f'hand_ik.{L}'] = ((s * .96, -.04, .42), (s * .96, -.24, .42), 'root', False, False)
        T[f'hand.{L}'] = ((s * .96, -.04, .42), (s * .96, -.24, .42), f'hand_ik.{L}', True, False)
        T[f'thigh.{L}'] = ((s * .3, 0, .92), (s * .32, -.07, .53), 'pelvis', True, False)
        T[f'shin.{L}'] = ((s * .32, -.07, .53), (s * .34, 0, .15), f'thigh.{L}', True, True)
        T[f'foot_ik.{L}'] = ((s * .34, 0, .15), (s * .34, -.4, .15), 'root', False, False)
        T[f'foot.{L}'] = ((s * .34, 0, .15), (s * .34, -.4, .15), f'foot_ik.{L}', True, False)
        T[f'toe.{L}'] = ((s * .34, -.32, .03), (s * .34, -.55, .03), f'foot.{L}', True, False)  # ball of the foot -> toe tip
    for s, L in ((1, 'L'), (-1, 'R')):  # hanging belt ends: two loose segments each, so they can swing and hang with gravity
        T[f'beltend_a.{L}'] = ((s * .06, -.56, 1.0), (s * .1, -.575, .86), 'pelvis', True, False)
        T[f'beltend_b.{L}'] = ((s * .1, -.575, .86), (s * .14, -.59, .72), f'beltend_a.{L}', True, True)
    knot = (-.6, .55, 2.62)
    T['tie1_a'] = (knot, (-1.0, .65, 2.66), 'head', True, False); T['tie1_b'] = ((-1.0, .65, 2.66), (-1.45, .75, 2.5), 'tie1_a', True, True)
    T['tie2_a'] = (knot, (-.95, .72, 2.38), 'head', True, False); T['tie2_b'] = ((-.95, .72, 2.38), (-1.25, .85, 2.0), 'tie2_a', True, True)
    return T

def build_armature(scene):
    arm = bpy.data.armatures.new('BunnyRig'); rig = bpy.data.objects.new('BunnyRig', arm); scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
    T = bone_table()
    for n, (h, t, par, deform, conn) in T.items():
        eb = arm.edit_bones.new(n); eb.head, eb.tail = warp(h), warp(t); eb.use_deform = deform
    for n, (h, t, par, deform, conn) in T.items():
        eb = arm.edit_bones[n]
        if par: eb.parent = arm.edit_bones[par]; eb.use_connect = conn
        eb.align_roll(Vector((0, -1, 0)) if abs((eb.tail - eb.head).normalized().y) < .9 else Vector((0, 0, 1)))
    bpy.ops.object.mode_set(mode='POSE')
    for s in ('L', 'R'):
        for chain_end, target in ((f'shin.{s}', f'foot_ik.{s}'), (f'forearm.{s}', f'hand_ik.{s}')):
            c = rig.pose.bones[chain_end].constraints.new('IK'); c.target = rig; c.subtarget = target; c.chain_count = 2; c.use_stretch = False  # IK stretch scales bones in every axis (fat limbs); moves.py stretches length only
        for b in (f'shin.{s}', f'forearm.{s}'):  # take the parent's stretch along the bone only, so stretched limbs keep their thickness
            rig.pose.bones[b].bone.inherit_scale = 'ALIGNED'
    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'
    bpy.ops.object.mode_set(mode='OBJECT')
    return rig

# ---- mesh helpers: build in rest pose (model space), weights from a function of the vertex position ----
def _bm_sphere(segs=32):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2, radius=1); return bm
def _xf(bm, M): bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
def ellipsoid(c, s, R=None, segs=32):
    bm = _bm_sphere(segs); _xf(bm, Matrix.Translation(Vector(c)) @ (R or Matrix.Identity(3)).to_4x4() @ Matrix.Diagonal(Vector(s)).to_4x4()); return bm
def capsule(a, b, r, squash=1.0, stretch=.55):
    a, b = Vector(a), Vector(b); d = b - a; R = d.to_track_quat('Z', 'Y').to_matrix()
    return ellipsoid((a + b) / 2, (r, r * squash, d.length / 2 + r * stretch), R)
def cone(c, r1, r2, depth, sy, verts=24):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r1, radius2=r2, depth=depth)
    _xf(bm, Matrix.Translation(Vector(c)) @ Matrix.Diagonal(Vector((1, sy, 1))).to_4x4()); return bm
def box(a, b, w, t):
    a, b = Vector(a), Vector(b); d = b - a; R = d.to_track_quat('Z', 'Y').to_matrix()
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    _xf(bm, Matrix.Translation((a + b) / 2) @ R.to_4x4() @ Matrix.Diagonal(Vector((w, t, d.length))).to_4x4()); return bm
def ring(c, rx, ry, rz, tube, n=64, m=12):
    bm = bmesh.new(); vs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m; rr = 1 + tube * math.cos(b)
            vs.append(bm.verts.new((c[0] + rx * rr * math.cos(a), c[1] + ry * rr * math.sin(a), c[2] + rz * tube * math.sin(b))))
    for i in range(n):
        for j in range(m):
            bm.faces.new((vs[i * m + j], vs[((i + 1) % n) * m + j], vs[((i + 1) % n) * m + (j + 1) % m], vs[i * m + (j + 1) % m]))
    return bm
def strip(points, width, up=(0, 0, 1), samples=24):  # a flat cloth ribbon through points (Catmull-Rom), width along `up`
    P = [Vector(p) for p in points]; pts = []
    for k in range(samples + 1):
        t = k / samples * (len(P) - 1); i = min(int(t), len(P) - 2); u = t - i
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        pts.append(.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    bm = bmesh.new(); U = Vector(up).normalized(); prev = None
    for k, p in enumerate(pts):
        w = width * (1 - .25 * k / samples); a, b = bm.verts.new(p + U * w / 2), bm.verts.new(p - U * w / 2)
        if prev: bm.faces.new((prev[0], prev[1], b, a))
        prev = (a, b)
    return bm
def tube_curve(points, depth):  # a thin inked line (eyes, brows, mouth) as a mesh
    cd = bpy.data.curves.new('ln', 'CURVE'); cd.dimensions = '3D'; cd.bevel_depth = depth; cd.bevel_resolution = 3
    sp = cd.splines.new('BEZIER'); sp.bezier_points.add(len(points) - 1)
    for bp, co in zip(sp.bezier_points, points): bp.co = co; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new('ln', cd); bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob); bpy.data.curves.remove(cd)
    bm = bmesh.new(); bm.from_mesh(me); bpy.data.meshes.remove(me); return bm

class Parts:
    def __init__(self, rig, decals):
        self.rig, self.decals, self.objs, self.groups = rig, decals, [], {}
    def add(self, name, bm, mat, weights, mask='none', decal=False, smooth=True, subsurf=0, bevel=0):
        for v in bm.verts: v.co = warp(v.co)
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(name, me); (self.decals if decal else bpy.context.scene.collection).objects.link(ob)
        me.materials.append(mat); ob['mask'] = mask; ob.parent = self.rig
        if smooth:
            for p in me.polygons: p.use_smooth = True
        groups = {}
        for v in me.vertices:
            for bone, w in weights(Vector(v.co)).items():
                if w <= 1e-4: continue
                g = groups.get(bone) or ob.vertex_groups.new(name=bone); groups[bone] = g; g.add([v.index], w, 'REPLACE')
        if bevel:
            bv = ob.modifiers.new('round', 'BEVEL'); bv.width = bevel; bv.segments = 3
        am = ob.modifiers.new('Armature', 'ARMATURE'); am.object = self.rig; am.use_vertex_groups = True; am.use_deform_preserve_volume = False  # volume preservation balloons limbs that IK stretches
        if subsurf:
            sb = ob.modifiers.new('soft', 'SUBSURF'); sb.levels = sb.render_levels = subsurf
        self.objs.append(ob); return ob

def rigid(bone): return lambda p: {bone: 1.0}
def along(a, b, joint, axis, width):  # blend bone a -> b across a band around `joint` along `axis`
    joint, axis = Vector(joint), Vector(axis).normalized()
    def f(p):
        w = ss(-width, width, (p - joint).dot(axis)); return {a: 1 - w, b: w}
    return f
def torso(p):  # pelvis below the waist, spine in the middle, chest at the top, soft bands between
    w_sp = ss(1.1, 1.26, p.z); w_ch = ss(1.36, 1.5, p.z)
    return {'pelvis': 1 - w_sp, 'spine': w_sp * (1 - w_ch), 'chest': w_ch}

def build_body(rig, decals):
    m = kbpuppet.materials(); P = Parts(rig, decals); T = bone_table(); V = lambda n, i: Vector(T[n][i])
    GI, FUR = m['GI'], m['FUR']
    for s, L in ((1, 'L'), (-1, 'R')):
        # legs: thigh and shin trousers blended at the knee, big soft foot on the foot bone
        hip, knee, ank = V(f'thigh.{L}', 0), V(f'shin.{L}', 0), V(f'shin.{L}', 1)
        legw = along(f'thigh.{L}', f'shin.{L}', knee, ank - knee, .1)
        P.add(f'thigh.{L}', capsule(hip, knee, .27, stretch=.45), GI, legw, 'legs')
        P.add(f'shin.{L}', capsule(knee, ank + Vector((0, 0, .1)), .26, stretch=.3), GI, legw, 'legs')
        P.add(f'foot.{L}', ellipsoid(ank + Vector((0, -.15, -.05)), (.29, .44, .16)), FUR,
              along(f'foot.{L}', f'toe.{L}', ank + Vector((0, -.3, -.12)), (0, -1, 0), .07))  # toes bend at the ball of the foot
        # arms: sleeves blended at the elbow, fist on the hand bone
        sh, el, wr = V(f'upper_arm.{L}', 0), V(f'forearm.{L}', 0), V(f'forearm.{L}', 1)
        armw = along(f'upper_arm.{L}', f'forearm.{L}', el, wr - el, .09)
        P.add(f'sleeve_u.{L}', capsule(sh, el, .21, stretch=.5), GI, armw)
        P.add(f'sleeve_f.{L}', capsule(el, wr + (wr - el).normalized() * -.05, .19, stretch=.5), GI, armw)
        hd = V(f'hand.{L}', 1) - V(f'hand.{L}', 0)
        P.add(f'fist.{L}', ellipsoid(wr + hd * .45, (.2, .18, .19)), FUR, rigid(f'hand.{L}'))
        # ears: base and tip blended mid-ear, pink inside
        e0, e1, e2 = V(f'ear_a.{L}', 0), V(f'ear_b.{L}', 0), V(f'ear_b.{L}', 1)
        earw = along(f'ear_a.{L}', f'ear_b.{L}', e1, e2 - e1, .18); R = (e2 - e0).to_track_quat('Z', 'Y').to_matrix()
        mid = (e0 + e2) / 2
        P.add(f'ear.{L}', ellipsoid(mid, (.31, .13, (e2 - e0).length / 2 + .06), R), FUR, earw)
        P.add(f'inner.{L}', ellipsoid(mid + Vector((0, -.09, -.02)), (.2, .06, (e2 - e0).length / 2 - .06), R), m['PINK'], earw, decal=True)
    # torso: tapered jacket, round shoulders, skirt over the trousers, fur V and lapels
    P.add('jacket', cone((0, 0, 1.36), .64, .5, .72, .76), GI, torso, subsurf=2)
    P.add('shoulders', ellipsoid((0, 0, 1.64), (.6, .42, .2)), GI, rigid('chest'))
    P.add('skirt', cone((0, 0, .95), .7, .63, .26, .78), GI, rigid('pelvis'), subsurf=2)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=.24, radius2=0, depth=.05)
    _xf(bm, Matrix.Translation((0, -.38, 1.6)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(math.radians(180), 4, 'Z') @ Matrix.Diagonal((1, 1.3, 1, 1)))
    P.add('chestV', bm, FUR, rigid('chest'), smooth=False)
    for s in (1, -1):
        P.add(f'lapel{s}', box((s * .27, -.39, 1.7), (-s * .03, -.51, 1.06), .1, .05), GI, torso, smooth=False, bevel=.02)
    # belt, knot and hanging ends
    P.add('belt', ring((0, 0, 1.06), .66, .52, 1.3, .085), m['BELT'], rigid('pelvis'), 'belt')
    P.add('knot', ellipsoid((0, -.53, 1.06), (.12, .08, .1)), m['BELT'], rigid('pelvis'), 'belt')
    for s, L in ((1, 'L'), (-1, 'R')):
        j0, j1 = warp((s * .1, -.575, .86)), warp((s * .14, -.59, .72))
        P.add(f'beltend{s}', box((s * .04, -.55, 1.01), (s * .14, -.59, .72), .11, .045), m['BELT'],
              along(f'beltend_a.{L}', f'beltend_b.{L}', j0, j1 - j0, .05), 'belt', smooth=False, bevel=.015)
    P.add('tail', ellipsoid((0, .58, 1.0), (.28, .25, .28)), FUR, rigid('tail'))
    # head
    P.add('head', ellipsoid(HEAD_C, HEAD_S, segs=48), FUR, rigid('head'))
    for s in (1, -1):
        P.add(f'blush{s}', ellipsoid((s * .55, face_y(s * .55, 2.08, -.02), 2.08), (.12, .03, .07)), m['BLUSH'], rigid('head'), decal=True)
    P.add('nose', ellipsoid((0, face_y(0, 2.1, -.01), 2.1), (.065, .035, .048)), m['NOSE'], rigid('head'), decal=True)
    # headband ring, knot and two ribbons (blended along their length)
    P.add('headband', ring((0, 0, 2.62), .85, .73, 1.5, .1), GI, rigid('head'), 'band')
    P.add('bandknot', ellipsoid((-.6, .55, 2.62), (.16, .13, .15)), GI, rigid('head'), 'band')
    for t, w in (('tie1', .17), ('tie2', .15)):
        a0, a1, b1 = V(f'{t}_a', 0), V(f'{t}_a', 1), V(f'{t}_b', 1)
        P.add(t, strip([a0, a1, b1], w * 2), GI, along(f'{t}_a', f'{t}_b', a1, b1 - a1, .15), 'band', smooth=False)
    build_faces(P, m)
    return P

EXPRESSIONS = {}
def build_faces(P, m):
    def eye(x, open_s=(.19, .06, .23), z=2.24):
        y = face_y(x, z)
        return [ellipsoid((x, y + .025, z), open_s), ]
    def add_set(key, parts):
        EXPRESSIONS[key] = [P.add(f'{key}_{i}', bm, mat, rigid('head'), decal=True) for i, (bm, mat) in enumerate(parts)]
    z = 2.24
    for kind in ('open', 'focus', 'happy', 'hurt'):
        parts = []
        for s in (1, -1):
            x = s * .33; y = face_y(x, z)
            if kind in ('open', 'focus'):
                zz = z - (.02 if kind == 'focus' else 0); hz = .21 if kind == 'focus' else .23
                parts += [(ellipsoid((x, y + .03, zz), (.19, .065, hz)), m['EYE']), (ellipsoid((x, y - .005, zz - .07), (.14, .03, .14)), m['IRIS']),
                          (ellipsoid((x - .07, y - .035, zz + .09), (.075, .02, .08)), m['WHITE']), (ellipsoid((x + .07, y - .03, zz - .1), (.035, .015, .035)), m['WHITE'])]
                if kind == 'open':
                    parts.append((tube_curve([(x - .21, face_y(x - .21, z + .14) - .01, z + .14), (x, face_y(x, z + .26) - .02, z + .26), (x + .2, face_y(x + .2, z + .15) - .01, z + .15)], .018), m['INK']))
                else:  # determined brow, low on the inside
                    parts.append((tube_curve([(x + s * .2, face_y(x + s * .2, z + .34) - .02, z + .34), (x - s * .19, face_y(x - s * .19, z + .25) - .02, z + .25)], .024), m['INK']))
            elif kind == 'happy':
                parts.append((tube_curve([(x - .15, face_y(x - .15, z - .03) - .01, z - .03), (x, face_y(x, z + .08) - .02, z + .08), (x + .15, face_y(x + .15, z - .03) - .01, z - .03)], .026), m['INK']))
            else:
                parts.append((tube_curve([(x - s * .13, face_y(x - s * .13, z + .09) - .01, z + .09), (x + s * .1, face_y(x + s * .1, z) - .02, z), (x - s * .13, face_y(x - s * .13, z - .09) - .01, z - .09)], .024), m['INK']))
        add_set('eyes_' + kind, parts)
    zm = 2.0
    add_set('mouth_smile', [(tube_curve([(x, face_y(x, zz) - .015, zz) for x, zz in ((-.12, zm + .04), (-.06, zm - .01), (0, zm + .03), (.06, zm - .01), (.12, zm + .04))], .012), m['INK'])])
    for key, big in (('mouth_open', 1.0), ('mouth_shout', 1.5)):
        add_set(key, [(ellipsoid((0, face_y(0, zm - .04) + .01, zm - .04), (.09 * big, .04, .07 * big)), m['MOUTH']),
                      (ellipsoid((0, face_y(0, zm - .06) - .008, zm - .06 - .01 * big), (.06 * big, .03, .032 * big)), m['TONGUE'])])
