# A WKF kumite exchange between two Karate Bunnies, rendered as a short film (PNG frames; the video is assembled with
# ffmpeg afterwards):  blender -b --factory-startup -P kumite.py -- <out dir> [res_x]
# Studied from the WKF Premier League Cairo 2024 -84 kg final (Badawy vs Aljafari): white gi, AKA with a red belt,
# gloves and foot protectors, AO in blue; a blue competition area with a red border; fighters stand tall and side-on,
# far apart, bouncing on the balls of their feet; an attack is answered by a slide back and a counter. The scoring
# moment is a jodan mawashi-geri: the knee snaps up, the trunk drops far back and the instep lands on the head in
# about 0.3 s, then the kicker re-chambers and lands. After the point both reset and bow (rei).
# Every frame of both fighters goes through the movement rules in moves.py (balance, planted feet, knees, cloth).
import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, kbpuppet, kbrig, kbmove as KM
importlib.reload(kbpuppet); importlib.reload(kbrig)
import moves as MV
importlib.reload(MV)
from mathutils import Vector, Matrix
from kbrig import rotm

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kumite-out')
RX = int(argv[1]) if len(argv) > 1 else 1280
FPS = 24
MV.VSCALE = 24 / 9

# ---------- mirroring: AO fights southpaw so both fighters show their chest to the broadcast camera ----------
SIDE = {'L': 'R', 'R': 'L'}
def mirror(P):
    Q = {}
    for k, v in P.items():
        k2 = k
        for base in ('footL', 'footR', 'handL', 'handR', 'heelL', 'heelR', 'chamberL', 'chamberR', 'strikeL', 'strikeR', 'kneeL', 'kneeR'):
            if k == base: k2 = base[:-1] + SIDE[base[-1]]
        if k in ('footLRot', 'footRRot'): k2 = 'foot' + SIDE[k[4]] + 'Rot'
        if k2.startswith(('foot', 'hand')) and not k2.endswith('Rot') and isinstance(v, tuple): v = (-v[0], v[1], v[2])
        elif k2.endswith('Rot') and isinstance(v, tuple) and k2.startswith('foot'): v = (v[0], -v[1], -v[2])
        elif k in ('pelvisRot', 'spine', 'chest', 'head'): v = (v[0], -v[1], -v[2])
        elif k in ('root', 'pelvis'): v = (-v[0], v[1], v[2])
        elif k == 'spin': v = -v
        elif k == 'ties': v = -v
        elif k in ('weight', 'drive') and v in ('L', 'R'): v = SIDE[v]
        elif k2.startswith('chamber') and isinstance(v, dict):
            v = dict(v); v['dir'] = (-v['dir'][0], v['dir'][1], v['dir'][2])
            if 'toward' in v: v['toward'] = (-v['toward'][0], v['toward'][1], v['toward'][2])
        Q[k2] = v
    Q['mirror'] = True; return Q

# ---------- scene ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene, root_empty, decals = kbpuppet.setup_scene(512, 8.0, (0, 2.7), 2.2)
bpy.data.objects.remove(root_empty)
scene.render.resolution_x, scene.render.resolution_y = RX, RX * 9 // 16
scene.render.film_transparent = False; scene.render.fps = FPS
cam = scene.camera; cam.data.type = 'PERSP'; cam.data.lens = 45
cam.location = (0, -15.5, 4.1); look = Vector((0, 0, 1.75)) - cam.location; cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
scene.world.node_tree.nodes['Background'].inputs[0].default_value = kbpuppet.hexc('#1b2130')
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .6
m = kbpuppet.materials()

