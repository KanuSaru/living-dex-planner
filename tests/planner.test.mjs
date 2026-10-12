import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createPlanner, periodAt, weekdayAt, condReady } from '../src/js/planner.js';
import { GAMES, loadGame, areaKey } from './helpers.mjs';

const at = (h, m = 0) => new Date(2026, 9, 11, h, m); // 11 Oct 2026 is a Sunday

test('Gen 4 clock periods switch at 4:00, 10:00 and 20:00', () => {
  assert.equal(periodAt(at(3, 59)), 'n');
  assert.equal(periodAt(at(4, 0)), 'm');
  assert.equal(periodAt(at(9, 59)), 'm');
  assert.equal(periodAt(at(10, 0)), 'd');
  assert.equal(periodAt(at(19, 59)), 'd');
  assert.equal(periodAt(at(20, 0)), 'n');
  assert.equal(weekdayAt(at(12)), 'sunday');
});

test('weekday and contest conditions only hold on their days', () => {
  assert.equal(condReady({ k: 'weekday', v: 'friday' }, { period: 'd', weekday: 'friday' }), true);
  assert.equal(condReady({ k: 'weekday', v: 'friday' }, { period: 'd', weekday: 'monday' }), false);
  assert.equal(condReady({ k: 'contest' }, { period: 'd', weekday: 'tuesday' }), true);
  assert.equal(condReady({ k: 'contest' }, { period: 'd', weekday: 'sunday' }), false);
  assert.equal(condReady({ k: 'swarm' }, { period: 'd', weekday: 'sunday' }), false);
});

test('Platinum: Garchomp comes from a Gible caught in Wayward Cave', () => {
  const data = loadGame('platinum');
  const P = createPlanner(data);
  const b = P.best(445);
  assert.equal(b.k, 'evolve');
  assert.equal(b.root.s, 443);
  assert.equal(areaKey(data, b.root.e.a), 'wayward-cave');
  assert.equal(b.ext, null);
});

test('starters: unchosen ones need a trade, the chosen one is a gift', () => {
  const data = loadGame('platinum');
  assert.equal(createPlanner(data).best(390).ext, 'starter');
  const P = createPlanner(data, { starters: { 0: 387 } });
  assert.equal(P.best(387).ext, null);
  assert.equal(P.best(390).ext, 'trade');
  assert.equal(P.best(392).ext, 'trade'); // Infernape follows Chimchar
});

test('HeartGold has three starter groups (Johto, Kanto, Hoenn)', () => {
  const data = loadGame('heartgold');
  assert.equal(data.game.starterGroups.length, 3);
  const P = createPlanner(data, { starters: { 0: 155, 1: 4, 2: 258 } });
  assert.equal(P.best(155).ext, null);
  assert.equal(P.best(4).ext, null);
  assert.equal(P.best(258).ext, null);
  assert.equal(P.best(1).ext, 'trade');
});

test('location evolutions exist only in Sinnoh games', () => {
  for (const id of ['diamond', 'pearl', 'platinum']) {
    const P = createPlanner(loadGame(id));
    assert.equal(P.best(470).k, 'evolve', `${id} Leafeon`);
    assert.equal(P.best(462).k, 'evolve', `${id} Magnezone`);
  }
  for (const id of ['heartgold', 'soulsilver']) {
    const P = createPlanner(loadGame(id));
    assert.equal(P.best(470), null, `${id} Leafeon`);
    assert.equal(P.best(462), null, `${id} Magnezone`);
  }
});

test('version exclusives differ between Diamond and Pearl', () => {
  assert.notEqual(createPlanner(loadGame('diamond')).best(198), null); // Murkrow
  assert.equal(createPlanner(loadGame('pearl')).best(198), null);
  assert.notEqual(createPlanner(loadGame('pearl')).best(200), null); // Misdreavus
});

test('Shedinja costs no extra Nincada in the plan', () => {
  const data = loadGame('platinum');
  const P = createPlanner(data);
  assert.equal(P.best(292).path.at(-1).ev.t, 'shed');
  const list = data.species.filter((s) => [290, 291, 292].includes(s.id));
  const plan = P.planGroups(list, new Set());
  const group = plan.stages.flatMap((s) => s.areas.flatMap((a) => a.groups)).find((g) => g.r.s === 290);
  assert.equal(group.targets.length, 3);
  assert.equal(group.need, 2);
});

