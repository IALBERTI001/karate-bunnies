# Mae geri (front kick), double: middle then head height, on the v3 long-legged bunny. v4, Nov 8 2026.
# Target: the user's 2D karate reference clip ("I want to feel the movements like the video"). Measured at 30 fps
# (karate-body-mechanics skill, mae geri beat table): knee drive 7f to a chest-high chamber with the foot tucked under
# the thigh; ONE drawing for the snap; hold 3f; re-chamber 2-3f with speed lines; second kick to head height with the
# trunk leaning back ~20 deg and the standing leg straight; snap back; land forward with a dust burst. Arms stay in a
# tight guard; the power reads from the hips, the lean, the follow-through (hair) and the effects. Drawn on twos and
# threes, on ones for the snaps.
# How it is built:
#  1. BODY: every drawing is SOLVED from the timeline (no Blender in-betweens): thigh and shin angles give the knee and
#     ankle on the leg's own arc, the trunk counter-leans, the standing foot stays planted. Keys are CONSTANT (stepped).
#  2. FOLLOW-THROUGH: ears, headband ribbons and belt ends are springs simulated every frame (stiffness, damping,
#     gravity, an angle cap), so they lag the snaps and overshoot, like the hair in the reference.
#  3. EFFECTS: a tapered streak along the foot's path on each snap, an impact star at full extension, dust at push-off
#     and landing. Cream with the same ink outline as the bunny.
# Run in Blender after kumite2 build():  M = {}; exec(open(r'...\maegeri.py').read(), M); M['kick'](G['FIGHTERS']['AKA'], G)
import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion

def ease(kind, t):
    t = max(0.0, min(1.0, t))
    if kind == 'in': return t * t * t                  # accelerating (leaving a pose with force)
    if kind == 'out': return 1 - (1 - t) ** 3          # decelerating (arriving and stopping)
    if kind == 'io': return t * t * (3 - 2 * t)
    if kind == 'snap': return 1 - (1 - t) ** 5         # the strike: all speed, stops dead
    return t

# th = thigh angle from straight down (+ forward), fold = knee flex (0 straight), pos = travel toward the target,
# wx = weight shift over the standing (left) foot, away = trunk counter-lean back, hipf = hip thrust forward,
# planted = kicking foot on the floor (1) or flying (0), fy = where it is planted (+ = in front), foot = extra toe pitch,
# hL/hR = fists from the chest head
GUARD = dict(pos=0, sink=.07, wx=0, away=0, lean=4, hipf=0, th=-12, fold=6, foot=0, planted=1, fy=-.32, turn=-10, out=0, ly=0,
             hL=(.24, -.46, .18), hR=(-.32, -.34, .12))   # fists in front of the chest, elbows bent and down  # tight guard: lead fist at the chin, rear fist back by the cheek, elbow tucked back (it hid the knee)
