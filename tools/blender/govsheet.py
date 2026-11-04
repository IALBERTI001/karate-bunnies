# Contact sheet of the moves with the movement rules drawn on: python3 govsheet.py <out dir> <log> <sheet.png>
# Plumb line from the centre of gravity to the floor (green: balanced, red: a rule is broken), the support point
# (white dot), and for kicks the target (ring) and where the striking surface actually lands (dot).
import sys, json, numpy as np
from PIL import Image, ImageDraw
out, log, dst = sys.argv[1:4]
MOVES = ['punch1', 'punch2', 'combo_kick', 'spin_kick', 'high_kick', 'low_kick', 'front_kick']
G = {}
for line in open(log, encoding='utf-8', errors='replace'):
    if line.startswith('KB-GOV '): d = json.loads(line[7:]); G[d['id']] = d
ims = {}; box = None
for m in MOVES:
    for k in range(4):
        im = Image.open(f'{out}/color/{m}-{k}.png').convert('RGBA'); ims[m, k] = im
        a = np.asarray(im)[..., 3]; yy, xx = np.nonzero(a > 8); b = (xx.min(), yy.min(), xx.max(), yy.max())
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
R = ims[MOVES[0], 0].width; px = lambda x, z: (R / 2 + x * R / 8, R / 2 - (z - 2.7) * R / 8)
pad = 16; box = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad); cw, ch = box[2] - box[0], box[3] - box[1]
sheet = Image.new('RGBA', (cw * 4, ch * len(MOVES)), (225, 220, 212, 255))
for r, m in enumerate(MOVES):
    for k in range(4):
        im = ims[m, k].copy(); d = G.get(f'{m}-{k}'); dr = ImageDraw.Draw(im)
        if d:
            col = (40, 160, 70, 255) if not d['bad'] else (210, 40, 40, 255)
            cx, cz = d['com']; gx, gy = px(cx, .15); dr.line([px(cx, cz), (gx, gy)], fill=col, width=2)
            x, y = px(cx, cz); dr.ellipse([x - 5, y - 5, x + 5, y + 5], outline=col, width=2)
            x, y = px(*d['sup'][:1], .15) if False else px(d['sup'][0], .15); dr.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            if d['target']:
                x, y = px(*d['target']); dr.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(230, 120, 0, 255), width=2)
                x, y = px(*d['hit']); dr.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(230, 120, 0, 255))
        sheet.alpha_composite(im.crop(box), (k * cw, r * ch))
sheet.convert('RGB').save(dst); print('ok', sheet.size)
