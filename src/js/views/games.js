// "My games" menu: the game your living dex lives in, the other games you own, and your consoles.
import { getLang, t } from '../i18n.js';
import { esc } from '../dom.js';

const nameOf = (g) => g.name[getLang()] || g.name.en;

// draft: { main, owned: Set, trade, gba, first }
export function render(index, draft) {
  const mains = index.games.filter((g) => g.main);
  const ds = index.games.filter((g) => g.gen === 4);
  const gba = index.games.filter((g) => g.gen === 3);
  const card = (g, type) => {
    const isMain = g.id === draft.main;
    const checked = type === 'radio' ? isMain : draft.owned.has(g.id) || isMain;
    const disabled = type === 'checkbox' && isMain;
    return `<label class="gcard ${checked ? 'on' : ''} ${disabled ? 'is-main' : ''}">
      <input type="${type}" name="${type === 'radio' ? 'menu-main' : 'menu-own'}" value="${g.id}" data-action="${type === 'radio' ? 'menu-main' : 'menu-own'}" ${checked ? 'checked' : ''} ${disabled ? 'disabled' : ''}>
      <span class="gcard-short">${esc(g.short)}</span><span class="gcard-name">${esc(nameOf(g))}</span>${disabled ? `<small>${t('menu.isMain')}</small>` : ''}</label>`;
  };
  return `<div class="sheet-in wide" role="dialog" aria-modal="true" aria-labelledby="games-title">
    <div class="d-head simple"><h2 id="games-title">${t('menu.title')}</h2>${draft.first ? '' : `<button class="btn ghost" data-action="menu-close">${t('menu.cancel')}</button>`}</div>
    <p class="note">${esc(t('menu.lede'))}</p>
    <h3 class="menu-h">${t('menu.main')}</h3>
    <div class="gcards">${mains.map((g) => card(g, 'radio')).join('')}</div>
    <h3 class="menu-h">${t('menu.own')}</h3>
    <p class="note">${t('menu.ds')}</p>
    <div class="gcards">${ds.map((g) => card(g, 'checkbox')).join('')}</div>
    <p class="note">${t('menu.gba')}</p>
    <div class="gcards">${gba.map((g) => card(g, 'checkbox')).join('')}</div>
    <h3 class="menu-h">${t('menu.hw')}</h3>
    <div class="menu-hw">
      <label class="chk"><input type="checkbox" id="hw-trade" data-action="menu-hw" data-hw="trade" ${draft.trade ? 'checked' : ''}> ${t('menu.trade')}</label>
      <label class="chk"><input type="checkbox" id="hw-gba" data-action="menu-hw" data-hw="gba" ${draft.gba ? 'checked' : ''}> ${t('menu.gbaSlot')}</label>
    </div>
    <div class="row-btns end"><button class="btn primary" data-action="menu-save">${draft.first ? t('menu.start') : t('menu.save')}</button></div>
  </div>`;
}
