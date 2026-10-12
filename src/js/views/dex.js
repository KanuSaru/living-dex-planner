// Pokédex tab: searchable grid of every species in scope.
import { t } from '../i18n.js';
import { boxBtn, esc, isLater, pad3, spr, statusChip } from '../dom.js';

export function toolbar(ctx) {
  const f = ctx.ui.dexFilter;
  const opts = ['all', 'catch', 'evolve', 'breed', 'ext', 'none', 'todo'];
  if (ctx.gs.progress != null) opts.push('now');
  return `<div class="toolbar"><input class="search" id="q" type="search" data-action="dex-search" placeholder="${esc(t('dex.search'))}" aria-label="${esc(t('dex.search'))}" value="${esc(ctx.ui.dexQuery)}">
    <select id="fStatus" data-action="dex-filter" aria-label="${esc(t('filter.all'))}">${opts.map((o) => `<option value="${o}" ${f === o ? 'selected' : ''}>${t(`filter.${o}`)}</option>`).join('')}</select></div>`;
}

export function grid(ctx) {
  const { P, T } = ctx;
  const q = ctx.ui.dexQuery.trim().toLowerCase();
  const num = q.replace(/^#?0*/, '');
  const f = ctx.ui.dexFilter;
  let list = ctx.scopeList();
  if (ctx.gs.scope === 'regional') list = [...list].sort((a, b) => a.rd - b.rd);
  list = list.filter((s) => {
    const boxed = ctx.caught.has(String(s.id));
    if (ctx.state.hide && boxed) return false;
    if (q && !(T.species(s).toLowerCase().includes(q) || s.n.toLowerCase().includes(q) || String(s.id) === num || String(ctx.dexNo(s)) === num)) return false;
    if (f === 'todo') return !boxed;
    if (f === 'now') { const b = P.best(s.id); return !boxed && b && !b.ext && !isLater(ctx, b.st); }
    if (f !== 'all' && P.status(s.id) !== f) return false;
    return true;
  });
  let h = '';
  for (const s of list) {
    const boxed = ctx.caught.has(String(s.id));
    h += `<div class="card ${boxed ? 'is-caught' : ''}" data-action="open" data-id="${s.id}" tabindex="0" ${ctx.current === s.id ? 'aria-current="true"' : ''}>
      <span class="box">${boxBtn(ctx, s.id, `${t('detail.box')}: ${T.species(s)}`)}</span>
      <span class="no">#${pad3(ctx.dexNo(s))}</span>${spr(ctx, s.id)}<span class="nm">${esc(T.species(s))}</span>${statusChip(ctx, s)}</div>`;
  }
  return h || `<div class="empty">${t('dex.empty')}</div>`;
}

export function render(ctx) {
  return toolbar(ctx) + `<div class="grid" id="grid">${grid(ctx)}</div>`;
}
