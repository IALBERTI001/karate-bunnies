# Kumite exchange v2: two Karate Bunnies built with kbbody (continuous body, IK rig with knee/elbow poles) and animated
# the professional way: key poses on the rig's CONTROLS, Bezier in-betweens done by Blender, the poses checked from four
# angles. Choreography from the WKF Cairo 2024 -84 kg final: Ao (blue) presses in with reverse punches, Aka (red) slides
# back, then counters with a rear-leg roundhouse to the head as Ao comes in; the knee whips back like a slingshot; both
# reset and bow. Measured beats: karate-body-mechanics skill.
#   In Blender: exec(open(r'...\kumite2.py').read()); build(); animate()        Headless: blender -b -P kumite2.py -- out res
import bpy, sys, os, math
from mathutils import Vector, Matrix, Euler, Quaternion
D = r'C:\Users\Ultim\Downloads\KarateBunnies3D'
if D not in sys.path: sys.path.insert(0, D)
import importlib, kbpuppet, kbrig, kbbody
FPS = 24

def R(p=0, r=0, y=0):  # character frame: pitch (+ = lean forward), roll (+ = top toward its left), yaw (+ = turn to its left)
    return (Matrix.Rotation(math.radians(y), 3, 'Z') @ Matrix.Rotation(math.radians(-r), 3, 'Y') @ Matrix.Rotation(math.radians(p), 3, 'X'))

# ---------------- scene ----------------
def scene_setup(res=960):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try: sc.render.engine = eng; break
        except TypeError: pass
    sc.view_settings.view_transform = 'Standard'; sc.render.use_freestyle = False; sc.render.film_transparent = False
    sc.render.resolution_x, sc.render.resolution_y = res, res * 9 // 16; sc.render.fps = FPS
    w = sc.world or bpy.data.worlds.new('w'); sc.world = w
    bg = w.node_tree.nodes.get('Background')
    if bg: bg.inputs[0].default_value = kbpuppet.hexc('#1b2130'); bg.inputs[1].default_value = .6
    env = bpy.data.collections.new('Arena'); sc.collection.children.link(env)
    def slab(name, x0, y0, x1, y1, z, mat):
        me = bpy.data.meshes.new(name); me.from_pydata([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [], [(0, 1, 2, 3)])
        o = bpy.data.objects.new(name, me); env.objects.link(o); me.materials.append(mat); return o
    T = kbpuppet._toon
    slab('floor', -40, -40, 40, 40, -.004, T('floor', '#3a4150', '#272c37')); slab('border', -8, -8, 8, 8, -.002, T('mat_red', '#c9343c', '#93222a'))
    slab('area', -6.4, -6.4, 6.4, 6.4, 0, T('mat_blue', '#2f6fc2', '#22508f'))
    def wall(name, z0, z1, mat, y):
        me = bpy.data.meshes.new(name); me.from_pydata([(-30, y, z0), (30, y, z0), (30, y, z1), (-30, y, z1)], [], [(0, 1, 2, 3)])
        o = bpy.data.objects.new(name, me); env.objects.link(o); me.materials.append(mat)
    wall('wall', -1, 20, kbpuppet._flat('wall', '#20283a'), 9.0); wall('band_r', 1.1, 1.6, kbpuppet._flat('band_r', '#b7202f'), 8.98)
    wall('band_b', 1.6, 2.0, kbpuppet._flat('band_b', '#1f4fa0'), 8.98)
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5; so = bpy.data.objects.new('sun', sun); env.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-35))
    cam = bpy.data.cameras.new('cam'); cam.lens = 40; co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
    co.location = (-1.0, -11.5, 2.6); co.rotation_euler = (Vector((0.1, 0, 1.25)) - co.location).to_track_quat('-Z', 'Y').to_euler()
    return sc

