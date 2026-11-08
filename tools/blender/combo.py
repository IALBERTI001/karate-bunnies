# Advancing combination: rear-leg mae geri (middle) -> land forward -> new rear-leg mae geri (head) -> land forward ->
# gyaku zuki lunge. Nov 8 2026, user: "now for the real test, lets chain a combination together. like kicking while
# moving forward."
# Same craft as maegeri.py (one solved body pose per drawing, CONSTANT keys, on twos with the snaps on ones, spring
# follow-through, speed lines / impact star / dust), generalised so EITHER leg can kick:
#  - every beat names the kicking leg; the other foot is the support and never moves while it carries the body
#  - feet live at absolute floor positions (yL, yR = metres forward of the start), the pelvis travels with pos
#  - each landing IS the load of the next technique (karate-body-mechanics, combos: the recovery of one move is the
#    load of the next), so the body never returns to a neutral stance until the end
# Run in Blender after kumite2 build():  C = {}; exec(open(r'...\combo.py').read(), C); C['combo'](G['FIGHTERS']['AKA'], G)
import bpy, bmesh, math
from mathutils import Vector, Matrix

def ease(kind, t):
    t = max(0.0, min(1.0, t))
    if kind == 'in': return t * t * t
    if kind == 'out': return 1 - (1 - t) ** 3
    if kind == 'io': return t * t * (3 - 2 * t)
    if kind == 'snap': return 1 - (1 - t) ** 5
    return t

def mir(h): return (-h[0], h[1], h[2])

# guard, left foot leading (the rear right leg kicks first). a = foot yaw, hl = support-foot heel lift
GUARD = dict(pos=0, sink=.07, wx=0, away=0, lean=4, hipf=0, th=-12, fold=6, foot=0, planted=1, turn=-10, out=0,
             yL=.1, yR=-.32, aL=25, aR=6, hl=0, hL=(.24, -.46, .18), hR=(-.32, -.34, .12))
NUM = ('pos', 'sink', 'wx', 'away', 'lean', 'hipf', 'th', 'fold', 'foot', 'planted', 'turn', 'out', 'yL', 'yR', 'aL', 'aR', 'hl')

def side(d, leg):
    """a right-leg (left-lead) pose dict -> the same pose for the given kicking leg (mirror the lateral parts)"""
    if leg == 'R': return dict(d)
    e = dict(d)
    for k in ('wx', 'turn', 'out'): e[k] = -d[k]
    e['hL'], e['hR'] = mir(d['hR']), mir(d['hL'])
    e['aL'], e['aR'] = -d['aR'], -d['aL']
    e['yL'], e['yR'] = d['yR'], d['yL']
    return e

