// Plans across the games you own (pure, no DOM).
// For each Pokémon: get it in your main game if you can; otherwise in another game you own, then move it along
// the real transfer chain:
//   trade        same generation (two systems)
//   timecapsule  Gen 1 ↔ Gen 2 (Gen 2 → Gen 1 only for the first 151)
//   palpark      Gen 3 → Gen 4 (a DS with a GBA slot; opens after the National Dex in the Gen 4 game)
//   transfer     Gen 4 → Gen 5, Poké Transfer (two DS systems; opens after the Hall of Fame in the Gen 5 game)
//   bank         Gen 5, or the 3DS Virtual Console Gen 1/2 games → Pokémon HOME (Poké Transporter and Pokémon Bank)
// Moves are one-way except trades and the Time Capsule, and a Pokémon can pass through several of your games.

import { createPlanner } from './planner.js';

export const HOP_RANK = { trade: 1, timecapsule: 1, palpark: 2, transfer: 2, bank: 2 };
// the gate each kind of move needs in the game it arrives in, when that game has the gate
const ARRIVAL_GATE = { palpark: 'national-dex', transfer: 'poke-transfer', timecapsule: 'time-capsule' };
const FRLG = ['firered', 'leafgreen'];
const NAT = [151, 251, 386, 493, 649, 1025];

// hw: { trade, gba, bank, vc }
export function hopKind(from, to, hw) {
  if (from.home || from.id === to.id) return null;
  if (to.home) return hw.bank && (from.gen === 5 || (from.gen <= 2 && hw.vc)) ? 'bank' : null;
  if (from.gen === to.gen) return hw.trade ? 'trade' : null;
  if (from.gen <= 2 && to.gen <= 2) return hw.trade ? 'timecapsule' : null;
  if (from.gen === 3 && to.gen === 4) return hw.gba ? 'palpark' : null;
  if (from.gen === 4 && to.gen === 5) return hw.trade ? 'transfer' : null;
  return null;
}

