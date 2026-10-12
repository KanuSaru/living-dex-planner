import { test } from 'node:test';
import assert from 'node:assert/strict';
import { decodeProgress, encodeProgress, peekProgress } from '../src/js/progress-code.js';
import { GAMES, loadGame } from './helpers.mjs';

test('progress codes round-trip species and forms in every game', () => {
  for (const id of GAMES) {
    const data = loadGame(id);
    const forms = data.forms.filter((f) => !f.def).map((f) => f.key);
    const caught = new Set(['1', '25', '133', '201', '493', ...forms.slice(0, 3), forms.at(-1)]);
    const code = encodeProgress(data, caught);
    assert.match(code, new RegExp(`^LD1\\.${id}\\.[A-Za-z0-9_-]+$`));
    assert.deepEqual([...decodeProgress(data, code)].sort(), [...caught].sort(), id);
  }
});

test('an empty dex and a full dex both round-trip', () => {
  const data = loadGame('platinum');
  assert.equal(decodeProgress(data, encodeProgress(data, new Set())).size, 0);
  const all = new Set([...Array(493).keys()].map((i) => String(i + 1)));
  for (const f of data.forms) if (!f.def) all.add(f.key);
  assert.equal(decodeProgress(data, encodeProgress(data, all)).size, all.size);
});

test('codes tolerate whitespace and reject other games or damage', () => {
  const pt = loadGame('platinum');
  const code = encodeProgress(pt, new Set(['445']));
  const spaced = `  ${code.slice(0, 20)}\n${code.slice(20)}  `;
  assert.ok(decodeProgress(pt, spaced).has('445'));
  assert.equal(peekProgress(code).game, 'platinum');
  assert.equal(decodeProgress(loadGame('diamond'), code), null);
  assert.equal(decodeProgress(pt, code.slice(0, -4)), null);
  assert.equal(decodeProgress(pt, 'hello'), null);
  assert.equal(peekProgress(''), null);
});
