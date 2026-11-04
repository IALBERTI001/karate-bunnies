# Unit tests for the movement rules: python3 kbmove_test.py
import kbmove as KM, math
# two_bone: joint at the right distances, bends toward the hint, never stretches
j, t, n = KM.two_bone((0, 0, 1), (0, -.5, 0), .6, .6, (0, -1, 0))
assert abs(KM.length(KM.sub(j, (0, 0, 1))) - .6) < 1e-6 and abs(KM.length(KM.sub(t, j)) - .6) < 1e-6
assert j[1] < -.25, j  # knee forward, toward the toes
j, t, n = KM.two_bone((0, 0, 1), (0, -5, 0), .6, .6, (0, 0, 1))
assert KM.length(KM.sub(t, (0, 0, 1))) <= 1.2 + 1e-6  # out of reach: pulled in, not stretched
# balance
assert KM.centre_of_gravity([((0, 0, 0), 1), ((2, 0, 0), 1)]) == (1, 0, 0)
# sinking keeps a planted foot reachable with a soft knee
s = KM.sink_needed((0, 0, 1.3), (0, -.4, 0), 1.2, .96)
assert abs(math.hypot(.4, 1.3 - s) - 1.2 * .96) < 1e-6
assert abs(KM.knee_bend_deg((0, 0, 2), (0, 0, 1), (0, 0, 0))) < 1e-6
# frame and move checks catch what the user flagged
f = dict(com_err=.2, com_tol=.06, ground=.15, single=True, hip_foot=80,
         legs=dict(L=dict(planted=True, ankle=(0, 0, .15), bend=2, knee_toe=50)))
bad = KM.check_frame(f); assert len(bad) == 4, bad
assert KM.check_move("punch", [dict(hip_yaw=-55, chest_yaw=0, weight=.5), {}, dict(hip_yaw=-55, chest_yaw=0, weight=.5)])
assert not KM.check_move('punch', [dict(hip_yaw=-55, chest_yaw=0, weight=.45), {}, dict(hip_yaw=-16, chest_yaw=10, weight=.7)])
print('kbmove ok')
# kick structure: fold -> snap -> re-chamber, roundhouse finishes past the target on the ball of the foot
f = lambda **k: dict(dict(hip_yaw=0, chest_yaw=0, weight=1, support_yaw=0, lean=0, kick_bend=0, heel=0, strike_z=None), **k)
good = [f(kick_bend=150, support_yaw=30), f(kick_bend=10, hip_yaw=85, support_yaw=135, heel=25, lean=-30, strike_z=2.45), f(kick_bend=140, hip_yaw=55), f()]
assert KM.check_move('roundhouse', good) == []
bad = [f(kick_bend=60), f(kick_bend=10, hip_yaw=40, lean=-5, strike_z=2.4), f(kick_bend=20, hip_yaw=50), f()]
assert len(KM.check_move('roundhouse', bad)) == 8
print('kick rules ok')
