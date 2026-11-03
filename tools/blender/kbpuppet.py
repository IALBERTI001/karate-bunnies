# Karate Bunnies 3D puppet: one bunny model built from soft shapes, posed by joint numbers, rendered in the game's
# cel style (cream fur, material-green gi, black belt, brown ink lines). Used by render_frames.py inside Blender 5.x.
# The gi stays the game's material green so the recolour shader, piping, prints and patches keep working.
import bpy, math
from mathutils import Vector, Matrix, Euler

def hexc(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c] + [1]

def _toon(name, base, shadow, light=None):
    m = bpy.data.materials.new(name); nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); dif = nt.nodes.new('ShaderNodeBsdfDiffuse')
    s2r = nt.nodes.new('ShaderNodeShaderToRGB'); ramp = nt.nodes.new('ShaderNodeValToRGB'); em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(dif.outputs[0], s2r.inputs[0]); nt.links.new(s2r.outputs[0], ramp.inputs[0])
    # Painted look: a soft light-to-shadow gradient (not hard cel bands) and a faint brush grain over the colour.
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 26; noise.inputs['Detail'].default_value = 3
    grain = nt.nodes.new('ShaderNodeMapRange'); grain.inputs['To Min'].default_value = .955; grain.inputs['To Max'].default_value = 1.045
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1
    nt.links.new(noise.outputs['Fac'], grain.inputs['Value']); nt.links.new(ramp.outputs[0], mul.inputs['A'])
    nt.links.new(grain.outputs['Result'], mul.inputs['B']); nt.links.new(mul.outputs['Result'], em.inputs[0]); nt.links.new(em.outputs[0], out.inputs[0])
    cr = ramp.color_ramp; cr.interpolation = 'LINEAR'
    cr.elements[0].position = .06; cr.elements[0].color = hexc(shadow)
    cr.elements[1].position = .5; cr.elements[1].color = hexc(base)
    if light: cr.elements.new(.97).color = hexc(light)
    return m

def _flat(name, col):
    m = bpy.data.materials.new(name); nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    em.inputs[0].default_value = hexc(col); nt.links.new(em.outputs[0], out.inputs[0]); return m

M = {}
def materials():
    if M: return M
    M.update(FUR=_toon('fur', '#f8e7d8', '#e3c4b0', '#fff6ee'), GI=_toon('gi', '#5fae78', '#3f8458', '#72c189'),
             BELT=_toon('belt', '#2b2523', '#151110'), PINK=_toon('pink', '#f7a596', '#e5877b'),
             NOSE=_toon('nose', '#f08f8f', '#d9706f'), EYE=_toon('eye', '#3a1d10', '#24110a'),
             IRIS=_toon('iris', '#8a4a24', '#6b3519'), WHITE=_flat('shine', '#ffffff'), INK=_flat('ink', '#4a3226'),
             BLUSH=_flat('blush', '#f9c4bd'), MOUTH=_toon('mouth', '#9c3b3b', '#7a2a2a'), TONGUE=_toon('tongue', '#f28b8b', '#d96e6e'),
             M_NONE=_flat('m_none', '#000000'), M_BELT=_flat('m_belt', '#ff0000'), M_BAND=_flat('m_band', '#00ff00'),
             M_LEGS=_flat('m_legs', '#0000ff'))
    return M

# Default pose: the guard stance of the idle sprites. Angles in degrees, positions in model units (feet at z=0,
# ear tips near z=4). Model space: the bunny faces -Y, +X is its left, Z is up.
DEFAULT = dict(
    hip=(0, 0, 0),            # pelvis offset (crouch is negative z)
    pelvis=(0, 0, 0),         # pelvis pitch (forward +), roll, yaw
    torso=(0, 0, 0),          # lean forward +, side bend (to its left +), twist (to its left +)
    head=(0, 0, 0),           # nod down +, tilt (to its left +), turn (to its left +)
    handL=(.36, -.68, .38), handR=(-.36, -.68, .38),   # fists, torso-local, relative to the pelvis
    footL=(.33, -.02, -.8), footR=(-.33, -.02, -.8),   # ankles, pelvis-local
    eyes='open', mouth='smile', ears=0, ties=0, blush=1,
    root=(0, 0, 0), rootRot=(0, 0, 0),  # whole-body offset and rotation (pitch back +, roll, spin)
)