def kick_beats(t, leg, yS, yK0, yK1, pS, pland, high, first):
    """beats for one rear-leg front kick. yS: support foot, yK0 -> yK1: kicking foot take-off -> landing,
    pS: pelvis over the support foot, pland: pelvis after landing. Values written for the right leg, mirrored for the left."""
    k = 1 if high else 0
    SNAP = dict(planted=0, turn=-6, hL=(.25 + .01 * k, -.44 + .02 * k, .22), hR=(-.56 - .01 * k, .1 + .01 * k, .08), out=.28 * k)
    G = dict(GUARD, yL=yS, yR=yK0)
    def b(**kw): return side(dict(G, **kw), leg)
    # tempo: the first kick starts from a still guard; the second launches straight out of the landing (shorter load)
    # review Nov 8: no guard resets between techniques; each landing launches the next one at once
    T = [2, 4, 6, 8, 10, 11, 13, 14, 15, 17, 19] if first else [1, 2, 4, 5, 6, 7, 9, 10, 11, 13, 15]
    snap_away = 34 if high else 31; th_snap = 132 if high else 100                     # body kick leans back ~15 deg more (review: ref 68)
    rows = [
        ('io', b(pos=pS - .1, sink=.14, wx=.15, lean=7, foot=30, turn=-6)),                                   # dip over the support foot
        ('in', b(pos=pS - .03, sink=.1, wx=.16, lean=3, th=24, fold=70, foot=10, planted=0, turn=-3)),          # the foot leaves on the dip
        ('out', b(pos=pS, sink=.04, wx=.16, away=3, th=104, fold=132, planted=0, turn=-6)),                    # knee pops: tight coil
        ('out', b(pos=pS, sink=.03, wx=.16, away=6, th=114, fold=142, planted=0, turn=-6)),
        ('lin', b(pos=pS, sink=.03, wx=.16, away=9, th=122 + 2 * k, fold=148, planted=0, turn=-6, hR=(-.34, -.3, .12))),
        ('snap', b(pos=pS + .12, sink=.075 + .005 * k, wx=.17, away=snap_away, hipf=.26 - .1 * k, th=th_snap, fold=-6, **SNAP)),  # SNAP: one drawing
        ('out', b(pos=pS + .12, sink=.065 + .01 * k, wx=.17, away=snap_away - 3, hipf=.17 - .02 * k, th=th_snap - 4, fold=12, **SNAP)),
        ('out', b(pos=pS + .1, sink=.02, wx=.16, away=12, hipf=.06, th=112 + 14 * k, fold=120 + 18 * k, planted=0, turn=-6)),  # whips back on its line (high kick: shin folds fully, a half-fold read as a third low kick)
        ('out', b(pos=pS + .1, sink=.02, wx=.16, away=8, th=114, fold=142, planted=0, turn=-6)),
        ('io', b(pos=(pS + pland) / 2, sink=.18, wx=.06, lean=9, th=40, fold=40, planted=0, turn=2, yR=yK1)),     # falls forward onto it, hips already turning to the new lead
        ('out', b(pos=pland, sink=.34, wx=-.04, lean=14, th=0, fold=0, planted=1, turn=9, yR=yK1)),             # lands deep in the NEW lead (turn mirrors the guard: no swing on the next frame), pelvis leads
    ]
    return [(t + dt, kind, d) for dt, (kind, d) in zip(T, rows)], [(t + T[4], t + T[5], leg)], t + T[-1]

def build_beats():
    beats = [(0, 'lin', dict(GUARD)), (1, 'lin', dict(GUARD))]
    for b_ in beats: b_[2]['leg'] = 'R'
    # 1: right leg, middle height. Support L at .10; lands at .85
    b1, s1, land1 = kick_beats(1, 'R', .1, -.32, .85, .1, .55, False, True)
    # 2: left leg, head height, straight out of that landing. Support R at .85; lands at 1.6
    b2, s2, land2 = kick_beats(land1, 'L', .85, .1, 1.6, .87, 1.3, True, False)
    for t_, kind, d in b1: d['leg'] = 'R'
    for t_, kind, d in b2: d['leg'] = 'L'
    beats += b1 + b2
    # 3: gyaku zuki lunge (left foot now leads). Load in the landing, then the front foot slides in, the rear leg
    # straightens with the heel up, the hips turn square, the trunk inclines ~20 deg and the right fist drives to head
    # height; the left hand pulls back to the chin (kumite, not the hip).
    L0 = dict(GUARD, yL=1.6, yR=.85, aL=-6, aR=-25, leg='R')            # feet as the left-leg kick landed them (no pivot on arrival)
    t = land2
    # head stays up with the eyes on the target; the lean goes into the rear heel -> hip -> shoulder line (review Nov 8)
    beats += [
        (t + 1, 'io', dict(L0, pos=1.36, sink=.36, lean=11, turn=-14, hR=(-.42, -.12, .02), hL=(.26, -.52, .24))),              # load in the landing: low, fist at the ribs
        (t + 3, 'in', dict(L0, pos=1.5, sink=.35, lean=14, turn=6, hipf=.08, yL=1.74, foot=25, aR=-16,
                           hR=(-.4, -.24, .06), hL=(.24, -.4, .3))),                                                         # hips lead: front foot slides, hips turn, fist still home
        (t + 4, 'snap', dict(L0, pos=1.6, sink=.34, lean=17, turn=26, hipf=.15, yL=1.8, foot=40, aR=-10,
                             hR=(-.06, -.92, .5), hL=(.22, -.2, .36))),                                                      # PUNCH: the fist arrives last, one drawing
        (t + 6, 'out', dict(L0, pos=1.62, sink=.33, lean=16, turn=24, hipf=.14, yL=1.8, foot=38, aR=-10,
                            hR=(-.07, -.9, .48), hL=(.22, -.2, .36))),                                                       # hold (kiai)
        (t + 8, 'lin', dict(L0, pos=1.62, sink=.32, lean=15, turn=23, hipf=.12, yL=1.8, foot=36, aR=-10,
                            hR=(-.08, -.88, .47), hL=(.22, -.2, .36))),
        (t + 10, 'io', dict(L0, pos=1.58, sink=.28, lean=9, turn=4, yL=1.8, yR=1.08, foot=10, aR=0,
                            hR=(-.22, -.5, .24), hL=(.24, -.4, .26))),                                                       # recover: the rear foot steps up first
        (t + 13, 'io', dict(L0, pos=1.52, sink=.14, lean=3, turn=-10, yL=1.8, yR=1.22, aR=6)),                               # then the hips rise (head lags via the springs)
        (t + 16, 'io', dict(L0, pos=1.5, sink=.18, lean=5, turn=-11, yL=1.8, yR=1.24)),                                      # settle with a small overshoot
        (t + 19, 'io', dict(L0, pos=1.5, sink=.15, lean=4, turn=-10, yL=1.8, yR=1.24)),
    ]
    punch = (t + 1, t + 4)
    return beats, s1 + s2, punch, (land1, land2, t + 4)

