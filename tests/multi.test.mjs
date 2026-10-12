import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createPlanner } from '../src/js/planner.js';
import { createMulti } from '../src/js/multi.js';
import { loadGame } from './helpers.mjs';

const GEN = { ruby: 3, sapphire: 3, emerald: 3, firered: 3, leafgreen: 3, diamond: 4, pearl: 4, platinum: 4, heartgold: 4, soulsilver: 4 };

// mirrors app.js: main planner + one planner per owned game
function setup(mainId, owned, { trade = true, gba = true } = {}) {
  const gen4 = 1 + owned.filter((id) => GEN[id] === 4).length;
  const tradeEvolutions = trade && gen4 >= 2;
  const gbaSet = gba ? new Set(owned.filter((id) => GEN[id] === 3)) : null;
  const P = createPlanner(loadGame(mainId), { gba: gbaSet, tradeEvolutions });
  const sources = owned.map((id) => ({ id, gen: GEN[id], data: loadGame(id),
    P: createPlanner(loadGame(id), { tradeEvolutions: GEN[id] === 4 && tradeEvolutions }) }));
  return createMulti({ id: mainId, gen: 4, P }, sources, { trade, palPark: gba });
}

test('with no other games, Kanto starters are missing from Platinum', () => {
  const M = setup('platinum', []);
  assert.equal(M.best(1), null);
  assert.equal(M.status(1), 'none');
});

test('FireRed reaches Platinum through Pal Park after the National Dex', () => {
  const M = setup('platinum', ['firered']);
  const b = M.best(1); // Bulbasaur
  assert.equal(b.where, 'firered');
  assert.equal(b.via, 'palpark');
  assert.equal(b.st, 9);
  assert.equal(M.status(1), 'xfer');
});

test('Pal Park needs the GBA slot and never covers Gen 4 Pokémon', () => {
  assert.equal(setup('platinum', ['firered'], { gba: false }).best(1), null);
  const M = setup('platinum', ['emerald']);
  for (let id = 387; id <= 493; id++) assert.ok(!M.best(id) || M.best(id).via !== 'palpark', String(id));
});

test('another DS game you own is used for its version exclusives', () => {
  const M = setup('pearl', ['diamond']);
  const b = M.best(198); // Murkrow is Diamond-only
  assert.equal(b.where, 'diamond');
  assert.equal(b.via, 'trade');
  assert.equal(setup('pearl', ['diamond'], { trade: false }).best(198), null);
});

test('main game comes first, then trades, then Pal Park', () => {
  const M = setup('platinum', ['diamond', 'firered']);
  assert.equal(M.best(445).where, 'platinum'); // Garchomp stays in the main game
  assert.equal(M.best(198).where, 'diamond'); // Murkrow by trade beats nothing in Pt
});

test('a second DS game turns trade evolutions into normal steps', () => {
  const alone = setup('platinum', []);
  assert.equal(alone.best(65).o.ext, 'trade'); // Alakazam
  const M = setup('platinum', ['diamond']);
  const b = M.best(65);
  assert.equal(b.where, 'platinum');
  assert.equal(b.o.ext, null);
  assert.equal(b.o.viaTrade, true);
});

test('owning a GBA game unlocks its dual-slot encounters in the main game', () => {
  const data = loadGame('platinum');
  const slotOnly = data.species.find((s) => (s.e || []).some((e) => (e.sp || []).some((sp) => sp.ext === 'gba' && sp.c.some((c) => c.k === 'slot2' && c.v === 'ruby'))));
  assert.ok(slotOnly, 'Platinum has Ruby dual-slot encounters');
  const without = createPlanner(data).options(slotOnly.id).filter((o) => o.ext === 'gba');
  const withRuby = createPlanner(data, { gba: new Set(['ruby']) }).options(slotOnly.id);
  assert.ok(without.length > 0);
  assert.ok(withRuby.some((o) => o.k === 'catch' && o.ext === null && o.cond.some((c) => c.k === 'slot2')));
});

test('a starter you did not pick can come from your other copy of the game', () => {
  const P = createPlanner(loadGame('platinum'), { starters: { 0: 387 } });
  const src = createPlanner(loadGame('diamond'));
  const M = createMulti({ id: 'platinum', gen: 4, P }, [{ id: 'diamond', gen: 4, data: loadGame('diamond'), P: src }], { trade: true });
  assert.equal(M.best(390).where, 'diamond');
});

test('Rotom forms in HeartGold come from an owned Platinum', () => {
  const M = setup('heartgold', ['platinum']);
  const heat = loadGame('heartgold').forms.find((f) => f.key === 'rotom-heat');
  assert.equal(M.formSource(heat), 'platinum');
  assert.equal(setup('heartgold', []).formSource(heat), null);
});
