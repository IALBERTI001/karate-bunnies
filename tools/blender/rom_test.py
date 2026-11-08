# Range-of-motion test for a character rig (run inside Blender after the character is built).
# A rig is only finished when EVERY joint a person has can move, moves the body with it, stops at a person's limit,
# and does the same thing on the left and the right. This test proves it on every build instead of finding out in an
# animation (Nov 8 2026: an elbow limit with the wrong sign locked both arms straight for a day, unnoticed).
#
# For every motion in MOTIONS it switches the limbs to FK, rotates the bone to the end of its range, and checks:
#   moves      - the bone's tip actually travels (a lock or a limit with the wrong sign shows up as zero travel)
#   follows    - the skin weighted to that bone (or the rigid part parented to it) travels with it
#   no_tear    - no edge of any deforming mesh stretches past 2.5x its rest length (spikes, torn seams)
#   stops      - pushed 25 deg past its range, the joint stays within ~3 deg of the limit
#   mirror     - the left and right versions of the motion land as mirror images
# and renders one tile per motion so a person can see every joint at both ends of its range.
#   In Blender: R = {}; exec(open(r'...\rom_test.py').read(), R); report = R['run'](rig, out_png)
import bpy, math
from mathutils import Vector, Quaternion, Matrix

# (name, bone, local axis index 0=X 1=Y 2=Z, min deg, max deg). 'L'/'R' in the bone name are expanded to both sides.
# Fingers/thumbs use their measured curl axis (bone['curl_axis'], bone['curl_sign']) and are given as 'curl'.
MOTIONS = [
    ('pelvis tilt', 'hips', 0, -25, 25), ('pelvis turn', 'hips', 1, -35, 35), ('pelvis side', 'hips', 2, -20, 20),
    ('spine bend', 'spine', 0, -30, 40), ('spine twist', 'spine', 1, -30, 30), ('spine side', 'spine', 2, -25, 25),
    ('chest bend', 'chest', 0, -25, 35), ('chest twist', 'chest', 1, -30, 30), ('chest side', 'chest', 2, -20, 20),
    ('neck nod', 'neck', 0, -40, 40), ('neck turn', 'neck', 1, -55, 55), ('neck tilt', 'neck', 2, -30, 30),
    ('head nod', 'head', 0, -35, 35), ('head turn', 'head', 1, -55, 55), ('head tilt', 'head', 2, -30, 30),
    ('shoulder shrug', 'shoulder.L', 0, -15, 30), ('shoulder roll', 'shoulder.L', 2, -25, 25),
    ('arm raise', 'upper_arm.L', 0, -60, 90), ('arm swing', 'upper_arm.L', 2, -80, 80), ('arm twist', 'upper_arm.L', 1, -60, 60),
    ('elbow bend', 'forearm.L', 0, 0, 140),
    ('wrist bend', 'hand.L', 0, -65, 65), ('wrist twist', 'hand.L', 1, -70, 70), ('wrist side', 'hand.L', 2, -30, 30),
    ('fingers curl', 'fingers_a.L', 'curl', 0, 95), ('fingertips curl', 'fingers_b.L', 'curl', 0, 95),
    ('thumb curl', 'thumb_a.L', 'curl', 0, 65), ('thumb tip curl', 'thumb_b.L', 'curl', 0, 65),
    ('hip raise', 'thigh.L', 0, -30, 120), ('hip open', 'thigh.L', 2, -40, 40), ('hip twist', 'thigh.L', 1, -40, 40),
    ('knee bend', 'shin.L', 0, -140, 0),
    ('ankle point', 'foot.L', 0, -40, 40), ('ankle roll', 'foot.L', 2, -20, 20),
    ('toes', 'toe.L', 0, -35, 55),
    ('ear bend', 'ear_a.L', 0, -40, 40), ('ear tip', 'ear_b.L', 0, -40, 40), ('tail', 'tail', 0, -30, 30),
]

