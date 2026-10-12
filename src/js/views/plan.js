// Route plan tab: your-game settings, "catch right now", and the stage-by-stage plan.
import { t } from '../i18n.js';
import { esc, gameName, hasGate, hopsText, lockChip, lockFor, lockText, pips, sourceCtx, spr, sprAt } from '../dom.js';
import { periodAt, weekdayAt } from '../planner.js';

const STARTER_LABEL = ['plan.starter', 'plan.starter.kanto', 'plan.starter.hoenn'];

function settings(ctx) {
  const { data, gs, T } = ctx;
  if (data.game.home) {
    return `<div class="panel settings"><h2 class="panel-h">${t('plan.home.title')}</h2><p class="note">${esc(t(ctx.M.sources.length ? 'plan.home.note' : 'plan.home.empty'))}</p>
      <div class="row-btns"><button class="btn small" data-action="menu-open">${t('menu.button')}</button></div></div>`;
  }
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
  h += '</div>';
  if (gs.progress != null) h += gateList(ctx);
  return h + '</div>';
}

// field moves and key items, ticked from your badges; you can change any of them
const FIELD_MOVES = ['cut', 'flash', 'rock-smash', 'headbutt', 'strength', 'surf', 'whirlpool', 'dive', 'rock-climb', 'waterfall'];
function gateList(ctx) {
  const gates = Object.keys(ctx.data.game.gates || {});
  const own = ctx.gs.gates || {};
  const box = (g) => {
    const on = hasGate(ctx, g);
    return `<label class="gchk ${on ? 'on' : ''} ${g in own ? 'set' : ''}"><input type="checkbox" data-action="gate" data-gate="${g}" ${on ? 'checked' : ''}> ${esc(t(`gate.${g}`))}</label>`;
  };
  const moves = gates.filter((g) => FIELD_MOVES.includes(g));
  const items = gates.filter((g) => !FIELD_MOVES.includes(g));
  return `<div class="have"><div class="have-h"><span class="panel-h small">${t('plan.have')}</span><span class="note">${esc(t('plan.have.note'))}</span>${Object.keys(own).length ? `<button class="btn small ghost" data-action="gates-reset">${t('plan.have.reset')}</button>` : ''}</div>
    <div class="have-row"><span class="have-l">${t('plan.have.moves')}</span>${moves.map(box).join('')}</div>
    <div class="have-row"><span class="have-l">${t('plan.have.items')}</span>${items.map(box).join('')}</div></div>`;
}

export function nowSection(ctx) {
  const { P, T, gs } = ctx;
  if (!ctx.data.areas.length) return '';
  const date = ctx.now;
  const clock = ctx.data.game.clock;
  const groups = P.catchNow({ date, wanted: (s) => ctx.inScope(s) && !ctx.caught.has(String(s.id)),
    isOpen: (story, gates) => !lockFor(ctx, { story, gates }) });
  const count = new Set(groups.flatMap((g) => g.items.map((i) => i.s.id))).size;
  const time = date.toLocaleTimeString(ctx.lang, { hour: '2-digit', minute: '2-digit' });
  let h = `<details class="panel now" id="now" data-action="now-toggle" ${ctx.state.nowOpen ? 'open' : ''}><summary><span class="panel-h">${t('now.title')}</span><span class="now-when">${esc(clock ? t(clock.kind === 'season' ? 'now.when.season' : 'now.when', { weekday: T.weekday(weekdayAt(date)), period: T.period(periodAt(date, clock)), time }) : t('now.when.plain', { weekday: T.weekday(weekdayAt(date)), time }))}</span><span class="now-count">${count}</span></summary>`;
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
  if (ctx.data.game.home) return '';
  return `<div class="legend"><span>${pips(ctx, 2)} ${t('legend.badges')}</span><span><span class="st evolve">${t('th.lv')} 14</span> ${t('legend.evolve')}</span>${ctx.P.canBreed ? `<span><span class="st breed">${t('status.breed')}</span> ${t('legend.breed')}</span>` : ''}<span><span class="st ext">${t('ext.trade')}</span> ${t('legend.ext')}</span></div>`;
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
  const lock = lockFor(ctx, b);
  return `<button class="tg ${b.k === 'breed' ? 'egg' : ''} ${done ? 'done' : ''} ${lock ? 'locked' : ''}" data-action="open" data-id="${tg.s.id}" ${lock ? `title="${esc(lockText(ctx, lock))}"` : ''}>${spr(ctx, tg.s.id)}${esc(T.species(tg.s))} ${tag}${late}</button>`;
}

