# Movement governor: the rules every Karate Bunnies pose must obey, so movement looks like a real body.
# Pure Python (no Blender) so the rules can be unit-tested: python3 kbmove_test.py
#
# The rules (user, Nov 3 2026: "weight transfer is a big thing for any movement ... the centre of gravity is shifting as
# parts move. That's why the body leans back as a kick goes forward. Pelvis rotation for kicks, torso for punches. It's
# all a transfer of energy."):
#  1. Balance. The centre of gravity (from every body part's mass) stays over the support: over the standing foot on
#     one leg, or at the declared weight split between the feet on two. When a limb reaches out, the body answers:
#     on one leg the trunk leans away (a kick forward = a lean back) and the hips shift; on two legs the hips travel
#     (weight transfer onto the front knee in a punch) and the trunk stays upright.
#  2. Planted feet stay planted. A foot on the ground never lifts because the hips are too high; the body sinks instead.
#  3. Knees. A standing knee is never locked and always tracks its toes. A lifted knee leads the kick (chamber points at
#     the target and above), and turns down in a back kick. Elbows point down and back. Limbs never stretch.
#  4. Energy transfer (ground up). The standing foot pivots with the hips (hips may lead the foot by at most
#     HIP_FOOT_MAX degrees, more would twist the knee); kicks are driven by the pelvis turning, punches by the hips and
#     torso turning; each strike's impact frame shows that turn and the weight shift compared with its load frame.
import math

HIP_FOOT_MAX = 50      # degrees the hips may turn past the standing foot
KNEE_SOFT = .96        # standing knees on two feet: hip-to-ankle at most this share of the leg's length
KNEE_SUPPORT = .975    # standing knee on one leg (tall but never locked)
KNEE_DRIVE = .99      # the driving rear leg of a reverse punch: straight, still not locked
COM_TOL_SINGLE = .06   # how far the centre of gravity may sit from the middle of the standing foot
COM_TOL_DOUBLE = .07
LEAN_RANGE = (-42, 35) # trunk lean the balance rule may use (degrees; negative = back; a back kick hunches forward)

def add(a, b): return tuple(x + y for x, y in zip(a, b))
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def mul(a, k): return tuple(x * k for x in a)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def length(a): return math.sqrt(dot(a, a))
def norm(a):
    l = length(a); return mul(a, 1 / l) if l > 1e-9 else a
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def lerp(a, b, t): return add(a, mul(sub(b, a), t))
def perp(v, axis):  # v without its component along the unit axis
    return sub(v, mul(axis, dot(v, axis)))
def angle(a, b): return math.degrees(math.acos(max(-1, min(1, dot(norm(a), norm(b))))))

def two_bone(hip, target, a, b, hint):
    """Joint position for a two-bone limb from `hip` toward `target` (bone lengths a, b) bending toward `hint`.
    Returns (joint, reached_target, bend_dir). The target is pulled in if out of reach: limbs never stretch."""
    d = sub(target, hip); D = length(d)
    dh = norm(d) if D > 1e-9 else (0, 0, -1)
    D = max(min(D, (a + b) * .9995), abs(a - b) + 1e-4)
    t = add(hip, mul(dh, D))
    n = perp(hint, dh)
    if length(n) < 1e-6: n = perp((0, 0, 1) if abs(dh[2]) < .9 else (0, 1, 0), dh)
    n = norm(n)
    cosA = (a * a + D * D - b * b) / (2 * a * D); sinA = math.sqrt(max(0.0, 1 - cosA * cosA))
    joint = add(hip, add(mul(dh, a * cosA), mul(n, a * sinA)))
    return joint, t, n

def centre_of_gravity(parts):
    """parts: [(point, mass)] -> weighted centre."""
    m = sum(w for _, w in parts); c = (0.0, 0.0, 0.0)
    for p, w in parts: c = add(c, mul(p, w / m))
    return c

