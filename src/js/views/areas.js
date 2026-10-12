// Areas tab: every place with encounters, how many Pokémon you still need there, and its full table.
import { t } from '../i18n.js';
import { encounterTable, esc, gateNames, lockChip, lockFor, pips, spr } from '../dom.js';

export function areaTableHTML(ctx, areaId) {
  const rows = [...(ctx.areaSpecies.get(areaId) || [])].sort((x, y) => x.s.id - y.s.id || x.e.m.localeCompare(y.e.m));
  return encounterTable(ctx, rows);
}

export function toolbar(ctx) {
  return `<div class="toolbar"><input class="search" id="qa" type="search" data-action="area-search" placeholder="${esc(t('areas.search'))}" aria-label="${esc(t('areas.search'))}" value="${esc(ctx.ui.areaQuery)}">
    <select id="aSort" data-action="area-sort" aria-label="${esc(t('areas.sort.stage'))}"><option value="stage" ${ctx.state.areaSort === 'stage' ? 'selected' : ''}>${t('areas.sort.stage')}</option><option value="need" ${ctx.state.areaSort === 'need' ? 'selected' : ''}>${t('areas.sort.need')}</option></select></div>`;
}

export function list(ctx) {
  const { P, T } = ctx;
  const q = ctx.ui.areaQuery.trim().toLowerCase();
  let rows = ctx.data.areas.map((a) => {
    const enc = ctx.areaSpecies.get(a.id) || [];
    const ids = [...new Set(enc.map((x) => x.s.id))];
    const need = new Set();
    for (const id of ids) for (const s of [P.S.get(id), ...P.descendants(id)]) if (ctx.inScope(s) && !ctx.caught.has(String(s.id))) need.add(s.id);
    return { a, ids, need };
  }).filter((x) => !q || T.area(x.a).toLowerCase().includes(q));
  if (ctx.state.areaSort === 'need') rows.sort((x, y) => y.need.size - x.need.size);
  let h = '';
  for (const x of rows) {
    const open = ctx.openAreas.has(x.a.id);
    const lock = lockFor(ctx, { story: x.a.st, gates: x.a.gt || [] });
    h += `<details class="ar ${lock ? 'locked' : ''}" data-area="${x.a.id}" ${open ? 'open' : ''}><summary>${pips(ctx, x.a.st)}<b>${esc(T.loc(x.a.loc))}</b>${x.a.sub ? `<small>${esc(T.areaSub(x.a))}</small>` : ''}${x.a.gt ? `<small class="gates">${esc(gateNames(x.a.gt))}</small>` : ''}<span class="minis">${x.ids.slice(0, 6).map((id) => spr(ctx, id)).join('')}</span><small>${t('areas.species', { n: x.ids.length })}</small><span class="need">${lock ? lockChip(ctx, lock) + ' ' : ''}${x.need.size ? `<span class="st catch">${t('areas.need', { n: x.need.size })}</span>` : `<span class="st caught">${t('areas.nothing')}</span>`}</span></summary>${open ? areaTableHTML(ctx, x.a.id) : ''}</details>`;
  }
  return h || `<div class="empty">${t('areas.empty')}</div>`;
}

export function render(ctx) {
  return `<p class="lede">${esc(t('areas.lede'))}</p>` + toolbar(ctx) + `<div class="alist" id="alist">${list(ctx)}</div>`;
}
