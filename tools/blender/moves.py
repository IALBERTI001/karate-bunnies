# Teaches the rigged bunny its moves and renders them:
#   blender -b --factory-startup -P moves.py -- <out dir> [only moves, comma separated] [res]
# Every move is 4 game frames keyed on one timeline (a marker names each move); the .blend is saved beside the renders
# so a person can open it, scrub the moves and pose the bunny by hand.
# Poses follow the painted sprites: wide bent-knee stance, fists up; strikes reach out toward the opponent (screen
# right), the body leans into punches and back from kicks, the active pose is the extreme, recovery settles low.
import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, kbpuppet, kbrig, kbmove as KM
importlib.reload(kbpuppet); importlib.reload(kbrig); importlib.reload(KM)
from mathutils import Vector, Matrix
from kbrig import rotm

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moves-out')
ONLY = set(argv[1].split(',')) if len(argv) > 1 and argv[1] else None
RES = int(argv[2]) if len(argv) > 2 else 512

# ---------- the moves ----------
# Real karate body mechanics (see the karate-body-mechanics skill), not stretchy limbs: reach comes from the stance,
# a step, the hips and shoulders turning and the trunk leaning. Arms and legs keep their length.
# The fighter stands on the line toward the opponent: model -Y is toward the opponent (screen right, yaw 90), +X is
# its left = away from the camera. Orthodox stance: left foot and left fist lead; the hips and chest turn side-on
# (hanmi) to their right, which is what shows the chest to the camera.
# Hands are offsets from the chest bone's head and feet are positions on the ground, both in body space (they turn
# with a spin, not with the hips); `root` steps the whole fighter.
GROUND = .15
# Poses below are read from side-on reference sheets of a real karate athlete (design/karate-refs, generated with
# ChatGPT on Nov 3 2026): long low stance, upright torso turned ~55 degrees toward the camera; punches keep the head
# at one height and the torso upright while the stance lengthens; kick chambers stand tall on a straight supporting
# leg; kick impacts lean the trunk back just enough to balance the leg (about 30 degrees for a head kick).
def stance(**kw):
    p = dict(root=(0, 0, 0), spin=0, pelvis=(0, 0, -.28), pelvisRot=(0, 0, -55), spine=(2, 0, 0), chest=(0, 0, -5), head=(0, 0, 10),
             footL=(.1, -.82, GROUND), footR=(-.15, .78, GROUND), footLRot=(0, 0, -5), footRRot=(0, 0, -60),
             handL=(.14, -.72, .18), handR=(-.08, -.28, .28), eyes='open', mouth='smile', ears=0, ties=0, yaw=90)
    p.update(kw); return p
FOCUS = dict(eyes='focus')
MOVES = {}
# Each pose names its support: weight=0..1 is the share on the lead (left) foot with both feet down, 'L' = standing
# on the lead leg. Kicks name the striking surface and the point on the opponent it lands on (strikeR), not where the
# ankle goes: the governor works the ankle back from the surface so the impact is centred on the target, and turns
# the foot so that surface faces the drive (ball of the foot: toes pulled back; instep: toes pointed; heel: sole out).
# Leans given here are only a starting point: the balance rule adds the lean and hip shift the body actually needs.
# Combo 1 - jab (kizami-zuki): the front foot slides in and the weight rides forward onto it; the lead hip and
# shoulder drive (hips turn further side-on), the lead fist goes straight out at chin height, rear fist guards.
MOVES['punch1'] = [stance(**FOCUS, pelvis=(0, 0, -.3), weight=.5),
                   stance(**FOCUS, root=(0, -.18, 0), footL=(.1, -1.02, GROUND), pelvis=(0, 0, -.33), pelvisRot=(0, 0, -64), chest=(0, 0, -10),
                          handL=(.12, -1.0, .24), weight=.6, ties=-6),
                   stance(**FOCUS, root=(0, -.24, 0), footL=(.1, -1.1, GROUND), pelvis=(0, 0, -.35), pelvisRot=(0, 0, -72), chest=(0, 0, -14),
                          handL=(.1, -1.6, .3), mouth='open', weight=.66, ties=-10),
                   stance(root=(0, -.08, 0), weight=.5)]
