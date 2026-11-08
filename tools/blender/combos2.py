# More combinations on the same machinery as combo.py (Nov 8 2026, user: "We are finding the correct way to animate.
# Lets see a different set of combinations."). Adds what the first chain never needed:
#  - roll: the kicking leg's plane rolls from vertical (front kick) to flat (roundhouse): the knee turns over and the
#    shin snaps ACROSS, the support foot pivots on its ball until the heel faces the target, the trunk drops away (tilt)
#  - kb: a back kick - the knee points down, the heel leads, the sole faces the target
#  - hspin: hands follow the body (needed when the body spins away from the opponent), blended with target-aimed hands
#  - head: eyes on the target through a full spin; the neck turns at most 75 deg, so the head whips round (spotting)
# Combos:
#  'mawashi': kizami-zuki -> gyaku-zuki -> rear-leg mawashi geri jodan (the punch leaves the hips turning, the kick
#             continues the turn), land forward in the other lead
#  'ushiro':  kizami mae geri (skip step) -> land forward -> spinning ushiro geri (360) -> land forward, other lead
# Run: C2 = {'HERE': folder}; exec(open(folder + r'\combos2.py').read(), C2); C2['run']('mawashi', F, G)
import os, math
exec(open(os.path.join(HERE, 'combo.py')).read(), globals())
from mathutils import Vector, Matrix

GUARD2 = dict(GUARD, roll=0, tilt=0, kb=0, hspin=0, leg='R')
NUM = NUM + ('roll', 'tilt', 'kb', 'hspin')

def Rz(deg): return Matrix.Rotation(math.radians(deg), 3, 'Z')
GW_L = dict(hL=GUARD['hL'], hR=GUARD['hR'])                                       # left-lead guard, aimed at the target
GW_R = dict(hL=mir(GUARD['hR']), hR=mir(GUARD['hL']))                             # right-lead guard
def body_rel(h, turn): return tuple(Rz(-turn) @ Vector(h))                         # target-aimed -> body-relative at that turn
HB_L = {k: body_rel(v, -10) for k, v in GW_L.items()}
HB_R = {k: body_rel(v, 10) for k, v in GW_R.items()}

def B(**kw): return dict(GUARD2, **kw)

def leg_frame(S):
    """thigh and shin directions. A front kick folds in the vertical plane. A roundhouse keeps the thigh raised and turns
    the knee OVER: the shin's fold plane rotates about the thigh's own axis (hip rotation), and the thigh opens out a
    little. (v1 rolled the whole leg about the forward axis, which turned the kick's height into sideways swing: Nov 8.)"""
    a = math.radians(S['th']); b = math.radians(S['th'] - S['fold']); o = S.get('out', 0); r = S.get('roll', 0)
    s = 1 if S['leg'] == 'R' else -1
    d1 = Vector((s * o * .5, -math.sin(a), -math.cos(a))).normalized()
    d2 = Vector((s * o * .5, -math.sin(b), -math.cos(b))).normalized()
    bend = Vector((0, -math.cos(a), math.sin(a)))
    Ro = Matrix.Rotation(s * math.radians(r * .25), 3, 'Y')                      # thigh opens out (abduction)
    d1, d2, bend = Ro @ d1, Ro @ d2, Ro @ bend
    Rk = Matrix.Rotation(math.radians(-s * r), 3, d1)                            # knee turns over about the thigh axis
    return d1, Rk @ d2, Rk @ bend, Rk @ Ro, b

def leg_points(hip, S, L, Ls):
    d1, d2, bend, Rleg, b = leg_frame(S)
    knee = hip + d1 * L; ankle = knee + d2 * Ls * .995
    return knee, ankle, bend, b

