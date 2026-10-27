// Finds the belt in bunny sprite atlases so it can be recoloured without touching outlines or eyes.
// In the source art the gi is green, the belt near-black, outlines mid-brown, and eyes sit on fur.
// A belt region is dark and mostly bordered by gi; it is either thick (a band) or very dark.
const SQUARE = r => { const o = []; for (let y = -r; y <= r; y++) for (let x = -r; x <= r; x++) o.push([x, y]); return o; };
function morph(src, w, h, r, erode, within) {
  const out = new Uint8Array(w * h), k = SQUARE(r);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x; if (within && !within[i]) continue;
    let v = erode ? 1 : 0;
    for (const [dx, dy] of k) {
      const xx = x + dx, yy = y + dy, s = xx >= 0 && yy >= 0 && xx < w && yy < h ? src[yy * w + xx] : 0;
      if (erode && !s) { v = 0; break; } if (!erode && s) { v = 1; break; }
    }
    out[i] = v;
  }
  return out;
}
const and = (a, b) => a.map((v, i) => v && b[i] ? 1 : 0);
function components(mask, w, h) {
  const label = new Int32Array(w * h), list = []; let id = 0;
  for (let s = 0; s < mask.length; s++) {
    if (!mask[s] || label[s]) continue;
    const px = [], stack = [s]; label[s] = ++id;
    while (stack.length) { const p = stack.pop(); px.push(p); const x = p % w, y = (p - x) / w;
      for (const q of [x ? p - 1 : -1, x < w - 1 ? p + 1 : -1, y ? p - w : -1, y < h - 1 ? p + w : -1])
        if (q >= 0 && mask[q] && !label[q]) { label[q] = id; stack.push(q); } }
    list.push(px);
  }
  return list;
}

export const BELT_DEFAULTS = { dark: 0.36, thickRadius: 2, minCore: 150, veryDark: 0.2, minVeryDark: 40, bandFraction: 0.15, veryDarkFraction: 0.6, grow: 12, minFragment: 40, fragmentReach: 6 };

export function beltMask(width, height, rgba, options = {}) {
  const o = { ...BELT_DEFAULTS, ...options }, n = width * height;
  const hi = new Float32Array(n), dark = new Uint8Array(n), green = new Uint8Array(n);
  for (let i = 0; i < n; i++) {
    const r = rgba[i * 4] / 255, g = rgba[i * 4 + 1] / 255, b = rgba[i * 4 + 2] / 255, a = rgba[i * 4 + 3] / 255;
    hi[i] = Math.max(r, g, b);
    if (a > 0.5) { dark[i] = hi[i] < o.dark ? 1 : 0; green[i] = g - Math.max(r, b) > 0.07 ? 1 : 0; }
  }
  const nearGreen = morph(green, width, height, 2, false);
  const edgeFraction = px => { const set = new Set(px); let edge = 0, touching = 0;
    for (const p of px) { const x = p % width;
      const boundary = [x ? p - 1 : -1, x < width - 1 ? p + 1 : -1, p - width, p + width].some(q => q < 0 || q >= n || !set.has(q));
      if (boundary) { edge++; if (nearGreen[p]) touching++; } }
    return edge ? touching / edge : 0; };
  const core = new Uint8Array(n);
  // Thick bands: survive an opening of the given radius.
  const thick = and(morph(morph(dark, width, height, o.thickRadius, true), width, height, o.thickRadius, false), dark);
  for (const px of components(thick, width, height))
    if (px.length >= o.minCore && edgeFraction(px) >= o.bandFraction) for (const p of px) core[p] = 1;
  // Very dark regions mostly enclosed by gi (a belt partly hidden behind a limb).
  for (const px of components(dark, width, height)) {
    if (px.length < o.minVeryDark) continue;
    const sorted = px.map(p => hi[p]).sort((a, b) => a - b);
    if (sorted[sorted.length >> 1] < o.veryDark && edgeFraction(px) >= o.veryDarkFraction) for (const p of px) core[p] = 1;
  }
  // Grow along connected belt pixels at least 3px thick, then fill the band; keep a 1px dark outline.
  const thin = and(morph(morph(dark, width, height, 1, true), width, height, 1, false), dark);
  let belt = core;
  for (let i = 0; i < o.grow; i++) belt = and(morph(belt, width, height, 1, false), thin);
  belt = and(morph(morph(belt, width, height, 1, false), width, height, 1, false), dark);
  belt = morph(belt, width, height, 1, true);
  // Drop specks along outlines: small fragments survive only beside a real belt region (knot tails, gaps behind a paw).
  const parts = components(belt, width, height), big = new Uint8Array(n);
  for (const px of parts) if (px.length >= o.minFragment) for (const p of px) big[p] = 1;
  const beside = morph(big, width, height, o.fragmentReach, false), out = new Uint8Array(n);
  for (const px of parts) if (px.length >= o.minFragment || px.some(p => beside[p])) for (const p of px) out[p] = 1;
  return out;
}