def B(**kw): return dict(GUARD, **kw)
# v5 (fresh-eyes review, Nov 8): the whole body throws each kick - trunk leans back 22/32 deg with the hips pushed through,
# the standing leg locks straight on the snap, the rear fist pulls back as the lead hand reaches; a 2-frame dip over the
# support foot, the foot leaves on the dip and the knee POPS; tight coil (heel under the seat); retract along the same
# line; travel a full foot length on the landing.
SNAP1 = dict(planted=0, turn=-6, hL=(.25, -.44, .22), hR=(-.56, .1, .08))    # rear fist pulls back to the ribs (hikite), outside the jacket (at .42 the sleeve sank half into it, Nov 8)           # lead glove stays at the chin line (it cluttered the impact)
SNAP2 = dict(planted=0, turn=-6, hL=(.26, -.42, .22), hR=(-.57, .11, .08), out=.28)     # high kick outside its own head line, AWAY from the front camera (toward it, the foot covered the face)
BEATS = [
    (0, 'lin', B()),
    (5, 'lin', B()),
    (7, 'io', B(sink=.14, wx=.15, lean=7, foot=30, turn=-6)),                                        # dip: hips over the support foot
    (9, 'in', B(sink=.1, wx=.16, lean=3, th=24, fold=70, foot=10, planted=0, turn=-3)),               # the foot LEAVES on the dip
    (11, 'out', B(sink=.04, wx=.16, away=3, th=104, fold=132, planted=0, turn=-6)),                    # knee pops up: tight coil
    (14, 'out', B(sink=.03, wx=.16, away=6, th=114, fold=142, planted=0, turn=-6)),                    # heel tucked under the knee, still rising
    (16, 'lin', B(sink=.03, wx=.16, away=9, th=122, fold=148, planted=0, turn=-6, hR=(-.34, -.3, .12))),  # wind-up: trunk eases back
    (17, 'snap', B(pos=.12, sink=.075, wx=.17, away=24, hipf=.22, th=100, fold=-6, **SNAP1)),          # SNAP 1 (overshoots)
    (19, 'out', B(pos=.12, sink=.065, wx=.17, away=21, hipf=.17, th=96, fold=12, **SNAP1)),           # recoils ~10% before the whip back
    (20, 'out', B(pos=.1, sink=.02, wx=.16, away=12, hipf=.06, th=112, fold=120, planted=0, turn=-6)),  # whips back on the same line
    (21, 'out', B(pos=.1, sink=.02, wx=.16, away=8, th=114, fold=142, planted=0, turn=-6)),
    (24, 'lin', B(pos=.1, sink=.02, wx=.16, away=12, th=124, fold=148, planted=0, turn=-6, hR=(-.34, -.3, .12))),
    (25, 'snap', B(pos=.13, sink=.08, wx=.17, away=34, hipf=.16, th=132, fold=-6, **SNAP2)),         # SNAP 2: head height
    (27, 'out', B(pos=.13, sink=.075, wx=.17, away=30, hipf=.15, th=128, fold=12, **SNAP2)),
    (28, 'out', B(pos=.13, sink=.06, wx=.16, away=22, hipf=.08, th=126, fold=105, planted=0, turn=-6, out=.05)),  # knee stays high, shin folds
    (29, 'out', B(pos=.14, sink=.03, wx=.16, away=12, hipf=.03, th=114, fold=140, planted=0, turn=-6)),            # tight chamber
    (32, 'io', B(pos=.45, sink=.12, wx=.06, away=0, lean=8, th=40, fold=40, planted=0, fy=.85, turn=-8)),            # falls forward onto it
    (34, 'out', B(pos=.72, sink=.36, wx=-.04, lean=14, th=0, fold=0, planted=1, fy=.85, turn=-9, ly=.22)),          # lands deep: pelvis leads, head drops; the back foot starts to slide up
    (37, 'io', B(pos=.76, sink=.2, wx=-.04, lean=7, fy=.85, turn=-10, ly=.42)),
    (40, 'io', B(pos=.77, sink=.13, wx=-.04, lean=4, fy=.85, turn=-10, ly=.5)),                                             # recovers, a touch high
    (44, 'io', B(pos=.77, sink=.16, wx=-.04, lean=5, fy=.85, turn=-10, ly=.5)),
]
END = BEATS[-1][0]
NUM = ('pos', 'sink', 'wx', 'away', 'lean', 'hipf', 'th', 'fold', 'foot', 'planted', 'fy', 'turn', 'out', 'ly')
ONES = set(range(6, 12)) | set(range(16, 22)) | set(range(24, 31)) | set(range(32, 36))  # fast parts on ones; the kick itself is ONE drawing (16->17, 24->25)
DRAWINGS = sorted({f for f in range(0, END + 1) if f % 2 == 0 or f in ONES})
SNAPS = [(16, 17), (24, 25)]                             # chamber -> full extension, for the streaks

def state(f):
    for (f0, _, a), (f1, kind, b) in zip(BEATS, BEATS[1:]):
        if f0 <= f <= f1:
            u = ease(kind, (f - f0) / (f1 - f0)); S = {k: a[k] + (b[k] - a[k]) * u for k in NUM}
            for h in ('hL', 'hR'): S[h] = tuple(x + (y - x) * u for x, y in zip(a[h], b[h]))
            return S
    return dict(BEATS[-1][2])