def body_pose(F, G, S):
    rig = F['rig']; pb = rig.pose.bones; R = G['R']; K = S['leg']; Sp = 'L' if K == 'R' else 'R'
    L = pb[f'thigh.{K}'].bone.length; Ls = pb[f'shin.{K}'].bone.length
    root = Vector((0, -S['pos'], 0))
    rel = ((-S['turn'] + 180) % 360) - 180                                          # where the target is, relative to the body
    hy = max(-75, min(75, rel * .95))
    hs = S['hspin']
    def hand(h): return tuple(Vector(h) * (1 - hs) + (Rz(S['turn']) @ Vector(h)) * hs)
    P = dict(G['DEFAULT'], pos=S['pos'], sink=S['sink'], shift=(S['wx'], S['hipf']), away=S['away'], lean=S['lean'], tilt=S['tilt'],
             turn=S['turn'], head=(S['away'] * .3 - S['lean'] * .75, -S['tilt'] * .6, hy), hL=hand(S['hL']), hR=hand(S['hR']))
    x = {'L': .2, 'R': -.2}; y = {'L': S['yL'], 'R': S['yR']}; a = {'L': S['aL'], 'R': S['aR']}
    def ballfoot(Lf, lift):
        off = R(0, 0, a[Lf]) @ Vector((0, -.3, 0))
        return (x[Lf] - off.x, y[Lf] - S['pos'] + .3 + off.y, a[Lf], lift)
    P['f' + Sp] = ballfoot(Sp, S['hl']); P['f' + K] = ballfoot(K, S['foot'])
    G['apply_pose'](F, P)
    if S['planted'] < .999:
        hip = pb[f'thigh.{K}'].head.copy(); planted_ankle = pb[f'foot_ik.{K}'].head.copy()
        knee, ankle, bend, b = leg_points(hip, S, L, Ls)
        w = S['planted']
        if w > 0: ankle = ankle.lerp(planted_ankle, w ** .5)
        ankle.z = max(ankle.z, .12)
        s = 1 if K == 'R' else -1
        if S['kb'] > .5:
            Rf = R(90 + S['foot'], 0, 180)                                            # back kick: toes down, sole to the target, heel leads
            pole = knee - bend * .8                                                  # knee points down
        else:
            Rf = leg_frame(S)[3] @ R(-math.degrees(b) + S['foot'], 0, 0)              # the foot turns over with the knee (instep leads)
            pole = knee + bend * .8
        P['f' + K] = (tuple(ankle - root), Rf); P['pole' + K] = tuple(pole - root)
        G['apply_pose'](F, P)
    return P

