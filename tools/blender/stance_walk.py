# Fighting-stance advance (kumite footwork, the "walk forward" of a fighting game). Nov 9 2026, user: "lets do the
# combat stance forward walk now."
# The bunny never leaves its guard: side-on, fists up, eyes on the target, knees bent, light on the rear heel.
# Each advance is a step-drag (yori ashi / okuri ashi):
#  1. the rear leg pushes: the rear heel rises, the pelvis starts forward, the front heel unweights
#  2. the front foot slides out low (skims the floor, toes first) and lands ball -> heel
#  3. the weight drops onto the front knee (the body's lowest point), the lead fist reaches a touch with the step
#  4. the rear foot glides up on its ball to restore the stance; the pelvis arrives over the same spot in the stance
# Built on the same rules as the walk and the combos: planted feet never slide (balls fixed while planted, heels pivot
# about the ball), the pelvis stays between the feet, the head is level on the target, ears on springs.
# Run: SW = {'HERE': folder}; exec(open(folder + r'\stance_walk.py').read(), SW); SW['advance'](F, G)
import os, math
exec(open(os.path.join(HERE, 'combo.py')).read(), globals())
CHAINS = [(('ear_a.L', 'ear_b.L'), 50, 3.5, 0, 45), (('ear_a.R', 'ear_b.R'), 50, 3.5, 0, 45),
          (('tie1_a', 'tie1_b'), 40, 4.5, 7, 110), (('tie2_a', 'tie2_b'), 34, 4, 7, 110)]
from mathutils import Vector

ADV = 16                 # frames per advance at 30 fps (~0.53 s)
D = .52                  # distance per advance (chibi: 2-3x adult; .34 read as a shuffle, .44 as a cautious step)
LEAD = 4                 # still guard frames before the first step
N = 3                    # advances
END = LEAD + ADV * N + 6
RH = 14                  # resting rear heel lift: kumite stance is light on the rear foot
FEET = {'L': dict(x=.2, Y=GUARD['yL'] + .08, yaw=GUARD['aL']),    # left foot leads (orthodox): the combos' guard, a longer stance
        'R': dict(x=-.2, Y=GUARD['yR'] - .06, yaw=GUARD['aR'])}   # (.42 apart read as feet together in profile)
SINK = .15               # the stance sits lower while moving: bent knees read as 'ready to fight'
ONES = set(range(0, END + 1)); DRAWINGS = list(range(0, END + 1))   # footwork reads smooth: every frame is a drawing

