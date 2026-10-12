// Small HTML helpers shared by the views.
import { t } from './i18n.js';
import { lockOf } from './planner.js';

export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export const pad3 = (n) => String(n).padStart(3, '0');
const COLS = 25;

// sprite by sheet index (species id - 1, or a form's index)
export function sprAt(index, label, attrs = '') {
  return `<span class="spr" style="--x:${index % COLS};--y:${Math.floor(index / COLS)}" role="img" aria-label="${esc(label)}" ${attrs}></span>`;
}
export function spr(ctx, id, attrs = '') {
  return sprAt(id - 1, ctx.T.species(id), attrs);
}

export function pips(ctx, st) {
  const stage = ctx.data.game.stages[st] || {};
  const n = stage.pips ?? 0;
  let h = `<span class="pips ${stage.post ? 'post' : ''}" title="${esc(ctx.T.stage(st))} · ${esc(ctx.T.stageTag(st))}">`;
  for (let i = 0; i < 8; i++) h += `<i class="${i < n ? 'on' : ''}"></i>`;
  return h + '</span>';
}

export function isLater(ctx, st) {
  return ctx.gs.progress != null && st > ctx.gs.progress;
}

// a field move or key item you have: ticked by you, or normal for your badge count
export function hasGate(ctx, g) {
  const own = (ctx.gs.gates || {})[g];
  if (own != null) return own;
  return ctx.gs.progress != null && ((ctx.data.game.gates || {})[g] ?? 0) <= ctx.gs.progress;
}
// why x ({story, gates}) is out of reach at your progress, or null
export function lockFor(ctx, x) {
  return lockOf(x, ctx.gs.progress, (g) => hasGate(ctx, g));
}
export function lockText(ctx, lock) {
  if (!lock) return '';
  return lock.gate ? t('lock.gate', { x: t(`gate.${lock.gate}`) }) : t('status.later', { stage: ctx.T.stage(lock.story) });
}
export function lockChip(ctx, lock) {
  return lock ? `<span class="st later">${esc(lockText(ctx, lock))}</span>` : '';
}
export const gateNames = (gates) => (gates || []).map((g) => t(`gate.${g}`)).join(' · ');

// a view context for another game you own (its own planner, names and stages; no progress filter)
export function sourceCtx(ctx, src) {
  return { ...ctx, data: src.data, P: src.P, T: src.T, gs: { ...ctx.gs, progress: null, onlyNow: false },
    areaSpecies: src.P.areaSpecies() };
}

export function gameName(ctx, id) {
  const m = ctx.metaOf ? ctx.metaOf(id) : null;
  return m ? m.name[ctx.lang] || m.name.en : id;
}

// "Pal Park → Platinum · Poké Transfer → Black" for a chain of moves between your games
export function hopsText(ctx, hops) {
  return (hops || []).map((h) => t(`via.${h.k}`, { main: gameName(ctx, h.to) })).join(' · ');
}

export function statusChip(ctx, s) {
  const id = s.id;
  if (ctx.caught.has(String(id))) return `<span class="st caught">${t('status.boxed')}</span>`;
  const m = ctx.M ? ctx.M.best(id) : null;
  if (m && m.via) return `<span class="st xfer" title="${esc(hopsText(ctx, m.via))}">${esc(t('status.from', { game: gameName(ctx, m.where) }))}</span>`;
  const b = m ? m.o : ctx.P.best(id);
  if (!b) return `<span class="st none">${t('status.none')}</span>`;
  if (b.ext) return `<span class="st ext">${esc(ctx.T.ext(b.ext))}</span>`;
  const lock = lockFor(ctx, m || b);
  if (lock) return lockChip(ctx, lock);
  const cls = { catch: 'catch', evolve: 'evolve', breed: 'breed' }[b.k] || 'catch';
  return `<span class="st ${cls}">${t(`status.${b.k}`)}</span>`;
}