BEATS, SNAPS, PUNCH, MARKS = build_beats()
END = BEATS[-1][0]
_snapf = [s[1] for s in SNAPS] + [PUNCH[1]]
ONES = set()
for f1 in _snapf: ONES |= set(range(f1 - 6, f1 + 5))
for f_land in MARKS[:2]: ONES |= set(range(f_land - 3, f_land + 2))
DRAWINGS = sorted({f for f in range(0, END + 1) if f % 2 == 0 or f in ONES})

def state(f):
    for (f0, _, a), (f1, kind, b) in zip(BEATS, BEATS[1:]):
        if f0 <= f <= f1:
            u = ease(kind, (f - f0) / (f1 - f0)) if f1 > f0 else 1
            S = {k: a[k] + (b[k] - a[k]) * u for k in NUM}
            for h in ('hL', 'hR'): S[h] = tuple(x + (y - x) * u for x, y in zip(a[h], b[h]))
            S['leg'] = b['leg']
            return S
    S = dict(BEATS[-1][2]); return S

def leg_points(hip, S, L, Ls):
    a = math.radians(S['th']); b = math.radians(S['th'] - S['fold']); o = S.get('out', 0)
    s = 1 if S['leg'] == 'R' else -1
    knee = hip + Vector((s * o * .5, -math.sin(a), -math.cos(a))).normalized() * L
    ankle = knee + Vector((s * o * .5, -math.sin(b), -math.cos(b))).normalized() * Ls * .995
    bend = Vector((0, -math.cos(a), math.sin(a)))
    return knee, ankle, bend, b

