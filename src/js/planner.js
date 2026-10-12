// Planner logic. Pure functions over one game's data file: no DOM, so it runs in Node tests too.
//
// Every option (a way to get a Pokémon) carries:
//   story  – the story stage (≈ badges) needed to reach it
//   gates  – field moves and key items it needs (Surf, Good Rod, Poké Radar, National Dex…)
//   st     – the overall stage, max(story, the stage at which you normally have each gate); used for ordering

export const PERIODS = ['m', 'd', 'n'];
export const SEASONS = ['sp', 'su', 'au', 'wi'];
export const WEEKDAYS = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
export const CONTEST_DAYS = ['tuesday', 'thursday', 'saturday'];
const GEN4_CLOCK = { kind: 'tod', hours: [4, 10, 20] };

// The game's clock at this moment: 'm' | 'd' | 'n' (Gen 2: night from 18:00, Gen 4: from 20:00),
// a season for Gen 5 ('sp' January, May, September; 'su' the month after, and so on), or 'a' for games without one.
export function periodAt(date, clock = GEN4_CLOCK) {
  if (!clock) return 'a';
  if (clock.kind === 'season') return SEASONS[date.getMonth() % 4];
  const [morning, day, night] = clock.hours;
  const h = date.getHours();
  if (h >= morning && h < day) return 'm';
  if (h >= day && h < night) return 'd';
  return 'n';
}
export function weekdayAt(date) {
  return WEEKDAYS[date.getDay()];
}

// Lower is easier. Anything external sorts after everything you can do in your own game.
const EXT_RANK = { gba: 1, vc: 1, trade: 2, starter: 2, one: 2, other: 3, event: 4 };
const extRank = (x) => (x ? EXT_RANK[x] || 3 : 0);

// Conditions the player can satisfy on the spot (vs. luck-of-the-day ones like swarms).
const INSTANT = new Set(['radar', 'radio', 'headbutt', 'give', 'coins', 'fossil', 'story', 'other', 'item', 'natdex',
  'weekday', 'contest', 'time', 'tv', 'starter-was', 'season', 'key']);

// Breeding across gender-split species: an egg can hatch as either one.
const BREED_PARTNERS = { 29: [32], 32: [29], 313: [314], 314: [313] };

export function condReady(c, { period, weekday }) {
  if (!INSTANT.has(c.k)) return false;
  if (c.k === 'weekday') return c.v === weekday;
  if (c.k === 'contest') return CONTEST_DAYS.includes(weekday);
  if (c.k === 'time' || c.k === 'season') return c.v === period;
  return true;
}

// Why an option is locked at your progress, or null if you can do it now.
// progress: your story stage (null = show everything); has(gate) → whether you have that move or item.
export function lockOf(x, progress, has) {
  if (progress == null || !x) return null;
  for (const g of x.gates || []) if (!has(g)) return { gate: g };
  if ((x.story || 0) > progress) return { story: x.story };
  return null;
}

const uniq = (a) => [...new Set(a)];