# ---------------- fighters ----------------
FIGHTERS = {}
def build():
    sc = scene_setup()
    for name, belt, x, yaw in (('AKA', ('#d02f37', '#9b1f27'), -1.45, 90), ('AO', ('#2d63c8', '#204a96'), 1.45, -90)):
        rig, coll = kbbody.build_bunny(name, belt, belt)
        rig.location = (x, 0, 0); rig.rotation_euler = (0, 0, math.radians(yaw))
        rest = {pb.name: pb.bone.matrix_local.copy() for pb in rig.pose.bones}
        FIGHTERS[name] = dict(rig=rig, rest=rest)
    bpy.context.view_layer.update()
    return sc

# ---------------- pose: body description -> control transforms ----------------
BALL = Vector((0, -.3, -.12))  # ball of the foot from the ankle, foot frame
GUARD_L, GUARD_R = (.1, -.62, .12), (-.06, -.42, -.08)  # fists from the chest head, in the OPPONENT's direction (not the turned chest): lead forward at chin height, rear closer and lower
DEFAULT = dict(pos=0.0, sink=0.0, shift=(0, 0), turn=0.0, lean=0.0, tilt=0.0, away=0.0, hips=(0, 0, 0), spine=(0, 0, 0), chest=(0, 0, 0), head=(0, 0, 0),
               fL=None, fR=None, hL=GUARD_L, hR=GUARD_R, poleR=None, poleL=None)

def stance(lead='L', width=.34, length=.8, side=35, sink=.0, **kw):
    """Kumite kamae: feet on the line toward the opponent, front foot pointing at him, rear foot turned out, knees bent,
    hips and shoulders side-on. Orthodox = left foot leads. Feet: (x, y, yaw, heel lift)."""
    s = 1 if lead == 'L' else -1
    P = dict(DEFAULT); P.update(sink=sink, turn=-s * side)  # side-on; a 'turn' in kw is an absolute yaw (+ = turn to its left)
    front = (s * width / 2, length / 2, -s * 5, 8); back = (-s * width / 2, -length / 2, -s * 55, 18)  # y: + = toward the opponent
    P['f' + lead] = front; P['f' + ('R' if lead == 'L' else 'L')] = back
    if lead == 'R': P['hR'], P['hL'] = (-GUARD_L[0],) + GUARD_L[1:], (-GUARD_R[0],) + GUARD_R[1:]
    P.update(kw); return P

HEAD_PAD = .15   # glove radius + a little air: a fist never sinks into the big head
def _head_check(pb, pt):
    """where a pose-space point sits against the padded head ellipsoid: (k < 1 inside, rest->pose matrix, rest point, centre, radii, unit offset)"""
    hb = pb['head']; Rm = hb.bone.matrix_local @ hb.matrix.inverted(); x = Rm @ pt
    c = kbbody.HEAD_C; r = kbbody.HEAD_R + Vector((HEAD_PAD, HEAD_PAD, HEAD_PAD))
    d = Vector(((x.x - c.x) / r.x, (x.y - c.y) / r.y, (x.z - c.z) / r.z))
    return d.length, Rm, x, c, r, d

def clear_head(F):
    """Collision rule (user, Nov 9: "arms go through the head"): after every pose, any paw that would enter the head is
    pushed out to the head's surface along the line from the head centre, and the arm re-solves to reach it."""
    rig = F['rig']; pb = rig.pose.bones; vl = bpy.context.view_layer
    for _ in range(3):
        moved = False
        for L in 'LR':
            for pt in (pb[f'hand.{L}'].tail.copy(), pb[f'hand.{L}'].head.copy(), (pb[f'forearm.{L}'].head + pb[f'forearm.{L}'].tail) / 2):
                k, Rm, x, c, r, d = _head_check(pb, pt)
                if k >= 1 or k < 1e-6: continue
                surf = Vector((c.x + d.x / k * r.x, c.y + d.y / k * r.y, c.z + d.z / k * r.z))
                delta = (Rm.inverted() @ surf) - pt
                m = pb[f'hand_ik.{L}'].matrix.copy(); m.translation += delta * 1.05; pb[f'hand_ik.{L}'].matrix = m
                vl.update(); moved = True; break
        if not moved: break