def body_pose(F, G, S):
    rig = F['rig']; pb = rig.pose.bones; R = G['R']; K = S['leg']; Sp = 'L' if K == 'R' else 'R'
    L = pb[f'thigh.{K}'].bone.length; Ls = pb[f'shin.{K}'].bone.length
    root = Vector((0, -S['pos'], 0))
    P = dict(G['DEFAULT'], pos=S['pos'], sink=S['sink'], shift=(S['wx'], S['hipf']), away=S['away'], lean=S['lean'], turn=S['turn'],
             head=(S['away'] * .3 - S['lean'] * .75, 0, -S['turn'] * .95), hL=S['hL'], hR=S['hR'])
    x = {'L': .2, 'R': -.2}; y = {'L': S['yL'], 'R': S['yR']}; a = {'L': S['aL'], 'R': S['aR']}
    # a planted foot turns on the ball of the foot, never the ankle (karate-body-mechanics: pivot on the BALL); the beat
    # positions are where the ball is at zero yaw, so a turn-out keeps the ball where it was
    def ballfoot(L, lift):
        off = R(0, 0, a[L]) @ Vector((0, -.3, 0))                     # apply_pose: ball = (x, -y) + off
        return (x[L] - off.x, y[L] - S['pos'] + .3 + off.y, a[L], lift)
    P['f' + Sp] = ballfoot(Sp, S['hl'])
    P['f' + K] = ballfoot(K, S['foot'])
    G['apply_pose'](F, P)
    if S['planted'] < .999:
        hip = pb[f'thigh.{K}'].head.copy(); planted_ankle = pb[f'foot_ik.{K}'].head.copy()
        knee, ankle, bend, b = leg_points(hip, S, L, Ls)
        w = S['planted']
        if w > 0: ankle = ankle.lerp(planted_ankle, w ** .5)
        ankle.z = max(ankle.z, .12)
        P['f' + K] = (tuple(ankle - root), R(-math.degrees(b) + S['foot'], 0, 0))
        P['pole' + K] = tuple(knee + bend * .8 - root)
        G['apply_pose'](F, P)
    return P

# ---------------- follow-through springs (as maegeri.py) ----------------
CHAINS = [(('ear_a.L', 'ear_b.L'), 95, 7, 0, 30), (('ear_a.R', 'ear_b.R'), 95, 7, 0, 30),     # looser than the single kick: the snaps and landings must show in the ears
          (('tie1_a', 'tie1_b'), 40, 4.5, 7, 110), (('tie2_a', 'tie2_b'), 34, 4, 7, 110)]
def follow_through(F, keep):
    import kbbody
    rig = F['rig']; pb = rig.pose.bones; vl = bpy.context.view_layer; sc = bpy.context.scene
    st = {}; dt = 1 / sc.render.fps; sub = 6
    for f in range(0, END + 1):
        sc.frame_set(f)
        for bones, k, c, g, cap in CHAINS:
            for n in bones:
                p = pb[n]; p.rotation_quaternion = (1, 0, 0, 0); vl.update()
                h = p.head.copy(); r = p.tail.copy(); ln = (r - h).length
                if n not in st: st[n] = [r.copy(), Vector()]
                xx, v = st[n]
                root_tie = n.startswith('tie') and n.endswith('_a')
                kk, cc, gg, cp = (k * 4, c * 2, g * .3, 35) if root_tie else (k, c, g, cap)
                for _ in range(sub):
                    acc = (r - xx) * kk - v * cc + Vector((0, 0, -gg)); v = v + acc * (dt / sub); xx = xx + v * (dt / sub)
                    xx = h + (xx - h).normalized() * ln
                d0, d1 = (r - h).normalized(), (xx - h).normalized(); ang = d0.angle(d1, 0)
                if ang > math.radians(cp): d1 = d0.slerp(d1, math.radians(cp) / ang); xx = h + d1 * ln
                if n.startswith('tie'):
                    hb = pb['head']; Rm = hb.bone.matrix_local @ hb.matrix.inverted(); xr = Rm @ xx
                    c0 = kbbody.HEAD_C; rr = Vector(kbbody.HEAD_R) + Vector((.08, .08, .08))
                    q_ = Vector(((xr.x - c0.x) / rr.x, (xr.y - c0.y) / rr.y, (xr.z - c0.z) / rr.z))
                    if q_.length < 1:
                        q_.normalize(); xx = Rm.inverted() @ Vector((c0.x + q_.x * rr.x, c0.y + q_.y * rr.y, c0.z + q_.z * rr.z)); xx = h + (xx - h).normalized() * ln
                st[n] = [xx, v]
                q = d0.rotation_difference(d1)
                p.matrix = Matrix.Translation(h) @ (q.to_matrix() @ p.matrix.to_3x3()).to_4x4(); vl.update()
                if f in keep: p.keyframe_insert('rotation_quaternion', frame=f)

