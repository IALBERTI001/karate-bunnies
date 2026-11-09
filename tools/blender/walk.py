# Walk cycle for the bunny (Nov 8 2026, user: "lets see if using these skills we can make a simple walking animation").
# Built from the same principles as the fight moves, applied to a walk (natural-movement-rules, blender-character-rig):
#  - contact -> down -> passing -> up -> contact, one step every 12 frames at 30 fps (a cycle of 24)
#  - planted feet never slide: heel strike (toes up) -> roll onto a flat foot -> heel peels off and the foot pushes
#    off the BALL -> the foot swings through, lifting past the support ankle, and reaches heel-first for the next contact
#  - the pelvis is lowest on "down" (the weight lands on the bent front knee) and highest on "up" (the support leg pushes),
#    sways over the support foot, and dips on the free-leg side at "passing"
#  - the hips and shoulders counter-rotate; the arms swing opposite to the legs and two frames late (follow-through)
#  - the head stays level with the eyes ahead; the ears bounce on the springs
# Run: W = {'HERE': folder}; exec(open(folder + r'\walk.py').read(), W); W['walk'](F, G)
import os, math
exec(open(os.path.join(HERE, 'combo.py')).read(), globals())
CHAINS = [(('ear_a.L', 'ear_b.L'), 45, 3.5, 0, 45), (('ear_a.R', 'ear_b.R'), 45, 3.5, 0, 45),     # loose ears: dip on the down, flick on the up
          (('tie1_a', 'tie1_b'), 40, 4.5, 7, 110), (('tie2_a', 'tie2_b'), 34, 4, 7, 110)]
from mathutils import Vector, Matrix

FPS_STEP = 12            # frames per step
S = .68                  # step length (heel to heel): chibi walks need exaggeration (review: 2-3x the adult amplitudes)
X = .13                  # half track width: the feet land near the centre line, never crossing
LIFT = .16               # how high the swing foot travels at passing
TOE_UP = -15             # heel strike: toes up (degrees, + = toes down)
PUSH = 38                # toe-off: the heel is up this far when the foot leaves the floor
CYCLES = 3
END = FPS_STEP * 2 * CYCLES
HEEL = Vector((0, .08, -.12))                             # ankle -> heel, foot frame (BALL is ankle -> ball)
ONES = set(range(0, END + 1)); DRAWINGS = list(range(0, END + 1))   # a walk is smooth: every frame is a drawing

def smooth(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)

def foot(L, f, G):
    """where foot L is at frame f: ('plant', x, Y, heel_lift) or ('free', ankle_abs, Rf). Y = forward distance of the
    ankle when the foot is flat; absolute rig coordinates use y = -forward."""
    R = G['R']; BALL = G['BALL']; c0 = 0 if L == 'L' else FPS_STEP; x = X if L == 'L' else -X
    k = math.floor((f - c0) / (2 * FPS_STEP)); t = f - c0 - k * 2 * FPS_STEP     # t: frames since this foot's last contact
    Y = (c0 / FPS_STEP) * S + 2 * S * k                                            # the footprint of that contact
    if t <= 3:                                                                      # heel strike, rolling onto the flat foot
        p = TOE_UP * (1 - smooth(t / 3))
        Hd = Vector((x, -Y, 0)) + Vector((0, 0, .16)) + HEEL                          # the heel point stays put
        ankle = Hd - R(p, 0, 0) @ HEEL
        return ('free', ankle, R(p, 0, 0))
    if t <= 9: return ('plant', x, Y, 0.0)                                          # flat: carries the body
    if t <= 14: return ('plant', x, Y, PUSH * smooth((t - 9) / 5) ** 1.3)           # the heel peels off, the ball pushes
    # swing: from toe-off at this footprint to heel strike two steps ahead
    u = (t - 14) / 10.
    ballA = Vector((x, -Y - .3, .04)); ankA = ballA - R(PUSH, 0, 0) @ BALL
    Hb = Vector((x, -(Y + 2 * S), 0)) + Vector((0, 0, .16)) + HEEL
    ankB = Hb - R(TOE_UP, 0, 0) @ HEEL
    s_ = smooth(u) * .85 + u * .15                                                  # fastest through passing
    ank = ankA.lerp(ankB, s_); ank.z += LIFT * math.sin(math.pi * min(1, u * 1.15)) ** 1.2
    pitch = PUSH * (1 - smooth(u / .45)) + TOE_UP * smooth((u - .45) / .55)          # toes point down leaving, up arriving
    return ('free', ank, R(pitch, 0, 0))