def apply_pose(F, P):
    rig, rest = F['rig'], F['rest']; pb = rig.pose.bones; vl = bpy.context.view_layer
    def put(name, M3, loc):
        pb[name].matrix = Matrix.Translation(loc) @ (M3 @ rest[name].to_3x3()).to_4x4(); vl.update()
    def reset(name):
        pb[name].location = (0, 0, 0); pb[name].rotation_quaternion = (1, 0, 0, 0); pb[name].scale = (1, 1, 1)
    for p in pb: reset(p.name)
    vl.update()
    root = Vector((0, -P['pos'], 0)); put('root', Matrix.Identity(3), root)
    # away: the trunk drops back from the opponent (world frame), e.g. the kick's seesaw
    Rt = R(-P['away'], 0, 0) @ R(P['lean'], P['tilt'], P['turn']); tor = root + Vector((P['shift'][0], -P['shift'][1], kbbody.HIP_Z + .04 - P['sink']))  # v3 long legs: the pelvis pivot comes from the body
    put('torso', Rt, tor)
    Rh = Rt @ R(*P['hips']); put('hips', Rh, pb['hips'].head.copy())
    Rs = Rt @ R(*P['spine']); put('spine', Rs, pb['spine'].head.copy())
    Rc = Rs @ R(*P['chest']); put('chest', Rc, pb['chest'].head.copy())
    put('neck', Rc, pb['neck'].head.copy())
    put('head', Rc @ R(*P['head']), pb['head'].head.copy())
    for L in 'LR':
        f = P['f' + L]
        if f is None: continue
        if len(f) == 4:  # planted: (x, y, yaw, heel lift) - the ball stays on the floor
            x, y, yaw, heel = f; Rf = R(heel, 0, yaw)  # + pitch tips the toes down: the heel rises, the ankle lifts (was inverted: ankles below the floor, legs locked straight)
            ball = root + Vector((x, -y, 0)) + R(0, 0, yaw) @ Vector((0, -.3, .04))
            ankle = ball - Rf @ BALL
        else:  # free foot: (ankle xyz in rig space, (pitch, roll, yaw))
            ankle, Rf = root + Vector(f[0]), (f[1] if isinstance(f[1], Matrix) else R(*f[1]))
        put(f'foot_ik.{L}', Rf, ankle)
        pole = P.get('pole' + L)
        if pole is not None: put(f'knee_pole.{L}', Matrix.Identity(3), root + Vector(pole))
    ch = pb['chest'].head.copy()
    for L in 'LR':
        h = P['h' + L]; put(f'hand_ik.{L}', Rc, ch + Vector(h))  # fists aim at the opponent whichever way the chest is turned
    # v4 rig: paws grip (1 fist, 0 open), shoulders shrug/roll (shL/shR = (raise, roll) deg), toes stay flat while the heel lifts
    grip = P.get('grip', 1.0)
    for L in 'LR':
        for b, k in ((f'fingers_a.{L}', .95), (f'fingers_b.{L}', .95), (f'thumb_a.{L}', .55), (f'thumb_b.{L}', .7)):
            if b not in pb: continue
            bone = pb[b].bone; ax = [0, 0, 0]; ax[bone['curl_axis']] = 1
            pb[b].rotation_quaternion = Quaternion(Vector(ax), math.radians(bone['curl_sign'] * k * 100 * P.get('grip' + L, grip)))
        sh = P.get('sh' + L)
        if sh and f'shoulder.{L}' in pb:
            pb[f'shoulder.{L}'].rotation_quaternion = Quaternion((1, 0, 0), math.radians(sh[0])) @ Quaternion((0, 0, 1), math.radians(sh[1]))
        f = P['f' + L]
        if f is not None and len(f) == 4 and f[3] and f'toe.{L}' in pb:
            pb[f'toe.{L}'].rotation_quaternion = Quaternion((1, 0, 0), math.radians(f[3]))   # +X lifts the toes: they stay on the floor
    vl.update()
    clear_head(F)

