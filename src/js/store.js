// Saved settings and boxed Pokémon, per game, in localStorage. Every access is guarded:
// storage can be missing or throw (private windows, blocked site data).

const KEY = 'livingDex.v2';
const OLD_KEY = 'ptLivingDex.v1';

function read(key) {
  try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : null; } catch { return null; }
}

export function defaultLang() {
  try { return (navigator.language || '').toLowerCase().startsWith('es') ? 'es' : 'en'; } catch { return 'en'; }
}

export function freshState(defaultGame = 'platinum') {
  return { v: 2, lang: defaultLang(), game: defaultGame, tab: 'plan', hide: false, nowOpen: true,
    areaSort: 'stage', boxTap: 'box', games: {} };
}

export function gameState(state, gameId) {
  if (!state.games[gameId]) state.games[gameId] = {};
  const g = state.games[gameId];
  g.caught ??= [];
  g.starters ??= {};
  g.progress ??= null;
  g.scope ??= 'regional';
  g.onlyNow ??= false;
  g.boxForms ??= false;
  g.boxStart ??= 1;
  return g;
}

export function loadState(defaultGame) {
  const state = Object.assign(freshState(defaultGame), read(KEY) || {});
  if (!read(KEY)) {
    const old = read(OLD_KEY); // version 1 was Platinum only
    if (old) {
      const g = gameState(state, 'platinum');
      g.caught = (old.caught || []).map(String);
      if (old.starter) g.starters = { 0: old.starter };
      g.scope = old.scope === 'national' ? 'national' : 'regional';
      state.hide = !!old.hide;
      state.tab = old.tab || 'plan';
    }
  }
  return state;
}

export function saveState(state) {
  try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* storage unavailable */ }
}
