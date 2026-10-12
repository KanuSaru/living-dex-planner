// App controller: loads data, keeps state, renders views and handles events.
import { getLang, setLang, t } from './i18n.js';
import { createPlanner, periodAt } from './planner.js';
import { createMulti } from './multi.js';
import { createText } from './text.js';
import { gameState, loadState, saveState } from './store.js';
import { decodeProgress, peekProgress } from './progress-code.js';
import { esc } from './dom.js';
import * as Plan from './views/plan.js';
import * as Dex from './views/dex.js';
import * as Forms from './views/forms.js';
import * as Boxes from './views/boxes.js';
import * as Areas from './views/areas.js';
import * as Detail from './views/detail.js';
import * as Sync from './views/sync.js';
import * as Games from './views/games.js';

const TABS = ['plan', 'dex', 'boxes', 'forms', 'areas'];
const VIEWS = { plan: Plan, dex: Dex, boxes: Boxes, forms: Forms, areas: Areas };
const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------- data sources
// The single-file build embeds everything in <script type="application/json"> tags; the website fetches files.
const embedCache = new Map();
function embedded(id) {
  if (!embedCache.has(id)) {
    const el = document.getElementById(id);
    embedCache.set(id, el ? JSON.parse(el.textContent) : null);
  }
  return embedCache.get(id);
}
const EMBEDDED = !!document.getElementById('ld-index');
async function fetchJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}
const loadIndex = () => embedded('ld-index') || fetchJSON('data/index.json');
const loadGameData = (id) => embedded(`ld-data-${id}`) || fetchJSON(`data/${id}.json`);
const loadAvailability = () => embedded('ld-avail') || fetchJSON('data/availability.json').catch(() => null);
// absolute URL: a relative url() inside a CSS variable resolves against the stylesheet, not the page
const spriteURL = (set) => (embedded('ld-sprites') || {})[set] || new URL(`sprites/${set}.webp`, document.baseURI).href;

// ------------------------------------------------------------------------ state
let index, avail;
const state = loadState('platinum');
setLang(state.lang);
let ctx = null;
const dataCache = new Map();
let installPrompt = null;
let menuDraft = null; // edits in the My games menu until saved
const metaOf = (id) => index.games.find((g) => g.id === id);

function save() {
  if (ctx) ctx.gs.caught = [...ctx.caught];
  saveState(state);
}

function buildCtx(data) {
  const gs = gameState(state, data.game.id);
  // other games you own: Gen 4 games trade with the main game, Gen 3 games reach it through Pal Park
  const ownedIds = (state.owned || []).filter((id) => id !== data.game.id && dataCache.has(id) && metaOf(id))
    .sort((a, b) => metaOf(b).gen - metaOf(a).gen || index.games.indexOf(metaOf(a)) - index.games.indexOf(metaOf(b)));
  const gen4 = 1 + ownedIds.filter((id) => metaOf(id).gen === 4).length;
  const tradeEvolutions = !!state.hw.trade && gen4 >= 2;
  const gba = state.hw.gba ? new Set(ownedIds.filter((id) => metaOf(id).gen === 3)) : null;
  const P = createPlanner(data, { starters: gs.starters, gba, tradeEvolutions });
  const T = createText(data);
  const sources = ownedIds.map((id) => {
    const d = dataCache.get(id);
    const gen = metaOf(id).gen;
    return { id, gen, data: d, T: createText(d),
      P: createPlanner(d, { starters: gameState(state, id).starters, tradeEvolutions: gen === 4 && tradeEvolutions }) };
  });
  const M = createMulti({ id: data.game.id, gen: 4, P }, sources, { trade: !!state.hw.trade, palPark: !!state.hw.gba });
  const prev = ctx && ctx.data === data ? ctx : null;
  const c = {
    index, data, P, T, M, state, gs, avail, embedded: EMBEDDED, metaOf,
    caught: new Set(gs.caught.map(String)),
    current: prev ? prev.current : null,
    openAreas: prev ? prev.openAreas : new Set(),
    ui: prev ? prev.ui : { dexQuery: '', dexFilter: 'all', areaQuery: '', syncMsg: '', pasteDraft: '', syncOpen: false, boxGaps: false },
    now: new Date(),
    get lang() { return getLang(); },
    get period() { return periodAt(this.now); },
    areaSpecies: P.areaSpecies(),
    inScope: (s) => gs.scope === 'national' || s.rd != null,
    dexNo: (s) => (gs.scope === 'regional' && s.rd != null ? s.rd : s.id),
  };
  c.scopeList = () => data.species.filter(c.inScope);
  return c;
}

