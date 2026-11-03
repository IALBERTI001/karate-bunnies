# Installs an assembled puppet atlas folder (from assemble.py) as the game's "3d" art set:
#   python3 -I tools/blender/install.py <atlas dir>
# Copies bunny3d-*.png, parts-pass-3d-<n>.png and belt-mask-3d-<n>.png into assets/ and writes assets/animations-3d.json
# with the same 20 animations (same names, speeds and order) as assets/animations.json. Then run:
#   python3 tools/soften-belt-masks.py --set 3d && python3 tools/gi-parts.py --set 3d && node refresh-assets.mjs
import json, shutil, sys
from pathlib import Path
src = Path(sys.argv[1]); root = Path(__file__).resolve().parents[2] / 'assets'
info = json.loads((src / 'atlases.json').read_text())
for a in info['atlases']: shutil.copyfile(src / a['file'], root / a['file'])
for i in range(len(info['atlases'])):
    shutil.copyfile(src / f'parts-pass-{i}.png', root / f'parts-pass-3d-{i}.png')
    shutil.copyfile(src / f'belt-mask-{i}.png', root / f'belt-mask-3d-{i}.png')
base = json.loads((root / 'animations.json').read_text())
keys = list(info['anims'])  # same order as the game's 18 fight animations
anims = []
for k, a in enumerate(base['animations']):
    a = {key: v for key, v in a.items() if key not in ('atlas', 'startFrame')}
    if k < len(keys): atlas, start = info['anims'][keys[k]]
    else: atlas, start = info['turnaround'], (k - len(keys)) * 4
    anims.append(dict(a, atlas=atlas, startFrame=start))
(root / 'animations-3d.json').write_text(json.dumps(dict(atlases=info['atlases'], animations=anims), indent=1))
print('installed', len(info['atlases']), 'atlases,', len(anims), 'animations')