# Combo 2 - reverse punch (gyaku-zuki): the energy comes up from the rear heel: the heel turns down and the back leg
# drives, the weight moves onto the bending front knee, the hips turn from side-on to nearly square and the chest
# keeps turning after them, so the rear fist travels out along the centre line; the lead fist pulls back to the hip.
MOVES['punch2'] = [stance(**FOCUS, handR=(-.2, -.05, -.3), handL=(.12, -.78, .18), weight=.45),
                   stance(**FOCUS, root=(0, -.1, 0), pelvis=(0, 0, -.36), pelvisRot=(0, 0, -34), chest=(0, 0, 2), footL=(.1, -.94, GROUND),
                          footR=(-.15, .8, GROUND), footRRot=(0, 0, -38), drive='R', handR=(-.05, -.85, .2), handL=(.24, -.1, -.22), weight=.6, ties=-6),
                   stance(**FOCUS, root=(0, -.14, 0), pelvis=(0, 0, -.4), pelvisRot=(0, 0, -16), chest=(0, 0, 10), footL=(.1, -.98, GROUND),
                          footR=(-.15, .8, GROUND), footRRot=(0, 0, -25), drive='R', handR=(-.02, -1.65, .3), handL=(.26, .05, -.28), mouth='shout',
                          weight=.65, ties=-12),
                   stance(root=(0, -.05, 0), weight=.5)]
# Every kick is four beats (karate-body-mechanics): FOLD the leg tight into the chamber (hip and knee both bent, heel to
# the buttock), SNAP out to the target, WHIP back to the same chamber with the knee still up, then set the foot down
# in stance. The standing leg carries the weight from the fold on and turns on the BALL of its foot (heel lifted); the
# trunk drops away from the kick as far as the kick's height asks (leanMin) and the balance rule does the rest.
GUARD = dict(handL=(.14, -.55, .26), handR=(-.1, -.3, .3))
def sup(pivot, heel=0, bend=0, thrust=0):
    return dict(footL=(.06, -.62, GROUND), footLRot=(0, 0, pivot), heelL=heel, pelvis=(0, 0, -.06 - bend), weight='L', thrust=thrust)
def lean_for(z):  # how far the trunk must drop away for a kick at height z (from the reference footage)
    return -30 if z >= 2.3 else (-10 if z >= 1.4 else None)
def kick4(fold, target, surface, hips, pivot, heel, rechamber=None, re_hips=None, re_pivot=None, chest=-30, bend=0, thrust=0, step=.1,
          arms=None, fold_hips=-20, fold_pivot=30, knee='up'):
    arms = arms or GUARD
    f0 = stance(**FOCUS, **sup(fold_pivot, heel * .5, bend), pelvisRot=(0, 0, fold_hips), spine=(-2, 0, 0), chest=(0, 0, -12),
                footR=(0, 0, 1), chamberR=fold, **GUARD)
    f1 = stance(**FOCUS, **sup(pivot, heel, bend, thrust), root=(0, -step, 0), footR=target, strikeR=surface, kneeR=knee, leanMin=lean_for(target[2]),
                pelvisRot=(0, 0, hips), chest=(0, 0, chest), head=(0, 0, 12), mouth='shout', ties=-16, **arms)
    f2 = stance(**FOCUS, **sup(pivot if re_pivot is None else re_pivot, heel, bend), root=(0, -step, 0), footR=(0, 0, 1), chamberR=rechamber or fold,
                pelvisRot=(0, 0, hips if re_hips is None else re_hips), chest=(0, 0, chest * .6), head=(0, 0, 12), mouth='open', ties=-10, **GUARD)
    return [f0, f1, f2, stance(root=(0, -step * .5, 0), weight=.5)]
FRONT_FOLD = lambda up: dict(dir=(-.05, -.6 + up * .2, .8 + up * .1), fold=150, toward=(0, 0, -1), foot='flex')
SIDE_FOLD = dict(dir=(-.1, -.92, .38), fold=140, toward=(-1, .35, 0), foot='point')  # roundhouse re-chamber: knee horizontal
# Combo 3 - roundhouse to the head (mawashi-geri, rear leg): fold the knee straight up in front; the standing foot
# rises onto its ball and pivots until its heel faces the target, which turns the knee from vertical to horizontal;
# the hips turn over until the belly faces past the target, the trunk drops away ~30 deg and the instep snaps into the
# head; whip back to a horizontal chamber, turn the standing foot and hips back in, then land.
MOVES['combo_kick'] = kick4(dict(dir=(-.1, -.6, .8), fold=150, toward=(0, 0, -1), foot='point'), (-.05, -2.05, 2.45), 'instep',
                            hips=85, pivot=135, heel=25, rechamber=SIDE_FOLD, re_hips=55, re_pivot=105, chest=-45, fold_hips=10, fold_pivot=60,
                            arms=dict(handR=(-.32, .38, -.18), handL=(.1, -.42, .34)))