KEYED = ('root', 'torso', 'hips', 'spine', 'chest', 'neck', 'head', 'foot_ik.L', 'foot_ik.R', 'knee_pole.L', 'knee_pole.R', 'hand_ik.L', 'hand_ik.R',
         'shoulder.L', 'shoulder.R', 'toe.L', 'toe.R', 'fingers_a.L', 'fingers_b.L', 'thumb_a.L', 'thumb_b.L', 'fingers_a.R', 'fingers_b.R', 'thumb_a.R', 'thumb_b.R')
def key(F, f, P, interp=None):
    apply_pose(F, P); pb = F['rig'].pose.bones
    for n in KEYED:
        pb[n].keyframe_insert('location', frame=f); pb[n].keyframe_insert('rotation_quaternion', frame=f)

def set_interp(rig, frames, mode):  # e.g. 'LINEAR' into a strike, 'CONSTANT' for holds
    act = rig.animation_data.action
    for lay in act.layers:
        for st in lay.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points:
                        if int(round(kp.co.x)) in frames: kp.interpolation = mode

# ---------------- quick four-angle preview ----------------
def preview(path, frame=None, res=360, views=('game', 'front', 'side', 'three'), target=None):
    sc = bpy.context.scene
    if frame is not None: sc.frame_set(frame)
    old = sc.camera; cam = bpy.data.objects.get('prevcam')
    if not cam:
        cam = bpy.data.objects.new('prevcam', bpy.data.cameras.new('prevcam')); sc.collection.objects.link(cam)
    t = Vector(target or (0, 0, 1.3)); outs = []
    sc.render.resolution_x = sc.render.resolution_y = res
    for v in views:
        if v == 'game': cam.matrix_world = old.matrix_world; cam.data.lens = old.data.lens; sc.render.resolution_y = res * 9 // 16
        else:
            d = {'front': Vector((0, -1, 0)), 'side': Vector((1, 0, 0)), 'three': Vector((.7, -.7, .25))}[v] if isinstance(v, str) else Vector(v)
            cam.data.type = 'ORTHO'; cam.data.ortho_scale = 4.2
            cam.location = t + d.normalized() * 9; cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
            sc.render.resolution_y = res
        sc.camera = cam; p = f'{path}_{v}.png'; sc.render.filepath = p; bpy.ops.render.render(write_still=True); outs.append(p)
        cam.data.type = 'PERSP'
    sc.camera = old; return outs


# ---------------- choreography ----------------
INSTEP = Vector((0, -.15, .05))  # top of the foot from the ankle, foot frame
def kick_foot(target, sweep, hip):
    """Free kicking foot whose instep lands on `target` (rig space): the foot continues the line hip -> target and its
    top (instep) faces the direction the kick sweeps. Returns (ankle, delta rotation)."""
    d = (Vector(target) - Vector(hip)).normalized(); sw = Vector(sweep)
    z = (sw - d * sw.dot(d)).normalized(); y = -d; x = y.cross(z)
    Rf = Matrix((x, y, z)).transposed()
    return Vector(target) - Rf @ INSTEP, Rf

def bounce_keys(F, lead, frames, pos=0.0, phase=0, **kw):
    for i, f in enumerate(frames):  # on the balls of the feet: heels and hips rise and fall
        up = (i + phase) % 2 == 0
        P = stance(lead, sink=-.02 if up else .05, pos=pos, **kw)
        for L in 'LR':
            x, y, yaw, heel = P['f' + L]; P['f' + L] = (x, y, yaw, heel + (14 if up else 0))
        key(F, f, P)

