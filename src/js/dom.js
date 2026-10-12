// Small HTML helpers shared by the views.
import { t } from './i18n.js';

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

export function statusChip(ctx, s) {
  const id = s.id;
  if (ctx.caught.has(String(id))) return `<span class="st caught">${t('status.boxed')}</span>`;
  const b = ctx.P.best(id);
  if (!b) return `<span class="st none">${t('status.none')}</span>`;
  if (b.ext) return `<span class="st ext">${esc(ctx.T.ext(b.ext))}</span>`;
  if (isLater(ctx, b.st)) return `<span class="st later">${t('status.later', { stage: esc(ctx.T.stage(b.st)) })}</span>`;
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
  const c = (p) => `<span class="${e.t[p] ? '' : 'z'} ${p === now ? 'now' : ''}" title="${esc(ctx.T.period(p))}">${e.t[p]}%</span>`;
  return `<span class="tod">${c('m')}${c('d')}${c('n')}</span>`;
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
  let h = `<div class="tablewrap"><table><thead><tr><th>${firstCol === 'pokemon' ? t('th.pokemon') : t('th.area')}</th><th>${t('th.how')}</th><th>${t('th.lv')}</th><th>${t('th.rates')}</th><th>${firstCol === 'pokemon' ? t('th.cond') : t('th.cond.short')}</th></tr></thead><tbody>`;
  for (const { s, e } of rows) {
    const a = P.A.get(e.a);
    const est = P.effStage(e);
    const locked = isLater(ctx, est);
    let first;
    if (firstCol === 'pokemon') {
      first = `<button class="pk linkish" data-action="open" data-id="${s.id}">${spr(ctx, s.id)}${esc(T.species(s))}${ctx.caught.has(String(s.id)) ? ' <span class="st caught">✓</span>' : ''}</button>`;
    } else {
      first = `<div class="strong">${esc(T.loc(a.loc))}</div>${a.sub ? `<div class="note">${esc(T.areaSub(a))}</div>` : ''}<div>${pips(ctx, est)} <span class="stagelbl">${esc(T.stage(est))}</span></div>`;
    }
    const mst = (ctx.data.game.methodStage || {})[e.m] || 0;
    h += `<tr class="${locked ? 'locked' : ''}"><td>${first}</td><td>${esc(T.method(e.m))}${firstCol === 'pokemon' && mst > a.st ? `<div class="stagelbl">${esc(T.stage(mst))}</div>` : ''}</td><td class="num">${lvText(e)}</td><td>${chanceCells(ctx, e)}</td><td>${condCells(ctx, e)}</td></tr>`;
  }
  return h + '</tbody></table></div>';
}