# Combo 4 / back - spinning back kick (ushiro-geri): turn on the lead foot, look over the shoulder and tuck the heel
# under the body with the knees together; drive the heel straight back from underneath with the hips behind it;
# re-tuck, land with the back still to the target, turn back. Frame 1 (the tuck, back view) is the one the game shows.
TUCK = dict(dir=(0, -.3, -.95), fold=140, toward=(0, 1, 0), foot='flex')
MOVES['spin_kick'] = [stance(**FOCUS, spin=110, pelvis=(0, 0, -.06), pelvisRot=(12, 0, 0), spine=(8, 0, 0), chest=(0, 0, 0), head=(0, 0, -50),
                             footL=(.0, -.25, GROUND), footLRot=(0, 0, 0), heelL=10, footR=(0, 0, 1), chamberR=TUCK, weight='L',
                             handL=(.15, -.35, .2), handR=(-.15, -.35, .2), ties=-14),
                      stance(**FOCUS, spin=180, root=(0, -.2, 0), pelvis=(0, 0, -.06), pelvisRot=(20, 0, -70), spine=(10, 0, -10), chest=(0, 0, -10),
                             head=(-6, 0, 40), footL=(.05, -.3, GROUND), heelL=15, footR=(-.05, 1.22, 1.5), strikeR='heel', kneeR='down', weight='L',
                             handL=(.2, -.35, .1), handR=(-.2, -.35, .1), mouth='shout', ties=-20),
                      stance(**FOCUS, spin=180, root=(0, -.2, 0), pelvis=(0, 0, -.06), pelvisRot=(16, 0, -70), spine=(8, 0, -10), chest=(0, 0, -10),
                             head=(-6, 0, 40), footL=(.05, -.3, GROUND), heelL=10, footR=(0, 0, 1), chamberR=TUCK, weight='L',
                             handL=(.2, -.35, .1), handR=(-.2, -.35, .1), mouth='open', ties=-12),
                      stance(root=(0, -.1, 0), weight=.5)]
# W - high front kick (jodan mae-geri, rear leg): fold the knee high to the chest with the toes pulled back; the hips
# thrust forward and the trunk drops back ~30 deg as the ball of the foot rises under the chin; whip back, land.
MOVES['high_kick'] = kick4(FRONT_FOLD(1), (-.05, -1.5, 2.8), 'ball', hips=-12, pivot=30, heel=15, chest=-6, thrust=.1)
# S - low roundhouse (gedan mawashi-geri, rear leg): sink on the bent standing leg, fold the knee up, pivot on the
# ball of the standing foot and turn the hips over as the instep and shin whip flat into the thigh; trunk upright.
MOVES['low_kick'] = kick4(dict(dir=(-.1, -.75, .6), fold=135, toward=(0, 0, -1), foot='point'), (-.05, -2.15, .8), 'instep',
                          hips=60, pivot=105, heel=20, rechamber=dict(dir=(-.15, -.97, .15), fold=130, toward=(-1, .35, 0), foot='point'),
                          re_hips=40, re_pivot=85, chest=-30, bend=.14, fold_hips=5, fold_pivot=50)
# Forward - front kick (chudan mae-geri, rear leg): fold, then the hips drive forward behind the ball of the foot at
# stomach height (toes pulled back), a short impact, whip back to the fold, land.
MOVES['front_kick'] = kick4(FRONT_FOLD(0), (-.05, -2.4, 1.65), 'ball', hips=-18, pivot=30, heel=10, chest=-8, thrust=.15, step=.18)
MOVES['idle'] = [stance(weight=.5)]
KIND = dict(punch1='punch', punch2='punch', combo_kick='roundhouse', spin_kick='spin', high_kick='front', low_kick='low', front_kick='front')

# ---------- posing, governed by the movement rules (kbmove.py) ----------
MASS = {'pelvis': .14, 'spine': .10, 'chest': .14, 'head': .24, 'tail': .01}
for _L in 'LR':
    MASS.update({f'ear_a.{_L}': .01, f'ear_b.{_L}': .01, f'upper_arm.{_L}': .025, f'forearm.{_L}': .015, f'hand.{_L}': .01,
                 f'thigh.{_L}': .07, f'shin.{_L}': .04, f'foot.{_L}': .025})
# striking surfaces, as offsets from the ankle in the foot's rest frame (toes -Y, top +Z), and how each one is aimed
SURFACE = {'ball': (0, -.42, -.17), 'heel': (0, .25, -.12), 'instep': (0, -.22, .08), 'sole': (0, -.15, -.2)}
SURF_AIM = {'ball': 'sole', 'heel': 'sole', 'instep': 'point', 'sole': 'sole'}

