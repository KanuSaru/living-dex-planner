// Detail panel for one species: fastest route, family, forms, other games, every encounter.
import { t } from '../i18n.js';
import { boxBtn, encounterTable, esc, gameName, lockFor, lockText, pad3, pips, sourceCtx, spr, statusChip } from '../dom.js';
import { speciesForms } from './forms.js';
import { positionFor } from './boxes.js';

const TYPE_COLOR = { 1: '#a8a77a', 2: '#c22e28', 3: '#a98ff3', 4: '#a33ea1', 5: '#e2bf65', 6: '#b6a136', 7: '#a6b91a',
  8: '#735797', 9: '#b7b7ce', 10: '#ee8130', 11: '#6390f0', 12: '#7ac74c', 13: '#f7d02c', 14: '#f95587', 15: '#96d9d6',
  16: '#6f35fc', 17: '#705746' };

function family(ctx, s) {
  const { P, T } = ctx;
  const members = P.families.get(s.ch) || [];
  if (members.length < 2) return '';
  const root = members.find((m) => !m.f) || members[0];
  const rows = [];
  (function walk(node, trail) {
    const kids = P.children.get(node.id) || [];
    const here = [...trail, node];
    if (!kids.length) { rows.push(here); return; }
    for (const k of kids) walk(k, here);
  })(root, []);
  let h = '';
  const seen = new Set();
  for (const r of rows) {
    h += '<div class="fam">';
    r.forEach((m, i) => {
      if (i > 0) h += `<span class="arrow">${esc((m.ev || []).map((e) => T.evo(e)).join(t('evo.or')) || '—')}</span>`;
      const dim = seen.has(m.id) && i < r.length - 1;
      h += `<button class="m ${m.id === s.id ? 'cur' : ''} ${dim ? 'dim' : ''}" data-action="open" data-id="${m.id}">${spr(ctx, m.id)}<small>${esc(T.species(m))}</small>${statusChip(ctx, m)}</button>`;
      seen.add(m.id);
    });
    h += '</div>';
  }
  return `<div class="d-sec"><h3>${t('detail.family')}</h3>${h}</div>`;
}

function otherGames(ctx, s) {
  if (!ctx.avail) return '';
  const row = ctx.avail[s.id] || {};
  const games = ctx.index.games.filter((g) => g.id !== ctx.data.game.id);
  const owned = new Set(ctx.state.owned || []);
  const chips = games.map((g) => {
    const v = row[g.id];
    const name = esc(g.name[ctx.lang] || g.name.en) + (owned.has(g.id) ? ` <span class="yours">${t('detail.yours')}</span>` : '');
    if (!v) return `<span class="gchip none">${name}</span>`;
    const [kind, ext] = v.split(':');
    const label = ext ? ctx.T.ext(ext) : kind === 'event' ? t('status.event') : t(`status.${kind}`);
    return `<span class="gchip ${ext ? 'ext' : 'ok'}">${name} · ${esc(label)}</span>`;
  }).join('');
  return `<div class="d-sec"><h3>${t('detail.otherGames')}</h3><div class="gchips">${chips}</div></div>`;
}