def leg_points(hip, S, L, Ls):
    a = math.radians(S['th']); b = math.radians(S['th'] - S['fold'])
    o = S.get('out', 0)
    knee = hip + Vector((o * .5, -math.sin(a), -math.cos(a))).normalized() * L
    ankle = knee + Vector((o * .5, -math.sin(b), -math.cos(b))).normalized() * Ls * .995
    bend = Vector((0, -math.cos(a), math.sin(a)))                  # the way the knee points (in the leg's plane)
    return knee, ankle, bend, b

def body_pose(F, G, S):
    rig = F['rig']; pb = rig.pose.bones; R = G['R']; L = pb['thigh.R'].bone.length; Ls = pb['shin.R'].bone.length
    root = Vector((0, -S['pos'], 0))
    P = dict(G['DEFAULT'], pos=S['pos'], sink=S['sink'], shift=(S['wx'], S['hipf']), away=S['away'], lean=S['lean'], turn=S['turn'],
             head=(S['away'] * .3 - S['lean'] * .2, 0, -S['turn'] * .6), hL=S['hL'], hR=S['hR'],
             fL=(.2, .1 + S['ly'] - S['pos'], 25, 0))                         # standing foot: planted, turned out, heel down; ly = its slide-up after the landing
    P['fR'] = (-.2, S['fy'] - S['pos'], 6, S['foot'])
    G['apply_pose'](F, P)
    if S['planted'] < .999:
        hip = pb['thigh.R'].head.copy(); planted_ankle = pb['foot_ik.R'].head.copy()   # where the planted pose puts the ankle
        knee, ankle, bend, b = leg_points(hip, S, L, Ls)
        w = S['planted']
        if w > 0: ankle = ankle.lerp(planted_ankle, w ** .5)                  # toe-off / touchdown: blend to the REAL planted ankle (v4a used a spot .3 off: the foot skated)
        ankle.z = max(ankle.z, .12)                                            # never through the floor
        P['fR'] = (tuple(ankle - root), R(-math.degrees(b) + S['foot'], 0, 0))  # toes pulled back square to the shin: ball of the foot leads
        P['poleR'] = tuple(knee + bend * .8 - root)
        G['apply_pose'](F, P)
    return P

# ---------------- 2. follow-through springs ----------------
CHAINS = [  # bones root to tip, stiffness, damping, gravity, max swing from the posed shape (deg)
    (('ear_a.L', 'ear_b.L'), 140, 9, 0, 24), (('ear_a.R', 'ear_b.R'), 140, 9, 0, 24),
    (('tie1_a', 'tie1_b'), 40, 4.5, 7, 110), (('tie2_a', 'tie2_b'), 34, 4, 7, 110),
]
def follow_through(F, keep):
    rig = F['rig']; pb = rig.pose.bones; vl = bpy.context.view_layer; sc = bpy.context.scene
    st = {}; dt = 1 / sc.render.fps; sub = 6
    for f in range(0, END + 1):
        sc.frame_set(f)
        for bones, k, c, g, cap in CHAINS:
            for n in bones:
                p = pb[n]; p.rotation_quaternion = (1, 0, 0, 0); vl.update()
                h = p.head.copy(); r = p.tail.copy(); ln = (r - h).length
                if n not in st: st[n] = [r.copy(), Vector()]
                x, v = st[n]
                root_tie = n.startswith('tie') and n.endswith('_a')               # the ribbon's first segment stands off the head
                kk, cc, gg, cp = (k * 4, c * 2, g * .3, 35) if root_tie else (k, c, g, cap)
                for _ in range(sub):
                    acc = (r - x) * kk - v * cc + Vector((0, 0, -gg)); v = v + acc * (dt / sub); x = x + v * (dt / sub)
                    x = h + (x - h).normalized() * ln
                d0, d1 = (r - h).normalized(), (x - h).normalized()
                ang = d0.angle(d1, 0)
                if ang > math.radians(cp):                                   # cap the swing (an uncapped ear flops)
                    d1 = d0.slerp(d1, math.radians(cp) / ang); x = h + d1 * ln
                if n.startswith('tie'):                                            # ribbons never lie on (or in) the skull
                    hb = pb['head']; Rm = hb.bone.matrix_local @ hb.matrix.inverted(); xr = Rm @ x
                    import kbbody; c = kbbody.HEAD_C; rr = Vector(kbbody.HEAD_R) + Vector((.08, .08, .08))
                    q_ = Vector(((xr.x - c.x) / rr.x, (xr.y - c.y) / rr.y, (xr.z - c.z) / rr.z))
                    if q_.length < 1: q_.normalize(); x = Rm.inverted() @ Vector((c.x + q_.x * rr.x, c.y + q_.y * rr.y, c.z + q_.z * rr.z)); x = h + (x - h).normalized() * ln
                st[n] = [x, v]
                q = d0.rotation_difference(d1)
                p.matrix = Matrix.Translation(h) @ (q.to_matrix() @ p.matrix.to_3x3()).to_4x4(); vl.update()
                if f in keep: p.keyframe_insert('rotation_quaternion', frame=f)