def slab(name, x0, y0, x1, y1, z, mat):
    me = bpy.data.meshes.new(name); me.from_pydata([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new(name, me); scene.collection.objects.link(o); me.materials.append(mat); return o
# WKF area: 8 x 8 m blue competition area inside a red 1 m safety border, on a dark floor (1 m = 1 unit here).
FLOOR = kbpuppet._toon('floor', '#3a4150', '#272c37'); RED = kbpuppet._toon('mat_red', '#c9343c', '#93222a')
BLUE = kbpuppet._toon('mat_blue', '#2f6fc2', '#22508f'); LINE = kbpuppet._toon('mat_line', '#e9edf2', '#b9c0c9')
slab('floor', -40, -40, 40, 40, -.002, FLOOR); slab('border', -8, -8, 8, 8, 0, RED); slab('area', -6.4, -6.4, 6.4, 6.4, .002, BLUE)  # bunny scale: 1 m = 1.6 units
for x in (-2.4, 2.4):  # the competitors' starting lines, 1.5 m from the centre
    slab(f'start{x}', x - .025, -.5, x + .025, .5, .004, LINE)
# backdrop: dark stands with the federation's red and blue bands (no logos)
WALL = kbpuppet._flat('wall', '#20283a'); BAND_R = kbpuppet._flat('band_r', '#b7202f'); BAND_B = kbpuppet._flat('band_b', '#1f4fa0')
def wall(name, z0, z1, mat, y=9.0):
    me = bpy.data.meshes.new(name); me.from_pydata([(-30, y, z0), (30, y, z0), (30, y, z1), (-30, y, z1)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new(name, me); scene.collection.objects.link(o); me.materials.append(mat); o.hide_select = True; return o
wall('wall', -1, 20, WALL); wall('band_r', 1.1, 1.6, BAND_R, 8.98); wall('band_b', 1.6, 2.0, BAND_B, 8.98)
for o in list(scene.collection.objects):  # scenery carries no ink lines
    if o.type == 'MESH' and o.name.startswith(('floor', 'border', 'area', 'start', 'wall', 'band')):
        scene.collection.objects.unlink(o); decals.objects.link(o)

# ---------- fighters ----------
GI = kbpuppet._toon('gi_white', '#f4f3ee', '#c9ccd3', '#ffffff')
def fighter(name, col, shadow):
    m['GI'] = GI; m['BELT'] = kbpuppet._toon(name + '_belt', col, shadow)
    kbrig.EXPRESSIONS.clear()
    rig = kbrig.build_armature(scene); rig.name = name
    parts = kbrig.build_body(rig, decals)
    expr = {k: list(v) for k, v in kbrig.EXPRESSIONS.items()}
    gear = kbpuppet._toon(name + '_gear', col, shadow)
    for o in parts.objs:
        if o.get('mask') == 'band' or o.name.startswith(('fist.', 'foot.')): o.data.materials.clear(); o.data.materials.append(gear)
    for pb in rig.pose.bones:
        for c in pb.constraints:
            if c.type == 'IK': c.mute = True
    return rig, parts, expr
AKA = fighter('AKA', '#d02f37', '#9b1f27')
AO = fighter('AO', '#2d63c8', '#204a96')
BASE = {'AKA': (-1.7, 90, False), 'AO': (2.4, -90, True)}  # world x, yaw, mirrored (each stands on its starting line)

# ---------- choreography (24 fps) ----------
def prep(name, P):  # place a pose in this fighter's world: its facing, and southpaw for AO
    P = dict(P, yaw=BASE[name][1])
    return mirror(P) if BASE[name][2] else P
def at(P, dy):  # shift a pose along the fighter's own line (negative = toward the opponent)
    r = P.get('root', (0, 0, 0)); return dict(P, root=(r[0], r[1] + dy, r[2]))
def bounce(n, y0, y1, phase=0.0, period=10):
    out = []
    for i in range(n):
        u = math.sin(2 * math.pi * (i / period + phase)); y = y0 + (y1 - y0) * MV.ease('io', i / max(n - 1, 1))
        out.append(MV.stance(**MV.FOCUS, root=(0, y, 0), pelvis=(0, 0, -.28 + .045 * u), heelL=6 + 10 * max(u, 0), heelR=6 + 10 * max(u, 0), weight=.5))
    out[-1] = MV.stance(**MV.FOCUS, root=(0, y1, 0), weight=.5)  # end each bounce in plain guard so the next move starts clean
    return out
def solve(rig, P, fid): return MV.apply_pose(rig, P, fid)
def tweens(rig, name, K0, K1, n, kind, tag):
    K0 = solve(rig, K0, f'{tag}-a'); K1 = solve(rig, K1, f'{tag}-b')
    return [MV.tween(K0, K1, MV.ease(kind, j / n)) if j < n else K1 for j in range(1, n + 1)]
def move(rig, name, mv, dy, tweak=None, dys=None):  # dys: a step per key (a kick that travels: plant and move the whole body)
    keys, sched = MV.sequence(mv)
    keys = [prep(name, at(K, dys[i] if dys else dy)) for i, K in enumerate(keys)]
    if tweak: tweak(keys)
    keys = [solve(rig, K, f'{name}-{mv}-k{i}') for i, K in enumerate(keys)]
    out = [keys[0]]
    for a_, b_, cnt, kind in sched:
        for j in range(1, cnt + 1):
            out.append(keys[a_] if kind == 'hold' else keys[b_] if j == cnt else MV.tween(keys[a_], keys[b_], MV.ease(kind, j / cnt)))
    return out

rigA, rigB = AKA[0], AO[0]
G = lambda dy, **kw: MV.stance(**MV.FOCUS, root=(0, dy, 0), weight=.5, **kw)
def head_kick(keys):  # the scoring kick: the trunk drops far back (about 40 degrees on the bunny, more on a person)
    keys[2]['leanMin'] = -40
A = [prep('AKA', P) for P in bounce(40, 0, 0, .0)]
A += [prep('AKA', P) for P in bounce(6, 0, .22, .0, 6)]                          # slide back out of AO's punch
A += move(rigA, 'AKA', 'combo_kick', .22, head_kick, dys=[.22, .2, .12, .12, .15, .2])  # jodan mawashi-geri counter from where it slid back (impact at frame 54)
A += [prep('AKA', P) for P in bounce(20, .2, 0, .25)]
B = [prep('AO', P) for P in bounce(36, 0, -.6, .5)]                              # AO creeps in
B += move(rigB, 'AO', 'punch2', -.6, dys=[-.6, -.8, -1.1, -1.3, -1.3, -1.3])                                            # gyaku-zuki entry (impact frame 44), falls short as AKA slides back
flinch = MV.stance(eyes='hurt', mouth='open', root=(0, 0, 0), pelvisRot=(0, 0, -45), head=(-12, 14, 4), chest=(0, 0, -12), weight=.4,
                   handL=(.2, -.5, .35), handR=(-.05, -.25, .4), ties=12)
B += tweens(rigB, 'AO', prep('AO', G(-1.3)), prep('AO', at(flinch, -1.2)), 5, 'out', 'ao-flinch')
B += tweens(rigB, 'AO', prep('AO', at(flinch, -1.2)), prep('AO', G(-.9)), 12, 'io', 'ao-recover')
n = max(len(A), len(B))
B += [prep('AO', P) for P in bounce(n - len(B), -.9, 0, .1)]
A = A[:n]
# rei: both stand in musubi-dachi (heels together), hands at the sides, and bow
READY = MV.stance(root=(0, 0, 0), footL=(.12, -.08, MV.GROUND), footR=(-.12, .08, MV.GROUND), footLRot=(0, 0, 25), footRRot=(0, 0, -25),
                  pelvis=(0, 0, -.06), pelvisRot=(0, 0, 0), chest=(0, 0, 0), handL=(.5, -.22, -.9), handR=(-.5, -.22, -.9), weight=.5)  # open hands at the thighs
BOW = dict(READY, pelvisRot=(26, 0, 0), spine=(8, 0, 0), head=(6, 0, 0), eyes='happy')
for nm, rig, L in (('AKA', rigA, A), ('AO', rigB, B)):
    L += tweens(rig, nm, prep(nm, G(0)), prep(nm, READY), 12, 'io', f'{nm}-ready')
    L += tweens(rig, nm, prep(nm, READY), prep(nm, BOW), 9, 'io', f'{nm}-bow')
    L += [L[-1]] * 6
    L += tweens(rig, nm, prep(nm, BOW), prep(nm, READY), 9, 'io', f'{nm}-up')
    L += [L[-1]] * 8

# ---------- solve every frame, key it, render ----------
def key_fighter(fig, f, P):
    rig, parts, expr = fig; x, yaw, _ = BASE[rig.name]
    rig.location = (x, 0, 0); rig.rotation_euler = (0, 0, math.radians(yaw))
    rig.keyframe_insert('location', frame=f); rig.keyframe_insert('rotation_euler', frame=f)
    for pb in rig.pose.bones:
        pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f); pb.keyframe_insert('scale', frame=f)
    for key, objs in expr.items():
        on = key in ('eyes_' + P['eyes'], 'mouth_' + P['mouth'])
        for o in objs: o.hide_render = not on; o.keyframe_insert('hide_render', frame=f)
N = min(len(A), len(B)); bad = 0
for f in range(N):
    for fig, L, nm in ((AKA, A, 'aka'), (AO, B, 'ao')):
        P = dict(L[f], _first=(f == 0)); P = MV.apply_pose(fig[0], P, f'{nm}-f{f:03d}')
        bad += bool(P['_solved']['bad'])
        key_fighter(fig, f + 1, P)
MV.constant_keys([rigA, rigB] + [o for fig in (AKA, AO) for objs in fig[2].values() for o in objs])
scene.frame_start, scene.frame_end = 1, N
print('KB-KUMITE frames', N, 'frames with a broken rule', bad, flush=True)
os.makedirs(os.path.join(OUT, 'frames'), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'kumite.blend'))
MV.kuwahara(scene)
for f in range(1, N + 1):
    scene.frame_set(f); scene.render.filepath = os.path.join(OUT, 'frames', f'f{f:04d}.png'); bpy.ops.render.render(write_still=True)
    print('KB-FRAME', f, flush=True)
print('KB-DONE', N, flush=True)