# ---------------- effects ----------------
def _flat(name, hexc):
    m = bpy.data.materials.get(name)
    if not m:
        import kbpuppet; m = kbpuppet._flat(name, hexc); m.name = name; m.use_backface_culling = False
    return m

def fx_obj(name, bm, coll, mat):
    import kbbody
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o

def show(o, frames):
    for f in range(0, END + 2):
        vis = f in frames; o.hide_render = o.hide_viewport = not vis
        o.keyframe_insert('hide_render', frame=f); o.keyframe_insert('hide_viewport', frame=f)

def tube(points, radii, ring=6):
    bm = bmesh.new(); rings = []
    for i, (p, r) in enumerate(zip(points, radii)):
        t = (points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]).normalized()
        u = t.cross(Vector((1, 0, 0))).normalized() if abs(t.x) < .9 else t.cross(Vector((0, 0, 1))).normalized(); w = t.cross(u)
        rings.append([bm.verts.new(p + (u * math.cos(a) + w * math.sin(a) * .55) * max(r, .004)) for a in [2 * math.pi * j / ring for j in range(ring)]])
    for A, Bv in zip(rings, rings[1:]):
        for j in range(ring): bm.faces.new((A[j], A[(j + 1) % ring], Bv[(j + 1) % ring], Bv[j]))
    return bm

def star(tip, plane_axes, coll, name, frame, size=1.0):
    bm = bmesh.new()
    for s in range(16):
        a = 2 * math.pi * (s % 8) / 8 + .3; ln = (.55 if s % 2 == 0 else .32) * size
        ax = plane_axes[0] if s < 8 else plane_axes[1]
        p0 = bm.verts.new(tip + ax(a - .25) * .16 * size); p1 = bm.verts.new(tip + ax(a) * ln); p2 = bm.verts.new(tip + ax(a + .25) * .16 * size)
        bm.faces.new((p0, p1, p2))
    o = fx_obj(name, bm, coll, _flat('KB_FX', '#fff1d0')); show(o, {frame}); return o

