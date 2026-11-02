# Packs a ChatGPT turnaround sheet (2 rows x 4 views on a transparent background) into assets/bunny-turnaround.png:
# 8 cells of 360x460 in turn order (front, front-right, right, back-right, back, back-left, left, front-left), one shared
# scale, feet on one baseline, bodies centred (headband ties may hang to either side).
# Usage: python3 -I tools/prepare-turnaround.py <sheet.png>   (numpy, scipy, Pillow)
import sys, numpy as np
from pathlib import Path
from PIL import Image
from scipy import ndimage as nd
root = Path(__file__).resolve().parent.parent / 'assets'
src = np.asarray(Image.open(sys.argv[1]).convert('RGBA')).copy()
src[src[..., 3] < 20] = 0
solid = src[..., 3] > 40
lab, n = nd.label(nd.binary_dilation(solid, iterations=6))
sizes = nd.sum(solid, lab, range(1, n + 1))
keep = sorted(np.argsort(sizes)[::-1][:8] + 1)
boxes = []
for k in keep:
    sl = nd.find_objects((lab == k).astype(np.int8))[0]
    boxes.append((k, sl))
assert len(boxes) == 8, f'expected 8 views, found {len(boxes)}'
mid = src.shape[0] / 2
boxes.sort(key=lambda b: (0 if (b[1][0].start + b[1][0].stop) / 2 < mid else 1, b[1][1].start))
CW, CH, BASE = 360, 460, 448
tallest = max(sl[0].stop - sl[0].start for _, sl in boxes)
scale = (BASE - 14) / tallest
out = Image.new('RGBA', (CW * 4, CH * 2), (0, 0, 0, 0))
for i, (k, sl) in enumerate(boxes):
    crop = src[sl].copy()
    crop[lab[sl] != k] = 0
    h, w = crop.shape[:2]
    a = crop[..., 3] > 40
    ys, xs = np.nonzero(a[int(h * .45):])
    cx = xs.mean()  # body centre from the lower body, so ties do not shift the bunny
    im = Image.fromarray(crop).resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    x = (i % 4) * CW + CW / 2 - cx * scale
    y = (i // 4) * CH + BASE - h * scale
    out.alpha_composite(im, (int(round(x)), int(round(y))))
out.save(root / 'bunny-turnaround.png', optimize=True)
print('bunny-turnaround.png', out.size, 'scale', round(scale, 3))
