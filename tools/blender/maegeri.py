# Mae geri (front kick) driven by momentum, on the v3 long-legged bunny (kbbody LEG .52).
# Every frame is SOLVED, not blended by Blender: the timeline below gives the body's state (weight, sink, lean, thigh
# angle, knee fold, arms) at a few beats with an easing per segment, and each frame rebuilds the pose from it, so the
# foot travels on the leg's own arc (thigh swings from the hip, shin from the knee) and nothing cuts through the body.
# Momentum rules (user, Nov 8 2026: "MOVEMENT is done with momentum"; reference: a 2D karate fighter clip):
#   anticipation: the weight goes onto the standing leg and the body sinks before the knee leaves;
#   the knee drives up accelerating, the shin hangs like a pendulum; the snap is the fastest part (2 frames);
#   the hips thrust into the kick and the trunk counter-leans; the arms counter-swing; the extension overshoots and
#   settles; the shin whips back; the leg lands FORWARD (the body follows the kick) and the landing is absorbed.
# Run in Blender after kumite2 build():  exec(open(r'...\maegeri.py').read()); kick(G['FIGHTERS']['AKA'], G)
import bpy, math
from mathutils import Vector

def ease(kind, t):
    t = max(0.0, min(1.0, t))
    if kind == 'in': return t * t * t                  # accelerating (leaving a pose with force)
    if kind == 'out': return 1 - (1 - t) ** 3          # decelerating (arriving and stopping)
    if kind == 'io': return t * t * (3 - 2 * t)
    if kind == 'snap': return 1 - (1 - t) ** 4         # the strike: all speed, stops dead
    return t

# beats: frame, easing INTO this beat, body state
# th = thigh angle from straight down (+ = forward), fold = knee flex (0 straight), pos = travel toward the target,
# wx = weight shift over the standing (left) foot, away = trunk counter-lean back, hipf = hip thrust forward,
# hR/hL = fists from the chest, fR_y = where the kicking foot is planted when on the floor
GUARD = dict(pos=0, sink=.06, wx=0, away=0, lean=4, hipf=0, th=-14, fold=8, foot=0, planted=1, fy=-.3,
             hL=(.13, -.46, .1), hR=(-.1, -.3, -.04), turn=-12)
BEATS = [
    (0, 'lin', dict(GUARD)),
    (6, 'io', dict(GUARD)),
    (10, 'io', dict(GUARD, sink=.12, wx=.12, lean=8, foot=30)),                              # load: sink, weight onto the left foot
    (13, 'io', dict(GUARD, sink=.07, wx=.15, lean=2, th=48, fold=100, foot=10, planted=0, turn=-4)),  # knee drives up (accelerating)
    (16, 'out', dict(GUARD, sink=.05, wx=.15, away=4, th=108, fold=104, foot=0, planted=0, turn=0,  # chamber: knee above the belt, shin hangs (the pendulum)
                     hR=(-.12, -.22, .04))),
    (18, 'snap', dict(GUARD, pos=.06, sink=.04, wx=.14, away=16, hipf=.1, th=84, fold=-4, foot=0, planted=0, turn=0,  # SNAP (2 frames), overshoots
                      hL=(.1, -.4, .16), hR=(-.2, .12, -.22))),
    (20, 'out', dict(GUARD, pos=.07, sink=.04, wx=.14, away=14, hipf=.09, th=82, fold=3, foot=0, planted=0, turn=0,
                     hL=(.1, -.4, .16), hR=(-.2, .12, -.22))),                                 # held: settles back from the overshoot
    (23, 'out', dict(GUARD, pos=.1, sink=.05, wx=.15, away=5, th=104, fold=104, foot=0, planted=0, turn=0, hR=(-.12, -.22, .04))),  # whip back
    (27, 'io', dict(GUARD, pos=.22, sink=.08, wx=.06, away=0, lean=6, th=26, fold=20, foot=0, planted=0, fy=.36)),  # falls forward onto it
    (29, 'out', dict(GUARD, pos=.26, sink=.17, wx=0, lean=10, th=0, fold=0, foot=0, planted=1, fy=.36)),          # lands: absorbs
    (34, 'io', dict(GUARD, pos=.27, sink=.08, lean=5, planted=1, fy=.36, turn=-6)),                              # settles in the new stance
    (42, 'io', dict(GUARD, pos=.27, sink=.08, lean=5, planted=1, fy=.36, turn=-6)),
]
NUM = ('pos', 'sink', 'wx', 'away', 'lean', 'hipf', 'th', 'fold', 'foot', 'planted', 'fy', 'turn')

def state(f):
    for (f0, _, a), (f1, kind, b) in zip(BEATS, BEATS[1:]):
        if f0 <= f <= f1:
            u = ease(kind, (f - f0) / (f1 - f0)); S = {k: a[k] + (b[k] - a[k]) * u for k in NUM}
            for h in ('hL', 'hR'): S[h] = tuple(x + (y - x) * u for x, y in zip(a[h], b[h]))
            return S
    return dict(BEATS[-1][2])

def kick(F, G, out_frames=None):
    rig = F['rig']; pb = rig.pose.bones; R = G['R']; L = pb['thigh.R'].bone.length; Ls = pb['shin.R'].bone.length
    rig.animation_data_clear(); sc = bpy.context.scene; sc.frame_start, sc.frame_end = 0, BEATS[-1][0]
    for f in range(0, BEATS[-1][0] + 1):
        S = state(f)
        P = dict(G['DEFAULT'], pos=S['pos'], sink=S['sink'], shift=(S['wx'], S['hipf']), away=S['away'], lean=S['lean'], turn=S['turn'],
                 head=(-S['lean'] * .5 + S['away'] * .3, 0, -S['turn'] * .6), hL=S['hL'], hR=S['hR'],
                 fL=(.2, .08 - S['pos'], 6, 0))                                  # standing foot stays put on the floor
        G['apply_pose'](F, dict(P, fR=(-.2, S['fy'] - S['pos'], 6, 0)))
        hip = pb['thigh.R'].head.copy()
        if S['planted'] > .999:
            P['fR'] = (-.2, S['fy'] - S['pos'], 6, 0)
        else:                                                                     # the leg's own arc: thigh from the hip, shin from the knee
            a = math.radians(S['th']); b = math.radians(S['th'] - S['fold'])
            knee = hip + Vector((0, -math.sin(a), -math.cos(a))) * L
            ankle = knee + Vector((0, -math.sin(b), -math.cos(b))) * Ls * .995
            floor = Vector((-.2, -S['fy'] + .3, .12))                            # the planted ankle (ball on the floor), for toe-off / touchdown
            w = S['planted']; ankle = ankle.lerp(floor, w) if w > 0 else ankle
            ankle.z = max(ankle.z, .12)                                         # never through the floor
            pitch = -math.degrees(b) + S['foot']                                 # toes pulled back square to the shin: the ball of the foot leads
            P['fR'] = (tuple(ankle - Vector((0, -P['pos'], 0))), (pitch, 0, 0))
            P['poleR'] = tuple(knee - Vector((0, -P['pos'], 0)) + Vector((0, -.9, .5)))
        G['key'](F, f, P)
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'          # every frame is its own solved pose