# ---------------- the combinations ----------------
def combo_mawashi():
    g = lambda **kw: B(leg='R', **kw)
    RG = dict(hL=GW_R['hL'], hR=GW_R['hR'])
    beats = [
        (0, 'lin', g()), (1, 'lin', g()),
        (3, 'io', g(sink=.13, lean=7, turn=-14, pos=.02)),                                                           # load
        (5, 'in', g(sink=.15, lean=12, turn=-20, pos=.12, yL=.26, hL=(.2, -.72, .34), hR=(-.24, -.3, .28))),            # front foot slides, lead hand leaves
        (6, 'snap', g(sink=.17, lean=17, turn=-26, pos=.2, yL=.34, hL=(.1, -.98, .5), hR=(-.22, -.28, .32))),           # JAB (one drawing)
        (8, 'out', g(sink=.17, lean=16, turn=-24, pos=.2, yL=.34, hL=(.12, -.93, .48), hR=(-.22, -.28, .32))),
        (10, 'in', g(sink=.22, lean=10, turn=-14, pos=.26, yL=.34, yR=-.14, hL=(.24, -.5, .26), hR=(-.42, -.12, .02))),  # jab home, rear foot follows, fist at the ribs
        (12, 'in', g(sink=.3, lean=13, turn=6, hipf=.08, pos=.36, yL=.38, yR=-.14, foot=22, aR=-14, hL=(.24, -.42, .3), hR=(-.4, -.24, .06))),  # hips lead
        (13, 'snap', g(sink=.32, lean=17, turn=26, hipf=.15, pos=.44, yL=.42, yR=-.14, foot=40, aR=-10, hL=(.22, -.2, .36), hR=(-.06, -.95, .5))),  # GYAKU-ZUKI
        (15, 'out', g(sink=.31, lean=16, turn=25, hipf=.14, pos=.44, yL=.42, yR=-.14, foot=40, aR=-10, hL=(.22, -.2, .36), hR=(-.07, -.92, .48))),
        # the hips keep turning: the rear leg comes off the floor into the roundhouse
        (17, 'in', g(planted=0, th=45, fold=85, roll=35, sink=.22, wx=.15, lean=8, turn=40, pos=.46, yL=.42, yR=-.14, aL=60, hl=15, foot=20,
                     hL=(.2, -.35, .4), hR=(-.4, -.1, .1))),
        (19, 'out', g(planted=0, th=95, fold=140, roll=80, sink=.12, wx=.17, tilt=14, away=4, turn=62, pos=.48, yL=.42, aL=110, hl=30, foot=60,
                      hL=(.15, -.35, .42), hR=(-.5, .12, -.05))),                                                       # knee turned over, heel tucked
        (21, 'lin', g(planted=0, th=110, fold=148, roll=88, sink=.11, wx=.17, tilt=22, away=6, turn=74, pos=.5, yL=.42, aL=130, hl=32, foot=70,
                      hL=(.14, -.32, .44), hR=(-.54, .18, -.1))),
        (22, 'snap', g(planted=0, th=128, fold=-4, roll=86, sink=.1, wx=.18, tilt=34, away=8, hipf=.1, turn=88, pos=.52, yL=.42, aL=150, hl=34, foot=80,
                       hL=(.12, -.3, .46), hR=(-.56, .22, -.12))),                                                      # MAWASHI GERI jodan (one drawing)
        (24, 'out', g(planted=0, th=124, fold=12, roll=86, sink=.1, wx=.18, tilt=31, away=8, hipf=.09, turn=86, pos=.52, yL=.42, aL=150, hl=34, foot=80,
                      hL=(.12, -.3, .46), hR=(-.56, .22, -.12))),
        (25, 'out', g(planted=0, th=114, fold=138, roll=86, sink=.12, wx=.17, tilt=22, away=5, turn=76, pos=.52, yL=.42, aL=135, hl=30, foot=60,
                      hL=(.18, -.36, .4), hR=(-.4, 0, .05))),                                                           # slingshots back to the chamber
        (26, 'out', g(planted=0, th=108, fold=148, roll=80, sink=.13, wx=.16, tilt=14, away=3, turn=60, pos=.54, yL=.42, aL=110, hl=26, foot=50,
                      hL=(.2, -.38, .36), hR=(-.36, -.1, .1))),
        (28, 'io', g(planted=0, th=40, fold=40, roll=20, sink=.2, wx=.06, lean=8, tilt=3, turn=22, pos=.86, yL=.42, yR=1.2, aL=40, hl=10, **RG)),  # hips unwind, falls forward
        (30, 'out', g(planted=1, th=0, fold=0, sink=.33, wx=-.04, lean=12, turn=10, pos=.98, yL=.42, yR=1.2, aL=-6, aR=-25, **RG)),                 # lands in the other lead
        (33, 'io', g(sink=.18, lean=5, turn=10, pos=.98, yL=.42, yR=1.2, aL=-6, aR=-25, **RG)),
        (36, 'io', g(sink=.14, lean=4, turn=10, pos=.97, yL=.42, yR=1.2, aL=-6, aR=-25, **RG)),
    ]
    return beats, [(21, 22, 'R')], [(5, 6, 'L'), (12, 13, 'R')], [(30, 'R')], [(3, 'R')]

