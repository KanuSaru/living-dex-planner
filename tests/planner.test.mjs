import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createPlanner, periodAt, weekdayAt, condReady, lockOf } from '../src/js/planner.js';
import { setupGames } from '../src/js/multi.js';
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
  const openAt = (p) => (story, gates) => !lockOf({ story, gates }, p, (g) => (data.game.gates[g] ?? 0) <= p);
  const night = P.catchNow({ date: at(22), wanted, isOpen: openAt(0) });
  const day = P.catchNow({ date: at(12), wanted, isOpen: openAt(0) });
  for (const g of [...night, ...day]) assert.ok(g.area.st <= 0, 'only start-of-game areas');
  const ids = (groups) => new Set(groups.flatMap((g) => g.items.map((i) => i.s.id)));
  // Kricketot (401) on Route 201 is morning and night only
  assert.ok(ids(night).has(401));
  assert.ok(!ids(day).has(401));
  // Drifloon (425) appears at Valley Windworks on Fridays only
  const friday = new Date(2026, 9, 16, 12);
  assert.ok(ids(P.catchNow({ date: friday, wanted, isOpen: openAt(9) })).has(425));
  assert.ok(!ids(P.catchNow({ date: at(12), wanted, isOpen: openAt(9) })).has(425));
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
    assert.equal(planned + plan.ext.length + plan.none.length, data.game.natMax, id);
  }
});

test('gates: surfing needs Surf, and an area reached by water needs it too', () => {
  const data = loadGame('platinum');
  const P = createPlanner(data);
  const has = (owned) => (g) => owned.includes(g);
  const psyduckSurf = data.species.find((s) => s.id === 54).e.find((e) => e.m === 'surf');
  assert.deepEqual(P.gatesOf(psyduckSurf), ['surf']);
  const route221 = data.areas.find((a) => a.key === 'sinnoh-route-221');
  assert.deepEqual(route221.gt, ['surf']);
  const o = { story: 2, gates: ['surf'] };
  assert.deepEqual(lockOf(o, 8, has([])), { gate: 'surf' });
  assert.equal(lockOf(o, 8, has(['surf'])), null);
  assert.deepEqual(lockOf(o, 1, has(['surf'])), { story: 2 });
  assert.equal(lockOf(o, null, has([])), null);
});

test('Poké Radar encounters need the Poké Radar, not just badges', () => {
  const data = loadGame('platinum');
  const P = createPlanner(data);
  const radar = data.species.flatMap((s) => (s.e || []).flatMap((e) => (e.sp || []).filter((sp) => sp.c.some((c) => c.k === 'radar')).map((sp) => ({ e, sp }))))[0];
  assert.ok(radar, 'Platinum has Poké Radar encounters');
  assert.ok(P.gatesOf(radar.e, radar.sp).includes('poke-radar'));
});

test('Diamond and Pearl use their own gym order', () => {
  assert.equal(loadGame('diamond').game.stages[3].tag_en, 'Cobble Badge');
  assert.equal(loadGame('platinum').game.stages[3].tag_en, 'Relic Badge');
});

test('copy counts: random Wurmple split and gender-only evolutions are flagged', () => {
  const data = loadGame('platinum');
  const P = createPlanner(data);
  assert.ok(P.randomSplit.has(265), 'Wurmple');
  assert.ok(!P.randomSplit.has(133), 'Eevee evolutions are chosen, not random');
  const vespiquen = P.notesFor(P.best(416));
  assert.deepEqual(vespiquen.map((n) => [n.k, n.g, n.pct]), [['gender', 'f', 12.5]]);
  const gallade = P.notesFor(P.best(475));
  assert.ok(gallade.some((n) => n.k === 'gender' && n.g === 'm' && n.pct === 50));
});

test('form copies add to the group of their species', () => {
  const data = loadGame('platinum');
  const P = createPlanner(data);
  const list = data.species.filter((s) => s.id === 201);
  const extraForms = data.forms.filter((f) => f.sp === 201 && !f.def);
  const g = P.planGroups(list, new Set(), { extraForms }).stages.flatMap((s) => s.areas.flatMap((a) => a.groups))[0];
  assert.equal(g.need, 28);
  assert.equal(P.planGroups(list, new Set(['201', 'unown-b'])).stages.length, 1);
});

test('Nidoran and Volbeat/Illumise can be bred from their partner species', () => {
  const P = createPlanner(loadGame('platinum'));
  for (const id of [29, 32, 313, 314]) {
    const b = P.options(id).find((o) => o.k === 'breed');
    assert.ok(b, `breed option for ${id}`);
  }
  const vol = P.options(313).find((o) => o.k === 'breed');
  assert.ok([313, 314].includes(vol.from));
});

// ------------------------------------------------------------------ every generation