// main and sources: { id, gen, home?, natMax, P, data? }
export function createMulti(main, sources, hw = {}) {
  hw = { trade: true, gba: true, bank: false, vc: false, ...hw };
  const nodes = [main, ...sources];
  const natOf = (g) => g.natMax || g.P.game.natMax || 493;
  const gatesFor = (kind) => {
    const g = ARRIVAL_GATE[kind];
    return g && main.P.game.gates && g in main.P.game.gates ? [g] : [];
  };
  // RSE ↔ FRLG trades need the network machine fixed in FireRed or LeafGreen (after the National Dex there)
  const frlgLink = (a, b) => a.gen === 3 && b.gen === 3 && FRLG.includes(a.id) !== FRLG.includes(b.id);

  // cheapest chain of moves from a source to the main game, through games that can hold a Pokémon numbered up to `cap`
  const pathMemo = new Map();
  function pathFrom(src, cap) {
    const key = `${src.id}|${cap}`;
    if (pathMemo.has(key)) return pathMemo.get(key);
    const dist = new Map([[src.id, { cost: 0, hops: [] }]]);
    const todo = [src];
    const done = new Set();
    while (todo.length) {
      todo.sort((a, b) => dist.get(a.id).cost - dist.get(b.id).cost);
      const cur = todo.shift();
      if (done.has(cur.id)) continue;
      done.add(cur.id);
      if (cur.id === main.id) break;
      for (const nxt of nodes) {
        if (done.has(nxt.id) || natOf(nxt) < cap) continue;
        const k = hopKind(cur, nxt, hw);
        if (!k) continue;
        const cost = dist.get(cur.id).cost + HOP_RANK[k];
        const prev = dist.get(nxt.id);
        if (!prev || cost < prev.cost) {
          const hop = { k, from: cur.id, to: nxt.id };
          if (k === 'trade' && frlgLink(cur, nxt)) hop.note = 'frlg-network';
          dist.set(nxt.id, { cost, hops: [...dist.get(cur.id).hops, hop] });
          todo.push(nxt);
        }
      }
    }
    const out = dist.get(main.id) || null;
    pathMemo.set(key, out);
    return out;
  }
  const capFor = (id) => NAT.find((n) => n >= id) || id;

  function arrival(hops) {
    const last = hops[hops.length - 1];
    let gates = gatesFor(last.k);
    if (last.note === 'frlg-network' && FRLG.includes(main.id)) gates = [...gates, 'national-dex'];
    gates = gates.filter((g) => main.P.game.gates && g in main.P.game.gates);
    return { gates, st: Math.max(0, ...gates.map((g) => main.P.game.gates[g])) };
  }

  const memo = new Map();
  function best(id) {
    if (memo.has(id)) return memo.get(id);
    const mb = main.P.best(id);
    let out = null;
    if (mb && !mb.ext) out = { where: main.id, o: mb, via: null, st: mb.st, story: mb.story, gates: mb.gates };
    else {
      let pick = null;
      for (const src of sources) {
        if (natOf(src) < id) continue;
        const b = src.P.best(id);
        if (!b || (b.ext && b.ext !== 'starter')) continue;
        const path = pathFrom(src, capFor(id));
        if (!path) continue;
        const arr = arrival(path.hops);
        const cand = { where: src.id, o: b, via: path.hops, src, cost: path.cost, st: arr.st, story: 0, gates: arr.gates };
        if (!pick || cand.cost < pick.cost || (cand.cost === pick.cost && b.st < pick.o.st)) pick = cand;
      }
      out = pick || (mb ? { where: main.id, o: mb, via: null, st: mb.st, story: mb.story, gates: mb.gates } : null);
    }
    memo.set(id, out);
    return out;
  }

  // 'catch' | 'evolve' | 'breed' | 'event' | 'ext' | 'xfer' | 'none'
  function status(id) {
    const b = best(id);
    if (!b) return 'none';
    if (b.via) return 'xfer';
    if (b.o.ext) return 'ext';
    return b.o.k;
  }

  // where to get an alternate form your main game can't: { where, via, st } or null
  const formMemo = new Map();
  function formBest(form) {
    if (formMemo.has(form.key)) return formMemo.get(form.key);
    let pick = null;
    for (const src of sources) {
      if (!src.data || natOf(src) < form.sp) continue;
      const sf = src.data.forms.find((f) => f.key === form.key);
      if (!sf) continue;
      const st = src.P.formStatus(sf);
      if (!st || st.ext) continue;
      const path = pathFrom(src, capFor(form.sp));
      if (!path) continue;
      const cand = { where: src.id, via: path.hops, cost: path.cost, st: arrival(path.hops).st, srcSt: st.st };
      if (!pick || cand.cost < pick.cost || (cand.cost === pick.cost && cand.srcSt < pick.srcSt)) pick = cand;
    }
    formMemo.set(form.key, pick);
    return pick;
  }
  const formSource = (form) => (formBest(form) || {}).where || null;

  const sourceById = new Map(sources.map((s) => [s.id, s]));
  return { main, sources, hw, best, status, formBest, formSource, pathFrom, source: (id) => sourceById.get(id) };
}

// Builds the planners for a main game and the other games you own, the way the app uses them.
// main: data file; owned: [data file]; hw: { trade, gba, bank, vc }; startersOf(gameId) → { group: speciesId }
export function setupGames(main, owned, hw = {}, startersOf = () => ({})) {
  hw = { trade: true, gba: true, bank: false, vc: false, ...hw };
  owned = owned.filter((d) => d.game.id !== main.game.id && !d.game.home);
  const all = [main, ...owned];
  // trades within a generation, and Time Capsule trades between Gen 1 and Gen 2, set off trade evolutions
  const tradeGroup = (g) => (g <= 2 ? 'gb' : String(g));
  const hasPartner = (d) => hw.trade && !d.game.home
    && all.some((o) => o !== d && !o.game.home && tradeGroup(o.game.gen) === tradeGroup(d.game.gen));
  const gba = hw.gba ? new Set(owned.filter((d) => d.game.gen === 3).map((d) => d.game.id)) : null;
  const make = (d) => createPlanner(d, { starters: startersOf(d.game.id), gba: d.game.gen === 4 ? gba : null,
    tradeEvolutions: hasPartner(d), vc: !!hw.vc });
  const node = (d) => ({ id: d.game.id, gen: d.game.gen, home: !!d.game.home, natMax: d.game.natMax, data: d, P: make(d) });
  const mainNode = node(main);
  const sources = owned.map(node);
  return { P: mainNode.P, sources, M: createMulti(mainNode, sources, hw) };
}