def combo_ushiro():
    gl = lambda **kw: B(leg='L', **kw)
    gr = lambda **kw: B(leg='R', **kw)
    SL = dict(hspin=1, **HB_L)                                                       # guard that turns with the body
    SR = dict(hspin=1, **HB_R)
    beats = [
        (0, 'lin', gl()), (1, 'lin', gl()),
        (3, 'io', gl(sink=.14, wx=-.14, lean=3, turn=-12, pos=-.04, yR=-.12, foot=25)),                               # skip: rear foot slides up, weight back
        (5, 'in', gl(planted=0, th=30, fold=75, sink=.1, wx=-.16, away=3, turn=-12, pos=-.04, yR=-.12, foot=10)),
        (7, 'out', gl(planted=0, th=104, fold=135, sink=.05, wx=-.16, away=7, turn=-12, pos=-.02, yR=-.12)),
        (9, 'lin', gl(planted=0, th=112, fold=146, sink=.05, wx=-.16, away=10, turn=-12, pos=-.02, yR=-.12)),
        (10, 'snap', gl(planted=0, th=98, fold=-6, sink=.08, wx=-.17, away=24, hipf=.2, turn=-8, pos=.08, yR=-.12,
                        hL=(.26, -.44, .24), hR=(-.4, -.05, .06))),                                                      # KIZAMI MAE GERI
        (12, 'out', gl(planted=0, th=94, fold=12, sink=.07, wx=-.17, away=21, hipf=.16, turn=-8, pos=.08, yR=-.12, hL=(.26, -.44, .24), hR=(-.4, -.05, .06))),
        (13, 'out', gl(planted=0, th=110, fold=125, sink=.05, wx=-.16, away=10, hipf=.05, turn=-10, pos=.1, yR=-.12)),
        (14, 'out', gl(planted=0, th=112, fold=142, sink=.05, wx=-.16, away=7, turn=-10, pos=.12, yR=-.12)),
        (16, 'io', gl(planted=0, th=40, fold=40, sink=.15, lean=8, turn=-10, pos=.42, yR=-.12, yL=.75)),               # drops forward onto it
        (17, 'out', gl(planted=1, sink=.26, lean=8, turn=-14, pos=.52, yR=-.12, yL=.75)),                              # plants: the landing starts the spin
        # spinning back kick with the right leg; the left foot pivots on its ball the whole way round
        (18, 'io', gr(sink=.22, wx=.12, lean=6, turn=-45, pos=.66, yL=.75, yR=-.12, aL=-20, hl=15, **SL)),             # the head turns first (spotting)
        (20, 'in', gr(planted=0, th=-50, fold=110, kb=1, sink=.15, wx=.15, lean=14, turn=-115, pos=.72, yL=.75, yR=-.12, aL=-90, hl=30, **SL)),
        (22, 'out', gr(planted=0, th=-100, fold=150, kb=1, sink=.12, wx=.16, lean=24, turn=-165, pos=.74, yL=.75, aL=-140, hl=32, **SL)),   # back to the target, knee to the chest
        (23, 'lin', gr(planted=0, th=-104, fold=152, kb=1, sink=.11, wx=.16, lean=28, turn=-172, pos=.75, yL=.75, aL=-146, hl=33, **SL)),
        (24, 'snap', gr(planted=0, th=97, fold=-4, kb=1, sink=.1, wx=.17, lean=42, hipf=.12, turn=-178, pos=.8, yL=.75, aL=-152, hl=34, **SL)),  # USHIRO GERI: heel straight back
        (26, 'out', gr(planted=0, th=93, fold=12, kb=1, sink=.1, wx=.17, lean=40, hipf=.1, turn=-178, pos=.8, yL=.75, aL=-152, hl=34, **SL)),
        (27, 'out', gr(planted=0, th=10, fold=135, kb=1, sink=.12, wx=.14, lean=20, turn=-205, pos=.82, yL=.75, aL=-180, hl=30, **SL)),       # knee snaps back in, keeps turning
        (29, 'io', gr(planted=0, th=40, fold=50, kb=0, sink=.18, wx=.05, lean=8, turn=-290, pos=1.0, yL=.75, yR=1.4, aL=-280, hl=15, **SR)),
        (31, 'out', gr(planted=1, sink=.32, wx=-.04, lean=12, turn=-350, pos=1.12, yL=.75, yR=1.4, aL=-366, aR=-385, **SR)),                 # lands in front, the other lead
        (34, 'io', gr(sink=.18, lean=5, turn=-350, pos=1.12, yL=.75, yR=1.4, aL=-366, aR=-385, **SR)),
        (37, 'io', gr(sink=.14, lean=4, turn=-350, pos=1.11, yL=.75, yR=1.4, aL=-366, aR=-385, **SR)),
    ]
    return beats, [(9, 10, 'L'), (23, 24, 'R')], [], [(17, 'L'), (31, 'R')], [(3, 'R')]

COMBOS = {'mawashi': combo_mawashi, 'ushiro': combo_ushiro}

def setup(name):
    global BEATS, SNAPS, PUNCHES, LANDS, PUSHES, END, ONES, DRAWINGS
    BEATS, SNAPS, PUNCHES, LANDS, PUSHES = COMBOS[name]()
    END = BEATS[-1][0]
    ONES = set()
    for (f0, f1, _) in SNAPS + PUNCHES: ONES |= set(range(f1 - 6, f1 + 5))
    for (f, _) in LANDS: ONES |= set(range(f - 3, f + 2))
    DRAWINGS = sorted({f for f in range(0, END + 1) if f % 2 == 0 or f in ONES})