// options: starters {group: speciesId}; gba: Set of owned GBA games (unlocks dual-slot encounters);
// tradeEvolutions: true when you can trade with another game of the same generation you own;
// vc: your Gen 1/2 games are the 3DS Virtual Console releases (Crystal's GS Ball Celebi)
export function createPlanner(data, { starters = {}, gba = null, tradeEvolutions = false, vc = false } = {}) {
  const G = data.game;
  const periods = G.periods || PERIODS;
  const canBreed = G.dayCareStage !== null;
  const S = new Map(data.species.map((s) => [s.id, s]));
  const A = new Map(data.areas.map((a) => [a.id, a]));
  const areaOrder = new Map(data.areas.map((a, i) => [a.id, i]));
  const GATES = G.gates || {};
  const MG = G.methodGates || {};
  const families = new Map();
  const children = new Map();
  for (const s of data.species) {
    if (!families.has(s.ch)) families.set(s.ch, []);
    families.get(s.ch).push(s);
    if (s.f) {
      if (!children.has(s.f)) children.set(s.f, []);
      children.get(s.f).push(s);
    }
  }
  const formsBySpecies = new Map();
  for (const f of data.forms || []) {
    if (!formsBySpecies.has(f.sp)) formsBySpecies.set(f.sp, []);
    formsBySpecies.get(f.sp).push(f);
  }

  // parents whose evolution is decided at random (Wurmple → Silcoon or Cascoon)
  const randomSplit = new Set();
  for (const [pid, kids] of children) {
    if (kids.length < 2) continue;
    const sig = kids.map((k) => JSON.stringify((k.ev || []).map((e) => ({ t: e.t, lv: e.lv, keys: Object.keys(e).sort() }))));
    if (sig.every((x) => x === sig[0]) && kids.every((k) => (k.ev || []).every((e) => e.t === 'level' && e.lv && Object.keys(e).every((key) => ['t', 'lv', 'st'].includes(key))))) randomSplit.add(pid);
  }

  function levelStage(level) {
    const caps = G.levelCaps || [];
    for (let i = 0; i < caps.length; i++) if (level <= caps[i]) return i;
    return caps.length;
  }
  const gateStage = (gates) => Math.max(0, ...gates.map((g) => GATES[g] ?? 0));
  function gatesOf(e, sp = null) {
    return uniq([...(A.get(e.a).gt || []), ...(MG[e.m] || []), ...(e.gt || []), ...((sp && sp.gt) || [])]);
  }
  function effStage(e) {
    return Math.max(A.get(e.a).st, gateStage(gatesOf(e)), e.cst || 0);
  }
  const withStage = (o) => { o.st = Math.max(o.story, gateStage(o.gates)); return o; };

  function catchOptions(s) {
    const out = [];
    for (const e of s.e || []) {
      const a = A.get(e.a);
      if (e.g) {
        let ext = (e.ext || []).find((x) => !(x === 'vc' && vc)) || null;
        const cond = e.req || [];
        let starterNote = null;
        if (e.sg != null && starters[e.sg] !== s.id) {
          ext = starters[e.sg] ? 'trade' : 'starter';
          starterNote = starters[e.sg] ? 'other-starter' : 'choose-starter';
        }
        out.push(withStage({ k: 'catch', s: s.id, e, a, story: Math.max(a.st, e.cst || 0), gates: gatesOf(e), p: 100,
          cond, starterNote, special: cond.length > 0 || !!starterNote, ext, lv: e.lv[0], lvMax: e.lv[1] }));
      } else {
        const mx = Math.max(...periods.map((p) => e.t[p] || 0));
        if (mx > 0) {
          const cond = [];
          if (periods.some((p) => !e.t[p])) cond.push({ k: 'periods', v: periods.filter((p) => e.t[p] > 0) });
          out.push(withStage({ k: 'catch', s: s.id, e, a, story: Math.max(a.st, e.cst || 0), gates: gatesOf(e), p: mx, cond, special: false,
            ext: null, lv: e.lv[0], lvMax: e.lv[1] }));
        }
        for (const sp of e.sp || []) {
          let ext = sp.ext || null;
          const slot = sp.c.filter((c) => c.k === 'slot2');
          if (ext === 'gba' && gba && slot.length && slot.every((c) => gba.has(c.v))) ext = null;
          out.push(withStage({ k: 'catch', s: s.id, e, a, story: Math.max(a.st, sp.st, e.cst || 0), gates: gatesOf(e, sp), p: sp.p,
            cond: sp.c, special: true, ext, lv: e.lv[0], lvMax: e.lv[1] }));
        }
      }
    }
    for (const o of out) { o.root = o; o.path = []; }
    return out;
  }

  function score(o) {
    const kind = o.k === 'catch' ? 0 : o.k === 'evolve' ? 0.5 : o.k === 'breed' ? 1 : 2;
    return [extRank(o.ext), o.st, kind, o.special ? 1 : 0, -o.p, o.lv || 0];
  }
  function better(a, b) {
    const x = score(a), y = score(b);
    for (let i = 0; i < x.length; i++) if (x[i] !== y[i]) return x[i] < y[i];
    return false;
  }
  function pick(opts) {
    let b = null;
    for (const o of opts) if (!b || better(o, b)) b = o;
    return b;
  }

  function evolveOpt(s, pb, ev) {
    const lvSt = ev.lv && ev.lv > pb.lvMax ? levelStage(ev.lv) : 0;
    const viaTrade = ev.t === 'trade' && tradeEvolutions;
    return withStage({ k: 'evolve', s: s.id, from: pb.s, ev, parent: pb, root: pb.root, viaTrade,
      story: Math.max(pb.story, ev.st || 0, lvSt), gates: pb.gates, p: pb.p, special: pb.special,
      ext: (viaTrade ? null : ev.ext) || pb.ext, lv: pb.lv, lvMax: Math.max(pb.lvMax, ev.lv || 0),
      path: [...pb.path, { to: s.id, from: pb.s, ev }] });
  }

  const nbMemo = new Map();
  function noBreedOptions(s) {
    if (nbMemo.has(s.id)) return nbMemo.get(s.id);
    nbMemo.set(s.id, []);
    const opts = catchOptions(s);
    if (s.f && s.ev) {
      const pb = pick(noBreedOptions(S.get(s.f)));
      if (pb) for (const ev of s.ev) opts.push(evolveOpt(s, pb, ev));
    }
    nbMemo.set(s.id, opts);
    return opts;
  }

  // Breeding gives the lowest stage of a family (or the post-baby stage when the baby needs an incense).
  function breedOption(s) {
    if (!canBreed || s.leg || s.myth && s.id !== 489) return null;
    let members, either = false;
    if (s.id === 489) members = [S.get(490)];
    else {
      const parent = s.f ? S.get(s.f) : null;
      const viaIncense = parent && parent.baby && parent.inc;
      if (s.f && !viaIncense) return null;
      members = families.get(s.ch).filter((m) => m.id !== s.id && !m.baby && !m.noegg && !m.ditto);
      for (const pid of BREED_PARTNERS[s.id] || []) {
        members.push(...families.get(S.get(pid).ch).filter((m) => !m.baby && !m.noegg));
        either = true;
      }
    }
    const ditto = S.get(132);
    const dittoBest = ditto ? pick(noBreedOptions(ditto)) : null;
    let best = null, who = null, needsDitto = false;
    for (const m of members) {
      const o = pick(noBreedOptions(m));
      if (!o) continue;
      const mustDitto = m.gr === -1 || m.gr === 0 || m.id === 490;
      let cand = o;
      if (mustDitto) {
        if (!dittoBest) continue;
        cand = withStage({ ...o, story: Math.max(o.story, dittoBest.story), gates: uniq([...o.gates, ...dittoBest.gates]),
          ext: o.ext || dittoBest.ext });
      }
      if (!best || better(cand, best)) { best = cand; who = m; needsDitto = mustDitto; }
    }
    if (!best) return null;
    return withStage({ k: 'breed', s: s.id, from: who.id, parent: best, root: best.root,
      story: Math.max(best.story, G.dayCareStage ?? 2), gates: best.gates, p: best.p, special: best.special,
      ext: best.ext, lv: 1, lvMax: 1, needsDitto, either: either && who.ch !== s.ch,
      incense: s.baby && s.inc ? s.inc : null, withoutIncense: s.f && S.get(s.f).baby ? S.get(s.f).inc : null,
      path: [...best.path] });
  }

  const memo = new Map();
  function options(id) {
    if (memo.has(id)) return memo.get(id);
    memo.set(id, []);
    const s = S.get(id);
    const opts = catchOptions(s);
    if (s.f && s.ev) {
      const pb = pick(options(s.f));
      if (pb) for (const ev of s.ev) opts.push(evolveOpt(s, pb, ev));
    }
    const b = breedOption(s);
    if (b) opts.push(b);
    if (!opts.length && s.myth) {
      opts.push({ k: 'event', s: s.id, story: 0, gates: [], st: 0, p: 0, special: true, ext: 'event', lv: 0, lvMax: 0, path: [], root: null });
    }
    memo.set(id, opts);
    return opts;
  }

  const bestMap = new Map();
  for (const s of data.species) bestMap.set(s.id, pick(options(s.id)));

  // A one-time gift or static Pokémon gives one copy. When its family can't be bred (Gen 1 has no eggs, legendaries
  // never breed), only one target can use that copy; the others need another way, or another game ('one').
  const familyBreeds = (s) => canBreed && !s.leg && !s.myth && !s.noegg && (s.gr !== -1 || S.has(132));
  const byOneRoot = new Map();
  for (const s of data.species) {
    const b = bestMap.get(s.id);
    if (!b || b.ext || !b.root || !b.root.e || !b.root.e.one) continue;
    if (!byOneRoot.has(b.root)) byOneRoot.set(b.root, []);
    byOneRoot.get(b.root).push(s.id);
  }
  for (const [root, ids] of byOneRoot) {
    if (ids.length < 2 || familyBreeds(S.get(root.s))) continue;
    const users = ids.filter((id) => !(bestMap.get(id).k === 'evolve' && bestMap.get(id).path.at(-1).ev.t === 'shed'));
    users.sort((x, y) => bestMap.get(x).path.length - bestMap.get(y).path.length || x - y);
    for (const id of users.slice(1)) {
      const alt = pick(options(id).filter((o) => o.root !== root && !o.ext));
      bestMap.set(id, alt || { ...bestMap.get(id), ext: 'one' });
    }
  }
  const best = (id) => bestMap.get(id) || null;

  function status(id) {
    const b = best(id);
    if (!b) return 'none';
    if (b.ext) return 'ext';
    return b.k;
  }

  // a Shedinja-style evolution costs no extra copy of the root Pokémon
  const freeCopy = (b) => b.k === 'evolve' && b.path.length && b.path[b.path.length - 1].ev.t === 'shed';

  // what to watch out for on the way to a target: gender-only evolutions and random branches
  function notesFor(b) {
    const notes = [];
    for (const step of b.path || []) {
      if (step.ev.g) {
        const from = S.get(step.from);
        const female = from.gr >= 0 ? (from.gr / 8) * 100 : 0;
        notes.push({ k: 'gender', g: step.ev.g, from: step.from, to: step.to, pct: step.ev.g === 'f' ? female : 100 - female });
      }
      if (randomSplit.has(step.from)) notes.push({ k: 'random', from: step.from, options: children.get(step.from).map((c) => c.id) });
    }
    return notes;
  }

  // list: species to plan; caught: Set of boxed keys; extraForms: alternate forms that need their own copy
  function planGroups(list, caught, { extraForms = [] } = {}) {
    const roots = new Map();
    const bySpecies = new Map();
    const ext = [], none = [];
    for (const s of list) {
      const b = best(s.id);
      if (!b) { none.push(s); continue; }
      if (b.ext || !b.root) { ext.push({ s, b }); continue; }
      const r = b.root;
      const key = `${r.s}|${r.e.a}|${r.e.m}|${JSON.stringify(r.cond)}`;
      if (!roots.has(key)) roots.set(key, { r, targets: [], forms: [] });
      roots.get(key).targets.push({ s, b });
      bySpecies.set(s.id, roots.get(key));
    }
    for (const f of extraForms) {
      const g = bySpecies.get(f.sp);
      if (g) g.forms.push(f);
    }
    const stages = new Map();
    for (const g of roots.values()) {
      g.targets.sort((x, y) => x.b.path.length - y.b.path.length || x.s.id - y.s.id);
      g.need = g.targets.filter((t) => t.b.k !== 'breed' && !freeCopy(t.b) && !caught.has(String(t.s.id))).length
        + g.forms.filter((f) => !caught.has(f.key)).length;
      g.bred = g.targets.filter((t) => t.b.k === 'breed' && !caught.has(String(t.s.id))).length;
      const seen = new Set();
      g.notes = [];
      for (const t of g.targets) {
        if (caught.has(String(t.s.id))) continue;
        for (const n of notesFor(t.b)) {
          const k = `${n.k}|${n.from}|${n.to || ''}`;
          if (!seen.has(k)) { seen.add(k); g.notes.push(n); }
        }
      }
      const st = g.r.st;
      if (!stages.has(st)) stages.set(st, new Map());
      const byArea = stages.get(st);
      if (!byArea.has(g.r.e.a)) byArea.set(g.r.e.a, []);
      byArea.get(g.r.e.a).push(g);
    }
    const ordered = [...stages.keys()].sort((a, b) => a - b).map((st) => ({
      st,
      areas: [...stages.get(st).entries()]
        .sort((x, y) => areaOrder.get(x[0]) - areaOrder.get(y[0]))
        .map(([a, groups]) => ({ area: A.get(a), groups: groups.sort((x, y) => x.r.s - y.r.s) })),
    }));
    return { stages: ordered, ext, none };
  }

  // Encounters you can use at this moment: reachable with your progress, right time and weekday, no luck needed.
  // isOpen(story, gates) decides reachability; leave it out to ignore progress.
  function catchNow({ date, wanted, isOpen = () => true }) {
    const period = periodAt(date, G.clock === undefined ? GEN4_CLOCK : G.clock), weekday = weekdayAt(date);
    const ctx = { period, weekday };
    const byArea = new Map();
    for (const s of data.species) {
      if (!wanted(s)) continue;
      for (const e of s.e || []) {
        const a = A.get(e.a);
        let rate = 0, cond = [];
        if (e.g) {
          if ((e.ext || []).some((x) => !(x === 'vc' && vc))) continue;
          if (e.sg != null && starters[e.sg] !== s.id) continue;
          if (!(e.req || []).every((c) => condReady(c, ctx))) continue;
          if (!isOpen(Math.max(a.st, e.cst || 0), gatesOf(e))) continue;
          rate = 100; cond = e.req || [];
        } else {
          if (isOpen(Math.max(a.st, e.cst || 0), gatesOf(e))) rate = e.t[period] || 0;
          for (const sp of e.sp || []) {
            if (sp.ext || !isOpen(Math.max(a.st, sp.st, e.cst || 0), gatesOf(e, sp))) continue;
            if (sp.c.every((c) => condReady(c, ctx)) && sp.p > rate) { rate = sp.p; cond = sp.c; }
          }
        }
        if (rate <= 0) continue;
        if (!byArea.has(e.a)) byArea.set(e.a, new Map());
        const m = byArea.get(e.a);
        const prev = m.get(s.id);
        if (!prev || prev.rate < rate) m.set(s.id, { s, e, rate, cond });
      }
    }
    return [...byArea.entries()]
      .sort((x, y) => areaOrder.get(x[0]) - areaOrder.get(y[0]))
      .map(([a, m]) => ({ area: A.get(a), items: [...m.values()].sort((x, y) => y.rate - x.rate || x.s.id - y.s.id) }));
  }

  function formStatus(f) {
    let st = f.st || 0, ext = f.ext || null;
    if (f.dep) {
      const b = best(f.dep);
      if (!b) return ext ? { st, ext } : null;
      st = Math.max(st, b.st);
      ext = ext || b.ext;
    }
    return { st, ext };
  }

  function areaSpecies() {
    const m = new Map();
    for (const s of data.species) for (const e of s.e || []) {
      if (!m.has(e.a)) m.set(e.a, []);
      m.get(e.a).push({ s, e });
    }
    return m;
  }

  function descendants(id) {
    const out = [], stack = [id];
    while (stack.length) {
      for (const c of children.get(stack.pop()) || []) { out.push(c); stack.push(c.id); }
    }
    return out;
  }

  return { data, game: G, S, A, areaOrder, families, children, formsBySpecies, best, options, status, effStage,
    gatesOf, gateStage, levelStage, planGroups, catchNow, formStatus, areaSpecies, descendants, freeCopy, notesFor,
    randomSplit, periods, canBreed };
}