function formChip(ctx, f) {
  const done = ctx.caught.has(f.key);
  return `<button class="tg form ${done ? 'done' : ''}" data-action="open" data-id="${f.sp}">${sprAt(f.spr, ctx.T.formName(f))}${esc(ctx.T.species(f.sp))} <em>${esc(ctx.T.formName(f))}</em></button>`;
}

function noteHTML(ctx, n) {
  const { T } = ctx;
  if (n.k === 'gender') {
    const pct = Number.isInteger(n.pct) ? n.pct : n.pct.toFixed(1);
    return t(n.g === 'f' ? 'note.female' : 'note.male', { to: T.species(n.to), from: T.species(n.from), pct });
  }
  return t('note.random', { list: n.options.map((id) => T.species(id)).join(t('evo.or')), from: T.species(n.from) });
}

function stagesHTML(ctx, stages, { small = false } = {}) {
  const { T, gs } = ctx;
  let body = '';
  for (const stage of stages) {
    const rootsLocked = stage.areas.every((a) => a.groups.every((g) => lockFor(ctx, g.r)));
    const later = gs.progress != null && rootsLocked;
    if (later && gs.onlyNow) continue;
    const total = stage.areas.reduce((n, a) => n + a.groups.reduce((m, g) => m + g.targets.length, 0), 0);
    body += `<section class="stage ${later ? 'locked' : ''} ${small ? 'small' : ''}"><div class="stage-h"><h2>${esc(T.stage(stage.st))}</h2>${pips(ctx, stage.st)}<span class="badge-name">${esc(T.stageTag(stage.st))}</span>${later ? `<span class="st later">${t('plan.locked')}</span>` : ''}<span class="cnt">${t('plan.pokemon', { n: total })}</span></div>`;
    for (const { area, groups } of stage.areas) {
      const n = groups.reduce((m, g) => m + g.targets.length, 0);
      body += `<div class="area"><div class="area-h"><h3>${esc(T.loc(area.loc))} ${area.sub ? `<small>${esc(T.areaSub(area))}</small>` : ''}</h3><span class="meta">${t('plan.forDex', { n })}</span></div>`;
      for (const g of groups) {
        const rs = g.r.s;
        let cnt = '';
        if (g.r.e.one && g.need > 1) cnt = `<span class="x">×1</span><span class="st breed">${t('plan.byBreeding', { n: g.need - 1 })}</span>`;
        else if (g.need > 1) cnt = `<span class="x">×${g.need}</span>`;
        const lock = lockFor(ctx, g.r);
        body += `<div class="root ${lock ? 'locked' : ''}"><button class="sprbtn" data-action="open" data-id="${rs}" aria-label="${esc(T.species(rs))}">${spr(ctx, rs)}</button><div class="root-body"><div class="root-t"><b>${esc(T.species(rs))}</b>${cnt}<span class="how">${esc(T.catchLine(g.r))}</span>${lockChip(ctx, lock)}</div><div class="targets">`;
        for (const tg of g.targets) body += targetChip(ctx, g, tg);
        for (const f of g.forms || []) body += formChip(ctx, f);
        body += '</div>';
        if (g.notes && g.notes.length) body += `<ul class="notes">${g.notes.map((n) => `<li>${esc(noteHTML(ctx, n))}</li>`).join('')}</ul>`;
        body += '</div></div>';
      }
      body += '</div>';
    }
    body += '</section>';
  }
  return body;
}

const chipList = (ctx, items) => items.map((x) => `<button class="tg ${ctx.caught.has(String(x.id)) ? 'done' : ''}" data-action="open" data-id="${x.id}">${spr(ctx, x.id)}${esc(ctx.T.species(x))}</button>`).join('');

