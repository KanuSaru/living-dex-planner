// Boxes tab: your PC boxes in dex order, 30 per box, with optional form slots.
import { t } from '../i18n.js';
import { esc, isLater, lockFor, pad3, sprAt } from '../dom.js';
import { boxShape, boxSlots, layoutBoxes, positionOf } from '../boxes.js';

export function slotsFor(ctx) {
  return boxSlots(ctx.data, { scope: ctx.gs.scope, includeForms: ctx.gs.boxForms });
}

export function positionFor(ctx, key) {
  const shape = boxShape(ctx.data);
  return positionOf(slotsFor(ctx), key, { start: ctx.gs.boxStart, size: shape.size, cols: shape.cols });
}

function slotState(ctx, slot) {
  if (ctx.caught.has(slot.key)) return 'boxed';
  if (slot.form) {
    const st = ctx.P.formStatus(slot.form);
    if (!st) return 'none';
    if (st.ext === 'trade' && ctx.M.formSource(slot.form)) return 'xfer';
    if (st.ext) return 'ext';
    return isLater(ctx, st.st) ? 'later' : 'now';
  }
  const b = ctx.M.best(slot.sp);
  if (!b) return 'none';
  if (b.via) return 'xfer';
  if (b.o.ext) return 'ext';
  return lockFor(ctx, b) ? 'later' : 'now';
}

function slotHTML(ctx, slot) {
  const { T } = ctx;
  const state = slotState(ctx, slot);
  const name = slot.form ? `${T.species(slot.sp)} · ${T.formName(slot.form)}` : T.species(slot.sp);
  const label = { boxed: t('status.boxed'), now: t('filter.now'), later: t('boxes.later'), xfer: t('filter.xfer'), ext: t('filter.ext'), none: t('status.none') }[state];
  const idx = slot.form ? slot.form.spr : slot.sp - 1;
  return `<button class="slot s-${state} ${slot.form ? 'is-form' : ''}" data-action="slot" data-key="${esc(slot.key)}" data-id="${slot.sp}" aria-pressed="${state === 'boxed'}" title="#${pad3(slot.no)} ${esc(name)} · ${esc(label)}" aria-label="#${pad3(slot.no)} ${esc(name)}, ${esc(label)}">${sprAt(idx, name)}<span class="slot-no">${slot.form ? '◆' : pad3(slot.no)}</span></button>`;
}

function legend() {
  const item = (cls, key) => `<span><i class="dot s-${cls}"></i>${t(key)}</span>`;
  return `<div class="legend">${item('boxed', 'status.boxed')}${item('now', 'filter.now')}${item('later', 'boxes.later')}${item('xfer', 'filter.xfer')}${item('ext', 'filter.ext')}${item('none', 'status.none')}</div>`;
}

export function render(ctx) {
  const { gs } = ctx;
  const slots = slotsFor(ctx);
  const shape = boxShape(ctx.data);
  const BOX_SIZE = shape.size, BOX_COUNT = shape.count;
  const boxes = layoutBoxes(slots, { start: gs.boxStart, size: BOX_SIZE });
  const filled = slots.filter((s) => ctx.caught.has(s.key)).length;
  const last = gs.boxStart + boxes.length - 1;
  const tap = ctx.state.boxTap;

  let h = `<p class="lede">${esc(t('boxes.lede', { size: BOX_SIZE, cols: shape.cols, rows: BOX_SIZE / shape.cols }))}</p>
    <div class="panel settings"><div class="fields">
      ${ctx.data.forms.length ? `<label class="chk"><input type="checkbox" id="boxForms" data-action="box-forms" ${gs.boxForms ? 'checked' : ''}> ${t('boxes.forms')}</label>` : ''}
      <label class="field"><span>${t('boxes.start')}</span><select id="boxStart" data-action="box-start">${[1, 2, 3, 4, 5, 6].map((n) => `<option value="${n}" ${gs.boxStart === n ? 'selected' : ''}>${esc(t('boxes.box', { n }))}</option>`).join('')}</select></label>
      <div class="field"><span>${t('boxes.tap')}</span><div class="seg" role="group" aria-label="${esc(t('boxes.tap'))}"><button data-action="box-tap" data-tap="box" aria-pressed="${tap === 'box'}">${t('boxes.tap.box')}</button><button data-action="box-tap" data-tap="open" aria-pressed="${tap === 'open'}">${t('boxes.tap.open')}</button></div></div>
      <label class="chk"><input type="checkbox" id="boxGaps" data-action="box-gaps" ${ctx.ui.boxGaps ? 'checked' : ''}> ${t('boxes.gaps')}</label>
    </div></div>
    <p class="summary">${esc(t('boxes.summary', { boxes: boxes.length, a: filled, b: slots.length }))}</p>`;
  if (last > BOX_COUNT) h += `<p class="warn">${esc(t('boxes.tooMany', { n: last, max: BOX_COUNT }))}</p>`;
  h += legend();

  let body = '';
  for (const box of boxes) {
    const done = box.slots.filter((s) => ctx.caught.has(s.key)).length;
    if (ctx.ui.boxGaps && done === box.slots.length) continue;
    const first = box.slots[0].no, lastNo = box.slots[box.slots.length - 1].no;
    const pct = (100 * done) / box.slots.length;
    body += `<section class="pcbox ${box.n > BOX_COUNT ? 'over' : ''}" id="box-${box.n}"><div class="pcbox-h"><h3>${esc(t('boxes.box', { n: box.n }))}</h3><span class="note">#${pad3(first)}–#${pad3(lastNo)}</span><span class="pcbox-count">${done === box.slots.length ? `<span class="st caught">${t('boxes.full')}</span>` : `${done} / ${box.slots.length}`}</span><span class="bar mini"><i style="width:${pct}%"></i></span></div><div class="pcbox-grid" style="--cols:${shape.cols}">`;
    body += box.slots.map((s) => slotHTML(ctx, s)).join('');
    for (let i = box.slots.length; i < BOX_SIZE; i++) body += '<span class="slot s-blank" aria-hidden="true"></span>';
    body += '</div></section>';
  }
  return h + `<div class="pcboxes">${body || `<div class="empty">${t('boxes.empty')}</div>`}</div>`;
}