def _mat(loc=(0, 0, 0), rot=None, scale=(1, 1, 1)):
    m = Matrix.Translation(Vector(loc))
    if rot is not None: m = m @ (rot.to_4x4() if hasattr(rot, 'to_4x4') else rot)
    return m @ Matrix.Diagonal(Vector(scale)).to_4x4()

def _rot(deg):  # (pitch about X, roll about Y, yaw about Z) in degrees
    p, r, y = [math.radians(a) for a in deg]
    return (Matrix.Rotation(y, 3, 'Z') @ Matrix.Rotation(r, 3, 'Y') @ Matrix.Rotation(p, 3, 'X'))

def _ik(a, target, l1, l2, pole, stretch=1.0):
    a, t = Vector(a), Vector(target); d = t - a; u = d.normalized()
    k = min(max(d.length / (l1 + l2), 1.0), stretch); l1, l2 = l1 * k, l2 * k  # cartoon stretch to reach
    dist = min(d.length, (l1 + l2) * .999)
    x = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist); h = math.sqrt(max(l1 * l1 - x * x, 0))
    p = Vector(pole); p = (p - u * p.dot(u)); p = p.normalized() if p.length > 1e-6 else Vector((0, 0, -1))
    return a + u * x + p * h, a + u * dist

class Builder:
    def __init__(self, root):
        self.root = root; self.objs = []
    def _put(self, o, mat, mask, matrix, smooth=True):
        o.data.materials.append(mat); o.parent = self.root; o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = matrix; o['mask'] = mask
        if smooth and o.type == 'MESH':
            for p in o.data.polygons: p.use_smooth = True
        self.objs.append(o); return o
    def ball(self, matrix, mat, mask='none', segs=40):
        me = bpy.data.meshes.new('ball'); import bmesh; bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2, radius=1); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new('ball', me); bpy.context.scene.collection.objects.link(o)
        return self._put(o, mat, mask, matrix)
    def capsule(self, a, b, r, mat, mask='none', squash=1.0, stretch=.6):
        a, b = Vector(a), Vector(b); d = b - a
        q = d.to_track_quat('Z', 'Y').to_matrix()
        return self.ball(_mat((a + b) / 2, q, (r, r * squash, d.length / 2 + r * stretch)), mat, mask)
    def box(self, a, b, w, t, mat, mask='none'):
        a, b = Vector(a), Vector(b); d = b - a
        me = bpy.data.meshes.new('box'); import bmesh; bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new('box', me); bpy.context.scene.collection.objects.link(o)
        bev = o.modifiers.new('round', 'BEVEL'); bev.width = min(w, t) * .45; bev.segments = 3
        q = d.to_track_quat('Z', 'Y').to_matrix()
        return self._put(o, mat, mask, _mat((a + b) / 2, q, (w, t, d.length)), smooth=False)
    def ring(self, matrix, tube, mat, mask='none'):
        me = bpy.data.meshes.new('ring'); import bmesh; bm = bmesh.new()
        R, n, m = 1.0, 64, 12
        verts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            for j in range(m):
                b = 2 * math.pi * j / m
                verts.append(bm.verts.new(((R + tube * math.cos(b)) * math.cos(a), (R + tube * math.cos(b)) * math.sin(a), tube * math.sin(b))))
        for i in range(n):
            for j in range(m):
                bm.faces.new((verts[i * m + j], verts[((i + 1) % n) * m + j], verts[((i + 1) % n) * m + (j + 1) % m], verts[i * m + (j + 1) % m]))
        bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new('ring', me); bpy.context.scene.collection.objects.link(o)
        return self._put(o, mat, mask, matrix)
    def cone(self, matrix, r1, r2, depth, verts, mat, mask='none', soft=True):
        me = bpy.data.meshes.new('cone'); import bmesh; bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r1, radius2=r2, depth=depth); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new('cone', me); bpy.context.scene.collection.objects.link(o)
        if soft:
            sub = o.modifiers.new('soft', 'SUBSURF'); sub.levels = sub.render_levels = 2
        return self._put(o, mat, mask, matrix, smooth=soft)
    def curve(self, pts, depth, mat, mask='none', cyclic=False, ribbon=0):
        cd = bpy.data.curves.new('c', 'CURVE'); cd.dimensions = '3D'; cd.bevel_depth = depth; cd.bevel_resolution = 3
        if ribbon: cd.extrude = ribbon; cd.twist_mode = 'Z_UP'; cd.resolution_u = 16  # a flat cloth strip
        sp = cd.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1); sp.use_cyclic_u = cyclic
        for bp, co in zip(sp.bezier_points, pts):
            bp.co = co; bp.handle_left_type = bp.handle_right_type = 'AUTO'
        o = bpy.data.objects.new('c', cd); bpy.context.scene.collection.objects.link(o)
        return self._put(o, mat, mask, Matrix.Identity(4), smooth=False)