function rebuildPlanner() {
  ctx = buildCtx(ctx.data);
}

async function switchGame(id, { keepScroll = false } = {}) {
  let meta = metaOf(id);
  if (!meta || !meta.main) meta = metaOf(index.default);
  state.game = meta.id;
  for (const gid of [meta.id, ...(state.owned || [])]) {
    const m = metaOf(gid);
    if (!m || dataCache.has(gid)) continue;
    $('tabs-body').innerHTML = `<div class="empty">${esc(t('loading', { game: m.name[getLang()] || m.name.en }))}</div>`;
    try {
      dataCache.set(gid, await loadGameData(gid));
    } catch (err) {
      if (gid === meta.id) {
        $('tabs-body').innerHTML = `<div class="empty error">${esc(t('load.error', { game: m.name[getLang()] || m.name.en }))}</div>`;
        return;
      }
    }
  }
  const data = dataCache.get(meta.id);
  ctx = null;
  ctx = buildCtx(data);
  document.documentElement.style.setProperty('--sheet', `url("${spriteURL(data.game.sprites)}")`);
  save();
  renderAll();
  if (!keepScroll) window.scrollTo(0, 0);
}

// ---------------------------------------------------------------------- render
function headerHTML() {
  const { T, gs, data } = ctx;
  const game = T.game();
  const list = ctx.scopeList();
  const boxed = list.filter((s) => ctx.caught.has(String(s.id))).length;
  const reach = list.filter((s) => { const b = ctx.M.best(s.id); return b && (b.via || !b.o.ext); }).length;
  const owned = (state.owned || []).filter((id) => id !== data.game.id && metaOf(id)).length;
  const fc = Forms.formCounts(ctx);
  const pct = list.length ? (100 * boxed) / list.length : 0;
  const region = t(`region.${data.game.region}`);
  return `<div class="brand"><div class="brand-text"><h1>Living Dex <span>Planner</span></h1><p>${esc(t('app.lede', { game }))}</p></div>
    <div class="prog" aria-live="polite"><div class="prog-row"><b>${boxed} / ${list.length}</b><small>${t('progress.boxed')} · ${esc(t(ctx.M.sources.length ? 'progress.possibleWith' : 'progress.possible', { n: reach, game }))}</small></div><div class="bar"><i style="width:${pct}%"></i></div><small class="forms-prog">${esc(t('progress.forms', { a: fc.a, b: fc.b }))}</small></div></div>
    <div class="controls">
      <div class="tabs" role="tablist">${TABS.map((k) => `<button role="tab" id="tab-${k}" data-action="tab" data-tab="${k}" aria-selected="${state.tab === k}">${t(`tab.${k}`)}</button>`).join('')}</div>
      <div class="opt">
        <button class="btn small mygames" data-action="menu-open" title="${esc(t('menu.title'))}">${esc(game)}${owned ? ` <span class="more">+${owned}</span>` : ''} · ${t('menu.button')}</button>
        <div class="seg" role="group" aria-label="${t('scope.label')}"><button data-action="scope" data-scope="regional" aria-pressed="${gs.scope === 'regional'}">${esc(t('scope.regional', { region, n: data.game.regionalSize }))}</button><button data-action="scope" data-scope="national" aria-pressed="${gs.scope === 'national'}">${esc(t('scope.national', { n: 493 }))}</button></div>
        <label class="chk"><input type="checkbox" id="hideCaught" data-action="hide" ${state.hide ? 'checked' : ''}> ${t('hide.boxed')}</label>
        <div class="seg" role="group" aria-label="${t('lang.label')}"><button data-action="lang" data-lang="en" aria-pressed="${getLang() === 'en'}" lang="en">EN</button><button data-action="lang" data-lang="es" aria-pressed="${getLang() === 'es'}" lang="es">ES</button></div>
        <button class="btn small" data-action="sync-open">${t('sync.button')}</button>
        ${installPrompt ? `<button class="btn small primary" data-action="install">${t('install.button')}</button>` : ''}
      </div></div>`;
}