function sourceSections(ctx, list) {
  const { M, gs } = ctx;
  const main = ctx.T.game();
  let body = '';
  for (const src of M.sources) {
    const sl = list.filter((s) => { const b = M.best(s.id); return b && b.where === src.id; });
    if (!sl.length) continue;
    // the longest chain this game's Pokémon take (a Gen 2 Pokémon past #151 can't go back to Gen 1, so chains differ)
    const first = sl.map((s) => M.best(s.id)).sort((a, b) => b.via.length - a.via.length)[0];
    const later = !!lockFor(ctx, { story: 0, gates: first.gates });
    if (later && gs.onlyNow) continue;
    const sc = sourceCtx(ctx, src);
    const name = sc.T.game();
    const sp = src.P.planGroups(sl, ctx.caught);
    const steps = first.via.map((h) => `<li>${esc(t(`hop.${h.k}`, { from: gameName(ctx, h.from), to: gameName(ctx, h.to) }))}${h.note ? ' ' + esc(t(`hop.note.${h.note}`)) : ''}</li>`).join('');
    body += `<section class="srcsec"><div class="src-h"><h2>${esc(t('plan.src.title', { game: name }))}</h2><span class="st xfer">${esc(hopsText(ctx, first.via))}</span>${later ? `<span class="st later">${t('plan.locked')}</span>` : ''}<span class="cnt">${t('plan.pokemon', { n: sl.length })}</span></div><p class="note">${esc(t('plan.src.lede', { game: name, main }))}</p><ol class="hops">${steps}</ol>`;
    body += stagesHTML(sc, sp.stages, { small: true });
    if (sp.ext.length) {
      body += `<div class="area"><div class="root wide"><div class="root-body"><div class="root-t"><b>${esc(t('plan.src.starter', { game: name }))}</b></div><div class="targets">${chipList(ctx, sp.ext.map((x) => x.s))}</div></div></div></div>`;
    }
    body += '</section>';
  }
  return body;
}

// with "Include forms" on in Boxes, forms caught the same way as their species need their own copy
const COPY_KINDS = new Set(['unown', 'alph', 'alph2', 'tanoby', 'cloak', 'evo-cloak', 'season']);
function copyForms(ctx, list) {
  if (!ctx.gs.boxForms) return [];
  const ids = new Set(list.map((s) => s.id));
  return (ctx.data.forms || []).filter((f) => !f.def && !f.nobox && ids.has(f.sp) && f.how.some((h) => COPY_KINDS.has(h.k))
    && !(ctx.state.hide && ctx.caught.has(f.key)) && (() => { const st = ctx.P.formStatus(f); return st && !st.ext; })());
}

export function render(ctx) {
  const { P, M, T, gs } = ctx;
  const game = T.game();
  const list = ctx.scopeList().filter((s) => !(ctx.state.hide && ctx.caught.has(String(s.id))));
  let h = `<p class="lede">${esc(t('plan.lede'))}</p>` + settings(ctx) + nowSection(ctx) + legend(ctx);

  if (gs.progress != null) {
    const left = ctx.scopeList().filter((s) => { const b = M.best(s.id); return !ctx.caught.has(String(s.id)) && b && (b.via || !b.o.ext); });
    const now = left.filter((s) => !lockFor(ctx, M.best(s.id))).length;
    h += `<p class="summary">${esc(t('plan.summary', { now, left: left.length, later: left.length - now }))}</p>`;
  }

  const mainList = list.filter((s) => { const b = M.best(s.id); return !b || !b.via; });
  const plan = P.planGroups(mainList, ctx.caught, { extraForms: copyForms(ctx, mainList) });
  let body = stagesHTML(ctx, plan.stages) + sourceSections(ctx, list);

  if (plan.ext.length) {
    const groups = {};
    for (const x of plan.ext) (groups[x.b.ext] ||= []).push(x);
    body += `<section class="stage"><div class="stage-h"><h2>${esc(t('plan.ext.title', { game }))}</h2><span class="cnt">${t('plan.pokemon', { n: plan.ext.length })}</span></div><div class="area">`;
    for (const k of ['starter', 'one', 'trade', 'gba', 'vc', 'other', 'event']) {
      if (!groups[k]) continue;
      body += `<div class="root wide"><div class="root-body"><div class="root-t"><b>${esc(T.extLong(k))}</b></div><div class="targets">${chipList(ctx, groups[k].map((x) => x.s))}</div></div></div>`;
    }
    body += '</div></section>';
  }
  if (plan.none.length) {
    body += `<section class="stage"><div class="stage-h"><h2>${esc(t('plan.none.title', { game }))}</h2><span class="cnt">${t('plan.pokemon', { n: plan.none.length })}</span></div><p class="note">${esc(t(M.sources.length ? 'plan.none.noteOwned' : 'plan.none.note'))}</p><div class="area"><div class="root wide"><div class="targets">${chipList(ctx, plan.none)}</div></div></div></section>`;
  }
  if (!body) body = `<div class="empty">${esc(gs.onlyNow ? t('plan.nothingNow') : t('plan.allDone'))}</div>`;
  return h + `<div id="plan">${body}</div>`;
}