# ---------------- 3. effects ----------------
def fx_material():
    m = bpy.data.materials.get('KB_FX')
    if not m:
        import kbpuppet; m = kbpuppet._flat('KB_FX', '#fff1d0'); m.name = 'KB_FX'; m.use_backface_culling = False
    return m

def fx_obj(name, bm, coll):
    import kbbody
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(fx_material())
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); coll.objects.link(o); kbbody.hull(o, .02); return o

def show(o, frames):
    for f in range(0, END + 2):
        vis = f in frames
        o.hide_render = o.hide_viewport = not vis
        o.keyframe_insert('hide_render', frame=f); o.keyframe_insert('hide_viewport', frame=f)

def tube(points, radii, ring=10):
    bm = bmesh.new(); rings = []
    for i, (p, r) in enumerate(zip(points, radii)):
        t = (points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]).normalized()
        u = t.cross(Vector((1, 0, 0))).normalized() if abs(t.x) < .9 else t.cross(Vector((0, 0, 1))).normalized(); w = t.cross(u)
        rings.append([bm.verts.new(p + (u * math.cos(a) + w * math.sin(a) * .55) * max(r, .004)) for a in [2 * math.pi * j / ring for j in range(ring)]])
    for A, Bv in zip(rings, rings[1:]):
        for j in range(ring): bm.faces.new((A[j], A[(j + 1) % ring], Bv[(j + 1) % ring], Bv[j]))
    bm.faces.new(rings[-1][::-1]); return bm

def ball_point(ankle, b):  # ball of the foot: along the foot, which is square to the shin
    return ankle + Vector((0, -math.cos(b), math.sin(b))) * .3 + Vector((0, -math.sin(b), -math.cos(b))) * .05

