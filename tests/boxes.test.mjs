import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BOX_SIZE, boxSlots, layoutBoxes, positionOf } from '../src/js/boxes.js';
import { loadGame } from './helpers.mjs';

test('National dex fills 17 boxes of 30', () => {
  const slots = boxSlots(loadGame('platinum'), { scope: 'national' });
  assert.equal(slots.length, 493);
  const boxes = layoutBoxes(slots);
  assert.equal(boxes.length, 17);
  assert.ok(boxes.slice(0, -1).every((b) => b.slots.length === BOX_SIZE));
  assert.equal(boxes.at(-1).slots.length, 13);
});

test('positions: #031 opens box 2, #036 ends its first row', () => {
  const slots = boxSlots(loadGame('platinum'), { scope: 'national' });
  assert.deepEqual(positionOf(slots, 31), { box: 2, slot: 1, row: 1, col: 1 });
  assert.deepEqual(positionOf(slots, 36), { box: 2, slot: 6, row: 1, col: 6 });
  assert.deepEqual(positionOf(slots, 37), { box: 2, slot: 7, row: 2, col: 1 });
  assert.equal(positionOf(slots, 31, { start: 3 }).box, 4);
});

test('regional order follows the regional dex numbers', () => {
  const data = loadGame('platinum');
  const slots = boxSlots(data, { scope: 'regional' });
  assert.equal(slots.length, 210);
  assert.equal(slots[0].sp, 387); // Turtwig is Sinnoh #001
  assert.equal(positionOf(slots, 445).slot, 111 - 90); // Garchomp, Sinnoh #111 -> box 4 slot 21
  assert.equal(positionOf(slots, 445).box, 4);
  assert.equal(positionOf(slots, 1), null); // Bulbasaur isn't in the Sinnoh dex
});

test('form slots follow their species and skip forms that cannot be boxed', () => {
  const data = loadGame('platinum');
  const slots = boxSlots(data, { scope: 'national', includeForms: true });
  const i = slots.findIndex((s) => s.key === '201');
  assert.equal(slots[i + 1].key, 'unown-b');
  assert.ok(!slots.some((s) => s.key === 'shaymin-sky'));
  assert.ok(!slots.some((s) => s.key === 'unown-a'), 'default forms share the species slot');
  const extra = data.forms.filter((f) => !f.def && !f.nobox).length;
  assert.equal(slots.length, 493 + extra);
});
