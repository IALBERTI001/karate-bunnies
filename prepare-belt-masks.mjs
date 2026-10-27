// Builds assets/belt-mask-<n>.png (white = belt) for each sprite atlas in assets/animations.json.
// Usage: node prepare-belt-masks.mjs [--preview <dir>]   (requires the sharp dev dependency)
import sharp from 'sharp';
import { readFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { beltMask } from './belt-mask.mjs';
const root = path.dirname(fileURLToPath(import.meta.url));
const manifest = JSON.parse(await readFile(path.join(root, 'assets/animations.json'), 'utf8'));
const previewAt = process.argv.indexOf('--preview'), previewDir = previewAt > 0 ? process.argv[previewAt + 1] : null;
if (previewDir) await mkdir(previewDir, { recursive: true });
for (const [i, atlas] of manifest.atlases.entries()) {
  const { data, info } = await sharp(path.join(root, 'assets', atlas.file)).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const mask = beltMask(info.width, info.height, data);
  const gray = Buffer.from(mask.map(v => v ? 255 : 0));
  await sharp(gray, { raw: { width: info.width, height: info.height, channels: 1 } }).png({ compressionLevel: 9 }).toFile(path.join(root, 'assets', `belt-mask-${i}.png`));
  if (previewDir) {
    const vis = Buffer.from(data);
    for (let p = 0; p < mask.length; p++) if (mask[p]) vis.set([255, 196, 0, 255], p * 4);
    await sharp(vis, { raw: { width: info.width, height: info.height, channels: 4 } }).flatten({ background: '#ffffff' }).png().toFile(path.join(previewDir, `belt-preview-${i}.png`));
  }
  console.log(`${atlas.file}: ${mask.reduce((a, b) => a + b, 0)} belt pixels`);
}
