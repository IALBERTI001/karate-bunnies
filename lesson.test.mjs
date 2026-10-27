import test from 'node:test';
import assert from 'node:assert/strict';
import { LESSON, CHEERS, LESSON_END, stepDone, glowTargets } from './lesson.mjs';
import { CAST, MAX_WORDS, wordCount } from './story.mjs';
import { createMatch, input, step } from './combat.mjs';

test('lesson lines are short and spoken by coaches', () => {
  for (const s of LESSON) { assert.ok(CAST[s.say[0]]); assert.ok(wordCount(s.say[1]) <= MAX_WORDS, s.say[1]); }
  for (const c of [...CHEERS, LESSON_END[1]]) assert.ok(wordCount(c) <= MAX_WORDS, c);
});

test('the lesson covers the whole move set once', () => {
  assert.deepEqual(LESSON.map(s => s.id), ['tap', 'chain', 'guard', 'high', 'front', 'low', 'spin']);
});

test('each step ticks off from the real combat event for that move, and only the player counts', () => {
  const m = createMatch(); m.phase = 'fight'; m.fighters[0].x = 440; m.fighters[1].x = 550; m.lesson = { mode: 'idle' };
  const run = t => { for (let i = 0; i < Math.ceil(t * 60); i++) step(m, 1 / 60, { ai: false }); };
  const swing = key => { input(m, 0, { type: 'attackDown' }); if (key) input(m, 0, { type: 'direction', key, value: true }); input(m, 0, { type: 'attackUp' }); if (key) input(m, 0, { type: 'direction', key, value: false }); run(0.8); m.fighters[0].x = 440; m.fighters[1].x = 550; };
  const last = () => m.events.filter(e => e.type === 'swing' && e.fighter === 0).at(-1);
  swing(null); assert.ok(stepDone(LESSON[0], last()));
  for (let k = 0; k < 3; k++) { input(m, 0, { type: 'attackDown' }); input(m, 0, { type: 'attackUp' }); run(0.8); m.fighters[0].x = 440; m.fighters[1].x = 550; }
  assert.ok(stepDone(LESSON[1], last()), JSON.stringify(last()));
  for (const [id, key] of [['high', 'up'], ['front', 'right'], ['low', 'down'], ['spin', 'left']]) {
    swing(key); assert.ok(stepDone(LESSON.find(s => s.id === id), last()), id);
  }
  assert.equal(stepDone(LESSON[3], { type: 'swing', fighter: 1, move: 'high' }), false, "Mochi's move does not count");
  assert.ok(stepDone(LESSON[2], { type: 'block', fighter: 0 }));
  assert.equal(stepDone(LESSON[2], { type: 'block', fighter: 1 }), false);
  assert.equal(stepDone(LESSON[6], { type: 'swing', fighter: 0, move: 'spin', chain: true }), false, 'chain spin is not the back kick');
});

test('forward and back glow the right arrow for the way the bunny faces', () => {
  const front = LESSON.find(s => s.id === 'front'), back = LESSON.find(s => s.id === 'spin');
  assert.deepEqual(glowTargets(front, 1), ['#attack', '.dir[data-dir="right"]']);
  assert.deepEqual(glowTargets(front, -1), ['#attack', '.dir[data-dir="left"]']);
  assert.deepEqual(glowTargets(back, 1), ['#attack', '.dir[data-dir="left"]']);
});