function renderHeader() {
  $('top-in').innerHTML = headerHTML();
  document.title = t('app.tab', { game: ctx.T.game() });
  document.documentElement.lang = getLang();
}
function renderTab() {
  $('tabs-body').innerHTML = VIEWS[state.tab].render(ctx);
}
function renderDetail() {
  const wrap = $('wrap'), box = $('detail'), scrim = $('scrim');
  if (ctx.current == null) {
    wrap.classList.remove('has-detail'); box.innerHTML = ''; scrim.hidden = true; return;
  }
  wrap.classList.add('has-detail');
  scrim.hidden = false;
  box.innerHTML = Detail.render(ctx);
  box.scrollTop = 0;
}
function renderSync() {
  const el = $('sync');
  if (!ctx.ui.syncOpen) { el.hidden = true; el.innerHTML = ''; return; }
  el.hidden = false;
  el.innerHTML = Sync.render(ctx);
}
function renderAll() {
  renderHeader(); renderTab(); renderDetail(); renderSync();
}
function renderMenu() {
  const el = $('games');
  if (!menuDraft) { el.hidden = true; el.innerHTML = ''; return; }
  el.hidden = false;
  el.innerHTML = Games.render(index, menuDraft);
}
function openMenu(first = false) {
  menuDraft = { main: state.game, owned: new Set((state.owned || []).filter((id) => id !== state.game)),
    trade: !!state.hw.trade, gba: !!state.hw.gba, first };
  renderMenu();
}
async function saveMenu() {
  const d = menuDraft;
  state.owned = [...d.owned].filter((id) => id !== d.main);
  state.hw = { trade: d.trade, gba: d.gba };
  state.setupDone = true;
  menuDraft = null;
  renderMenu();
  saveState(state);
  await switchGame(d.main);
}

// --------------------------------------------------------------------- actions
function toggleBox(key) {
  key = String(key);
  if (ctx.caught.has(key)) ctx.caught.delete(key); else ctx.caught.add(key);
  save();
  const y = window.scrollY;
  renderHeader(); renderTab(); renderDetail();
  window.scrollTo(0, y);
}

function setSyncMsg(msg) {
  ctx.ui.syncMsg = msg;
  const el = $('sync-msg');
  if (el) el.textContent = msg;
}

async function applyCode(code, mode) {
  const peek = peekProgress(code);
  if (!peek || !index.games.some((g) => g.id === peek.game)) { setSyncMsg(t('sync.bad')); return; }
  let switched = false;
  if (peek.game !== ctx.data.game.id) { await switchGame(peek.game, { keepScroll: true }); switched = true; ctx.ui.syncOpen = true; }
  const set = decodeProgress(ctx.data, code);
  if (!set) { setSyncMsg(t('sync.bad')); renderSync(); return; }
  if (mode === 'replace') ctx.caught = set; else for (const k of set) ctx.caught.add(k);
  save();
  ctx.ui.pasteDraft = '';
  const game = ctx.T.game();
  ctx.ui.syncMsg = switched ? t('sync.otherGame', { game }) + ' ' + t('sync.done', { n: set.size, game }) : t('sync.done', { n: set.size, game });
  renderAll();
}

async function copyText(text, btn) {
  try {
    await navigator.clipboard.writeText(text);
    setSyncMsg(t('sync.copied'));
    if (btn) { const old = btn.textContent; btn.textContent = '✓ ' + t('sync.copied'); setTimeout(() => { btn.textContent = old; }, 1500); }
  } catch {
    const ta = $('sync-code');
    if (ta) { ta.focus(); ta.select(); }
    setSyncMsg(t('sync.copyFailed'));
  }
}

