// Route plan tab: your-game settings, "catch right now", and the stage-by-stage plan.
import { t } from '../i18n.js';
import { esc, isLater, pips, spr } from '../dom.js';
import { periodAt, weekdayAt } from '../planner.js';

const STARTER_LABEL = ['plan.starter', 'plan.starter.kanto', 'plan.starter.hoenn'];

function settings(ctx) {
  const { data, gs, T } = ctx;
  let h = `<div class="panel settings"><h2 class="panel-h">${t('plan.yourGame')}</h2><div class="fields">`;
  data.game.starterGroups.forEach((grp, i) => {
    h += `<label class="field"><span>${t(STARTER_LABEL[i] || 'plan.starter')}</span><select id="starter-${i}" data-action="starter" data-group="${i}">`;
    h += `<option value="">${t('plan.starter.none')}</option>`;
    for (const id of grp) h += `<option value="${id}" ${gs.starters[i] === id ? 'selected' : ''}>${esc(T.species(id))}</option>`;
    h += '</select></label>';
  });
  h += `<label class="field"><span>${t('plan.progress')}</span><select id="progress" data-action="progress"><option value="">${t('plan.progress.any')}</option>`;
  data.game.stages.forEach((s, i) => {
    h += `<option value="${i}" ${gs.progress === i ? 'selected' : ''}>${esc(T.stage(i))} · ${esc(T.stageTag(i))}</option>`;
  });
  h += '</select></label>';
  h += `<label class="chk"><input type="checkbox" id="onlyNow" data-action="only-now" ${gs.onlyNow ? 'checked' : ''} ${gs.progress == null ? 'disabled' : ''}> ${t('plan.onlyNow')}</label>`;
  return h + '</div></div>';
}

export function nowSection(ctx) {
  const { P, T, gs } = ctx;
  const date = ctx.now;
  const groups = P.catchNow({ date, progress: gs.progress, wanted: (s) => ctx.inScope(s) && !ctx.caught.has(String(s.id)) });
  const count = new Set(groups.flatMap((g) => g.items.map((i) => i.s.id))).size;
  const time = date.toLocaleTimeString(ctx.lang, { hour: '2-digit', minute: '2-digit' });
  let h = `<details class="panel now" id="now" data-action="now-toggle" ${ctx.state.nowOpen ? 'open' : ''}><summary><span class="panel-h">${t('now.title')}</span><span class="now-when">${esc(t('now.when', { weekday: T.weekday(weekdayAt(date)), period: T.period(periodAt(date)), time }))}</span><span class="now-count">${count}</span></summary>`;
  h += `<p class="note">${count ? esc(t('now.summary', { n: count, areas: groups.length })) : esc(t('now.none'))} ${gs.progress == null ? esc(t('now.setProgress')) : ''} ${esc(t('now.special'))}</p>`;
  if (count) {
    h += '<div class="now-list">';
    for (const g of groups) {
      h += `<div class="now-area"><div class="now-area-h">${pips(ctx, g.area.st)} <b>${esc(T.loc(g.area.loc))}</b>${g.area.sub ? ` <small>${esc(T.areaSub(g.area))}</small>` : ''}</div><div class="targets">`;
      for (const it of g.items) {
        const how = `${T.method(it.e.m)}${it.cond.length ? ' · ' + T.conds(it.cond) : ''}`;
        h += `<button class="tg" data-action="open" data-id="${it.s.id}" title="${esc(how)}">${spr(ctx, it.s.id)}${esc(T.species(it.s))} <em>${it.rate}%</em></button>`;
      }
      h += '</div></div>';
    }
    h += '</div>';
  }
  return h + '</details>';
}

function legend(ctx) {
  return `<div class="legend"><span>${pips(ctx, 2)} ${t('legend.badges')}</span><span><span class="st evolve">${t('th.lv')} 14</span> ${t('legend.evolve')}</span><span><span class="st breed">${t('status.breed')}</span> ${t('legend.breed')}</span><span><span class="st ext">${t('ext.trade')}</span> ${t('legend.ext')}</span></div>`;
}

function targetChip(ctx, g, tg) {
  const { T } = ctx;
  const b = tg.b;
  let tag;
  if (b.k === 'breed') tag = `<span class="st breed">${t('status.breed')}</span>`;
  else if (b.k === 'evolve') {
    const last = b.path[b.path.length - 1].ev;
    tag = `<span class="st evolve" title="${esc(T.evo(last))}">${esc(T.evoShort(last))}</span>`;
  } else tag = `<em>${t('plan.keep')}</em>`;
  const late = b.st > g.r.st ? ` <em title="${esc(T.stageTag(b.st))}">· ${esc(T.stage(b.st))}</em>` : '';
  const done = ctx.caught.has(String(tg.s.id));
  return `<button class="tg ${b.k === 'breed' ? 'egg' : ''} ${done ? 'done' : ''} ${isLater(ctx, b.st) ? 'locked' : ''}" data-action="open" data-id="${tg.s.id}">${spr(ctx, tg.s.id)}${esc(T.species(tg.s))} ${tag}${late}</button>`;
}