test('each game uses its own clock: Gen 2 nights start at 18:00, Gen 5 has seasons, Gen 1 and 3 have none', () => {
  const gold = loadGame('gold').game.clock, black = loadGame('black').game.clock;
  assert.equal(periodAt(at(17, 59), gold), 'd');
  assert.equal(periodAt(at(18, 0), gold), 'n');
  assert.equal(periodAt(at(19, 0)), 'd'); // Gen 4 default
  assert.equal(periodAt(new Date(2026, 0, 5), black), 'sp'); // January
  assert.equal(periodAt(new Date(2026, 5, 5), black), 'su'); // June
  assert.equal(periodAt(new Date(2026, 9, 11), black), 'su'); // October
  assert.equal(periodAt(new Date(2026, 11, 5), black), 'wi'); // December
  assert.equal(periodAt(at(12), loadGame('red').game.clock), 'a');
  assert.deepEqual(loadGame('black').game.periods, ['sp', 'su', 'au', 'wi']);
  assert.deepEqual(loadGame('emerald').game.periods, ['a']);
});

test('Gen 1 has no breeding: a single gift copy covers one member of its family', () => {
  const P = createPlanner(loadGame('red'), { starters: { 0: 1 } });
  assert.equal(P.canBreed, false);
  assert.equal(P.best(1).ext, null); // Bulbasaur is your starter
  assert.equal(P.best(2).ext, 'one'); // Ivysaur needs a second Bulbasaur
  assert.equal(P.best(133).ext, null); // the Celadon Eevee
  for (const id of [134, 135, 136]) assert.equal(P.best(id).ext, 'one', String(id));
  assert.equal(P.best(26).ext, null); // Raichu: wild Pikachu in Red
  assert.equal(createPlanner(loadGame('yellow')).best(26).ext, 'trade'); // Yellow's Pikachu won't evolve
});

test('games with eggs still breed extra copies of one-time gifts', () => {
  const P = createPlanner(loadGame('platinum'));
  assert.equal(P.canBreed, true);
  for (const id of [133, 134, 135, 136, 196, 197, 470, 471]) assert.notEqual(P.best(id).ext, 'one', String(id));
});

test('Gen 2 swarms count during the story; Crystal needs the Virtual Console for Celebi', () => {
  const P = createPlanner(loadGame('crystal'));
  assert.equal(P.best(251).ext, 'vc');
  assert.equal(createPlanner(loadGame('crystal'), { vc: true }).best(251).ext, null);
  const swarm = loadGame('gold').species.find((s) => s.id === 206).e.flatMap((e) => e.sp || []).find((sp) => sp.c.some((c) => c.k === 'swarm'));
  assert.equal(swarm.st, 0);
});

test('Gen 5 seasons: encounters and catch-right-now follow the season', () => {
  const data = loadGame('black');
  const seasonal = data.species.flatMap((s) => (s.e || []).filter((e) => !e.g && new Set(Object.values(e.t)).size > 1).map((e) => ({ s, e })));
  assert.ok(seasonal.length > 0);
  const P = createPlanner(data);
  const { s, e } = seasonal.find(({ e }) => e.t.wi === 0 && e.t.sp > 0 && e.m === 'walk') || seasonal[0];
  const now = (d) => P.catchNow({ date: d, wanted: (x) => x.id === s.id }).some((g) => g.area.id === e.a);
  if (e.t.wi === 0 && e.t.sp > 0) {
    assert.equal(now(new Date(2026, 0, 5, 12)), true);
    assert.equal(now(new Date(2026, 3, 5, 12)), false);
  }
});

test('Black 2 gets Registeel; Regice needs the other version\'s key', () => {
  const P = createPlanner(loadGame('black2'));
  assert.equal(P.best(379).ext, null);
  assert.equal(P.best(378).ext, 'other');
  const W = createPlanner(loadGame('white2'));
  assert.equal(W.best(378).ext, null);
  assert.equal(W.best(379).ext, 'other');
});

test('Karrablast and Shelmet evolve by trading for each other', () => {
  const data = loadGame('black');
  const S = new Map(data.species.map((s) => [s.id, s]));
  assert.equal(S.get(589).ev[0].ts, 616);
  assert.equal(S.get(617).ev[0].ts, 588);
});

test('Fairy is a Gen 6 type: Clefairy is Normal before HOME', () => {
  for (const id of ['red', 'platinum', 'black']) assert.deepEqual(loadGame(id).species.find((s) => s.id === 35).ty, [1], id);
  assert.deepEqual(loadGame('home').species.find((s) => s.id === 35).ty, [18]);
});

test('setupGames gives trade evolutions to games with a partner of the same generation (Gen 1 and 2 pair up)', () => {
  const alone = setupGames(loadGame('red'), []);
  assert.equal(alone.P.best(65).ext, 'trade');
  const withGold = setupGames(loadGame('red'), [loadGame('gold')]);
  assert.equal(withGold.P.best(65).ext, null);
});