def upd(): bpy.context.view_layer.update()
def set_bone(rig, name, R, pos=None):
    pb = rig.pose.bones[name]; pb.matrix_basis = Matrix.Identity(4); upd()
    head = Vector(pos) if pos is not None else pb.head.copy()
    pb.matrix = Matrix.Translation(head) @ (R @ pb.bone.matrix_local.to_3x3()).to_4x4(); upd()

def set_axes(rig, name, head, Y, bend):  # bone along Y with its local Z toward `bend` (the hinge stays one plane)
    Y = Y.normalized(); Z = (bend - Y * bend.dot(Y)).normalized(); X = Y.cross(Z)
    M = Matrix((X, Y, Z)).transposed().to_4x4(); M.translation = head; rig.pose.bones[name].matrix = M; upd()

def solve_limb(rig, upper, lower, target, hint, joint_is_z):
    # Two-bone limb solved exactly, with the knee/elbow placed by rule rather than wherever an IK solver lands it.
    pu = rig.pose.bones[upper]; H = pu.head.copy(); a, b = pu.bone.length, rig.pose.bones[lower].bone.length
    j, t, n = (Vector(v) for v in KM.two_bone(tuple(H), tuple(target), a, b, tuple(hint)))
    z = n if joint_is_z else -n
    set_axes(rig, upper, H, j - H, z); set_axes(rig, lower, j, t - j, z)
    return H, j, t

def foot_frame(aim, hip, ankle):  # 'point': toes lead along the leg; 'sole': sole to the target, toes up
    d = (ankle - hip).normalized(); up = Vector((0, 0, 1))
    side = d.cross(up).normalized() if abs(d.z) < .95 else Vector((1, 0, 0))
    if aim == 'point': ax_y, ax_z = -d, side.cross(d).normalized()
    else: ax_z, ax_y = -d, (-(up - d * up.dot(d)).normalized() if abs(d.z) < .95 else Vector((0, 1, 0)))
    ax_x = ax_y.cross(ax_z).normalized(); return Matrix((ax_x, ax_y, ax_z)).transposed()

BALL = Vector((0, -.32, -.12))  # ball of the foot (the toe joint) from the ankle, foot rest frame
def foot_axes(toe_dir, top_hint):  # foot frame with its toes (-Y) along toe_dir and its top (+Z) toward top_hint
    ay = -toe_dir.normalized(); az = (top_hint - ay * top_hint.dot(ay)).normalized(); ax = ay.cross(az)
    return Matrix((ax, ay, az)).transposed()

