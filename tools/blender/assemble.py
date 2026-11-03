# Packs rendered puppet frames into game atlases: python3 assemble.py <frames dir> <out dir>
# Writes bunny3d-<name>.png (sprites), parts-pass-<n>.png (rgb masks: red belt, green headband, blue trousers),
# belt-mask-<n>.png (white belt) and atlases.json (the atlas and animation entries for assets/animations.json).
# Every fight atlas starts with the same standing reference frame, so all atlases share one scale in game.
import sys, os, json
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
GROUPS = [
    ('moves', ['idle', 'walk_f', 'walk_b', 'guard', 'punch1', 'punch2']),
    ('kicks', ['combo_kick', 'spin_kick', 'low_kick', 'high_kick', 'front_kick']),
    ('reactions', ['hit', 'knockback', 'launch', 'landing', 'bow', 'victory', 'recover']),
]
ANIM_ORDER = ['idle', 'walk_f', 'walk_b', 'guard', 'punch1', 'punch2', 'combo_kick', 'spin_kick', 'low_kick', 'high_kick',
              'front_kick', 'hit', 'knockback', 'launch', 'landing', 'bow', 'victory', 'recover']
PAD = 8
def load(fid):
    c = Image.open(os.path.join(src, 'color', fid + '.png')).convert('RGBA'); m = Image.open(os.path.join(src, 'mask', fid + '.png')).convert('RGBA')
    a = np.asarray(c)[..., 3]; ys, xs = np.nonzero(a > 8)
    box = (max(0, xs.min() - PAD), max(0, ys.min() - PAD), min(c.width, xs.max() + 1 + PAD), min(c.height, ys.max() + 1 + PAD))
    return c.crop(box), m.crop(box)
def legs_x(m):
    b = np.asarray(m)[..., 2] > 127; xs = np.nonzero(b)[1]
    return xs.mean() if xs.size else m.width / 2
def pack(name, ids, cols, spin=False):
    crops = [load(i) for i in ids]
    cxs = [legs_x(m) if spin else c.width / 2 for c, m in crops]
    cw = int(max(2 * max(cx, c.width - cx) for (c, _), cx in zip(crops, cxs))) + 2; ch = max(c.height for c, _ in crops); rows = (len(ids) + cols - 1) // cols
    sheet = Image.new('RGBA', (cw * cols, ch * rows), (0, 0, 0, 0)); mask = Image.new('RGB', sheet.size, (0, 0, 0))
    for k, (c, m) in enumerate(crops):
        x = (k % cols) * cw + int(round(cw / 2 - cxs[k])); y = (k // cols) * ch + (ch - c.height)  # bottom-aligned in the cell
        sheet.alpha_composite(c, (x, y))
        mm = np.asarray(m).astype(np.float32) / 255; rgb = (mm[..., :3] * mm[..., 3:4] * 255).astype(np.uint8)
        mask.paste(Image.fromarray(rgb), (x, y))
    return sheet, mask, cols, rows
atlases, anims = [], {}
for gi, (name, group) in enumerate(GROUPS):
    ids = ['idle-0'] + [f'{a}-{i}' for a in group for i in range(4)]
    cols = 5 if len(ids) <= 25 else 6
    ids += ['idle-0'] * (-len(ids) % cols)  # the game expects a pose in every cell
    sheet, mask, cols, rows = pack(name, ids, cols)
    sheet.save(os.path.join(out, f'bunny3d-{name}.png'), optimize=True)
    mask.save(os.path.join(out, f'parts-pass-{len(atlases)}.png'), optimize=True)
    belt = (np.asarray(mask)[..., 0] > 127).astype(np.uint8) * 255
    Image.fromarray(belt).save(os.path.join(out, f'belt-mask-{len(atlases)}.png'), optimize=True)
    for k, a in enumerate(group): anims[a] = (len(atlases), 1 + k * 4)
    atlases.append(dict(file=f'bunny3d-{name}.png', columns=cols, rows=rows, passes=True))
    print(name, sheet.size, cols, rows)
ids = [f'turn-{i}' for i in range(8)]
sheet, mask, cols, rows = pack('turnaround', ids, 4, spin=True)
sheet.save(os.path.join(out, 'bunny3d-turnaround.png'), optimize=True); mask.save(os.path.join(out, f'parts-pass-{len(atlases)}.png'), optimize=True)
Image.fromarray((np.asarray(mask)[..., 0] > 127).astype(np.uint8) * 255).save(os.path.join(out, f'belt-mask-{len(atlases)}.png'), optimize=True)
turn = len(atlases); atlases.append(dict(file='bunny3d-turnaround.png', columns=4, rows=2, turnaround=True, passes=True))
print('turnaround', sheet.size)
json.dump(dict(atlases=atlases, anims={a: anims[a] for a in ANIM_ORDER}, turnaround=turn), open(os.path.join(out, 'atlases.json'), 'w'), indent=1)
