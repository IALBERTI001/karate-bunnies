# Writes poses.json: the shop turnaround (8 views) and the 18 fight animations (4 frames each) for render_frames.py.
# Fighters face screen-right at a three-quarter angle (yaw 55). Run: python3 poses.py > poses.json
import json
YAW = 40          # stances and reactions: a friendly three-quarter view like the painted sprites
ATTACK_YAW = 55   # punches and kicks turn further side-on so the reach reads
GROUND = .15  # ankle height when standing

def foot(x, y, z=GROUND, hipz=0):  # ankle in pelvis-local space from a model-space position
    return (x, y, z - .95 - hipz)

def stance(hipz=-.08, spread=.28, **kw):
    p = dict(hip=(0, 0, hipz), footL=foot(.32, -spread, hipz=hipz), footR=foot(-.3, spread * .9, hipz=hipz))
    p.update(kw); return p

GUARD_L, GUARD_R = (.3, -.66, .45), (-.36, -.62, .36)
anims = []
def anim(name, frames): anims.append((name, frames))

anim('idle', [stance(-.06, handL=GUARD_L, handR=GUARD_R, ties=0),
              stance(-.09, handL=GUARD_L, handR=GUARD_R, ties=6, eyes='happy', head=(4, 0, 0)),
              stance(-.11, handL=(.3, -.66, .42), handR=(-.36, -.62, .33), ties=10, head=(3, 0, 0)),
              stance(-.08, handL=GUARD_L, handR=GUARD_R, ties=4)])
def walk(sign):
    out = []
    for i, ph in enumerate((0, 1, 2, 3)):
        a = [.28, 0, -.28, 0][ph] * sign; lift = [0, .14, 0, .14][ph]; hipz = [-.08, -.03, -.08, -.03][ph]
        fl = foot(.3, -a, GROUND + (lift if ph == 3 else 0), hipz); fr = foot(-.3, a, GROUND + (lift if ph == 1 else 0), hipz)
        out.append(dict(hip=(0, 0, hipz), footL=fl, footR=fr, handL=GUARD_L, handR=GUARD_R, torso=(6 * sign, 0, 0), ties=[4, 10, 4, 10][ph] * sign, mouth='smile'))
    return out
anim('walk_f', walk(1))
anim('walk_b', walk(-1))
G2L, G2R = (.26, -.6, .72), (-.3, -.62, .6)
anim('guard', [stance(-.12, handL=G2L, handR=G2R, eyes='focus', head=(8, 0, 0)),
               stance(-.14, handL=G2L, handR=G2R, eyes='focus', head=(9, 0, 0), ties=5),
               stance(-.15, handL=(.26, -.6, .68), handR=(-.3, -.62, .57), eyes='focus', head=(9, 0, 0), ties=8),
               stance(-.13, handL=G2L, handR=G2R, eyes='focus', head=(8, 0, 0), ties=4)])
anim('punch1', [stance(-.1, handL=(.32, -.5, .45), handR=GUARD_R, torso=(4, 0, -12), eyes='focus'),
                stance(-.1, handL=(.2, -1.12, .52), handR=(-.36, -.5, .36), torso=(10, 0, 18), eyes='focus', mouth='open', ties=-8),
                stance(-.1, handL=(.22, -1.08, .5), handR=(-.36, -.5, .36), torso=(9, 0, 15), eyes='focus', mouth='smile', ties=-4),
                stance(-.09, handL=GUARD_L, handR=GUARD_R, torso=(3, 0, 4))])
anim('punch2', [stance(-.1, handL=GUARD_L, handR=(-.36, -.45, .36), torso=(4, 0, 12), eyes='focus'),
                stance(-.1, handL=(.32, -.5, .45), handR=(-.1, -1.15, .5), torso=(10, 0, -22), eyes='focus', mouth='shout', ties=-8),
                stance(-.1, handL=(.32, -.5, .45), handR=(-.12, -1.1, .48), torso=(9, 0, -18), eyes='focus', mouth='open', ties=-4),
                stance(-.09, handL=GUARD_L, handR=GUARD_R, torso=(3, 0, -4))])