# Skin really stretches at the far end of a few big joints (armpit at a 90 deg raise, groin at a 120 deg knee lift, back of
# a fully bent knee). These allowances were set after close-up renders from three angles showed cloth stretch and no tear
# (Nov 8 2026); every other motion keeps the 2.5x limit. Raise one only after looking at the close-up yourself.
STRETCH_OK = {'arm raise': 3.0, 'arm swing': 3.0, 'hip raise': 5.0, 'knee bend': 3.0}

def _ik(rig, on):
    for k in list(rig.keys()):
        if k.startswith(('ik_arm.', 'ik_leg.')): rig[k] = 1.0 if on else 0.0
    rig.update_tag(); bpy.context.view_layer.update()

def _reset(rig):
    for p in rig.pose.bones:
        p.location = (0, 0, 0); p.rotation_quaternion = (1, 0, 0, 0); p.scale = (1, 1, 1)
    bpy.context.view_layer.update()

def _axis(bone, ax):
    if ax == 'curl':
        v = [0, 0, 0]; v[bone['curl_axis']] = 1; return Vector(v), bone['curl_sign']
    v = [0, 0, 0]; v[ax] = 1; return Vector(v), 1

def _meshes(rig):
    return [o for o in bpy.data.objects if o.type == 'MESH' and (o.parent == rig or (o.find_armature() == rig)) and not o.hide_render]

def _snapshot(obs):
    dg = bpy.context.evaluated_depsgraph_get(); out = {}
    for o in obs:
        sol = [m for m in o.modifiers if m.type == 'SOLIDIFY' and m.show_viewport]
        for m in sol: m.show_viewport = False
    dg.update()
    for o in obs:
        e = o.evaluated_get(dg); me = e.to_mesh()
        out[o.name] = ([e.matrix_world @ v.co for v in me.vertices], [tuple(ed.vertices) for ed in me.edges]); e.to_mesh_clear()
    for o in obs:
        for m in o.modifiers:
            if m.type == 'SOLIDIFY': m.show_viewport = True
    return out

def _family(rig, bone):
    """the bone and every bone below it (rotating the neck moves the head too)"""
    out = set(); st = [rig.data.bones[bone]]
    while st:
        b = st.pop(); out.add(b.name); st.extend(b.children)
    return out

def _followers(rig, obs, bone):
    """vertex indices per object that move with this bone: summed weight of the bone and its children > .5,
    or the whole object if it is parented to one of them"""
    fam = _family(rig, bone); f = {}
    for o in obs:
        if o.parent_type == 'BONE' and o.parent_bone in fam: f[o.name] = None; continue
        gi = {g.index for g in o.vertex_groups if g.name in fam}
        if gi:
            idx = [v.index for v in o.data.vertices if sum(gg.weight for gg in v.groups if gg.group in gi) > .5]
            if idx: f[o.name] = idx
    return f

def _local_angle(rig, name, axv):
    pb = rig.pose.bones[name]; b = pb.bone
    par = (pb.parent.matrix @ b.parent.matrix_local.inverted() @ b.matrix_local) if pb.parent else b.matrix_local
    q = (par.inverted() @ pb.matrix).to_quaternion()
    ang = 2 * math.degrees(math.atan2(Vector(q[1:]).dot(axv), q[0]))
    return ang

def _limit(pb, ax_index):
    c = pb.constraints.get('ROM')
    if not c: return None
    k = 'xyz'[ax_index]
    if not getattr(c, f'use_limit_{k}'): return None
    return math.degrees(getattr(c, f'min_{k}')), math.degrees(getattr(c, f'max_{k}'))

