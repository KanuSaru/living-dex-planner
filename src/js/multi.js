// Plans across the games you own (pure, no DOM).
// For each Pokémon: get it in your main game if you can; otherwise from another Gen 4 game you own by trading,
// or from a Gen 3 game you own through Pal Park (which opens after the National Dex in the main game).

const RANK = { trade: 1, palpark: 2 };
const SINNOH = ['diamond', 'pearl', 'platinum'];

// main: { id, gen, P }; sources: [{ id, gen, P, data, T }]
export function createMulti(main, sources, { trade = true, palPark = true } = {}) {
  const natStage = Math.max(0, main.P.game.stages.findIndex((s) => s.post));
  const usable = sources.filter((s) => (s.gen === 4 ? trade : palPark));
  const memo = new Map();

  function best(id) {
    if (memo.has(id)) return memo.get(id);
    const mb = main.P.best(id);
    let out = null;
    if (mb && !mb.ext) out = { where: main.id, o: mb, via: null, st: mb.st, story: mb.story, gates: mb.gates };
    else {
      let pick = null;
      for (const src of usable) {
        if (src.gen === 3 && id > 386) continue;
        const b = src.P.best(id);
        if (!b || (b.ext && b.ext !== 'starter')) continue;
        const via = src.gen === 3 ? 'palpark' : 'trade';
        // Pal Park needs the National Dex in the main game; trading works any time
        const cand = { where: src.id, o: b, via, src, st: via === 'palpark' ? natStage : 0, rank: RANK[via],
          story: 0, gates: via === 'palpark' && main.P.game.gates && 'national-dex' in main.P.game.gates ? ['national-dex'] : [] };
        if (!pick || cand.rank < pick.rank || (cand.rank === pick.rank && b.st < pick.o.st)) pick = cand;
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

  // a form that needs a trade from another game you own
  function formSource(form) {
    if (!trade) return null;
    for (const h of form.how || []) {
      if (h.k !== 'trade-in') continue;
      const want = h.v === 'sinnoh' ? SINNOH : [h.v];
      const src = sources.find((s) => want.includes(s.id));
      if (src) return src.id;
    }
    return null;
  }

  const sourceById = new Map(sources.map((s) => [s.id, s]));
  return { main, sources, natStage, best, status, formSource, source: (id) => sourceById.get(id) };
}
