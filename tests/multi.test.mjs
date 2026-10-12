import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createPlanner } from '../src/js/planner.js';
import { createMulti, hopKind, setupGames } from '../src/js/multi.js';
import { loadGame } from './helpers.mjs';

// mirrors app.js
const setup = (mainId, owned, hw = {}) => setupGames(loadGame(mainId), owned.map(loadGame), { bank: true, ...hw }).M;
const kinds = (b) => (b.via || []).map((h) => h.k).join('>');

test('with no other games, Kanto starters are missing from Platinum', () => {
  const M = setup('platinum', []);
  assert.equal(M.best(1), null);
  assert.equal(M.status(1), 'none');
});

test('FireRed reaches Platinum through Pal Park after the National Dex', () => {
  const M = setup('platinum', ['firered']);
  const b = M.best(1); // Bulbasaur
  assert.equal(b.where, 'firered');
  assert.equal(kinds(b), 'palpark');
  assert.deepEqual(b.gates, ['national-dex']);
  assert.equal(b.st, 9);
  assert.equal(M.status(1), 'xfer');
});

test('Pal Park needs the GBA slot and never covers Gen 4 Pokémon', () => {
  assert.equal(setup('platinum', ['firered'], { gba: false }).best(1), null);
  const M = setup('platinum', ['emerald']);
  for (let id = 387; id <= 493; id++) assert.ok(!M.best(id) || !M.best(id).via, String(id));
});

test('another DS game you own is used for its version exclusives', () => {
  const M = setup('pearl', ['diamond']);
  const b = M.best(198); // Murkrow is Diamond-only
  assert.equal(b.where, 'diamond');
  assert.equal(kinds(b), 'trade');
  assert.equal(setup('pearl', ['diamond'], { trade: false }).best(198), null);
});

test('main game comes first, then trades, then Pal Park', () => {
  const M = setup('platinum', ['diamond', 'firered']);
  assert.equal(M.best(445).where, 'platinum'); // Garchomp stays in the main game
  assert.equal(M.best(198).where, 'diamond'); // Murkrow by trade beats nothing in Pt
});

test('a second DS game turns trade evolutions into normal steps', () => {
  assert.equal(setup('platinum', []).best(65).o.ext, 'trade'); // Alakazam
  const b = setup('platinum', ['diamond']).best(65);
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
  const M = setupGames(loadGame('platinum'), [loadGame('diamond')], {}, (id) => (id === 'platinum' ? { 0: 387 } : {})).M;
  assert.equal(M.best(390).where, 'diamond');
});

test('East Sea Shellos in HeartGold comes from an owned Sinnoh game', () => {
  const east = loadGame('heartgold').forms.find((f) => f.key === 'shellos-east');
  assert.equal(setup('heartgold', ['platinum']).formSource(east), 'platinum');
  assert.equal(setup('heartgold', []).formSource(east), null);
});

test('Rotom forms need the Secret Key event in Platinum, but Black 2 changes them in a shop', () => {
  const heat = loadGame('home').forms.find((f) => f.key === 'rotom-heat');
  assert.equal(setup('home', ['platinum', 'black']).formSource(heat), null);
  assert.equal(setup('home', ['black2']).formSource(heat), 'black2');
});

// ------------------------------------------------------------------ the transfer chain

test('hop kinds follow the real transfer rules', () => {
  const g = (id, gen, home = false) => ({ id, gen, home });
  const hw = { trade: true, gba: true, bank: true, vc: false };
  assert.equal(hopKind(g('red', 1), g('gold', 2), hw), 'timecapsule');
  assert.equal(hopKind(g('gold', 2), g('red', 1), hw), 'timecapsule');
  assert.equal(hopKind(g('gold', 2), g('ruby', 3), hw), null); // no way from Game Boy to GBA
  assert.equal(hopKind(g('ruby', 3), g('platinum', 4), hw), 'palpark');
  assert.equal(hopKind(g('platinum', 4), g('ruby', 3), hw), null); // one-way
  assert.equal(hopKind(g('platinum', 4), g('black', 5), hw), 'transfer');
  assert.equal(hopKind(g('black', 5), g('platinum', 4), hw), null);
  assert.equal(hopKind(g('black', 5), g('home', 9, true), hw), 'bank');
  assert.equal(hopKind(g('platinum', 4), g('home', 9, true), hw), null); // only through Gen 5
  assert.equal(hopKind(g('red', 1), g('home', 9, true), hw), null); // cartridges can't
  assert.equal(hopKind(g('red', 1), g('home', 9, true), { ...hw, vc: true }), 'bank');
  assert.equal(hopKind(g('black', 5), g('home', 9, true), { ...hw, bank: false }), null);
});

test('Gen 2 Pokémon past #151 cannot go back to Gen 1; the first 151 come through the Time Capsule', () => {
  const M = setup('red', ['crystal'], { trade: true });
  assert.equal(kinds(M.best(134)), 'timecapsule'); // Vaporeon: breed Eevees in Crystal
  assert.equal(M.best(134).where, 'crystal');
  assert.equal(M.status(134), 'xfer');
});

test('Gen 3 reaches Gen 5 through a Gen 4 game you own, never directly', () => {
  assert.equal(setup('black', ['emerald']).best(252), null); // Treecko: no Gen 4 game to bridge the gap
  const M = setup('black', ['emerald', 'platinum']);
  const b = M.best(252);
  assert.equal(b.where, 'emerald');
  assert.equal(kinds(b), 'palpark>transfer');
  assert.deepEqual(b.gates, ['poke-transfer']);
  assert.equal(b.st, 9);
});

test('HOME gets everything along the chain, and needs Pokémon Bank', () => {
  const M = setup('home', ['black', 'platinum', 'emerald', 'yellow'], { vc: true });
  assert.equal(kinds(M.best(494 + 1)), 'bank'); // Snivy from Black
  assert.equal(kinds(M.best(252)), 'palpark>transfer>bank'); // Treecko from Emerald
  assert.equal(M.best(1).where, 'yellow'); // Bulbasaur gift in Yellow, by Virtual Console
  assert.equal(setup('home', ['black'], { bank: false }).best(495), null);
  assert.equal(M.best(700), null); // Sylveon needs a Gen 6+ game
});

test('HOME forms come from the game that can make them', () => {
  const M = setup('home', ['black']);
  const winter = loadGame('home').forms.find((f) => f.key === 'deerling-winter');
  assert.equal(M.formSource(winter), 'black');
  const zen = loadGame('home').forms.find((f) => f.key === 'darmanitan-zen');
  assert.equal(zen, undefined); // battle-only forms are left out
});