export function boxBtn(ctx, key, label, big = false) {
  const on = ctx.caught.has(String(key));
  if (big) {
    return `<button class="btn box" data-action="box" data-key="${esc(key)}" aria-pressed="${on}">${on ? '✓ ' + t('detail.boxed') : t('detail.box')}</button>`;
  }
  return `<button class="boxbtn" data-action="box" data-key="${esc(key)}" aria-pressed="${on}" aria-label="${esc(label)}"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.5"/></svg></button>`;
}

export function chanceCells(ctx, e) {
  if (e.g) return `<span class="tod"><span>${t('rate.fixed')}</span></span>`;
  const now = ctx.period;
  const periods = ctx.P.periods || ['m', 'd', 'n'];
  const c = (p) => `<span class="${e.t[p] ? '' : 'z'} ${p === now && periods.length > 1 ? 'now' : ''}" title="${esc(ctx.T.period(p))}">${e.t[p] || 0}%</span>`;
  return `<span class="tod n${periods.length}">${periods.map(c).join('')}</span>`;
}

// table header for the rate columns: morning/day/night, the four seasons, or a single rate
export function ratesHeader(ctx) {
  const kind = ctx.data.game.clock ? ctx.data.game.clock.kind : null;
  return t(kind === 'season' ? 'th.rates.season' : kind === 'tod' ? 'th.rates' : 'th.rates.one');
}

export function condCells(ctx, e) {
  let h = '';
  for (const c of e.req || []) h += `<span class="cond">${esc(ctx.T.cond(c))}</span>`;
  for (const x of e.ext || []) h += `<span class="cond ext">${esc(ctx.T.ext(x))}</span>`;
  for (const sp of e.sp || []) h += `<span class="cond ${sp.ext ? 'ext' : ''}">${esc(ctx.T.conds(sp.c))}: ${sp.p}%</span>`;
  return h || '<span class="note">—</span>';
}

export const lvText = (e) => (e.m === 'npc-trade' ? '—' : e.lv[0] === e.lv[1] ? e.lv[0] : `${e.lv[0]}–${e.lv[1]}`);

export function encounterTable(ctx, rows, { firstCol = 'pokemon' } = {}) {
  const P = ctx.P, T = ctx.T;
  let h = `<div class="tablewrap"><table><thead><tr><th>${firstCol === 'pokemon' ? t('th.pokemon') : t('th.area')}</th><th>${t('th.how')}</th><th>${t('th.lv')}</th><th>${esc(ratesHeader(ctx))}</th><th>${firstCol === 'pokemon' ? t('th.cond') : t('th.cond.short')}</th></tr></thead><tbody>`;
  for (const { s, e } of rows) {
    const a = P.A.get(e.a);
    const est = P.effStage(e);
    const gates = P.gatesOf(e);
    const locked = lockFor(ctx, { story: Math.max(a.st, e.cst || 0), gates });
    let first;
    if (firstCol === 'pokemon') {
      first = `<button class="pk linkish" data-action="open" data-id="${s.id}">${spr(ctx, s.id)}${esc(T.species(s))}${ctx.caught.has(String(s.id)) ? ' <span class="st caught">✓</span>' : ''}</button>`;
    } else {
      first = `<div class="strong">${esc(T.loc(a.loc))}</div>${a.sub ? `<div class="note">${esc(T.areaSub(a))}</div>` : ''}<div>${pips(ctx, est)} <span class="stagelbl">${esc(T.stage(est))}</span></div>`;
    }
    const mst = (ctx.data.game.methodStage || {})[e.m] || 0;
    h += `<tr class="${locked ? 'locked' : ''}"><td>${first}</td><td>${esc(T.method(e.m))}${gates.length ? `<div class="stagelbl gates">${esc(gateNames(gates))}</div>` : firstCol === 'pokemon' && mst > a.st ? `<div class="stagelbl">${esc(T.stage(mst))}</div>` : ''}</td><td class="num">${lvText(e)}</td><td>${chanceCells(ctx, e)}</td><td>${condCells(ctx, e)}</td></tr>`;
  }
  return h + '</tbody></table></div>';
}