def pose_once(rig, P, adj):
    for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    upd()
    Rs = rotm((0, 0, P['spin'])); R0 = Vector(P['root'])
    set_bone(rig, 'root', Rs, R0)
    pr = P['pelvisRot']; Rp = Rs @ rotm((adj['lean'], 0, 0)) @ rotm(pr)  # balance lean is along the strike line, whatever way the hips face
    off = Vector(P['pelvis']) + Vector((adj['shift'][0], adj['shift'][1], -adj['sink']))
    set_bone(rig, 'pelvis', Rp, R0 + Rs @ (kbrig.warp((0, 0, 1.0)) + off))
    Rsp = Rp @ rotm(P['spine']); set_bone(rig, 'spine', Rsp)
    Rc = Rsp @ rotm(P['chest']); set_bone(rig, 'chest', Rc)
    # The head stays level and the eyes stay on the opponent: it takes the body's turn (within a neck's range), not its lean.
    # Readability: the face never turns fully away from the camera outside a spin (at least one eye shows).
    turn = max(-75, min(-30, P['pelvisRot'][2] + P['spine'][2] + P['chest'][2])) + P['spin']
    Rh = rotm((0, 0, turn)) @ rotm(P['head']); set_bone(rig, 'head', Rh)
    out = dict(Rs=Rs, legs={}, strike=None)
    for s, L in ((1, 'L'), (-1, 'R')):
        Re = Rh @ rotm((-P['ears'], 0, 0)); set_bone(rig, f'ear_a.{L}', Re); set_bone(rig, f'ear_b.{L}', Re @ rotm((-P['ears'] * .6, 0, 0)))
        # arms: elbows down, back and a little out
        chest_head = rig.pose.bones['chest'].head.copy()
        hint = Rs @ Vector((s * .35, .5, 0)) + Vector((0, 0, -1))
        _, _, t = solve_limb(rig, f'upper_arm.{L}', f'forearm.{L}', chest_head + Rs @ Vector(P['hand' + L]), hint, False)
        set_bone(rig, f'hand_ik.{L}', Rc, t)
        # legs
        fb = Vector(P['foot' + L]); planted = fb.z <= GROUND + .02; goal = R0 + Rs @ fb
        fr = P['foot' + L + 'Rot']; surface = P.get('strike' + L); ch = P.get('chamber' + L)
        hip = rig.pose.bones[f'thigh.{L}'].head.copy(); a_ = rig.pose.bones[f'thigh.{L}'].bone.length; b_ = rig.pose.bones[f'shin.{L}'].bone.length
        aim = SURF_AIM[surface] if surface else (fr if isinstance(fr, str) else None)
        ankle = goal.copy(); Rch = None; heel = 0; toe = None; Rflat = None
        if ch:  # folded chamber: thigh along `dir`, shin folded back by `fold` degrees toward `toward` (heel to the buttock)
            d = (Rs @ Vector(ch['dir'])).normalized(); tw = Rs @ Vector(ch.get('toward', (0, 0, -1)))
            pp = (tw - d * tw.dot(d)).normalized(); f = math.radians(ch['fold'])
            sh = d * math.cos(f) + pp * math.sin(f); kn = hip + d * a_; ankle = kn + sh * b_; hint = kn - hip
            if ch.get('foot', 'point') == 'point': Rch = foot_axes(sh, -d)              # toes continue the shin (instep leads)
            else: Rch = foot_axes((Rs @ Vector((0, -1, 0)) - sh * (Rs @ Vector((0, -1, 0))).dot(sh)), -sh)  # toes pulled back, foot square to the shin
        elif surface:  # work the ankle back from the striking surface so the impact is centred on the target
            for _ in range(4): ankle = goal - foot_frame(aim, hip, ankle) @ Vector(SURFACE[surface])
        if planted:
            Rflat = Rs @ rotm(fr); toe = Rflat @ Vector((0, -1, 0)); hint = toe  # knee tracks the toes
            heel = P.get('heel' + L, 0)  # up on the ball of the foot: the ball stays on the floor, the heel lifts
            if heel: ankle = goal + Rflat @ BALL - (Rflat @ rotm((heel, 0, 0))) @ BALL
        elif not ch:
            k = P.get('knee' + L, 'lead')
            hint = {'lead': Rs @ Vector((0, -1, 0)) + Vector((0, 0, .7)), 'up': Vector((0, 0, 1)) + Rs @ Vector((0, -.3, 0)),
                    'down': Vector((0, 0, -1)) + Rs @ Vector((0, .3, 0))}[k]
        H, knee, t = solve_limb(rig, f'thigh.{L}', f'shin.{L}', ankle, hint, True)
        if planted: Rf = Rflat @ rotm((heel, 0, 0))
        elif Rch is not None: Rf = Rch
        else: Rf = foot_frame(aim, H, t) if aim else Rs @ rotm(fr)
        set_bone(rig, f'foot_ik.{L}', Rf, t)
        # toes: flat on the floor when standing (also on the ball), pulled back for the ball of the foot, pointed for the instep
        if planted: Rt = Rflat
        elif surface == 'ball' or (ch and ch.get('foot') == 'flex'): Rt = Rf @ rotm((-45, 0, 0))
        elif surface in ('instep',) or aim == 'point' or (ch and ch.get('foot', 'point') == 'point'): Rt = Rf @ rotm((10, 0, 0))
        else: Rt = Rf
        set_bone(rig, f'toe.{L}', Rt)
        contact = t + Rf @ BALL - (Rflat @ BALL if planted else Rf @ BALL) if planted else t
        out['legs'][L] = dict(planted=planted, hip=H, knee=knee, ankle=t, contact=contact, heel=heel, toe=toe,
                              mid=(goal + toe * (.3 if heel else .12)) if toe is not None else t)  # on the ball of the foot the support moves to the ball
        if surface:
            hit = t + Rf @ Vector(SURFACE[surface]); drive = (goal - H).normalized()
            face = Rf @ Vector({'ball': (0, 0, -1), 'heel': (0, 0, -1), 'sole': (0, 0, -1), 'instep': (0, 0, 1)}[surface])
            out['strike'] = dict(goal=goal, hit=hit, miss=(hit - goal).length, facing=math.degrees(face.angle(drive)) if surface != 'instep' else None)
    for t_ in ('tie1', 'tie2'):
        set_bone(rig, f'{t_}_a', Rh @ rotm((0, 0, P['ties']))); set_bone(rig, f'{t_}_b', Rh @ rotm((0, 0, P['ties'] * 1.6)))
    return out