def run(rig, out_png=None, cam_dist=7.0):
    sc = bpy.context.scene; frame = sc.frame_current
    ad = rig.animation_data; act = ad.action if ad else None
    if ad: ad.action = None
    obs = _meshes(rig); _ik(rig, False); _reset(rig); rest = _snapshot(obs)
    rest_len = {n: [ (v[a] - v[b]).length for a, b in ed] for n, (v, ed) in rest.items()}
    report = []; tiles = []
    for (label, bname, ax, lo, hi) in MOTIONS:
        sides = [bname.replace('.L', '.L'), bname.replace('.L', '.R')] if '.L' in bname else [bname]
        res = {'motion': label, 'bone': bname}; tips = {}
        for side in sides:
            if side not in rig.pose.bones: res[side] = 'MISSING BONE'; continue
            pb = rig.pose.bones[side]; axv, sg = _axis(pb.bone, ax)
            fol = _followers(rig, obs, side)
            axi = pb.bone['curl_axis'] if ax == 'curl' else ax
            # Blender mirrors .L/.R bones with X rotations the same sign and Y/Z rotations flipped
            msg = -1 if (side.endswith('.R') and ax in (1, 2)) else 1
            lim = _limit(pb, axi)
            for end in (lo, hi):
                if end == 0: continue
                _reset(rig)
                tgt = sg * msg * end
                pb.rotation_quaternion = Quaternion(axv, math.radians(tgt)); bpy.context.view_layer.update()
                snap = _snapshot(obs)
                tip0 = pb.bone.tail_local; tip = pb.tail
                tipmove = (Vector(tip) - Vector(tip0)).length
                reach = abs(_local_angle(rig, side, axv) - tgt) if lim else 0.0   # a limit must not block the normal range
                fm = []
                for n, idx in fol.items():
                    v1, _ = snap[n]; v0, _ = rest[n]
                    ids = range(len(v1)) if idx is None else idx
                    if ids: fm.append(sum((v1[i] - v0[i]).length for i in ids) / len(ids))
                follows = max(fm) if fm else 0.0
                travel = max(tipmove, follows)        # a twist leaves the tip in place but turns the body part
                worst = 1.0; where = ''
                for n, (v1, ed) in snap.items():
                    for k, (a, b) in enumerate(ed):
                        r = rest_len[n][k]
                        if r > 1e-4:
                            L = (v1[a] - v1[b]).length
                            if L - r > .02 and L / r > worst: worst = L / r; where = f'{n}:v{a}'
                push = tgt + 25 * (1 if tgt > 0 else -1)
                pb.rotation_quaternion = Quaternion(axv, math.radians(push)); bpy.context.view_layer.update()
                if lim:
                    clamp = min(max(push, lim[0]), lim[1])
                    over = abs(_local_angle(rig, side, axv) - clamp)
                else:
                    over = 0.0   # free joints (ears, tail) have no stop
                key = f'{side}@{end}'
                res[key] = dict(travel=round(travel, 3), follows=round(follows, 3), stretch=round(worst, 2), where=where,
                                reach_err=round(reach, 1), over_limit=round(over, 1))
                d = Vector(tip) - Vector(tip0)
                tips[(side, end)] = d
                if side == sides[0] and end == (hi if hi else lo): tiles.append((label, side, tgt, axv))
        # mirror check
        if len(sides) == 2:
            errs = []
            for end in (lo, hi):
                if (sides[0], end) in tips and (sides[1], end) in tips:
                    a, b = tips[(sides[0], end)], tips[(sides[1], end)]
                    errs.append((a - Vector((-b.x, b.y, b.z))).length)
            res['mirror_err'] = round(max(errs), 3) if errs else None
        # verdict
        fails = []
        for k, v in res.items():
            if isinstance(v, str) and 'MISSING' in v: fails.append(f'{k} missing')
            if isinstance(v, dict):
                if v['travel'] < .01: fails.append(f'{k} does not move')
                if v['follows'] < .25 * v['travel'] and v['travel'] > .03: fails.append(f'{k} body does not follow')
                if v['stretch'] > STRETCH_OK.get(label, 2.5): fails.append(f'{k} tears/spikes x{v["stretch"]} at {v["where"]}')
                if v['over_limit'] > 3: fails.append(f'{k} passes its limit by {v["over_limit"]} deg')
                if v['reach_err'] > 3: fails.append(f'{k} is blocked {v["reach_err"]} deg short by its own limit')
        if res.get('mirror_err') and res['mirror_err'] > .03: fails.append(f'left/right differ by {res["mirror_err"]}')
        res['pass'] = not fails; res['fails'] = fails; report.append(res)
    _reset(rig); _ik(rig, True)
    if ad: ad.action = act
    sc.frame_set(frame)
    if out_png: render_sheet(rig, tiles, out_png, cam_dist)
    return report

