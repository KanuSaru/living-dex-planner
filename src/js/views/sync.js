// Sync panel: copy a progress code or link, paste one back, or save/load a file.
import { t } from '../i18n.js';
import { esc } from '../dom.js';
import { encodeProgress } from '../progress-code.js';

export function render(ctx) {
  const code = encodeProgress(ctx.data, ctx.caught);
  const game = ctx.T.game();
  const canLink = !ctx.embedded && /^https?:/.test(location.protocol);
  return `<div class="sheet-in" role="dialog" aria-modal="true" aria-labelledby="sync-title">
    <div class="d-head simple"><h2 id="sync-title">${t('sync.title')}</h2><button class="btn ghost" data-action="sync-close">${t('sync.close')}</button></div>
    <p class="note">${esc(t('sync.lede'))} ${esc(t('sync.note'))}</p>
    <label class="field block" for="sync-code"><span>${esc(t('sync.yourCode', { game }))}</span>
      <textarea id="sync-code" readonly rows="3" spellcheck="false">${esc(code)}</textarea></label>
    <div class="row-btns"><button class="btn" data-action="sync-copy">${t('sync.copy')}</button>${canLink ? `<button class="btn" data-action="sync-copy-link">${t('sync.copyLink')}</button>` : ''}${ctx.embedded ? '' : `<button class="btn" data-action="sync-export">${t('sync.exportFile')}</button>`}</div>
    <label class="field block" for="sync-paste"><span>${t('sync.paste')}</span>
      <textarea id="sync-paste" rows="3" spellcheck="false" placeholder="LD1.${esc(ctx.data.game.id)}.…">${esc(ctx.ui.pasteDraft)}</textarea></label>
    <div class="row-btns"><button class="btn primary" data-action="sync-merge">${t('sync.merge')}</button><button class="btn" data-action="sync-replace">${t('sync.replace')}</button>
      <label class="btn filebtn">${t('sync.importFile')}<input type="file" id="sync-file" accept=".txt,.json,text/plain,application/json" data-action="sync-file"></label></div>
    <p class="msg" id="sync-msg" role="status">${esc(ctx.ui.syncMsg)}</p></div>`;
}