def kick(target, chamber, lean=-10, high=False):
    # The far leg kicks, so the leg reaches out past the body toward the opponent instead of crossing in front of it.
    base = dict(hip=(0, 0, -.02), footR=foot(-.3, .1, hipz=-.02), handL=(.36, -.55, .45), handR=(-.42, -.4, .3), eyes='focus')
    return [dict(base, footL=foot(.25, .05, .4, -.02), torso=(lean * .3, 0, 0)),
            dict(base, footL=chamber, torso=(lean * .6, 0, 6)),
            dict(base, footL=target, torso=(lean, 0, 12), mouth='shout', ties=-10, handL=(.6, -.1, .4) if high else base['handL'], handR=(-.42, -.3, .55) if high else base['handR']),
            dict(base, footL=chamber, torso=(lean * .5, 0, 4), ties=-4)]
anim('combo_kick', kick((.15, -1.2, -.12), (.2, -.5, -.2)))
spin = []
for i, deg in enumerate((90, 180, 360, 360)):
    p = dict(hip=(0, 0, -.04), footL=foot(.25, 0, hipz=-.04), footR=foot(-.25, .05, hipz=-.04), handL=(.5, -.4, .4), handR=(-.5, -.35, .4),
             rootRot=(0, 0, deg), eyes='focus', ties=-14)
    if i == 1: p.update(footL=(.3, .2, -.55))
    if i == 2: p.update(footL=(.15, -1.25, .1), torso=(-16, 0, 8), mouth='shout', ties=-18)
    if i == 3: p.update(footL=(.2, -.5, -.25), torso=(-6, 0, 0), ties=-8)
    spin.append(p)
anim('spin_kick', spin)
anim('low_kick', kick((.18, -1.15, -.6), (.22, -.45, -.42), lean=6))
anim('high_kick', kick((.05, -.8, .85), (.2, -.55, .1), lean=-24, high=True))
anim('front_kick', kick((.12, -1.2, .22), (.22, -.55, -.05), lean=-14))
anim('hit', [stance(-.08, handL=(.34, -.5, .55), handR=(-.36, -.45, .5), torso=(-14, 0, 0), head=(-12, 0, 0), eyes='hurt', mouth='open', ears=18, root=(0, .15, 0)),
             stance(-.1, handL=(.36, -.45, .6), handR=(-.4, -.4, .5), torso=(-20, 0, 0), head=(-16, 0, 0), eyes='hurt', mouth='open', ears=26, ties=14, root=(0, .3, 0)),
             stance(-.1, handL=(.34, -.55, .5), handR=(-.38, -.5, .42), torso=(-10, 0, 0), head=(-6, 0, 0), eyes='hurt', mouth='smile', ears=14, ties=8, root=(0, .2, 0)),
             stance(-.08, handL=GUARD_L, handR=GUARD_R, torso=(-2, 0, 0), ears=4)])
kb = []
for i, (pitch, lift) in enumerate(((22, .2), (48, .6), (72, .8), (86, .4))):
    kb.append(dict(hip=(0, 0, 0), footL=foot(.3, -.4, .35), footR=foot(-.3, -.5, .2), handL=(.6, -.2, .7), handR=(-.6, -.15, .75),
                   rootRot=(pitch, 0, 0), root=(0, .2 + i * .25, lift), eyes='hurt', mouth='open', ears=30, ties=20))
anim('knockback', kb)
launch = []
for i, z in enumerate((.3, .8, 1.1, .9)):
    launch.append(dict(hip=(0, 0, .05), footL=(.3, -.25, -.5), footR=(-.3, .05, -.55), handL=(.5, -.3, .9), handR=(-.5, -.25, .85),
                       root=(0, 0, z), rootRot=(10 + 6 * i, 0, 0), eyes='hurt' if i < 2 else 'open', mouth='open', ears=20, ties=16))