function exportFile() {
  const code = $('sync-code').value;
  const blob = new Blob([code + '\n'], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `living-dex-${ctx.data.game.id}-${new Date().toISOString().slice(0, 10)}.txt`;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

document.addEventListener('click', async (ev) => {
  const el = ev.target.closest('[data-action]');
  if (el && el.dataset.action === 'menu-save') { saveMenu(); return; }
  if (el && el.dataset.action === 'menu-close') { menuDraft = null; renderMenu(); return; }
  if (el && el.dataset.action === 'menu-open') { openMenu(); return; }
  if (!el && ev.target.id === 'games' && menuDraft && !menuDraft.first) { menuDraft = null; renderMenu(); return; }
  if (!el || !ctx) {
    if (ev.target.id === 'scrim' && ctx) { ctx.current = null; renderDetail(); }
    if (ev.target.id === 'sync' && ctx) { ctx.ui.syncOpen = false; renderSync(); }
    return;
  }
  const a = el.dataset.action;
  if (el.tagName === 'SELECT' || el.tagName === 'INPUT' && el.type !== 'button' || el.tagName === 'DETAILS') return;
  switch (a) {
    case 'box': ev.stopPropagation(); toggleBox(el.dataset.key); break;
    case 'open': ctx.current = +el.dataset.id; renderDetail(); if (state.tab === 'dex') markCurrent(); break;
    case 'close': ctx.current = null; renderDetail(); if (state.tab === 'dex') markCurrent(); break;
    case 'tab': state.tab = TABS.includes(el.dataset.tab) ? el.dataset.tab : 'plan'; save(); renderHeader(); renderTab(); break;
    case 'slot':
      if (state.boxTap === 'open') { ctx.current = +el.dataset.id; renderDetail(); } else toggleBox(el.dataset.key);
      break;
    case 'box-tap': state.boxTap = el.dataset.tap; save(); renderTab(); break;
    case 'gates-reset': { ctx.gs.gates = {}; save(); const y = window.scrollY; renderAll(); window.scrollTo(0, y); break; }
    case 'scope': ctx.gs.scope = el.dataset.scope; save(); renderAll(); break;
    case 'lang': state.lang = el.dataset.lang; setLang(state.lang); save(); renderAll(); break;
    case 'sync-open': ctx.ui.syncOpen = true; ctx.ui.syncMsg = ''; renderSync(); $('sync-code')?.focus(); break;
    case 'sync-close': ctx.ui.syncOpen = false; renderSync(); break;
    case 'sync-copy': copyText($('sync-code').value, el); break;
    case 'sync-copy-link': copyText(`${location.origin}${location.pathname}#import=${$('sync-code').value}`, el); break;
    case 'sync-export': exportFile(); break;
    case 'sync-merge': case 'sync-replace': applyCode($('sync-paste').value, a === 'sync-replace' ? 'replace' : 'merge'); break;
    case 'install':
      if (installPrompt) { installPrompt.prompt(); installPrompt = null; renderHeader(); }
      break;
    default: break;
  }
});

function markCurrent() {
  for (const c of document.querySelectorAll('.card[aria-current]')) c.removeAttribute('aria-current');
  if (ctx.current != null) document.querySelector(`.card[data-id="${ctx.current}"]`)?.setAttribute('aria-current', 'true');
}

document.addEventListener('change', async (ev) => {
  const el = ev.target;
  if (menuDraft && el.dataset.action && el.dataset.action.startsWith('menu-')) {
    if (el.dataset.action === 'menu-main') { menuDraft.main = el.value; menuDraft.owned.delete(el.value); }
    if (el.dataset.action === 'menu-own') { if (el.checked) menuDraft.owned.add(el.value); else menuDraft.owned.delete(el.value); }
    if (el.dataset.action === 'menu-hw') menuDraft[el.dataset.hw] = el.checked;
    renderMenu();
    return;
  }
  if (!ctx || !el.dataset.action) return;
  switch (el.dataset.action) {
    case 'starter': {
      const v = el.value ? +el.value : null;
      if (v) ctx.gs.starters[el.dataset.group] = v; else delete ctx.gs.starters[el.dataset.group];
      save(); rebuildPlanner(); renderAll(); break;
    }
    case 'progress':
      ctx.gs.progress = el.value === '' ? null : +el.value;
      ctx.gs.gates = {}; // re-derive moves and items from the new badge count
      if (ctx.gs.progress == null) ctx.gs.onlyNow = false;
      save(); renderAll(); break;
    case 'only-now': ctx.gs.onlyNow = el.checked; save(); renderTab(); break;
    case 'gate': {
      const auto = ((ctx.data.game.gates || {})[el.dataset.gate] ?? 0) <= ctx.gs.progress;
      if (el.checked === auto) delete ctx.gs.gates[el.dataset.gate]; else ctx.gs.gates[el.dataset.gate] = el.checked;
      save(); const y = window.scrollY; renderAll(); window.scrollTo(0, y); break;
    }
    case 'hide': state.hide = el.checked; save(); renderAll(); break;
    case 'box-forms': ctx.gs.boxForms = el.checked; save(); renderTab(); renderDetail(); break;
    case 'box-start': ctx.gs.boxStart = +el.value; save(); renderTab(); renderDetail(); break;
    case 'box-gaps': ctx.ui.boxGaps = el.checked; renderTab(); break;
    case 'dex-filter': ctx.ui.dexFilter = el.value; $('grid').innerHTML = Dex.grid(ctx); break;
    case 'area-sort': state.areaSort = el.value; save(); $('alist').innerHTML = Areas.list(ctx); break;
    case 'sync-file': {
      const file = el.files && el.files[0];
      if (!file) break;
      const text = await file.text();
      const m = text.match(/LD1\.[a-z]+\.[A-Za-z0-9_-]+/);
      if (m) { $('sync-paste').value = m[0]; ctx.ui.pasteDraft = m[0]; setSyncMsg(''); } else setSyncMsg(t('sync.bad'));
      break;
    }
    default: break;
  }
});

document.addEventListener('input', (ev) => {
  const el = ev.target;
  if (!ctx) return;
  if (el.dataset.action === 'dex-search') { ctx.ui.dexQuery = el.value; $('grid').innerHTML = Dex.grid(ctx); }
  if (el.dataset.action === 'area-search') { ctx.ui.areaQuery = el.value; $('alist').innerHTML = Areas.list(ctx); }
  if (el.id === 'sync-paste') ctx.ui.pasteDraft = el.value;
});

document.addEventListener('toggle', (ev) => {
  const d = ev.target;
  if (!ctx || !(d instanceof HTMLDetailsElement)) return;
  if (d.id === 'now') { state.nowOpen = d.open; save(); return; }
  if (!d.matches('details.ar')) return;
  const id = +d.dataset.area;
  if (d.open) {
    ctx.openAreas.add(id);
    if (!d.querySelector('.tablewrap')) d.insertAdjacentHTML('beforeend', Areas.areaTableHTML(ctx, id));
  } else ctx.openAreas.delete(id);
}, true);

document.addEventListener('keydown', (ev) => {
  if (!ctx) return;
  if (ev.key === 'Escape') {
    if (menuDraft && !menuDraft.first) { menuDraft = null; renderMenu(); return; }
    if (ctx.ui.syncOpen) { ctx.ui.syncOpen = false; renderSync(); } else if (ctx.current != null) { ctx.current = null; renderDetail(); }
  }
  if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.classList && ev.target.classList.contains('card')) {
    ev.preventDefault(); ctx.current = +ev.target.dataset.id; renderDetail(); markCurrent();
  }
});

// refresh "Catch right now" every minute
setInterval(() => {
  if (!ctx) return;
  ctx.now = new Date();
  if (state.tab === 'plan') {
    const el = $('now');
    if (el) el.outerHTML = Plan.nowSection(ctx);
  }
}, 60000);

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  installPrompt = e;
  if (ctx) renderHeader();
});

// ------------------------------------------------------------------------ boot
async function boot() {
  try {
    index = await loadIndex();
  } catch {
    $('tabs-body').innerHTML = `<div class="empty error">${esc(t('load.error', { game: 'Pokémon' }))}</div>`;
    return;
  }
  avail = await loadAvailability();
  const hash = location.hash.startsWith('#import=') ? decodeURIComponent(location.hash.slice(8)) : null;
  const peek = hash ? peekProgress(hash) : null;
  await switchGame(peek && index.games.some((g) => g.id === peek.game) ? peek.game : state.game);
  if (!state.setupDone && !peek) openMenu(true);
  if (peek && ctx) {
    ctx.ui.syncOpen = true;
    ctx.ui.pasteDraft = hash;
    renderSync();
    try { history.replaceState(null, '', location.pathname + location.search); } catch { /* ignore */ }
  }
  if (!EMBEDDED && 'serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }
}
boot();