def effects(F, G, hips):
    rig = F['rig']; pb = rig.pose.bones; M = rig.matrix_world; M3 = M.to_3x3()
    coll = bpy.data.collections.get('FX') or bpy.data.collections.new('FX')
    if coll.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(coll)
    for o in list(coll.objects): bpy.data.objects.remove(o, do_unlink=True)
    ink = _flat('KB_SPEED', '#3a2a24'); dust = _flat('KB_DUST', '#d9e4fb')
    for i, (f0, f1, leg) in enumerate(SNAPS):
        L = pb[f'thigh.{leg}'].bone.length; Ls = pb[f'shin.{leg}'].bone.length; sg = 1 if leg == 'R' else -1
        pts, outs = [], []; n = 16
        for j in range(n + 1):
            f = f0 + (f1 - f0) * j / n; S = state(f); S['leg'] = leg
            knee, ankle, bend, bb = leg_points(hips[(f1, leg)], S, L, Ls)
            ball = ankle + Vector((0, -math.cos(bb), math.sin(bb))) * .3 + Vector((0, -math.sin(bb), -math.cos(bb))) * .05
            pts.append(M @ ball); outs.append((M3 @ (ball - knee)).normalized())
        for part, (j0, frames) in enumerate(((3, {f1}), (int(n * .5), {f1 + 1}))):
            for k, off in enumerate((.1, .2, .3)):
                sd = M3 @ Vector((-.12 * sg, 0, 0))
                path = [p + o * off + sd for p, o in zip(pts[j0:], outs[j0:])]; path = path[:max(3, int(len(path) * .7))]
                m_ = len(path); rad = [.05 * math.sin(math.pi * (jj + .5) / m_) ** .7 for jj in range(m_)]
                show(fx_obj(f'fx_speed{i}_{part}_{k}', tube(path, rad), coll, ink), frames)
        tip = pts[-1] + outs[-1] * (.25 if i else .05) + M3 @ Vector((-.18 * sg if i else 0, 0, 0))   # the high kick's flash sits outside the face
        star(tip, (lambda a: M3 @ Vector((0, math.cos(a), math.sin(a))), lambda a: M3 @ Vector((math.cos(a), 0, math.sin(a)))), coll, f'fx_star{i}', f1)
    # punch: short straight streaks behind the fist and a smaller star at the knuckles
    f0, f1 = PUNCH; bpy.context.scene.frame_set(f1); fist = M @ pb['hand.R'].tail.copy(); bpy.context.scene.frame_set(f0); start = M @ pb['hand.R'].tail.copy()
    dvec = (fist - start); dn = dvec.normalized()
    for k, off in enumerate((-.09, 0, .09)):
        sdv = (M3 @ Vector((0, 0, 1))) * off
        path = [start.lerp(fist, .2 + .6 * j / 7) + sdv for j in range(8)]
        show(fx_obj(f'fx_punch{k}', tube(path, [.035 * math.sin(math.pi * (j + .5) / 8) ** .7 for j in range(8)]), coll, ink), {f1, f1 + 1})
    star(fist + dn * .1, (lambda a: M3 @ Vector((0, math.cos(a), math.sin(a))), lambda a: M3 @ Vector((math.cos(a), 0, math.sin(a)))), coll, 'fx_star_punch', f1, .8)
    # dust where a foot pushes off and where it lands
    puffs = [('off0', SNAPS[0][0] - 6, 'R', -1), ('land0', MARKS[0], 'R', 1), ('land1', MARKS[1], 'L', 1), ('slide', MARKS[2], 'L', 1)]
    for tag, f0, foot, back in puffs:
        bpy.context.scene.frame_set(f0); base = M @ pb[f'foot_ik.{foot}'].head.copy(); base.z = .03
        for k in range(5 if tag == 'slide' else 7):
            a = (k - 3) * .42 + (.12 if k % 2 else -.08)
            d = Vector((math.sin(a) * .8, -back * math.cos(a) * .7, .12)).normalized() * (1.15 if k % 2 else .85)
            bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=.07)
            o = fx_obj(f'fx_dust_{tag}{k}', bm, coll, dust); dw = (M3 @ d).normalized()
            o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = dw.to_track_quat('Y', 'Z')
            for j, sc_ in enumerate((.8, 1.0, .8, .45)):
                f = f0 + j * 2
                o.location = base + dw * (.2 + .32 * j) + Vector((0, 0, .05 * j - .012 * j * j)); o.scale = (sc_ * .45, sc_ * (2.6 + 1.2 * j), sc_ * .35)
                o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
            show(o, set(range(f0, f0 + 8)))
    for o in coll.objects:
        for fc in (G['fcurves'](o) if o.animation_data else []):
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

def combo(F, G, fx=True):
    rig = F['rig']; pb = rig.pose.bones
    rig.animation_data_clear(); sc = bpy.context.scene; sc.frame_start, sc.frame_end = 0, END
    for f in DRAWINGS:
        S = state(f); P = body_pose(F, G, S); G['key'](F, f, P)
    hips = {}
    for (f0, f1, leg) in SNAPS:
        S = state(f1); body_pose(F, G, S); hips[(f1, leg)] = pb[f'thigh.{leg}'].head.copy()
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    follow_through(F, set(DRAWINGS))
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    if fx: effects(F, G, hips)
    return DRAWINGS

def check(F):
    """per drawing: how far each foot that should be planted moved since the last drawing, and support-balance error"""
    rig = F['rig']; pb = rig.pose.bones; sc = bpy.context.scene; out = []; last = {}
    for f in DRAWINGS:
        sc.frame_set(f); S = state(f); row = {'f': f}
        for L in 'LR':
            p = rig.matrix_world @ pb[f'foot.{L}'].head
            flying = (S['leg'] == L and S['planted'] < .999)
            if not flying and L in last and not last[L][1]:
                row['slide' + L] = round((p.xy - last[L][0].xy).length, 3)
            last[L] = (p.copy(), flying)
        out.append(row)
    return out
