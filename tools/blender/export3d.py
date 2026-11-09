# Export the rigged bunny and its moves for the real-time 3D fight (Nov 9 2026, user: "knowing what you know, give me a
# 3d version of the karate bunnies" -> a playable 3D fight). Every move is the same solved, reviewed animation as the
# videos (planted feet, counterbalance, spring ears), baked into one named action each, then exported as a single GLB.
# The game reads moves.json for the timing: hit frames, landings (lead switches) and loop ranges.
# Run inside Blender after kumite2 build(), one step per call (each bake takes ~15 s):
#   X = {'HERE': folder}; exec(open(folder + r'\export3d.py').read(), X)
#   for n in X['ORDER']: X['bake'](n, F, G)        # one per call
#   X['export'](F, folder + r'\export')
import os, json, math, bpy
from mathutils import Vector

ORDER = ['idle', 'advance', 'kick', 'gyaku', 'mawashi', 'ushiro', 'hit', 'ko', 'win']
INFO = {}
FPS = 30

def _store(rig, name, info):
    act = rig.animation_data.action
    old = bpy.data.actions.get('KB_' + name)
    if old and old != act: bpy.data.actions.remove(old)
    act.name = 'KB_' + name; act.use_fake_user = True
    info['frames'] = int(bpy.context.scene.frame_end)
    INFO[name] = info
    with open(os.path.join(HERE, 'export', 'moves.json'), 'w') as fh: json.dump(INFO, fh, indent=1)
    return info

def _load():
    p = os.path.join(HERE, 'export', 'moves.json')
    if os.path.exists(p): INFO.update(json.load(open(p)))

def _ns(fname):
    ns = {'HERE': HERE}; exec(open(os.path.join(HERE, fname)).read(), ns); return ns

def _beats_clip(F, G, CB, beats, end, ones=None):
    """animate a beat list with combo.py's solver (planted feet, ball pivots), springs on, every frame keyed"""
    rig = F['rig']; rig.animation_data_clear(); sc = bpy.context.scene; sc.frame_start, sc.frame_end = 0, end
    for b in beats: b[2].setdefault('leg', 'R')
    CB['BEATS'] = beats; CB['END'] = end
    frames = list(range(0, end + 1))
    for f in frames:
        S = CB['state'](f); P = CB['body_pose'](F, G, S); G['key'](F, f, P)
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    CB['follow_through'](F, set(frames))
    for fc in G['fcurves'](rig):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