def cog(rig):
    return Vector(KM.centre_of_gravity([(tuple((pb.head + pb.tail) / 2), MASS[pb.name]) for pb in rig.pose.bones if pb.name in MASS]))

# ---------- secondary motion: loose cloth and ears (natural-movement-rules) ----------
# Belt ends, headband ribbons and ear tips are not rigid. Each segment keeps a little of its posed shape (stiff), hangs
# with gravity, trails opposite to how fast its root just moved (drag) and keeps some of last frame's direction (lag,
# follow-through). Gravity is what shows a lean (the ends hang straight down while the body tilts); drag and lag show
# speed. Cloth never passes into the body: belt ends stay in front of the belly, ribbons behind the face.
SEC = {}
LOOSE = [  # (bone, parent segment or None, stiff, gravity, drag, lag, keep-out: ('front', bone) = stay in front of, ('behind', bone))
    ('tie1_a', None, 1.4, .22, 3.0, .35, ('behind', 'head')), ('tie1_b', 'tie1_a', .8, .45, 4.0, .55, ('behind', 'head')),
    ('tie2_a', None, 1.4, .3, 2.6, .35, ('behind', 'head')), ('tie2_b', 'tie2_a', .8, .55, 3.6, .55, ('behind', 'head')),
    ('beltend_a.L', None, .35, 1.0, 1.3, .3, ('front', 'pelvis')), ('beltend_b.L', 'beltend_a.L', .2, 1.0, 1.8, .5, ('front', 'pelvis')),
    ('beltend_a.R', None, .35, 1.0, 1.3, .3, ('front', 'pelvis')), ('beltend_b.R', 'beltend_a.R', .2, 1.0, 1.8, .5, ('front', 'pelvis')),
    ('ear_b.L', None, 3.0, .15, .7, .2, None), ('ear_b.R', None, 3.0, .15, .7, .2, None)]

def aim_bone(rig, name, d):
    pb = rig.pose.bones[name]; cur = (pb.tail - pb.head).normalized(); q = cur.rotation_difference(d.normalized())
    head = pb.head.copy(); pb.matrix = Matrix.Translation(head) @ (q.to_matrix() @ pb.matrix.to_3x3()).to_4x4(); upd()

def secondary(rig, reset=False):
    if reset: SEC.clear()
    PB = rig.pose.bones; down = Vector((0, 0, -1)); prev_pts = SEC.get('pts', {}); prev_dir = SEC.get('dirs', {})
    pts = {n: PB[n].head.copy() for n, *_ in LOOSE}; dirs = {}
    for n, par, stiff, grav, drag, lag, keep in LOOSE:
        v = pts[n] - prev_pts.get(n, pts[n])
        cur = (PB[n].tail - PB[n].head).normalized()
        d = cur * stiff + down * grav - v * drag + prev_dir.get(n, cur) * lag
        if keep:
            fwd = PB[keep[1]].matrix.to_3x3() @ Vector((0, 0, 1))  # the bone's local Z is the body's forward (align_roll -Y)
            fwd.normalize(); c = d.normalized().dot(fwd)
            if keep[0] == 'front' and c < .05: d = d + fwd * (.05 - c) * d.length
            if keep[0] == 'behind' and c > -.1: d = d - fwd * (c + .1) * d.length
        aim_bone(rig, n, d); dirs[n] = (PB[n].tail - PB[n].head).normalized()
    SEC['pts'] = pts; SEC['dirs'] = dirs