def effects(F, G, hips):
    rig = F['rig']; pb = rig.pose.bones; M = rig.matrix_world; M3 = M.to_3x3(); sc = bpy.context.scene
    coll = bpy.data.collections.get('FX') or bpy.data.collections.new('FX')
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    for o in list(coll.objects): bpy.data.objects.remove(o, do_unlink=True)
    ink = _flat('KB_SPEED', '#3a2a24'); dust = _flat('KB_DUST', '#d9e4fb')
    ax2 = (lambda a: M3 @ Vector((0, math.cos(a), math.sin(a))), lambda a: M3 @ Vector((math.cos(a), 0, math.sin(a))))
    for i, (f0, f1, leg) in enumerate(SNAPS):                                      # streaks along the foot's real path
        pts = []
        for j in range(13):
            f = f0 + (f1 - f0) * j / 12; S = state(f); S['leg'] = leg
            L = pb[f'thigh.{leg}'].bone.length; Ls = pb[f'shin.{leg}'].bone.length
            knee, ankle, bend, bb = leg_points(hips[(f1, leg)], S, L, Ls); pts.append((M @ ankle, M3 @ (ankle - knee).normalized()))
        for k, off in enumerate((.1, .2, .3)):
            path = [p + o * off for p, o in pts[3:]][:7]
            m_ = len(path); rad = [.05 * math.sin(math.pi * (jj + .5) / m_) ** .7 for jj in range(m_)]
            show(fx_obj(f'fx_speed{i}_{k}', tube(path, rad), coll, ink), {f1, f1 + 1})
        tip = pts[-1][0] + pts[-1][1] * .3
        star(tip, ax2, coll, f'fx_star{i}', f1)
    for i, (f0, f1, hd) in enumerate(PUNCHES):
        sc.frame_set(f1); fist = M @ pb[f'hand.{hd}'].tail.copy(); sc.frame_set(f0); start = M @ pb[f'hand.{hd}'].tail.copy()
        dn = (fist - start).normalized()
        for k, off in enumerate((-.09, 0, .09)):
            sdv = (M3 @ Vector((0, 0, 1))) * off
            path = [start.lerp(fist, .2 + .6 * j / 7) + sdv for j in range(8)]
            show(fx_obj(f'fx_punch{i}_{k}', tube(path, [.035 * math.sin(math.pi * (j + .5) / 8) ** .7 for j in range(8)]), coll, ink), {f1, f1 + 1})
        star(fist + dn * .1, ax2, coll, f'fx_pstar{i}', f1, .8)
    for tag, lst, back in (('land', LANDS, 1), ('push', PUSHES, -1)):
        for n, (f0, foot) in enumerate(lst):
            sc.frame_set(f0); base = M @ pb[f'foot_ik.{foot}'].head.copy(); base.z = .03
            for k in range(7):
                a = (k - 3) * .42 + (.12 if k % 2 else -.08)
                d = Vector((math.sin(a) * .8, -back * math.cos(a) * .7, .12)).normalized() * (1.15 if k % 2 else .85)
                bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=.07)
                o = fx_obj(f'fx_dust_{tag}{n}_{k}', bm, coll, dust); dw = (M3 @ d).normalized()
                o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = dw.to_track_quat('Y', 'Z')
                for j, sc_ in enumerate((.8, 1.0, .8, .45)):
                    f = f0 + j * 2
                    o.location = base + dw * (.2 + .32 * j) + Vector((0, 0, .05 * j - .012 * j * j)); o.scale = (sc_ * .45, sc_ * (2.6 + 1.2 * j), sc_ * .35)
                    o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
                show(o, set(range(f0, f0 + 8)))
    for o in coll.objects:
        for fc in (G['fcurves'](o) if o.animation_data else []):
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

def run(name, F, G, fx=True):
    setup(name); return combo(F, G, fx)

def slides(F, tol=.02):
    rig = F['rig']; pb = rig.pose.bones; sc = bpy.context.scene; last = {}; rows = []
    for f in DRAWINGS:
        sc.frame_set(f); S = state(f); r = {'f': f}
        for L_ in 'LR':
            p = rig.matrix_world @ pb[f'toe.{L_}'].head; fly = S['leg'] == L_ and S['planted'] < .999
            if not fly and L_ in last and not last[L_][1]: r[L_] = round((p.xy - last[L_][0].xy).length, 3)
            last[L_] = (p.copy(), fly)
        if any(v > tol for k, v in r.items() if k != 'f'): rows.append(r)
    return rows