def effects(F, G, hips):
    rig = F['rig']; pb = rig.pose.bones; M = rig.matrix_world; L = pb['thigh.R'].bone.length; Ls = pb['shin.R'].bone.length
    coll = bpy.data.collections.get('FX') or bpy.data.collections.new('FX')
    if coll.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(coll)
    for o in list(coll.objects): bpy.data.objects.remove(o, do_unlink=True)
    for i, (f0, f1) in enumerate(SNAPS):
        pts, outs = [], []
        n = 16
        for j in range(n + 1):                                                # the foot's path from chamber to extension
            f = f0 + (f1 - f0) * j / n; S = state(f)
            knee, ankle, bend, bb = leg_points(hips[f1], S, L, Ls)
            ball = ball_point(ankle, bb); pts.append(M @ ball); outs.append((M.to_3x3() @ (ball - knee)).normalized())
        # speed lines (reference frames 71 and 86): three dark tapered arcs trailing the foot, on the snap frame and the next
        ink = bpy.data.materials.get('KB_SPEED')                           # its own dark flat material (the ink-hull material only draws back faces)
        if not ink:
            import kbpuppet; ink = kbpuppet._flat('KB_SPEED', '#3a2a24'); ink.name = 'KB_SPEED'; ink.use_backface_culling = False
        for part, (j0, frames) in enumerate(((3, {f1}), (int(n * .5), {f1 + 1}))):
            for k, off in enumerate((.1, .2, .3)):                                # OUTSIDE the foot's arc: never across the leg
                side = M.to_3x3() @ Vector((-.12, 0, 0))                          # out on the kicking leg's outer side, so they draw over the body
                path = [p + o * off + side for p, o in zip(pts[j0:], outs[j0:])]
                path = path[:max(3, int(len(path) * .7))]                      # stop well short of the foot: the leg covers the end of its own path
                m_ = len(path); rad = [.05 * math.sin(math.pi * (jj + .5) / m_) ** .7 for jj in range(m_)]
                o = fx_obj(f'fx_speed{i}_{part}_{k}', tube(path, rad, ring=6), coll); o.modifiers.clear(); o.data.materials[0] = ink
                show(o, frames)
        # impact star at the ball of the foot: spikes in two crossed planes so it reads from the side and the front
        tip = pts[-1]; bm = bmesh.new()
        for s in range(16):
            a = 2 * math.pi * (s % 8) / 8 + .3; ln = .55 if s % 2 == 0 else .32
            ax = (lambda a: Vector((0, math.cos(a), math.sin(a)))) if s < 8 else (lambda a: Vector((math.cos(a), 0, math.sin(a))))
            p0 = bm.verts.new(tip + ax(a - .25) * .16); p1 = bm.verts.new(tip + ax(a) * ln); p2 = bm.verts.new(tip + ax(a + .25) * .16)
            bm.faces.new((p0, p1, p2))
        star = fx_obj(f'fx_star{i}', bm, coll); star.modifiers.clear()
        star.data.materials[0].use_backface_culling = False
        show(star, {f1})                                                    # the flash is one drawing (a lingering star read as a stray dot)
    # dust: pale wisps (not foot-coloured blobs), stretched along their direction, from the foot that pushes / lands
    dm = bpy.data.materials.get('KB_DUST')
    if not dm:
        import kbpuppet; dm = kbpuppet._flat('KB_DUST', '#d9e4fb'); dm.name = 'KB_DUST'
    for tag, f0, where, back in (('off', 8, Vector((-.2, .36, .03)), 1), ('land', 34, Vector((-.2, -.75, .03)), -1)):
        for k in range(7):
            a = (k - 3) * .42 + (.12 if k % 2 else -.08)
            d = Vector((math.sin(a) * .8, back * math.cos(a) * .7, .12)).normalized() * (1.15 if k % 2 else .85)
            bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=.07)
            o = fx_obj(f'fx_dust_{tag}{k}', bm, coll); o.data.materials[0] = dm; base = M @ where
            dw = (M.to_3x3() @ d).normalized(); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = dw.to_track_quat('Y', 'Z')
            for j, sc_ in enumerate((.8, 1.0, .8, .45)):
                f = f0 + j * 2
                o.location = base + dw * (.2 + .32 * j) + Vector((0, 0, .05 * j - .012 * j * j)); o.scale = (sc_ * .45, sc_ * (2.6 + 1.2 * j), sc_ * .35)
                o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
            show(o, set(range(f0, f0 + 8)))
    for o in coll.objects:
        if o.animation_data and o.animation_data.action:
            for fc in G['fcurves'](o) if 'fcurves' in G else []:
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

def ribbon_thickness(name):
    for t in ('tie1', 'tie2'):
        o = bpy.data.objects.get(f'{name}_{t}')
        if not o or o.modifiers.get('thick'): continue
        ink = bpy.data.materials.get('KB_INK')
        if ink and ink.name not in [m.name for m in o.data.materials if m]: o.data.materials.append(ink)
        m = o.modifiers.new('thick', 'SOLIDIFY'); m.thickness = .035; m.offset = 0; m.use_rim = True
        m.material_offset_rim = len(o.data.materials) - 1

def kick(F, G, fx=True):
    rig = F['rig']; pb = rig.pose.bones; ribbon_thickness(rig.name.replace('_rig', ''))
    rig.animation_data_clear(); sc = bpy.context.scene; sc.frame_start, sc.frame_end = 0, END
    hips = {}
    for f in DRAWINGS:
        S = state(f); P = body_pose(F, G, S)
        G['key'](F, f, P)
    for f in range(0, END + 1):                                            # the hip at every frame (for the streak paths)
        S = state(f); body_pose(F, G, S); hips[f] = pb['thigh.R'].head.copy()
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'          # stepped: every drawing is its own solved pose
    follow_through(F, set(DRAWINGS))
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    if fx: effects(F, G, hips)
    return DRAWINGS