def body(f):
    w = 2 * math.pi / (2 * FPS_STEP)
    pos = S * f / FPS_STEP - S / 2 + .012 * math.sin(2 * w * (f - 3))               # slight surge: slows on "down", speeds on "up"
    sink = .088 + .062 * math.cos(2 * w * (f - 3))                                   # a visible bob: deep on "down", up on "up"
    wx = .08 * math.cos(w * (f - 6))                                               # over the support foot (L at 6, R at 18)
    yaw_h = -11 * math.cos(w * f)                                                    # the front leg's hip leads
    roll_h = 5 * math.cos(w * (f - 6))                                              # the free-leg side of the pelvis dips at passing
    arm = math.cos(w * (f - 2))                                                     # arms opposite to the legs, two frames late
    return dict(pos=pos, sink=sink, wx=wx, yaw_h=yaw_h, roll_h=roll_h, arm=arm)

def pose(F, G, f):
    rig = F['rig']; pb = rig.pose.bones; R = G['R']; B = body(f)
    root = Vector((0, -B['pos'], 0))
    lean = 5 + 1.5 * math.cos(4 * math.pi * (f - 9) / (2 * FPS_STEP))               # leans in a touch more on the push
    spine = (0, -B['roll_h'] * .8, -B['yaw_h'] * .5); chest = (0, 0, -B['yaw_h'] * .8)   # shoulders counter the hips (~14 deg)
    Rc = R(lean, 0, 0) @ R(*spine) @ R(*chest)
    e = (Rc.inverted() @ R(0, 4 * math.cos(2 * math.pi * (f - 7) / (2 * FPS_STEP)), 0)).to_euler('XYZ')   # eyes ahead, a small tilt toward the support foot
    a = B['arm']; A = .42                                                          # ~35 deg swing: the forward paw reaches the belly line
    hR = (-.52, -A * a + .04, -.6 + .14 * max(0, a) - .04 * max(0, -a)); hL = (.52, A * a + .04, -.6 + .14 * max(0, -a) - .04 * max(0, a))
    P = dict(G['DEFAULT'], pos=B['pos'], sink=B['sink'], shift=(B['wx'], 0), lean=lean,
             hips=(0, B['roll_h'], B['yaw_h']), spine=spine, chest=chest, head=(math.degrees(e.x), -math.degrees(e.y), math.degrees(e.z)),
             hL=hL, hR=hR, grip=.3, shL=(1.5 * max(0, -a), 6 * -a), shR=(1.5 * max(0, a), 6 * a))
    for L in 'LR':
        fo = foot(L, f, G)
        if fo[0] == 'plant':
            _, x, Y, lift = fo
            # apply_pose lifts the heel about a point 4 cm behind the toe joint; shift the foot so the TOE JOINT stays put
            dy = (R(lift, 0, 0) @ Vector((0, -.04, .03))).y + .04
            P['f' + L] = (x, Y - B['pos'] + dy, 0, lift)
        else:
            _, ank, Rf = fo; P['f' + L] = (tuple(ank - root), Rf)
            P['pole' + L] = tuple(Vector((ank.x * 1.1, ank.y - .9, .75)) - root)        # knees point forward
    G['apply_pose'](F, P)
    return P

def walk(F, G, fx=False):
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
    """planted feet must not slide; the leg must reach every foot target"""
    rig = F['rig']; pb = rig.pose.bones; rows = []; last = {}
    for f in DRAWINGS:
        pose(F, G, f); r = {'f': f}
        for L in 'LR':
            fo = foot(L, f, G); toe = pb[f'toe.{L}'].head.copy()
            gap = (pb[f'foot_ik.{L}'].head - pb[f'shin.{L}'].tail).length
            if gap > .02: r['gap' + L] = round(gap, 3)
            if fo[0] == 'plant' and L in last and last[L][0] == 'plant':
                d = (toe.xy - last[L][1].xy).length
                if d > .01: r['slide' + L] = round(d, 3)
            last[L] = (fo[0], toe)
        if len(r) > 1: rows.append(r)
    return rows