def bake(name, F, G):
    _load(); os.makedirs(os.path.join(HERE, 'export'), exist_ok=True)
    rig = F['rig']
    if name == 'idle':
        # fighting guard (the combos' guard, so every move starts from it), breathing on a 48-frame loop; baked twice
        # so the springs settle, the game plays 48-96
        CB = _ns('combo.py'); GU = CB['GUARD']; beats = []
        for i in range(0, 97, 4):
            w = 2 * math.pi * i / 48
            beats.append((i, 'io', dict(GU, sink=GU['sink'] + .03 + .025 * math.sin(w), lean=GU['lean'] + 1.5 * math.sin(w - .6),
                                        hL=(GU['hL'][0], GU['hL'][1], GU['hL'][2] + .012 * math.sin(w - .9)),
                                        hR=(GU['hR'][0], GU['hR'][1], GU['hR'][2] + .012 * math.sin(w - 1.1)))))
        _beats_clip(F, G, CB, beats, 96)
        return _store(rig, name, dict(loop=[48, 96], lead_switch=False, hits=[], travel=0))
    if name == 'advance':
        SW = _ns('stance_walk.py'); SW['advance'](F, G)
        a0 = SW['LEAD'] + SW['ADV']; a1 = a0 + SW['ADV']
        return _store(rig, name, dict(loop=[a0, a1], lead_switch=False, hits=[], travel=SW['D']))
    if name in ('kick', 'gyaku'):
        CB = _ns('combo.py'); CB['combo'](F, G, fx=False)
        land1, land2, punch = CB['MARKS']
        if name == 'kick':
            f0, f1, leg = CB['SNAPS'][0]
            return _store(rig, name, dict(range=[0, land1 + 5], lead_switch=True, travel=None,
                                          hits=[dict(f=f1, limb='foot.R', height='mid', dmg=12, reach=1.25)]))
        return _store(rig, name, dict(range=[land2, CB['END']], lead_switch=False, travel=None,
                                      hits=[dict(f=punch, limb='hand.R', height='high', dmg=9, reach=1.05)]))
    if name in ('mawashi', 'ushiro'):
        C2 = _ns('combos2.py'); C2['run'](name, F, G, fx=False)
        hits = []
        for (f0, f1, side_) in C2['PUNCHES']: hits.append(dict(f=f1, limb='hand.' + side_, height='high', dmg=5, reach=1.05))
        for (f0, f1, leg) in C2['SNAPS']: hits.append(dict(f=f1, limb='foot.' + leg, height='high', dmg=14 if name == 'mawashi' else 12, reach=1.3))
        hits.sort(key=lambda h: h['f'])
        if name == 'ushiro': hits[0].update(height='mid', dmg=7)
        return _store(rig, name, dict(range=[0, C2['END']], lead_switch=True, travel=None, hits=hits))
    if name == 'hit':
        # struck: the head snaps back first, the trunk follows, the bunny skids back on both feet and re-guards
        CB = _ns('combo.py'); GU = CB['GUARD']
        b = lambda **kw: dict(GU, **kw)
        beats = [(0, 'lin', b()),
                 (2, 'out', b(away=26, lean=-2, sink=.12, pos=-.08, turn=-16, hL=(.3, -.3, .26), hR=(-.36, -.2, .22))),
                 (5, 'out', b(away=18, sink=.16, pos=-.2, yL=-.06, yR=-.46, turn=-14, hL=(.28, -.36, .22), hR=(-.34, -.26, .16))),
                 (10, 'io', b(away=4, sink=.12, pos=-.24, yL=-.12, yR=-.54, turn=-11)),
                 (15, 'io', b(sink=.08, pos=-.24, yL=-.12, yR=-.54))]
        _beats_clip(F, G, CB, beats, 15)
        return _store(rig, name, dict(range=[0, 15], lead_switch=False, hits=[], travel=None))
    if name == 'ko':
        # knocked down: staggers back, sits down hard on its bottom with the legs out in front, wobbles dazed
        CB = _ns('combo.py'); GU = CB['GUARD']
        b = lambda **kw: dict(GU, **kw)
        beats = [(0, 'lin', b()),
                 (2, 'out', b(away=30, sink=.14, pos=-.12, turn=-18, hL=(.34, -.26, .2), hR=(-.4, -.16, .16))),
                 (6, 'out', b(away=26, sink=.3, pos=-.36, yL=-.1, yR=-.5, turn=-14, hL=(.4, -.1, -.1), hR=(-.42, -.06, -.12))),
                 (10, 'in', b(away=18, sink=.62, pos=-.52, yL=-.02, yR=-.36, turn=-10, hL=(.42, 0, -.36), hR=(-.44, 0, -.38))),
                 (12, 'out', b(away=14, sink=.78, pos=-.56, yL=.04, yR=-.24, turn=-8, hL=(.44, .02, -.44), hR=(-.46, .02, -.46))),
                 (15, 'out', b(away=8, sink=.72, pos=-.56, yL=.04, yR=-.24, turn=-8, hL=(.44, 0, -.42), hR=(-.46, 0, -.44))),
                 (20, 'io', b(away=12, sink=.76, pos=-.56, yL=.04, yR=-.24, turn=-12, hL=(.44, .02, -.44), hR=(-.46, .02, -.46))),
                 (28, 'io', b(away=10, sink=.75, pos=-.56, yL=.04, yR=-.24, turn=-5, hL=(.44, .02, -.44), hR=(-.46, .02, -.46))),
                 (36, 'io', b(away=12, sink=.76, pos=-.56, yL=.04, yR=-.24, turn=-11, hL=(.44, .02, -.44), hR=(-.46, .02, -.46))),
                 (44, 'io', b(away=10, sink=.75, pos=-.56, yL=.04, yR=-.24, turn=-6, hL=(.44, .02, -.44), hR=(-.46, .02, -.46)))]
        _beats_clip(F, G, CB, beats, 44)
        return _store(rig, name, dict(range=[0, 44], loop=[20, 36], lead_switch=False, hits=[], travel=None))
    if name == 'win':
        # victory: rises out of the guard, rear fist punches the sky BESIDE the head (user, Nov 9: the arm went through the head)
        CB = _ns('combo.py'); GU = CB['GUARD']
        b = lambda **kw: dict(GU, **kw)
        beats = [(0, 'lin', b()),
                 (4, 'io', b(sink=.16, lean=8, turn=-4, hR=(-.3, -.2, .02))),
                 (8, 'out', b(sink=-.02, lean=-4, away=6, turn=0, hL=(.36, -.3, .06), hR=(-.7, -.1, .84))),
                 (12, 'io', b(sink=.02, lean=-2, away=4, turn=0, hL=(.36, -.28, .04), hR=(-.68, -.08, .82))),
                 (16, 'io', b(sink=.0, lean=-3, away=5, turn=0, hL=(.36, -.28, .06), hR=(-.7, -.1, .84))),
                 (24, 'io', b(sink=.02, lean=-2, away=4, turn=0, hL=(.36, -.28, .04), hR=(-.68, -.08, .82)))]
        _beats_clip(F, G, CB, beats, 24)
        return _store(rig, name, dict(range=[0, 24], loop=[12, 24], lead_switch=False, hits=[], travel=None))
    raise KeyError(name)