GOV = {}  # fid -> measured frame, for the move checks and the report
def apply_pose(rig, P, fid=''):
    P = dict(P); w = P.get('weight', .5); single = isinstance(w, str)
    if single and not isinstance(P['foot' + w + 'Rot'], str):  # rule 4: the standing foot pivots with the hips
        fx, fy, fz = P['foot' + w + 'Rot']; hy = P['pelvisRot'][2]
        P['foot' + w + 'Rot'] = (fx, fy, min(max(fz, hy - KM.HIP_FOOT_MAX), hy + KM.HIP_FOOT_MAX))
    adj = dict(lean=0.0, shift=Vector((0, 0)), sink=0.0); share = KM.KNEE_SUPPORT if single else KM.KNEE_SOFT
    forced = False
    for it in range(48):
        o = pose_once(rig, P, adj); legs = o['legs']; Rs = o['Rs']
        legl = rig.pose.bones['thigh.L'].bone.length + rig.pose.bones['shin.L'].bone.length
        need = max([KM.sink_needed(tuple(g['hip']), tuple(g['ankle']), legl, KM.KNEE_DRIVE if P.get('drive') == L else share)
                    for L, g in legs.items() if g['planted']] or [0])
        c = cog(rig)
        S = legs[w]['mid'] if single else legs['R']['mid'].lerp(legs['L']['mid'], w)
        e = Vector((c.x - S.x, c.y - S.y, 0)); eb = Rs.inverted() @ e; tol = KM.COM_TOL_SINGLE if single else KM.COM_TOL_DOUBLE
        if need < .004 and e.length <= tol * .8 and (not single or it >= 3): break
        adj['sink'] += need
        if single:  # weight transfer: the hips travel over the standing foot (a thrust drives them past it); then the
                    # trunk leans away from the reaching limb until the centre of gravity is over the foot
            pel = rig.pose.bones['pelvis'].head; ep = Rs.inverted() @ Vector((pel.x - S.x, pel.y - S.y, 0)) + Vector((0, P.get('thrust', 0), 0))
            adj['shift'] -= Vector((eb.x, eb.y if forced else ep.y)) * .8  # along the line: hips over the foot (or balance, if the lean is set by the kick)
            if it >= 3:  # the hips arrive first; then the lean (damped so it settles instead of swinging)
                base = P['pelvisRot'][0]; want = base + adj['lean'] + eb.y * 30
                new = min(max(want, KM.LEAN_RANGE[0]), KM.LEAN_RANGE[1])
                if P.get('leanMin') is not None: new = min(new, P['leanMin'])  # karate: the trunk drops away as far as the kick's height asks
                forced = abs(new - want) > 1e-6; adj['lean'] = new - base
        else:       # on two legs the hips travel (weight transfer) and the trunk stays upright
            adj['shift'] -= Vector((eb.x, eb.y)) * .8
    secondary(rig, reset=P.get('_first', False))
    # measure the result against the rules
    legs = o['legs']; rep = dict(com_err=e.length, com_tol=tol, ground=GROUND, single=single, legs={})
    for L, g in legs.items():
        bend = KM.knee_bend_deg(tuple(g['hip']), tuple(g['knee']), tuple(g['ankle']))
        kt = 0
        if g['toe'] is not None:
            line = (g['ankle'] - g['hip']).normalized(); kd = (g['knee'] - g['hip']); kd = kd - line * kd.dot(line)
            tz = g['toe'] - line * g['toe'].dot(line); kt = math.degrees(kd.angle(tz)) if kd.length > 1e-4 and tz.length > 1e-4 else 0
        rep['legs'][L] = dict(planted=g['planted'], ankle=tuple(g['contact']), bend=bend, knee_toe=kt, drive=P.get('drive') == L)
    if single and not isinstance(P['foot' + w + 'Rot'], str): rep['hip_foot'] = P['pelvisRot'][2] - P['foot' + w + 'Rot'][2]
    bad = KM.check_frame(rep)
    st = o['strike']
    if st:
        if st['miss'] > .04: bad.append(f"kick lands {st['miss']:.2f} short of the target")
        if st['facing'] is not None and st['facing'] > 25: bad.append(f"striking surface turned {st['facing']:.0f} deg off the drive")
    W = rotm((0, 0, P['yaw']))
    xz = lambda v: [round((W @ v).x, 3), round((W @ v).z, 3)]
    lifted = [v for v in rep['legs'].values() if not v['planted']]
    GOV[fid] = dict(hip_yaw=P['pelvisRot'][2], chest_yaw=P['spine'][2] + P['chest'][2], weight=1.0 if single else w,
                    kick_bend=lifted[0]['bend'] if lifted else 0, heel=legs['L']['heel'], strike_z=(st['goal'].z if st else None),
                    support_yaw=(P['footLRot'][2] if not isinstance(P['footLRot'], str) else 0), lean=P['pelvisRot'][0] + adj['lean'])
    print('KB-GOV', json.dumps(dict(id=fid, com=xz(c), sup=xz(S), lean=round(P['pelvisRot'][0] + adj['lean'], 1), sink=round(adj['sink'], 3),
          shift=[round(adj['shift'][0], 3), round(adj['shift'][1], 3)], iters=it + 1,
          knees={L: round(v['bend']) for L, v in rep['legs'].items()},
          target=xz(st['goal']) if st else None, hit=xz(st['hit']) if st else None, miss=round(st['miss'], 3) if st else None,
          facing=round(st['facing']) if st and st['facing'] is not None else None, bad=bad)), flush=True)
    return P