def sink_needed(hip, ankle, leg_len, share):
    """How far the hips must drop so a planted ankle is reached with the knee bent to `share` of the leg's length."""
    h = math.hypot(ankle[0] - hip[0], ankle[1] - hip[1]); v = hip[2] - ankle[2]; L = leg_len * share
    if h >= L: return v  # cannot reach by sinking alone; sink to the ankle's height (caller shortens the step)
    return max(0.0, v - math.sqrt(L * L - h * h))

def knee_bend_deg(hip, knee, ankle):
    """0 = straight (locked) leg."""
    return 180 - angle(sub(hip, knee), sub(ankle, knee))

def check_frame(f):
    """f: measured frame dict -> list of rule violations (empty = the pose obeys the rules)."""
    bad = []
    if f['com_err'] > f['com_tol'] + 1e-3: bad.append(f"balance: centre of gravity {f['com_err']:.2f} from the support")
    for L, leg in f['legs'].items():
        if leg['planted']:
            if abs(leg['ankle'][2] - f['ground']) > .02: bad.append(f'{L} planted foot off the ground')
            if leg['bend'] < (4 if leg.get('drive') else 8): bad.append(f"{L} standing knee locked ({leg['bend']:.0f} deg)")
            if leg['knee_toe'] > 30: bad.append(f"{L} knee does not track the toes ({leg['knee_toe']:.0f} deg)")
    if f.get('single') and abs(f['hip_foot']) > HIP_FOOT_MAX + 1: bad.append(f"hips turned {f['hip_foot']:.0f} deg past the standing foot (knee twist)")
    return bad

def check_move(kind, frames):
    """Energy transfer and kick structure between a move's frames. frames: dicts with hip_yaw, chest_yaw, weight (share on
    the lead foot, or 1 for one-legged), support_yaw, lean, kick_bend (knee bend of the lifted leg), heel (standing heel
    lift, degrees), strike_z (target height)."""
    a, b = frames[0], frames[2 if kind == 'punch' else 1]; bad = []
    if kind == 'punch':
        turn = abs((b['hip_yaw'] + b['chest_yaw']) - (a['hip_yaw'] + a['chest_yaw']))
        if turn < 12: bad.append(f'punch has no torso rotation ({turn:.0f} deg)')
        if b['weight'] - a['weight'] < .08: bad.append('punch has no weight transfer onto the front foot')
        return bad
    # every kick: fold -> snap -> re-chamber -> land
    if a['kick_bend'] < 110: bad.append(f"chamber is not folded (knee {a['kick_bend']:.0f} deg, needs 110+)")
    if frames[2]['kick_bend'] < 100: bad.append(f"no re-chamber: the leg drops instead of whipping back ({frames[2]['kick_bend']:.0f} deg)")
    if b['kick_bend'] > 60: bad.append(f"impact leg not extended ({b['kick_bend']:.0f} deg bend)")
    z = b.get('strike_z')
    if z is not None:
        if z >= 2.3 and b['lean'] > -22: bad.append(f"head-height kick without the trunk dropping away ({b['lean']:.0f} deg)")
        if z < 1.0 and b['lean'] < -18: bad.append(f"low kick leans too far ({b['lean']:.0f} deg)")
    if kind in ('roundhouse', 'low'):
        if b['heel'] <= 0: bad.append('standing foot does not rise onto the ball to pivot')
        if abs(b['support_yaw'] - a['support_yaw']) < 25: bad.append('standing foot does not pivot')
    if kind == 'roundhouse':
        if b['hip_yaw'] < 75: bad.append(f"hips stop short: the belly must face past the target ({b['hip_yaw']:.0f} deg)")
        if b['support_yaw'] < 120: bad.append(f"standing heel does not face the target ({b['support_yaw']:.0f} deg)")
        if frames[2]['hip_yaw'] >= b['hip_yaw']: bad.append('hips do not come back in before landing')
    elif kind == 'low':
        if b['hip_yaw'] - a['hip_yaw'] < 30: bad.append('low kick has no pelvis rotation')
    elif kind == 'front':
        if b['lean'] > -4: bad.append('front kick: trunk does not counter-lean behind the hip thrust')
    return bad
