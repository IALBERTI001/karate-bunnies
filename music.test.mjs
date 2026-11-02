import test from 'node:test';
import assert from 'node:assert/strict';
import { musicScore, LOOP, BAR } from './music.mjs';

test('the theme is a long loop, not a short repeating jingle', () => {
  assert.ok(LOOP >= 30, `loop is ${LOOP}s`);
  const lead = musicScore().filter(e => e.kind === 'lead');
  assert.ok(new Set(lead.map(e => Math.round(e.f))).size >= 7, 'melody uses a range of notes');
});

test('no bar is silent and every note ends inside the loop', () => {
  const score = musicScore();
  for (let b = 0; b < LOOP / BAR; b++) assert.ok(score.some(e => e.t >= b * BAR && e.t < (b + 1) * BAR), `bar ${b} empty`);
  for (const e of score) { assert.ok(e.t + e.d <= LOOP + 1e-6, 'note runs past the loop'); assert.ok(e.f > 50 && e.f < 1500); }
});