export function render(ctx) {
  const { P, T, data } = ctx;
  const s = P.S.get(ctx.current);
  if (!s) return '';
  const m = ctx.M.best(s.id);
  const b = m && !m.via ? m.o : P.best(s.id);
  const regional = s.rd != null ? `${esc(t('scope.regional', { region: t(`region.${data.game.region}`), n: '' }).trim().toUpperCase())} #${pad3(s.rd)} · ` : '';
  let h = `<div class="d-in"><div class="d-head">${spr(ctx, s.id)}<div class="d-title"><div class="no">${regional}${esc(t('scope.national', { n: '' }).trim().toUpperCase())} #${pad3(s.id)}</div><h2>${esc(T.species(s))}</h2><div class="types">${s.ty.map((ty) => `<span class="type" style="--tc:${TYPE_COLOR[ty] || '#999'}">${esc(T.type(ty))}</span>`).join('')}</div></div><button class="btn ghost" data-action="close">${t('detail.close')}</button></div>`;
  const pos = positionFor(ctx, s.id);
  h += `<div class="d-actions">${boxBtn(ctx, s.id, T.species(s), true)}${statusChip(ctx, s)}${pos ? `<span class="note boxpos">${esc(t('detail.position', pos))}</span>` : ''}</div>`;
  let srcTable = '';
  if (m && m.via) {
    const sc = sourceCtx(ctx, m.src);
    const name = gameName(ctx, m.where);
    const steps = [...sc.T.steps(m.o), t(m.via === 'palpark' ? 'step.palpark' : 'step.trade', { main: T.game() })];
    h += `<div class="best xfer"><span class="lbl">${esc(t('detail.from', { game: name, via: t(`via.${m.via}`, { main: T.game() }) }))} · ${esc(m.via === 'palpark' ? T.stageTag(ctx.M.natStage) : sc.T.stageTag(m.o.st))}</span><ol>${steps.map((x) => `<li>${x}</li>`).join('')}</ol></div>`;
    const se = sc.P.S.get(s.id);
    const rows = [...(se.e || [])].sort((x, y) => sc.P.effStage(x) - sc.P.effStage(y)).map((e) => ({ s: se, e }));
    if (rows.length) srcTable = `<div class="d-sec"><h3>${esc(t('detail.whereIn', { name: T.species(s), game: name }))}</h3>${encounterTable(sc, rows, { firstCol: 'area' })}</div>`;
  } else if (b) {
    const label = b.ext ? t('detail.needs', { x: T.ext(b.ext) }) : t('detail.fastest');
    const lock = lockFor(ctx, b);
    h += `<div class="best ${b.ext ? 'ext' : ''}"><span class="lbl">${esc(label)} · ${esc(T.stageTag(b.st))}</span><ol>${T.steps(b).map((x) => `<li>${x}</li>`).join('')}</ol>${lock ? `<div class="lockline">🔒 ${esc(lockText(ctx, lock))}</div>` : ''}${ctx.P.notesFor(b).map((n) => `<div class="note">${esc(n.k === 'gender' ? t(n.g === 'f' ? 'note.female' : 'note.male', { to: T.species(n.to), from: T.species(n.from), pct: Number.isInteger(n.pct) ? n.pct : n.pct.toFixed(1) }) : t('note.random', { list: n.options.map((id) => T.species(id)).join(t('evo.or')), from: T.species(n.from) }))}</div>`).join('')}</div>`;
  } else {
    h += `<div class="best ext"><span class="lbl">${t('status.none')}</span><div>${esc(t('detail.none', { name: T.species(s), game: T.game() }))}</div></div>`;
  }
  if (P.formsBySpecies.has(s.id)) h += `<div class="d-sec"><h3>${t('detail.forms')}</h3>${speciesForms(ctx, s.id)}</div>`;
  h += family(ctx, s);
  const alts = P.options(s.id).filter((o) => o.k !== 'catch' && o !== b);
  if (alts.length) {
    h += `<div class="d-sec"><h3>${t('detail.other')}</h3>${alts.map((o) => `<div class="note alt">${pips(ctx, o.st)} ${T.steps(o).join(' → ')}${o.ext ? ` <span class="cond ext">${esc(T.ext(o.ext))}</span>` : ''}</div>`).join('')}</div>`;
  }
  h += srcTable;
  h += otherGames(ctx, s);
  const enc = [...(s.e || [])].sort((x, y) => P.effStage(x) - P.effStage(y)).map((e) => ({ s, e }));
  const nAreas = new Set(enc.map((x) => x.e.a)).size;
  h += `<div class="d-sec"><h3>${esc(t('detail.where', { name: T.species(s) }))} ${nAreas ? `<span class="note">(${nAreas === 1 ? t('detail.area') : t('detail.areas', { n: nAreas })})</span>` : ''}</h3>`;
  h += enc.length ? encounterTable(ctx, enc, { firstCol: 'area' }) : `<div class="empty">${t('detail.noWild')} ${b ? t('detail.useRoute') : ''}</div>`;
  return h + '</div></div>';
}