anim('launch', launch)
anim('landing', [dict(stance(-.32, spread=.32), handL=(.5, -.4, .2), handR=(-.5, -.4, .15), torso=(18, 0, 0), eyes='focus', ears=-8, ties=-10),
                 dict(stance(-.24, spread=.3), handL=(.4, -.5, .3), handR=(-.45, -.45, .25), torso=(12, 0, 0), eyes='focus', ties=-6),
                 dict(stance(-.14), handL=GUARD_L, handR=GUARD_R, torso=(5, 0, 0)),
                 stance(-.08, handL=GUARD_L, handR=GUARD_R)])
SIDES = dict(handL=(.62, -.12, -.12), handR=(-.62, -.12, -.12))
anim('bow', [dict(hip=(0, 0, 0), footL=foot(.22, 0), footR=foot(-.22, 0), **SIDES, eyes='open'),
             dict(hip=(0, 0, 0), footL=foot(.22, 0), footR=foot(-.22, 0), **SIDES, torso=(25, 0, 0), head=(12, 0, 0), eyes='happy'),
             dict(hip=(0, 0, -.02), footL=foot(.22, 0, hipz=-.02), footR=foot(-.22, 0, hipz=-.02), handL=(.55, -.25, -.1), handR=(-.55, -.25, -.1), torso=(42, 0, 0), head=(16, 0, 0), eyes='happy', ears=-10),
             dict(hip=(0, 0, 0), footL=foot(.22, 0), footR=foot(-.22, 0), **SIDES, torso=(10, 0, 0), eyes='happy', mouth='open')])
anim('victory', [stance(-.15, handL=(.4, -.5, .2), handR=(-.4, -.5, .2), eyes='happy', mouth='open'),
                 dict(hip=(0, 0, 0), footL=(.28, 0, -.65), footR=(-.28, 0, -.7), handR=(-.45, -.2, 1.35), handL=(.5, -.45, .4), root=(0, 0, .45), eyes='happy', mouth='shout', ears=-6, ties=18),
                 dict(hip=(0, 0, 0), footL=(.28, 0, -.65), footR=(-.28, .1, -.62), handR=(-.4, -.25, 1.4), handL=(.45, -.5, .45), root=(0, 0, .3), eyes='happy', mouth='open', ties=12),
                 dict(stance(-.04), handR=(-.4, -.25, 1.3), handL=(.42, -.55, .4), eyes='happy', mouth='open', ties=6)])
SIT = -.62
anim('recover', [dict(hip=(0, -.05, SIT), footL=foot(.32, -.6, hipz=SIT), footR=foot(-.32, -.55, hipz=SIT), handL=(.6, .05, -.2), handR=(-.6, .05, -.2), torso=(-8, 0, 0), eyes='hurt', mouth='open', ears=24),
                 dict(hip=(0, 0, -.45), footL=foot(.3, -.35, hipz=-.45), footR=foot(-.3, .1, hipz=-.45), handL=(.45, -.45, -.15), handR=(-.5, -.3, -.25), torso=(22, 0, 0), eyes='open', ears=14),
                 dict(stance(-.2), handL=(.4, -.5, .25), handR=(-.45, -.45, .2), torso=(10, 0, 0), ears=6),
                 dict(stance(-.08), handL=GUARD_L, handR=GUARD_R, eyes='happy')])

frames = [dict(id=f'turn-{i}', yaw=i * 45, pose=dict(handL=GUARD_L, handR=GUARD_R)) for i in range(8)]
for name, fs in anims:
    assert len(fs) == 4, name
    yaw = ATTACK_YAW if name in ('punch1', 'punch2', 'combo_kick', 'spin_kick', 'low_kick', 'high_kick', 'front_kick') else YAW
    frames += [dict(id=f'{name}-{i}', yaw=yaw, pose=f) for i, f in enumerate(fs)]
print(json.dumps(frames))