export function render(ctx) {
  const { P, T, gs, data } = ctx;
  const game = T.game();
  const list = ctx.scopeList().filter((s) => !(ctx.state.hide && ctx.caught.has(String(s.id))));
  let h = `<p class="lede">${esc(t('plan.lede'))}</p>` + settings(ctx) + nowSection(ctx) + legend(ctx);

  if (gs.progress != null) {
    const left = ctx.scopeList().filter((s) => !ctx.caught.has(String(s.id)) && P.best(s.id) && !P.best(s.id).ext);
    const now = left.filter((s) => P.best(s.id).st <= gs.progress).length;
    h += `<p class="summary">${esc(t('plan.summary', { now, left: left.length, later: left.length - now }))}</p>`;
  }

  const plan = P.planGroups(list, ctx.caught);
  let body = '';
  for (const stage of plan.stages) {
    const later = isLater(ctx, stage.st);
    if (later && gs.onlyNow) continue;
    const total = stage.areas.reduce((n, a) => n + a.groups.reduce((m, g) => m + g.targets.length, 0), 0);
    body += `<section class="stage ${later ? 'locked' : ''}"><div class="stage-h"><h2>${esc(T.stage(stage.st))}</h2>${pips(ctx, stage.st)}<span class="badge-name">${esc(T.stageTag(stage.st))}</span>${later ? `<span class="st later">${t('plan.locked')}</span>` : ''}<span class="cnt">${t('plan.pokemon', { n: total })}</span></div>`;
    for (const { area, groups } of stage.areas) {
      const n = groups.reduce((m, g) => m + g.targets.length, 0);
      body += `<div class="area"><div class="area-h"><h3>${esc(T.loc(area.loc))} ${area.sub ? `<small>${esc(T.areaSub(area))}</small>` : ''}</h3><span class="meta">${t('plan.forDex', { n })}</span></div>`;
      for (const g of groups) {
        const rs = g.r.s;
        let cnt = '';
        if (g.r.e.one && g.need > 1) cnt = `<span class="x">×1</span><span class="st breed">${t('plan.byBreeding', { n: g.need - 1 })}</span>`;
        else if (g.need > 1) cnt = `<span class="x">×${g.need}</span>`;
        body += `<div class="root"><button class="sprbtn" data-action="open" data-id="${rs}" aria-label="${esc(T.species(rs))}">${spr(ctx, rs)}</button><div class="root-body"><div class="root-t"><b>${esc(T.species(rs))}</b>${cnt}<span class="how">${esc(T.catchLine(g.r))}</span></div><div class="targets">`;
        for (const tg of g.targets) body += targetChip(ctx, g, tg);
        body += '</div></div></div>';
      }
      body += '</div>';
    }
    body += '</section>';
  }

  if (plan.ext.length) {
    const groups = {};
    for (const x of plan.ext) (groups[x.b.ext] ||= []).push(x);
    body += `<section class="stage"><div class="stage-h"><h2>${esc(t('plan.ext.title', { game }))}</h2><span class="cnt">${t('plan.pokemon', { n: plan.ext.length })}</span></div><div class="area">`;
    for (const k of ['starter', 'trade', 'gba', 'other', 'event']) {
      if (!groups[k]) continue;
      body += `<div class="root wide"><div class="root-body"><div class="root-t"><b>${esc(T.extLong(k))}</b></div><div class="targets">`;
      for (const x of groups[k]) body += `<button class="tg ${ctx.caught.has(String(x.s.id)) ? 'done' : ''}" data-action="open" data-id="${x.s.id}">${spr(ctx, x.s.id)}${esc(T.species(x.s))}</button>`;
      body += '</div></div></div>';
    }
    body += '</div></section>';
  }
  if (plan.none.length) {
    body += `<section class="stage"><div class="stage-h"><h2>${esc(t('plan.none.title', { game }))}</h2><span class="cnt">${t('plan.pokemon', { n: plan.none.length })}</span></div><p class="note">${esc(t('plan.none.note'))}</p><div class="area"><div class="root wide"><div class="targets">`;
    for (const s of plan.none) body += `<button class="tg ${ctx.caught.has(String(s.id)) ? 'done' : ''}" data-action="open" data-id="${s.id}">${spr(ctx, s.id)}${esc(T.species(s))}</button>`;
    body += '</div></div></div></section>';
  }
  if (!body) body = `<div class="empty">${esc(gs.onlyNow ? t('plan.nothingNow') : t('plan.allDone'))}</div>`;
  return h + `<div id="plan">${body}</div>`;
}

