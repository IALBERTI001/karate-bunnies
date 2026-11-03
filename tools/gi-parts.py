# Garment map for the gi shader (assets/gi-parts-<n>.png), so gi designs follow the clothes instead of being a flat wallpaper:
#   red   = trim: the gi edge where cloth meets fur (collar, sleeve cuffs, trouser hems), soft-edged
#   green = headband (shop turnaround only)
#   blue  = trousers (shop turnaround only; the small fight sprites have no clean hem lines): cloth pieces below the belt that the ink lines separate from the jacket (the jacket skirt stays jacket)
# Paws held in front of the jacket and the tail get no trim. Also writes assets/gi-anchors.json: the belt centre of
# every atlas cell, so prints and gradients stay put on the body from pose to pose.
# Usage: python3 tools/gi-parts.py [--debug outdir]   (numpy, scipy, Pillow)
import json, sys, numpy as np
from pathlib import Path
from PIL import Image
from scipy import ndimage as nd
root = Path(__file__).resolve().parent.parent / 'assets'
ss = lambda a, b, x: (lambda t: t * t * (3 - 2 * t))(np.clip((x - a) / (b - a), 0, 1))
debug = sys.argv[sys.argv.index('--debug') + 1] if '--debug' in sys.argv else None
anchors = []
for i, atlas in enumerate(json.loads((root / 'animations.json').read_text())['atlases']):
    c = np.asarray(Image.open(root / atlas['file']).convert('RGBA'), dtype=np.float32) / 255
    r, g, b, a = c[..., 0], c[..., 1], c[..., 2], c[..., 3]
    hi, lo = c[..., :3].max(-1), c[..., :3].min(-1)
    cell = c.shape[0] / atlas['rows']
    green = ss(.025, .13, g - np.maximum(r, b)) * (a > .5)
    gi = green > .5
    sat = (hi - lo) / np.maximum(hi, 1e-3)
    pink = (r - g > .12) & (r - b > .08)
    fur = (a > .5) & ~gi & (hi > .55) & ((sat < .45) | pink)
    fur = nd.binary_opening(fur, iterations=1)
    belt = np.asarray(Image.open(root / f'belt-mask-{i}.png').convert('L')) > 127
    # Trim: a band of cloth along the fur edge. Paws held in front of the jacket also border cloth; keep only edges
    # where the fur continues past the cloth outline (neck, wrist, ankle), approximated by fur blobs of limb size.
    # Paws held in front of the jacket and the tail are fur islands mostly ringed by cloth: no trim around those.
    core, nl = nd.label(nd.binary_erosion(fur, iterations=4 if atlas.get('turnaround') else 1))
    _, (iy, ix) = nd.distance_transform_edt(core == 0, return_indices=True)
    lab = np.where(fur, core[iy, ix], 0)
    ring = nd.binary_dilation(fur, iterations=2) & ~fur
    keep = np.zeros(nl + 1, bool)
    reach = int(cell * .02) + 3
    H, W = fur.shape
    for f, sl in enumerate(nd.find_objects(lab), 1):
        if sl is None: continue
        y0, y1 = max(0, sl[0].start - reach), min(H, sl[0].stop + reach)
        x0, x1 = max(0, sl[1].start - reach), min(W, sl[1].stop + reach)
        m = lab[y0:y1, x0:x1] == f
        edge = nd.binary_dilation(m, iterations=reach) & ~nd.binary_dilation(m, iterations=reach - 2)
        e_gi = (edge & gi[y0:y1, x0:x1]).sum(); e_out = (edge & (a[y0:y1, x0:x1] < .3)).sum()
        keep[f] = m.sum() > 12 and (e_gi < .5 * (e_gi + e_out + 1) or m.sum() > .035 * cell * cell)
    edgefur = keep[lab]
    d = nd.distance_transform_edt(~edgefur)
    width = max(2.5, cell * .02)
    trim = gi * (1 - ss(width * .7, width * 1.25, d))
    trim = np.clip(nd.gaussian_filter(trim.astype(np.float32), .6), 0, 1) * green
    # Belt knot position per atlas cell, so prints, gradients and emblems are anchored to the body, not the frame box.
    cols, rows = atlas['columns'], atlas['rows']; cw = c.shape[1] / cols
    cells = []
    for k in range(cols * rows):
        y0, x0 = int(k // cols * cell), int(k % cols * cw)
        bm = belt[y0:int(y0 + cell), x0:int(x0 + cw)]
        ys, xs = np.nonzero(bm)
        cells.append([round(float(xs.mean() + x0), 1), round(float(ys.mean() + y0), 1)] if ys.size > 20 else None)
    anchors.append(cells)
    # Atlases without a face in every view (the shop turnaround) mark their headband here, in the green channel:
    # cloth pieces that do not touch the belt and sit above the collar.
    band = np.zeros(gi.shape, bool)
    if atlas.get('turnaround'):
        for k in range(cols * rows):
            y0, x0 = int(k // cols * cell), int(k % cols * cw); ys_, xs_ = slice(y0, int(y0 + cell)), slice(x0, int(x0 + cw))
            g_, b_ = (green[ys_, xs_] > .97) & ~belt[ys_, xs_], nd.binary_dilation(belt[ys_, xs_], iterations=4)
            lab_, nn = nd.label(g_)
            if not nn: continue
            touch = [f for f in range(1, nn + 1) if ((lab_ == f) & b_).any()]
            if not touch: continue
            collar = min(np.nonzero(np.isin(lab_, touch))[0])
            for f in range(1, nn + 1):
                if f in touch: continue
                fy = np.nonzero(lab_ == f)[0]
                if fy.mean() < collar: band[ys_, xs_] |= lab_ == f
        band = nd.binary_dilation(band, iterations=3) & (green > .2)
    # Trousers: with the ink lines as walls, cloth pieces that touch the belt are the jacket (its skirt hangs below the
    # knot); separate pieces whose middle is below the knot are trouser legs.
    legs = np.zeros(gi.shape, bool)
    for k in range(cols * rows if atlas.get('turnaround') else 0):
        if cells[k] is None: continue
        y0, x0 = int(k // cols * cell), int(k % cols * cw); ys_, xs_ = slice(y0, int(y0 + cell)), slice(x0, int(x0 + cw))
        solid = (green[ys_, xs_] > .9) & (g[ys_, xs_] > .42) & ~belt[ys_, xs_] & ~band[ys_, xs_]
        solid = nd.binary_erosion(solid, iterations=1)
        lab_, nn = nd.label(solid)
        near = nd.binary_dilation(belt[ys_, xs_], iterations=5)
        by = cells[k][1] - y0
        for f, sl in enumerate(nd.find_objects(lab_), 1):
            m = lab_[sl] == f
            if m.sum() < 30 or (m & near[sl]).any(): continue
            if np.nonzero(m)[0].mean() + sl[0].start > by + cell * .03: legs[ys_, xs_][sl] |= m
    # Grow the legs back over their soft edges, but never into the jacket.
    jacket = gi & ~nd.binary_dilation(legs, iterations=3)
    legs_soft = nd.binary_dilation(legs, iterations=3) & (green > .2) & ~(jacket & ~gi)
    lower = np.clip(nd.gaussian_filter(legs_soft.astype(np.float32), .8), 0, 1) * (green > .2)
    out = np.zeros(c.shape[:2] + (3,), np.uint8)
    out[..., 2] = np.round(lower * 255)
    out[..., 1] = np.round(band * green * 255)
    out[..., 0] = np.round(trim * 255); 
    Image.fromarray(out).save(root / f'gi-parts-{i}.png', optimize=True)
    print(f'gi-parts-{i}.png trim', int((trim > .5).sum()))
    if debug:
        vis = (c[..., :3] * 255).astype(np.uint8).copy(); vis[a < .3] = 200
        vis[trim > .5] = [230, 60, 60]; vis[band & (trim <= .5)] = [60, 80, 220]; vis[(lower > .5) & (trim <= .5)] = [40, 170, 230]
        Image.fromarray(vis).save(f'{debug}/parts-{i}.png')
(root / 'gi-anchors.json').write_text(json.dumps(anchors, separators=(',', ':')))