def bake_visual(rig, act):
    """Replace an action with its evaluated pose (IK, limits and springs resolved) keyed on every bone and frame, so the
    game plays exactly what Blender shows. The glTF exporter's own sampling dropped the IK leg solve (Nov 9: a roundhouse
    foot at 0.2 m instead of 1.88 m)."""
    sc = bpy.context.scene; ad = rig.animation_data; ad.action = act
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    pbs = list(rig.pose.bones); rows = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        rows.append([rig.convert_space(pose_bone=pb, matrix=pb.matrix, from_space='POSE', to_space='LOCAL') for pb in pbs])
    baked = bpy.data.actions.new(act.name + '_baked'); ad.action = baked
    for i, f in enumerate(range(f0, f1 + 1)):
        for pb, m in zip(pbs, rows[i]):
            loc, rot, scl = m.decompose()
            pb.location = loc; pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = rot; pb.scale = scl
            for prop in ('location', 'rotation_quaternion', 'scale'): pb.keyframe_insert(prop, frame=f)
    name = act.name; bpy.data.actions.remove(act); baked.name = name; baked.use_fake_user = True
    return baked

def export(F, folder):
    rig = F['rig']; os.makedirs(folder, exist_ok=True)
    for a in list(bpy.data.actions):
        if a.name.startswith(rig.name + 'Action') and a.users == 0: bpy.data.actions.remove(a)
    # every KB_ action as its own NLA strip so the exporter writes one clip per move
    ad = rig.animation_data or rig.animation_data_create(); ad.action = None
    for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
    for n in ORDER:
        act = bpy.data.actions.get('KB_' + n)
        if not act: continue
        tr = ad.nla_tracks.new(); tr.name = n; st = tr.strips.new(n, int(act.frame_range[0]), act)
    parts = [o for o in bpy.data.objects if o.parent == rig or (o.type == 'MESH' and any(m.type == 'ARMATURE' and m.object == rig for m in o.modifiers))]
    loc, rot = rig.location.copy(), rig.rotation_euler.copy(); rig.location = (0, 0, 0); rig.rotation_euler = (0, 0, 0)
    muted = [c for pb in rig.pose.bones for c in pb.constraints if not c.mute]
    for c in muted: c.mute = True
    ink = []
    for o in parts:
        for m in o.modifiers:
            if m.type == 'SOLIDIFY' and m.show_viewport: ink.append(m); m.show_viewport = False; m.show_render = False
    for o in bpy.context.view_layer.objects: o.select_set(False)
    for o in parts + [rig]: o.hide_set(False); o.select_set(True)
    bpy.context.view_layer.objects.active = rig
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(folder, 'bunny.glb'), export_format='GLB', use_selection=True,
                                  export_animations=True, export_animation_mode='NLA_TRACKS', export_force_sampling=True,
                                  export_frame_step=1, export_def_bones=False, export_apply=False, export_yup=True,
                                  export_morph=False, export_skins=True, export_materials='EXPORT', export_extras=True)
    finally:
        rig.location = loc; rig.rotation_euler = rot
        for c in muted: c.mute = False
        for m in ink: m.show_viewport = True; m.show_render = True
        for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
    return os.path.getsize(os.path.join(folder, 'bunny.glb'))
