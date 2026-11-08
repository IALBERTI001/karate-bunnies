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
GUARD = dict(pos=0, sink=.07, wx=0, away=0, lean=4, hipf=0, th=-12, fold=6, foot=0, planted=1, fy=-.32, turn=-10,
             hL=(.12, -.36, .3), hR=(-.22, -.04, .28))  # tight guard: lead fist at the chin, rear fist back by the cheek, elbow tucked back (it hid the knee)
def B(**kw): return dict(GUARD, **kw)
BEATS = [
    (0, 'lin', B()),
    (6, 'lin', B()),
    (8, 'io', B(sink=.11, wx=.1, lean=6, foot=28, turn=-6)),                                          # load: weight onto the front foot, heel peels
    (11, 'in', B(sink=.07, wx=.14, lean=2, away=2, th=62, fold=110, planted=0, turn=-2)),              # knee DRIVES (accelerating)
    (13, 'out', B(sink=.05, wx=.15, away=4, th=104, fold=114, planted=0, turn=0)),                     # chamber: knee to the chest, foot tucked
    (15, 'out', B(sink=.05, wx=.15, away=5, th=110, fold=118, planted=0, turn=0)),      # knee up and OUT in front (a round body hides a chest-high knee)
    (16, 'lin', B(sink=.05, wx=.15, away=5, th=111, fold=119, planted=0, turn=0)),     # chamber HELD (reference: 2-3f), then
    (17, 'snap', B(pos=.05, sink=.05, wx=.15, away=13, hipf=.1, th=92, fold=-3, planted=0, turn=0,     # SNAP 1: middle
                   hL=(.14, -.42, .26))),
    (19, 'out', B(pos=.05, sink=.05, wx=.15, away=12, hipf=.09, th=90, fold=2, planted=0, turn=0, hL=(.14, -.42, .26))),
    (21, 'out', B(pos=.06, sink=.05, wx=.15, away=6, hipf=.02, th=108, fold=116, planted=0, turn=0)),  # re-chamber
    (23, 'io', B(pos=.06, sink=.04, wx=.15, away=8, th=116, fold=124, planted=0, turn=0)),
    (24, 'lin', B(pos=.06, sink=.04, wx=.15, away=9, th=117, fold=125, planted=0, turn=0)),  # held
    (25, 'snap', B(pos=.09, sink=.04, wx=.16, away=22, hipf=.1, th=124, fold=-3, planted=0, turn=0,     # SNAP 2: the opponent's head height, out in FRONT of
                   hL=(.16, -.42, .2), hR=(-.24, .02, .26))),                         # its own big head (th 150 went up past its face)
    (27, 'out', B(pos=.09, sink=.04, wx=.16, away=23, hipf=.1, th=127, fold=0, planted=0, turn=0,
                  hL=(.16, -.42, .2), hR=(-.24, .02, .26))),
    (28, 'in', B(pos=.1, sink=.05, wx=.15, away=16, hipf=.05, th=124, fold=75, planted=0, turn=0)),    # snaps back
    (30, 'out', B(pos=.11, sink=.06, wx=.15, away=8, th=106, fold=114, planted=0, turn=0)),
    (33, 'io', B(pos=.2, sink=.08, wx=.07, away=0, lean=4, th=35, fold=30, planted=0, fy=.42, turn=-4)),  # falls forward onto it
    (35, 'out', B(pos=.26, sink=.19, wx=0, lean=11, th=0, fold=0, planted=1, fy=.42, turn=-6)),           # lands, absorbs
    (39, 'io', B(pos=.27, sink=.08, lean=5, fy=.42, turn=-8)),                                            # settles in the new stance
    (48, 'lin', B(pos=.27, sink=.08, lean=5, fy=.42, turn=-8)),
]
END = BEATS[-1][0]
NUM = ('pos', 'sink', 'wx', 'away', 'lean', 'hipf', 'th', 'fold', 'foot', 'planted', 'fy', 'turn')
ONES = set(range(15, 20)) | set(range(23, 30))           # the kick itself is ONE drawing (16->17, 24->25), the streak shows the path           # the snaps change every frame; the rest is on twos
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
    knee = hip + Vector((0, -math.sin(a), -math.cos(a))) * L
    ankle = knee + Vector((0, -math.sin(b), -math.cos(b))) * Ls * .995
    bend = Vector((0, -math.cos(a), math.sin(a)))                  # the way the knee points (in the leg's plane)
    return knee, ankle, bend, b

