// Forms tab: alternate forms per species, with how to get each one.
import { t } from '../i18n.js';
import { boxBtn, esc, gameName, isLater, pips, sprAt } from '../dom.js';

export function formCounts(ctx) {
  let a = 0, b = 0;
  for (const f of ctx.data.forms) {
    if (f.def || f.nobox) continue;
    const s = ctx.P.S.get(f.sp);
    if (!ctx.inScope(s)) continue;
    b++;
    if (ctx.caught.has(f.key)) a++;
  }
  return { a, b };
}

function formTile(ctx, f) {
  const { P, T } = ctx;
  const st = P.formStatus(f);
  const key = f.def ? String(f.sp) : f.key;
  const boxed = ctx.caught.has(key);
  let chip;
  if (f.def) chip = `<span class="st plain">${t('forms.default')}</span>`;
  else if (boxed) chip = `<span class="st caught">${t('status.boxed')}</span>`;
  else if (!st) chip = `<span class="st none">${t('forms.unavailable')}</span>`;
  else if (st.ext === 'trade' && ctx.M && ctx.M.formSource(f)) chip = `<span class="st xfer">${esc(t('status.from', { game: gameName(ctx, ctx.M.formSource(f)) }))}</span>`;
  else if (st.ext) chip = `<span class="st ext">${esc(T.ext(st.ext))}</span>`;
  else if (isLater(ctx, st.st)) chip = `<span class="st later">${t('status.later', { stage: esc(T.stage(st.st)) })}</span>`;
  else chip = `<span class="st catch">${esc(T.stage(st.st))}</span>`;
  const how = f.how.map((h) => esc(T.formHow(h))).join(' · ');
  return `<div class="ftile ${boxed ? 'is-caught' : ''} ${f.nobox ? 'nobox' : ''}">
    <div class="ftile-top">${sprAt(f.spr, `${T.species(f.sp)} ${T.formName(f)}`)}<div class="ftile-name"><b>${esc(T.formName(f))}</b>${chip}${st && !f.def ? ` ${pips(ctx, st.st)}` : ''}</div>${f.nobox ? '' : boxBtn(ctx, key, `${t('detail.box')}: ${T.species(f.sp)} ${T.formName(f)}`)}</div>
    <p class="ftile-how">${how}${f.nobox ? `<br><strong>${t('forms.notBoxable')}</strong>` : ''}</p></div>`;
}

export function speciesForms(ctx, sid) {
  const forms = ctx.P.formsBySpecies.get(sid) || [];
  return `<div class="fgrid">${forms.map((f) => formTile(ctx, f)).join('')}</div>`;
}

export function render(ctx) {
  const { T } = ctx;
  const { a, b } = formCounts(ctx);
  let h = `<p class="lede">${esc(t('forms.lede'))}</p><p class="summary">${esc(t('forms.count', { a, b }))}</p>`;
  let any = false;
  for (const [sid, forms] of ctx.P.formsBySpecies) {
    const s = ctx.P.S.get(sid);
    if (!ctx.inScope(s)) continue;
    const extra = forms.filter((f) => !f.def && !f.nobox);
    const done = extra.filter((f) => ctx.caught.has(f.key)).length;
    if (ctx.state.hide && extra.length && done === extra.length && ctx.caught.has(String(sid))) continue;
    any = true;
    h += `<section class="fspecies"><div class="area-h"><h3><button class="linkish" data-action="open" data-id="${sid}">${esc(T.species(s))}</button></h3><span class="meta">${done} / ${extra.length}</span></div>${speciesForms(ctx, sid)}</section>`;
  }
  return any ? h : h + `<div class="empty">${t('forms.empty')}</div>`;
}