def smooth(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def g(t, c, w): return math.exp(-((t - c) / w) ** 2)

def phase(f):
    """(advance index k, frame t inside it)"""
    k = (f - LEAD) // ADV
    if f < LEAD: return 0, 0
    if k >= N: return N, 0
    return k, f - LEAD - ADV * k

def foot(L, f):
    """('plant', Y_abs, heel) or ('free', Y_abs, lift, pitch). Y_abs: ankle forward distance at zero yaw (the ball is .3 ahead)."""
    k, t = phase(f); Y0 = FEET[L]['Y'] + D * k
    if L == 'L':                                                       # the FRONT foot moves first, t 2 -> 8
        if t < 3: return ('plant', Y0, 8 * smooth(t / 3))              # unweights while the rear leg pushes: the heel lifts
        if t < 8:
            u = (t - 3) / 5.
            return ('free', Y0 + D * smooth(u), .075 * math.sin(math.pi * u), 8 * (1 - u) + 6 * u + 9 * math.sin(math.pi * u))
        return ('plant', Y0 + D, 6 * (1 - smooth((t - 8) / 2.5)))       # lands on the ball, the heel settles
    # the REAR foot drives, then glides up, t 8 -> 14
    if t < 8: return ('plant', Y0, RH + 16 * smooth(t / 3.5))         # the push FIRST (t 0-3): the rear heel drives up, the knee straightens
    if t < 14:
        u = (t - 8) / 6.
        return ('free', Y0 + D * smooth(u), .045 * math.sin(math.pi * u), 30 - 4 * u)            # glides on the ball, heel clearly up
    return ('plant', Y0 + D, 22 - (22 - RH) * smooth((t - 14) / 2))

def body(f):
    k, t = phase(f)
    p = .25 * smooth(t / 4) + .45 * smooth((t - 3) / 6) + .3 * smooth((t - 8) / 7)   # the push moves the hips first, then the step, then the drag
    return dict(pos=D * (k + p),
                sink=SINK + .12 * g(t, 9, 1.8) - .035 * g(t, 2.5, 1.6),   # rises on the push, settles hard onto the front knee   # rises on the push, drops onto the front knee
                lean=GUARD['lean'] + 5 + 6 * g(t, 5, 2.5),       # committed: the trunk drives toward the target
                turn=GUARD['turn'] - 6 + 4 * g(t, 5, 2.5),       # more side-on: the lead shoulder forward                  # the hips open a touch with the push
                reach=g(t, 6, 2.5))

def pose(F, G, f):
    R = G['R']; B = body(f); root = Vector((0, -B['pos'], 0))
    # karate kamae, not a boxer's peekaboo (review): the lead fist a forearm forward at shoulder height, far enough to clear the big head in profile, the rear fist at the chin
    hL = Vector((.14, -.86, .1)) + Vector((0, -.04, .01)) * B['reach']    # the lead fist covers forward with the step
    hR = Vector((-.12, -.34, .2)) + Vector((0, 0, .015)) * B['reach']
    P = dict(G['DEFAULT'], pos=B['pos'], sink=B['sink'], shift=(0, 0), away=0, lean=B['lean'], turn=B['turn'],
             head=(-B['lean'] * .75 + 7, 0, -B['turn'] * .95), hL=tuple(hL), hR=tuple(hR))
    for L in 'LR':
        fo = foot(L, f); x = FEET[L]['x']; yaw = FEET[L]['yaw']
        if fo[0] == 'plant':
            _, Y, heel = fo; P['f' + L] = (x, Y - B['pos'], yaw, heel)
        else:
            _, Y, lift, pitch = fo
            ball = Vector((x, -Y, 0)) + R(0, 0, yaw) @ Vector((0, -.3, .04)) + Vector((0, 0, lift))
            Rf = R(pitch, 0, yaw); ankle = ball - Rf @ G['BALL']
            P['f' + L] = (tuple(ankle - root), Rf)
    G['apply_pose'](F, P)
    return P

def advance(F, G, fx=False):
    rig = F['rig']; rig.animation_data_clear(); sc = bpy.context.scene; sc.frame_start, sc.frame_end = 0, END
    coll = bpy.data.collections.get('FX')
    if coll:
        for o in list(coll.objects): bpy.data.objects.remove(o, do_unlink=True)
    for f in DRAWINGS:
        P = pose(F, G, f); G['key'](F, f, P)
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    follow_through(F, set(DRAWINGS))
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    return DRAWINGS

def check(F, G):
    """planted balls must not slide; legs must reach their feet; the pelvis must stay between the feet"""
    rig = F['rig']; pb = rig.pose.bones; rows = []; last = {}
    for f in DRAWINGS:
        pose(F, G, f); r = {'f': f}
        for L in 'LR':
            fo = foot(L, f); toe = pb[f'toe.{L}'].head.copy()
            gap = (pb[f'foot_ik.{L}'].head - pb[f'shin.{L}'].tail).length
            if gap > .02: r['gap' + L] = round(gap, 3)
            if fo[0] == 'plant' and L in last and last[L][0] == 'plant':
                d = (toe.xy - last[L][1].xy).length
                if d > .01: r['slide' + L] = round(d, 3)
            last[L] = (fo[0], toe)
        py = -pb['hips'].head.y; fy = -pb['foot_ik.L'].head.y; ry = -pb['foot_ik.R'].head.y
        if not (min(fy, ry) - .02 <= py <= max(fy, ry) + .05): r['pelvis_out'] = round(py, 3)
        if len(r) > 1: rows.append(r)
    return rows
