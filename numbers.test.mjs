import test from 'node:test';
import assert from 'node:assert/strict';
import { formatCount } from './numbers.mjs';

test('small counts are plain integers', () => {
  assert.equal(formatCount(0), '0');
  assert.equal(formatCount(7), '7');
  assert.equal(formatCount(999), '999');
});

test('large counts are compact with no commas', () => {
  assert.equal(formatCount(1000), '1K');
  assert.equal(formatCount(1040), '1.04K');
  assert.equal(formatCount(2400), '2.4K');
  assert.equal(formatCount(12500), '12.5K');
  assert.equal(formatCount(999999), '999K');
  assert.equal(formatCount(1000000), '1M');
  assert.equal(formatCount(3250000), '3.25M');
  for (const n of [1234, 56789, 1234567]) assert.ok(!formatCount(n).includes(','));
});

test('rounds down so it never overstates a balance', () => {
  assert.equal(formatCount(1999), '1.99K');
  assert.equal(formatCount(9999), '9.99K');
});

test('bad input is safe', () => {
  assert.equal(formatCount(undefined), '0');
  assert.equal(formatCount('abc'), '0');
  assert.equal(formatCount(-1500), '-1.5K');
});