def build(root, pose=None, decals=None):
    P = dict(DEFAULT); P.update(pose or {}); m = materials(); B = Builder(root)
    def decal(o):
        if decals:
            for c in o.users_collection: c.objects.unlink(o)
            decals.objects.link(o)
        return o
    pelvis = _mat(Vector((0, 0, .95)) + Vector(P['hip']), _rot(P['pelvis']))
    torso = pelvis @ _mat(rot=_rot(P['torso']))
    head = torso @ _mat((0, 0, .8), _rot(P['head']))
    T = lambda f, v: f @ Vector(v)
    rot3 = lambda f: f.to_3x3().normalized()
    # Legs: thigh and shin trousers from the hip to the ankle, big soft feet
    for s, key in ((1, 'footL'), (-1, 'footR')):
        hipj = Vector((s * .3, 0, -.15)); ank = Vector(P[key])
        knee, ank = _ik(hipj, ank, .37, .36, (s * .25, -1, .1), 1.8)
        w = lambda v: T(pelvis, v)
        B.capsule(w(hipj), w(knee), .31, m['GI'], 'legs', stretch=.55)
        B.capsule(w(knee), w(ank), .3, m['GI'], 'legs', stretch=.4)
        shin = (knee - ank).normalized(); fwd = Vector((0, -1, 0)); f = fwd - shin * fwd.dot(shin)
        f = f.normalized() if f.length > .2 else Vector((0, 0, 1)) if shin.y < 0 else Vector((0, -1, 0))
        side = shin.cross(f).normalized(); basis = Matrix((side, f, shin)).transposed()
        B.ball(pelvis @ _mat(ank + f * .16 - shin * .07, basis, (.33, .47, .18)), m['FUR'])
    # Jacket: soft tapered box, skirt flaring over the trousers, round shoulders, the fur V and lapels
    B.cone(torso @ _mat((0, 0, .25), Matrix.Diagonal((1, .78, 1))), .8, .58, .98, 24, m['GI'])
    B.cone(torso @ _mat((0, 0, -.13), Matrix.Diagonal((1, .8, 1))), .84, .76, .32, 24, m['GI'])
    B.ball(torso @ _mat((0, 0, .65), None, (.72, .5, .24)), m['GI'])
    B.cone(torso @ _mat((0, -.43, .6), Euler((math.radians(90), 0, math.radians(180))).to_matrix() @ Matrix.Diagonal((1, 1.3, 1))), .25, 0, .05, 3, m['FUR'], soft=False)
    for s in (1, -1):
        B.box(T(torso, (s * .32, -.42, .73)), T(torso, (-s * .03, -.58, .09)), .11, .06, m['GI'])
    # Belt with knot and hanging ends
    B.ring(torso @ _mat((0, 0, .02), None, (.74, .59, 1.3)), .085, m['BELT'], 'belt')
    B.ball(torso @ _mat((0, -.6, .02), None, (.13, .08, .11)), m['BELT'], 'belt')
    B.box(T(torso, (-.04, -.62, -.03)), T(torso, (-.15, -.66, -.39)), .12, .05, m['BELT'], 'belt')
    B.box(T(torso, (.04, -.62, -.03)), T(torso, (.13, -.66, -.41)), .12, .05, m['BELT'], 'belt')
    # Arms: upper and lower sleeves, big soft fists
    for s, key in ((1, 'handL'), (-1, 'handR')):
        sh = Vector((s * .66, -.02, .53)); hand = Vector(P[key])
        elbow, hand = _ik(sh, hand, .4, .4, (s * 1, .4, -.6), 1.6)
        B.capsule(T(torso, sh), T(torso, elbow), .22, m['GI'], stretch=.5)
        wrist = hand + (elbow - hand).normalized() * .12
        B.capsule(T(torso, elbow), T(torso, wrist), .2, m['GI'], stretch=.5)
        B.ball(torso @ _mat(hand, None, (.22, .19, .2)), m['FUR'])
    # Tail
    B.ball(pelvis @ _mat((0, .64, -.01), None, (.3, .27, .3)), m['FUR'])
    # Head: wide and soft with full cheeks
    B.ball(head @ _mat((0, 0, .45), None, (1.08, .88, .78)), m['FUR'])
    B.ball(head @ _mat((0, -.1, .2), None, (.85, .7, .38)), m['FUR'])
    for s in (1, -1):  # fluffy cheek tufts that widen the face like the painted bunnies
        B.ball(head @ _mat((s * .86, -.32, .26), _rot((0, s * 28, s * 10)), (.3, .22, .15)), m['FUR'])
        B.ball(head @ _mat((s * .8, -.3, .1), _rot((0, s * 48, s * 6)), (.22, .18, .11)), m['FUR'])
    if P['blush']:
        for s in (1, -1): decal(B.ball(head @ _mat((s * .6, -.67, .23), None, (.13, .035, .075)), m['BLUSH']))
    # Eyes
    for s in (1, -1):
        cx, cz = s * .38, .39
        if P['eyes'] == 'open':
            decal(B.ball(head @ _mat((cx, -.775, cz), None, (.22, .07, .26)), m['EYE']))
            decal(B.ball(head @ _mat((cx, -.815, cz - .07), None, (.165, .035, .16)), m['IRIS']))
            decal(B.ball(head @ _mat((cx - .075, -.855, cz + .1), None, (.085, .02, .09)), m['WHITE']))
            decal(B.ball(head @ _mat((cx + .08, -.85, cz - .11), None, (.04, .015, .04)), m['WHITE']))
            decal(B.curve([T(head, (cx - .24, -.77, cz + .14)), T(head, (cx, -.83, cz + .27)), T(head, (cx + .23, -.77, cz + .15))], .02, m['INK']))
        elif P['eyes'] == 'happy':  # closed, smiling arcs
            decal(B.curve([T(head, (cx - .16, -.8, cz - .04)), T(head, (cx, -.84, cz + .08)), T(head, (cx + .16, -.8, cz - .04))], .028, m['INK']))
        elif P['eyes'] == 'hurt':  # squeezed shut > <
            decal(B.curve([T(head, (cx - s * .14, -.8, cz + .1)), T(head, (cx + s * .1, -.84, cz)), T(head, (cx - s * .14, -.8, cz - .1))], .026, m['INK']))
        elif P['eyes'] == 'focus':  # determined: wide open eyes under a slanted brow
            decal(B.ball(head @ _mat((cx, -.775, cz - .02), None, (.21, .07, .23)), m['EYE']))
            decal(B.ball(head @ _mat((cx, -.815, cz - .08), None, (.16, .035, .14)), m['IRIS']))
            decal(B.ball(head @ _mat((cx - .07, -.855, cz + .07), None, (.075, .02, .08)), m['WHITE']))
            decal(B.curve([T(head, (cx + s * .2, -.79, cz + .36)), T(head, (cx - s * .2, -.8, cz + .27))], .026, m['INK']))
    decal(B.ball(head @ _mat((0, -.845, .22), None, (.07, .035, .05)), m['NOSE']))
    if P['mouth'] == 'smile':
        decal(B.curve([T(head, p) for p in [(-.13, -.79, .15), (-.065, -.815, .1), (0, -.82, .15), (.065, -.815, .1), (.13, -.79, .15)]], .013, m['INK']))
    else:  # 'open' or 'shout': a little open mouth with a tongue
        big = 1.5 if P['mouth'] == 'shout' else 1
        decal(B.ball(head @ _mat((0, -.79, .09), None, (.1 * big, .04, .075 * big)), m['MOUTH']))
        decal(B.ball(head @ _mat((0, -.81, .06 - .01 * big), None, (.065 * big, .03, .035 * big)), m['TONGUE']))
    # Ears, tall, leaning out, with optional droop backwards
    for s in (1, -1):
        ear = head @ _mat((s * .34, .05, .74), _rot((-P['ears'], s * 17, s * 8)))
        B.ball(ear @ _mat((s * .04, 0, .68), None, (.4, .16, .84)), m['FUR'])
        decal(B.ball(ear @ _mat((s * .05, -.13, .66), None, (.26, .07, .66)), m['PINK']))
    # Headband: wide band, knot at the back on its right, two broad ribbons that can swing
    B.ring(head @ _mat((0, 0, .8), _rot((-3, 0, 0)), (1.0, .82, 1.55)), .1, m['GI'], 'band')
    knot = Vector((-.62, .55, .8)); B.ball(head @ _mat(knot, None, (.17, .14, .16)), m['GI'], 'band')
    sw = _rot((0, 0, P['ties'])); fl = math.radians(P['ties'])
    for path, w in (([(-.05, .02, .02), (-.45, .1, .06), (-.9, .14, -.06 + .25 * math.sin(fl)), (-1.25, .16, -.12)], .17),
                    ([(-.05, .04, -.04), (-.36, .14, -.2), (-.7, .2, -.42 + .2 * math.sin(fl)), (-.95, .22, -.62)], .15)):
        B.curve([T(head, knot + sw @ Vector(q)) for q in path], 0, m['GI'], 'band', ribbon=w)
    return B.objs