def render_sheet(rig, tiles, out_png, cam_dist=7.0, size=300, cols=8):
    """one tile per motion at the end of its range, from the front three-quarter"""
    import os, tempfile
    sc = bpy.context.scene; cam = bpy.data.objects.get('romcam')
    if not cam: cam = bpy.data.objects.new('romcam', bpy.data.cameras.new('romcam')); sc.collection.objects.link(cam)
    cam.data.lens = 50; old = sc.camera; sc.camera = cam
    R = sc.render; stamp_was = {k: getattr(R, k) for k in dir(R) if k.startswith('use_stamp')}
    for k in stamp_was: setattr(R, k, False)
    R.use_stamp = True; R.use_stamp_note = True; R.stamp_font_size = 22
    rx, ry = sc.render.resolution_x, sc.render.resolution_y; sc.render.resolution_x = sc.render.resolution_y = size
    ad = rig.animation_data; act = ad.action if ad else None
    if ad: ad.action = None
    _ik(rig, False); tmp = tempfile.mkdtemp(); paths = []
    fwd = rig.matrix_world.to_3x3() @ Vector((0, -1, 0)); side = rig.matrix_world.to_3x3() @ Vector((1, 0, 0))
    for i, (label, bname, ang, axv) in enumerate(tiles):
        _reset(rig); pb = rig.pose.bones[bname]
        pb.rotation_quaternion = Quaternion(axv, math.radians(ang)); bpy.context.view_layer.update()
        close = bname.startswith(('fingers_', 'thumb_', 'hand.', 'toe.', 'foot.'))
        # body joints: the whole bunny, so the pose reads; paws and feet: a close-up of the bone
        t = rig.matrix_world @ (((pb.head + pb.tail) / 2) if close else Vector((0, 0, 1.75)))
        d = (fwd * .8 - side * .6 + Vector((0, 0, .25))).normalized()
        cam.location = t + d * (1.6 if close else cam_dist); cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.stamp_note_text = f'{label}  {ang:+.0f}'
        p = os.path.join(tmp, f'{i:02d}.png'); sc.render.filepath = p; bpy.ops.render.render(write_still=True); paths.append((label, p))
    _reset(rig); _ik(rig, True)
    if ad: ad.action = act
    sc.camera = old; sc.render.resolution_x, sc.render.resolution_y = rx, ry
    for k, v in stamp_was.items(): setattr(R, k, v)
    # stitch with Blender's image API (no PIL inside Blender)
    rows = (len(paths) + cols - 1) // cols; W, H = cols * size, rows * size
    import numpy as np
    canvas = np.zeros((H, W, 4), dtype=np.float32); canvas[..., 3] = 1
    for i, (label, p) in enumerate(paths):
        img = bpy.data.images.load(p); px = np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4)
        r, c = i // cols, i % cols; y0 = H - (r + 1) * size
        canvas[y0:y0 + size, c * size:(c + 1) * size] = px; bpy.data.images.remove(img)
    out = bpy.data.images.new('rom_sheet', W, H); out.pixels = canvas.ravel(); out.filepath_raw = out_png; out.file_format = 'PNG'; out.save()
    bpy.data.images.remove(out)
    return [l for l, _ in paths]
