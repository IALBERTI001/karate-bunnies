import test from 'node:test';
import assert from 'node:assert/strict';
import { SCRIPT, CAST, LOSS, MAX_WORDS, wordCount, storyLines, opponentName, blipSchedule } from './story.mjs';
import { STAGES } from './campaign.mjs';

test('twenty stages, each with lines before the fight and after a win', () => {
  assert.equal(SCRIPT.length, 20);
  for (const s of SCRIPT) { assert.ok(s.before.length >= 1); assert.ok(s.win.length >= 1); }
});

test('every line is short and spoken by a known character', () => {
  const all = [...SCRIPT.flatMap(s => [...s.before, ...s.win]), ...LOSS];
  for (const [who, text] of all) {
    assert.ok(CAST[who], `unknown speaker ${who}`);
    assert.ok(wordCount(text) <= MAX_WORDS, `"${text}" has ${wordCount(text)} words`);
  }
});

test('story opponents match the campaign roster', () => {
  STAGES.forEach((stage, i) => assert.equal(opponentName(i + 1), stage.opponent));
});

test('lines know which side speaks', () => {
  const lines = storyLines(1, 'win');
  assert.equal(lines[0].side, 'player');
  assert.equal(lines[1].side, 'opponent');
  assert.equal(storyLines(1, 'before')[0].side, 'aside');
  assert.equal(storyLines(1, 'loss', () => 0).length, 1);
  assert.deepEqual(storyLines(99, 'before'), []);
});

test('blips follow syllables, pause on punctuation and rise on questions', () => {
  const plain = blipSchedule('Paws up', 500);
  assert.equal(plain.blips.length, 2);
  const q = blipSchedule('Friends?', 500);
  assert.ok(q.blips.at(-1).freq > plain.blips[0].freq);
  assert.ok(blipSchedule('Hi. Hi', 500).duration > blipSchedule('Hi Hi', 500).duration);
  assert.equal(blipSchedule('…', 500).blips.length, 0);
});

test('belt award lines are short and land on the right stages', async () => {
  const { BELT_LINES, beltLine } = await import('./story.mjs');
  const { BELT_AWARDS, beltFor } = await import('./campaign.mjs');
  for (const [belt, [who, text]] of Object.entries(BELT_LINES)) { assert.ok(CAST[who]); assert.ok(wordCount(text) <= MAX_WORDS, text); }
  for (const belt of Object.values(BELT_AWARDS)) assert.ok(BELT_LINES[belt], `no line for ${belt}`);
  assert.equal(beltLine('Black', 20).side, 'opponent');
  assert.equal(beltLine('Yellow', 4).award, 'Yellow');
  assert.equal(beltFor({ cleared: [] }), 'White');
  assert.equal(beltFor({ cleared: [1, 2, 3, 4] }), 'Yellow');
  assert.equal(beltFor({ cleared: [...Array(12).keys()].map(i => i + 1) }), 'Brown');
  assert.equal(beltFor({ cleared: [...Array(16).keys()].map(i => i + 1) }), 'Red');
  assert.equal(beltFor({ cleared: [...Array(20).keys()].map(i => i + 1) }), 'Black');
});