def setup_scene(res=512, ortho=5.0, center=(0, 2.15), line=2.2):
    scene = bpy.context.scene
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try: scene.render.engine = eng; break
        except TypeError: pass
    scene.view_settings.view_transform = 'Standard'
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = res
    scene.render.use_freestyle = True; scene.render.line_thickness_mode = 'ABSOLUTE'; scene.render.line_thickness = line
    decals = bpy.data.collections.new('Decals'); scene.collection.children.link(decals)
    vl = scene.view_layers[0]; fs = vl.freestyle_settings
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new('ink')
    ls.select_by_visibility = True; ls.select_silhouette = True; ls.select_border = True; ls.select_crease = False
    ls.select_by_collection = True; ls.collection = decals; ls.collection_negation = 'EXCLUSIVE'
    ls.linestyle = ls.linestyle or bpy.data.linestyles.new('ink'); ls.linestyle.color = hexc('#5a3a28')[:3]; ls.linestyle.thickness = line
    cal = ls.linestyle.thickness_modifiers.new('brush', 'CALLIGRAPHY'); cal.thickness_min = line * .45; cal.thickness_max = line * 1.15; cal.orientation = 1.0
    ls.linestyle.use_chaining = True; ls.linestyle.chaining = 'PLAIN'
    world = bpy.data.worlds.new('w'); scene.world = world
    world.node_tree.nodes['Background'].inputs[1].default_value = .35
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5
    so = bpy.data.objects.new('sun', sun); scene.collection.objects.link(so); so.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-35))
    cam = bpy.data.cameras.new('cam'); cam.type = 'ORTHO'; cam.ortho_scale = ortho
    co = bpy.data.objects.new('cam', cam); scene.collection.objects.link(co); scene.camera = co
    co.location = (center[0], -14, center[1]); co.rotation_euler = (math.radians(90), 0, 0)
    root = bpy.data.objects.new('Bunny', None); scene.collection.objects.link(root)
    return scene, root, decals

def place_root(root, pose, yaw):
    P = dict(DEFAULT); P.update(pose or {})
    p, r, s = [math.radians(a) for a in P['rootRot']]
    root.matrix_world = (Matrix.Translation(Vector(P['root'])) @ Matrix.Rotation(math.radians(yaw), 4, 'Z')
                         @ Matrix.Translation((0, 0, 1.0)) @ Matrix.Rotation(-p, 4, 'X') @ Matrix.Rotation(r, 4, 'Y')
                         @ Matrix.Rotation(s, 4, 'Z') @ Matrix.Translation((0, 0, -1.0)))

MASK_COLORS = {'belt': 'M_BELT', 'band': 'M_BAND', 'legs': 'M_LEGS'}
def to_mask(objs):
    m = materials()
    for o in objs:
        o.data.materials.clear(); o.data.materials.append(m[MASK_COLORS.get(o.get('mask'), 'M_NONE')])

def clear(objs):
    for o in objs:
        data = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if data and data.users == 0:
            (bpy.data.meshes if isinstance(data, bpy.types.Mesh) else bpy.data.curves).remove(data)