def key_frame(rig, f, P):
    for pb in rig.pose.bones:
        pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f); pb.keyframe_insert('scale', frame=f)
    rig.rotation_euler = (0, 0, math.radians(P['yaw'])); rig.keyframe_insert('rotation_euler', frame=f)
    for key, objs in kbrig.EXPRESSIONS.items():
        on = key in ('eyes_' + P['eyes'], 'mouth_' + P['mouth'])
        for o in objs: o.hide_render = not on; o.keyframe_insert('hide_render', frame=f)

def constant_keys(ids):
    for idb in ids:
        ad = idb.animation_data
        if not ad or not ad.action: continue
        for fc in getattr(ad.action, 'fcurves', []) or []:
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
        for layer in getattr(ad.action, 'layers', []) or []:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# ---------- painterly finish: anisotropic Kuwahara over the colour pass (alpha kept) ----------
def kuwahara(scene, size=4):
    try:
        tree = bpy.data.node_groups.new('Paint', 'CompositorNodeTree'); scene.compositing_node_group = tree
        tree.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = tree.nodes.new('CompositorNodeRLayers'); kw = tree.nodes.new('CompositorNodeKuwahara'); out = tree.nodes.new('NodeGroupOutput')
        sa = tree.nodes.new('CompositorNodeSetAlpha')
        for name, val in (('Size', size), ('Uniformity', 4), ('Sharpness', .6), ('Eccentricity', 1.2)):
            if name in kw.inputs: kw.inputs[name].default_value = val
        if 'Type' in kw.inputs:
            try: kw.inputs['Type'].default_value = 'Anisotropic'
            except Exception: pass
        elif hasattr(kw, 'variation'): kw.variation = 'ANISOTROPIC'
        tree.links.new(rl.outputs['Image'], kw.inputs['Image']); tree.links.new(kw.outputs['Image'], sa.inputs['Image'])
        tree.links.new(rl.outputs['Alpha'], sa.inputs['Alpha']); tree.links.new(sa.outputs['Image'], out.inputs[0])
        print('KB-KUWAHARA on', flush=True); return tree
    except Exception as e:
        print('KB-KUWAHARA off:', e, flush=True); return None

# ---------- build, key, render ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene, root_empty, decals = kbpuppet.setup_scene(RES, 8.0, (0, 2.7), 2.0 * RES / 512)
bpy.data.objects.remove(root_empty)
rig = kbrig.build_armature(scene); parts = kbrig.build_body(rig, decals)
for _pb in rig.pose.bones:  # limbs are solved by the movement rules (moves.py solve_limb), so the IK solver stays off
    for _c in _pb.constraints:
        if _c.type == 'IK': _c.mute = True
names = [n for n in MOVES if not ONLY or n in ONLY]
frames = []
for k, name in enumerate(names):
    m = scene.timeline_markers.new(name, frame=k * 10 + 1)
    for i, P in enumerate(MOVES[name]):
        P = dict(P, _first=(i == 0 and k == 0))
        f = k * 10 + 1 + i; apply_pose(rig, P, f'{name}-{i}'); key_frame(rig, f, P); frames.append((f, f'{name}-{i}'))
    if name in KIND:
        print('KB-MOVE', json.dumps(dict(id=name, bad=KM.check_move(KIND[name], [GOV[f'{name}-{i}'] for i in range(len(MOVES[name]))]))), flush=True)
constant_keys([rig] + [o for objs in kbrig.EXPRESSIONS.values() for o in objs])
scene.frame_start, scene.frame_end = 1, frames[-1][0]
os.makedirs(os.path.join(OUT, 'color'), exist_ok=True); os.makedirs(os.path.join(OUT, 'mask'), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'bunny-rig.blend'))
paint = kuwahara(scene)
for f, fid in frames:
    scene.frame_set(f); scene.render.filepath = os.path.join(OUT, 'color', fid + '.png'); bpy.ops.render.render(write_still=True)
    print('KB-FRAME', fid, flush=True)
if paint is not None: scene.compositing_node_group = None
scene.render.use_freestyle = False; kbpuppet.to_mask(parts.objs)
for f, fid in frames:
    scene.frame_set(f); scene.render.filepath = os.path.join(OUT, 'mask', fid + '.png'); bpy.ops.render.render(write_still=True)
print('KB-DONE', len(frames), flush=True)