test('boxed Pokémon lower the copy count', () => {
  const data = loadGame('platinum');
  const P = createPlanner(data);
  const list = data.species.filter((s) => [396, 397, 398].includes(s.id));
  const g = (caught) => P.planGroups(list, caught).stages[0].areas.flatMap((a) => a.groups).find((x) => x.r.s === 396);
  assert.equal(g(new Set()).need, 3);
  assert.equal(g(new Set(['397'])).need, 2);
});

test('Spiritomb needs the Odd Keystone and 32 Underground chats', () => {
  const P = createPlanner(loadGame('platinum'));
  const b = P.best(442);
  assert.equal(b.k, 'catch');
  assert.deepEqual(b.cond.map((c) => c.k), ['item', 'other']);
  assert.equal(b.st, 2);
});

test('Milotic needs a trade in HeartGold (no Poffins) but not in Platinum', () => {
  assert.equal(createPlanner(loadGame('platinum')).best(350).ext, null);
  const hg = createPlanner(loadGame('heartgold')).best(350);
  assert.ok(hg === null || hg.ext === 'trade');
});

test('mythical Pokémon with no source are event-only, not missing', () => {
  const P = createPlanner(loadGame('platinum'));
  for (const id of [151, 251, 385, 386]) assert.equal(P.best(id).ext, 'event', String(id));
  assert.equal(P.best(491).ext, 'event'); // Darkrai needs the Member Card
});

test('genderless Pokémon breed only with Ditto', () => {
  const P = createPlanner(loadGame('platinum'));
  const breed = P.options(81).find((o) => o.k === 'breed'); // Magnemite
  if (breed) assert.equal(breed.needsDitto, true);
  const pichu = P.options(172).find((o) => o.k === 'breed');
  assert.ok(pichu, 'Pichu can be bred');
  assert.equal(pichu.needsDitto, false);
});

test('catch right now respects time, progress and weekday', () => {
  const data = loadGame('platinum');
  const P = createPlanner(data);
  const wanted = () => true;
  const night = P.catchNow({ date: at(22), progress: 0, wanted });
  const day = P.catchNow({ date: at(12), progress: 0, wanted });
  for (const g of [...night, ...day]) assert.ok(g.area.st <= 0, 'only start-of-game areas');
  const ids = (groups) => new Set(groups.flatMap((g) => g.items.map((i) => i.s.id)));
  // Kricketot (401) on Route 201 is morning and night only
  assert.ok(ids(night).has(401));
  assert.ok(!ids(day).has(401));
  // Drifloon (425) appears at Valley Windworks on Fridays only
  const friday = new Date(2026, 9, 16, 12);
  assert.ok(ids(P.catchNow({ date: friday, progress: 9, wanted })).has(425));
  assert.ok(!ids(P.catchNow({ date: at(12), progress: 9, wanted })).has(425));
});

test('form availability: Rotom forms are event-only in Platinum and trades in HeartGold', () => {
  const pt = createPlanner(loadGame('platinum'));
  const heat = pt.data.forms.find((f) => f.key === 'rotom-heat');
  assert.equal(pt.formStatus(heat).ext, 'event');
  const hg = createPlanner(loadGame('heartgold'));
  const heatHG = hg.data.forms.find((f) => f.key === 'rotom-heat');
  assert.equal(hg.formStatus(heatHG).ext, 'trade');
  assert.equal(loadGame('diamond').forms.some((f) => f.key === 'rotom-heat'), false);
});

test('Shellos sea forms follow the side of Mt. Coronet', () => {
  const data = loadGame('platinum');
  const west = data.forms.find((f) => f.key === 'shellos-west');
  const east = data.forms.find((f) => f.key === 'shellos-east');
  assert.deepEqual(west.how.map((h) => h.v), ['west']);
  assert.ok(west.st < east.st, 'the West Sea form is reachable earlier');
});

test('every game builds a plan without throwing', () => {
  for (const id of GAMES) {
    const data = loadGame(id);
    const P = createPlanner(data);
    const plan = P.planGroups(data.species, new Set());
    const planned = plan.stages.reduce((n, s) => n + s.areas.reduce((m, a) => m + a.groups.reduce((k, g) => k + g.targets.length, 0), 0), 0);
    assert.equal(planned + plan.ext.length + plan.none.length, 493, id);
  }
});
