# Turns the hard 0/1 belt masks (assets/belt-mask-<n>.png, from prepare-belt-masks.mjs) into soft masks the
# renderer uses (assets/belt-soft-<n>.png): red = belt fill with anti-aliased edges, green = a thin warm-brown
# outline where the original black belt met the gi, so a recoloured belt reads as cloth, not a pasted cut-out.
# Usage: python3 tools/soften-belt-masks.py   (numpy, scipy, Pillow)
import json, numpy as np
from pathlib import Path
from PIL import Image
from scipy import ndimage as nd
root = Path(__file__).resolve().parent.parent / 'assets'
ss = lambda a, b, x: (lambda t: t * t * (3 - 2 * t))(np.clip((x - a) / (b - a), 0, 1))
for i, atlas in enumerate(json.loads((root / 'animations.json').read_text())['atlases']):
    c = np.asarray(Image.open(root / atlas['file']).convert('RGBA'), dtype=np.float32) / 255
    hard = np.asarray(Image.open(root / f'belt-mask-{i}.png').convert('L')) > 127
    hi = c[..., :3].max(-1)
    region = np.clip(nd.gaussian_filter((nd.binary_dilation(hard, iterations=1) * (1 - ss(.25, .5, hi))).astype(np.float32), .55) * 1.3, 0, 1) * (c[..., 3] > .05)
    fill = np.clip(nd.gaussian_filter(hard.astype(np.float32), .65) * 1.6 - .3, 0, 1)
    line = np.clip(region - fill, 0, 1) * .85
    out = np.zeros(c.shape[:2] + (3,), np.uint8); out[..., 0] = np.round(fill * 255); out[..., 1] = np.round(line * 255)
    Image.fromarray(out).save(root / f'belt-soft-{i}.png', optimize=True)
    print(f'belt-soft-{i}.png', int((fill > .5).sum()), 'fill px')