def animate(interp='CONSTANT'):
    sc = bpy.context.scene; A, B = FIGHTERS['AKA'], FIGHTERS['AO']
    for F in (A, B):  # live rigs built before the Nov 7 knee fix
        for L in 'LR':
            p = F['rig'].pose.bones[f'shin.{L}']; p.ik_min_x, p.ik_max_x = math.radians(-150), 0
            for c in p.constraints:
                if c.type == 'IK': c.pole_angle = math.radians(90)
    for F in (A, B):
        F['rig'].animation_data_clear(); F['rig'].location.y = 0
    A['rig'].location.x, B['rig'].location.x = -1.45, 1.45
    A['rig'].rotation_euler = (0, 0, math.radians(90)); B['rig'].rotation_euler = (0, 0, math.radians(-90))
    for c in ('AKA', 'AO'): bpy.data.collections[c].hide_render = False
    cam = sc.camera; cam.location = (-0.7, -9.4, 2.25); cam.data.lens = 38
    cam.rotation_euler = (Vector((-0.1, 0, 1.3)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    # ---- AO (southpaw, blue): bounce, lunge reverse punch, press in low, gets hit, recoils ----
    bounce_keys(B, 'R', [1, 6, 11, 16], phase=1)
    key(B, 21, stance('R', sink=.14, pos=-.05, lean=4))                                       # anticipation: sink and draw back
    lunge = stance('R', sink=.27, pos=.75, turn=-12, lean=22, length=1.1, hL=(.03, -.95, .38), hR=(-.04, -.4, .02), head=(-12, 0, 0))
    lunge['fL'] = (.17, -.75 + .2, -40, 30)                                                     # rear foot drags, heel up, leg straight
    key(B, 26, lunge); key(B, 29, lunge)                                                        # reverse punch lands at head height, held
    press = stance('R', sink=.34, pos=1.3, turn=20, lean=44, length=.8, head=(-28, 0, 0), hR=(-.1, -.55, .3), hL=(.08, -.35, .1))
    key(B, 34, dict(press, pos=.85, lean=18, sink=.18, head=(-10, 0, 0))); key(B, 40, press)                                        # comes in low behind the punch, still closing at the kick
    hit = dict(press, lean=26, head=(-35, -18, 22), hR=(-.25, -.3, .45), hL=(.2, -.2, .25))
    key(B, 42, hit)                                                                             # the kick lands: head snaps away
    snap = dict(hit, pos=1.15, lean=4, head=(-30, -28, 35), hR=(-.35, -.1, .55), hL=(.3, .1, .3)); key(B, 45, snap)   # recoil carries the whole body back
    rec = stance('R', sink=.15, pos=.6, lean=-10, head=(-8, -12, 15)); key(B, 52, rec)       # staggers back, catches the balance
    key(B, 62, stance('R', pos=0)); key(B, 74, stance('R', pos=0))
    # ---- AKA (orthodox, red): bounce, slide back, counter roundhouse, slingshot, land ----
    bounce_keys(A, 'L', [1, 6, 11, 16, 21])
    key(A, 25, stance('L', pos=-.05, sink=.08))
    slide = stance('L', pos=-.4, sink=.1, lean=-6, hL=(.12, -.55, .2)); key(A, 30, slide)
    # impact pose first (needs AO's head at frame 42), then build chamber and re-chamber around it
    sc.frame_set(42); bpy.context.view_layer.update()
    hb = B['rig'].pose.bones['head']; Mh = B['rig'].matrix_world @ hb.matrix
    head_c = Mh @ Vector((0, .46, 0))                                                          # bone-local: .46 up the head bone = centre
    tgt_w = head_c + Vector((-.88, -.32, -.38)).normalized() * .62                             # ON the head's surface: the cheek facing Aka and the camera (inside the big head the foot vanishes)
    tgt = A['rig'].matrix_world.inverted() @ tgt_w
    REACH = .8  # hip to instep with the knee straight but not locked (thigh .35 + shin .34 + foot to instep .15, x .95)
    for pos_k in [p / 20 for p in range(-4, 16)]:  # step in until the kick can land: a counter closes the gap, limbs never stretch
        imp = stance('L', pos=pos_k, sink=-.04, turn=95, away=32, hips=(0, 0, 10), hL=(.25, -.45, .35), hR=(-.55, .25, -.15))
        imp['fL'] = (.17, .31 - .1 + .05, 135, 28)                                              # standing heel turned to the target, up on the ball
        apply_pose(A, dict(imp, fR=((-.3, -.5, .9), (0, 0, 0))))
        hip = A['rig'].pose.bones['thigh.R'].head.copy()
        if (Vector(tgt) - hip).length <= REACH: break
    A['kick_pos'] = pos_k; A['kick_reach'] = (Vector(tgt) - hip).length
    ank, Rf = kick_foot(tgt, (1, 0, .15), hip)
    root = Vector((0, -pos_k, 0))
    imp['fR'] = (tuple(ank - root), Rf); imp['poleR'] = tuple(Vector(tgt) - root + Vector((-.6, 0, .6)))
    # chamber: the knee points AT THE OPPONENT (rig -Y) and up, the shin folds back under it. (Nov 7: the knee was aimed
    # toward the camera side, so the thigh pointed at the lens and read as a stump with no knee.)
    cham = stance('L', pos=pos_k - .45, sink=0, turn=15, away=8, hL=(.15, -.6, .42), hR=(-.12, -.3, .5))  # measured: the chamber is nearly square, the hips turn over during the snap
    cham['fL'] = (.17, .31 - .1, 35, 18)
    apply_pose(A, dict(cham, fR=((-.3, -.3, .5), (0, 0, 0))))
    hip_c = A['rig'].pose.bones['thigh.R'].head.copy(); root_c = Vector((0, -(pos_k - .45), 0))
    knee_c = hip_c + Vector((0, -.29, .2))   # the high-knee L: thigh level, pointing at Ao (a pendulum swing from the hip)                                                     # thigh .35 long, aimed at Ao, 45 degrees up (knee at chest height, measured)
    ankle_c = knee_c + Vector((0, .02, -.34))  # shin hangs straight down below the belly, where nothing covers it                                                   # shin hangs down and back: knee folded about 120 degrees
    cham['fR'] = (tuple(ankle_c - root_c), R(25, 0, 0)); cham['poleR'] = tuple(knee_c - root_c + Vector((0, -1.0, .2)))
    shift = stance('L', pos=(pos_k - .45 - .4) / 2, sink=.08, turn=10); shift['fL'] = (.17, .31 - .1, 20, 15)  # step in, weight onto the front foot, it starts to turn
    key(A, 33, shift); key(A, 37, cham)
    key(A, 41, imp); key(A, 44, imp)                                                            # snap out, held a beat (kime)
    apply_pose(A, imp); knee_i = A['rig'].pose.bones['shin.R'].head.copy()                     # slingshot: the knee stays exactly here
    back = (hip - knee_i).normalized()
    ankle_s = knee_i + back * .2 + Vector((0, 0, -.26))                                        # only the shin whips back around the knee
    sling = dict(imp, fR=(tuple(ankle_s - root), R(60, 0, 70)), poleR=imp['poleR'])
    key(A, 47, sling); key(A, 48, sling)                                                       # slingshot: knee stays, shin whips back
    land = stance('L', pos=pos_k - .35, sink=.12, lean=4)
    drop = dict(land, sink=.17, turn=40)                                                       # the knee stays aimed at Ao while the foot comes down
    apply_pose(A, dict(drop, fR=((-.3, -.3, .5), (0, 0, 0)))); hip_d = A['rig'].pose.bones['thigh.R'].head.copy(); root_d = Vector((0, -(pos_k - .35), 0))
    knee_d = hip_d + Vector((-.04, -.3, -.12)); drop['fR'] = (tuple(knee_d + Vector((0, .06, -.32)) - root_d), R(35, 0, 0)); drop['poleR'] = tuple(knee_d - root_d + Vector((0, -1, 0)))
    key(A, 51, drop); key(A, 55, land)                                                         # sets the foot down a step back
    key(A, 62, stance('L', pos=0)); key(A, 74, stance('L', pos=0))
    # ---- both: stand, bow, rise ----
    for F, lead in ((A, 'L'), (B, 'R')):
        s = 1 if lead == 'L' else -1
        ready = dict(DEFAULT, pos=-.45, turn=-s * 35, fL=(.15, 0, -s * 35 + 8, 0), fR=(-.15, 0, -s * 35 - 8, 0), hL=(.32, -.05, -.45), hR=(-.32, -.05, -.45), sink=.0)  # step back to the line before rei
        key(F, 82, ready); key(F, 88, ready)
        bow = dict(ready, lean=28, head=(10, 0, 0)); key(F, 94, bow); key(F, 99, bow); key(F, 106, ready)
    sc.frame_start, sc.frame_end = 1, 112
    for F in (A, B): set_interp(F['rig'], range(0, 200), interp)
    return tgt_w


# ---------------- splining: from stepped blocking to final motion ----------------
def fcurves(rig):
    act = rig.animation_data.action
    for lay in act.layers:
        for st in lay.strips:
            for cb in st.channelbags:
                yield from cb.fcurves

OVERLAP = {'head': 2, 'neck': 1, 'hand_ik.L': 1, 'hand_ik.R': 1, 'chest': 1}  # trailing parts settle a frame or two after the body
CONTACT = {'AKA': (41, 55), 'AO': (26, 42, 45)}  # frames a strike or a foot arrives: no ease into them

def spline():
    for name, F in FIGHTERS.items():
        rig = F['rig']
        for fc in fcurves(rig):
            bone = fc.data_path.split('"')[1] if '"' in fc.data_path else ''
            n = OVERLAP.get(bone, 0)
            for kp in fc.keyframe_points:
                if n and kp.co.x > 1.5: kp.co.x += n; kp.handle_left.x += n; kp.handle_right.x += n
                kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
            fc.update()
            for kp in fc.keyframe_points:
                if int(round(kp.co.x)) - n in CONTACT[name]: kp.handle_left_type = 'VECTOR'
            fc.update()

def look(res=1280):
    sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y = res, res * 9 // 16
    import moves
    moves.kuwahara(sc)

def render_job(out_dir, res=1280):
    """Save the scene and render the frames in a background Blender (no window), so this Blender stays usable."""
    import subprocess
    look(res); os.makedirs(os.path.join(out_dir, 'frames'), exist_ok=True)
    sc = bpy.context.scene; sc.render.filepath = os.path.join(out_dir, 'frames', 'f####')
    sc.render.image_settings.file_format = 'PNG'
    blend = os.path.join(out_dir, 'kumite2.blend'); bpy.ops.wm.save_as_mainfile(filepath=blend, copy=True)
    log = open(os.path.join(out_dir, 'render.log'), 'w')
    subprocess.Popen([bpy.app.binary_path, '-b', blend, '-a'], stdout=log, stderr=subprocess.STDOUT, creationflags=0x08000000)
    return blend


def end_on(frames, limit=25):
    """Frames where a thigh or shin points at the camera (seen end-on it reads as a stump with no knee)."""
    sc = bpy.context.scene; cam = sc.camera; bad = []
    for f in frames:
        sc.frame_set(f)
        for name, F in FIGHTERS.items():
            rig = F['rig']
            for b in ('thigh.L', 'thigh.R', 'shin.L', 'shin.R'):
                pb = rig.pose.bones[b]; h = rig.matrix_world @ pb.head; t = rig.matrix_world @ pb.tail
                view = (h - cam.matrix_world.translation).normalized(); d = (t - h).normalized()
                ang = math.degrees(math.acos(min(1, abs(d.dot(view)))))
                if ang < limit: bad.append((f, name, b, round(ang)))
    return bad


def camera_cuts():
    """Staging: a wide side shot, then a cut to a three-quarter angle facing Aka for the chamber, kick and slingshot (from the
    side the short thigh hides behind the big head and arms), then back. Cuts are CONSTANT keys: no camera drift."""
    sc = bpy.context.scene; cam = sc.camera
    shots = {'wide': ((-0.7, -9.4, 2.25), (-0.1, 0, 1.3), 38), 'kick': ((3.6, -6.0, 2.2), (-1.0, 0, 1.1), 40)}
    cam.animation_data_clear(); cam.data.animation_data_clear()
    for f, s in ((1, 'wide'), (32, 'kick'), (57, 'wide')):
        loc, aim, lens = shots[s]
        cam.location = loc; cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = lens
        cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f); cam.data.keyframe_insert('lens', frame=f)
    for ad in (cam.animation_data, cam.data.animation_data):
        for lay in ad.action.layers:
            for st in lay.strips:
                for cb in st.channelbags:
                    for fc in cb.fcurves:
                        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