def body_pose(F, G, S):
    rig = F['rig']; pb = rig.pose.bones; R = G['R']; L = pb['thigh.R'].bone.length; Ls = pb['shin.R'].bone.length
    root = Vector((0, -S['pos'], 0))
    P = dict(G['DEFAULT'], pos=S['pos'], sink=S['sink'], shift=(S['wx'], S['hipf']), away=S['away'], lean=S['lean'], turn=S['turn'],
             head=(S['away'] * .45 - S['lean'] * .4, 0, -S['turn'] * .6), hL=S['hL'], hR=S['hR'],
             fL=(.2, .1 - S['pos'], 25, 0))                                   # standing foot: planted, turned out, heel down
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
    (('bend1_a', 'bend1_b'), 90, 9, 9, 50), (('bend2_a', 'bend2_b'), 90, 9, 9, 50),
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
                for _ in range(sub):
                    acc = (r - x) * k - v * c + Vector((0, 0, -g)); v = v + acc * (dt / sub); x = x + v * (dt / sub)
                    x = h + (x - h).normalized() * ln
                d0, d1 = (r - h).normalized(), (x - h).normalized()
                ang = d0.angle(d1, 0)
                if ang > math.radians(cap):                                   # cap the swing (an uncapped ear flops)
                    d1 = d0.slerp(d1, math.radians(cap) / ang); x = h + d1 * ln
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
        pts, inner = [], []
        n = 16
        for j in range(n + 1):                                                # the area the foot sweeps between chamber and extension
            f = f0 + (f1 - f0) * j / n; S = state(f)
            knee, ankle, bend, bb = leg_points(hips[f1], S, L, Ls)
            ball = ball_point(ankle, bb); pts.append(M @ ball)
            inner.append(M @ (ball + (ankle.lerp(knee, .35) - ball) * (j / n) ** .8))  # thin at the start, as wide as the foot+shin at the end
        bm = bmesh.new(); A = [bm.verts.new(p) for p in pts]; Bv = [bm.verts.new(p) for p in inner]
        for j in range(n): bm.faces.new((A[j], A[j + 1], Bv[j + 1], Bv[j]))
        sw = fx_obj(f'fx_streak{i}', bm, coll); sw.modifiers.clear()
        show(sw, {f1, f1 + 1})
        # impact star at the ball of the foot: spikes in two crossed planes so it reads from the side and the front
        tip = pts[-1]; bm = bmesh.new()
        for s in range(16):
            a = 2 * math.pi * (s % 8) / 8 + .3; ln = .55 if s % 2 == 0 else .32
            ax = (lambda a: Vector((0, math.cos(a), math.sin(a)))) if s < 8 else (lambda a: Vector((math.cos(a), 0, math.sin(a))))
            p0 = bm.verts.new(tip + ax(a - .25) * .16); p1 = bm.verts.new(tip + ax(a) * ln); p2 = bm.verts.new(tip + ax(a + .25) * .16)
            bm.faces.new((p0, p1, p2))
        star = fx_obj(f'fx_star{i}', bm, coll); star.modifiers.clear()
        star.data.materials[0].use_backface_culling = False
        show(star, {f1, f1 + 1})
    # dust: a burst at toe-off behind the kicking foot, and at the landing foot (on twos, like the drawn effects)
    for tag, f0, where, back in (('off', 10, Vector((-.2, .2, .03)), 1), ('land', 34, Vector((-.2, -.25, .03)), -1)):
        for k in range(7):
            a = (k - 3) * .5 + (.17 if k % 2 else -.11)
            d = Vector((math.sin(a) * .9, back * math.cos(a) * .6, 0)) * (1.15 if k % 2 else .85)
            bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=.12)
            o = fx_obj(f'fx_dust_{tag}{k}', bm, coll); base = M @ where
            for j, sc_ in enumerate((.7, 1.15, 1.25, 1.0)):                     # puff out, then gone (shrinking to dots read as rings)
                f = f0 + j * 2
                o.location = base + (M.to_3x3() @ d) * (.1 + .16 * j) + Vector((0, 0, .03 + .05 * j)); o.scale = (sc_, sc_, sc_ * .8)
                o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
            show(o, set(range(f0, f0 + 8)))
    for o in coll.objects:
        if o.animation_data and o.animation_data.action:
            for fc in G['fcurves'](o) if 'fcurves' in G else []:
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

def kick(F, G, fx=True):
    rig = F['rig']; pb = rig.pose.bones
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
