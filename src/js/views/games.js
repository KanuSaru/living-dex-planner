// "My games" menu: the game your living dex lives in, the other games you own, and your consoles.
import { getLang, t } from '../i18n.js';
import { esc } from '../dom.js';

const nameOf = (g) => g.name[getLang()] || g.name.en;
// the systems each generation plays on, for grouping the "games you own" list
const CONSOLES = [
  { key: 'gb', gens: [1, 2] },
  { key: 'gba', gens: [3] },
  { key: 'ds', gens: [4, 5] },
];

// draft: { main, owned: Set, trade, gba, bank, vc, first }
export function render(index, draft) {
  const games = index.games.filter((g) => g.main);
  const card = (g, type) => {
    const isMain = g.id === draft.main;
    const checked = type === 'radio' ? isMain : draft.owned.has(g.id) || isMain;
    const disabled = type === 'checkbox' && isMain;
    return `<label class="gcard ${checked ? 'on' : ''} ${disabled ? 'is-main' : ''} ${g.home ? 'home' : ''}">
      <input type="${type}" name="${type === 'radio' ? 'menu-main' : 'menu-own'}" value="${g.id}" data-action="${type === 'radio' ? 'menu-main' : 'menu-own'}" ${checked ? 'checked' : ''} ${disabled ? 'disabled' : ''}>
      <span class="gcard-short">${esc(g.short)}</span><span class="gcard-name">${esc(nameOf(g))}</span>${disabled ? `<small>${t('menu.isMain')}</small>` : ''}</label>`;
  };
  const gens = [...new Set(games.filter((g) => !g.home).map((g) => g.gen))];
  const mainHome = games.filter((g) => g.home);
  const mains = gens.map((gen) => `<div class="gen-row"><span class="gen-l">${esc(t('gen.long', { n: gen }))}</span><div class="gcards">${games.filter((g) => g.gen === gen).map((g) => card(g, 'radio')).join('')}</div></div>`).join('')
    + (mainHome.length ? `<div class="gen-row"><span class="gen-l">${esc(t('gen.home'))}</span><div class="gcards">${mainHome.map((g) => card(g, 'radio')).join('')}</div></div>` : '');
  const owned = CONSOLES.map((c) => {
    const list = games.filter((g) => !g.home && c.gens.includes(g.gen));
    return list.length ? `<p class="note">${t(`menu.${c.key}`)}</p><div class="gcards">${list.map((g) => card(g, 'checkbox')).join('')}</div>` : '';
  }).join('');
  const hw = (key) => `<label class="chk"><input type="checkbox" id="hw-${key}" data-action="menu-hw" data-hw="${key}" ${draft[key] ? 'checked' : ''}> ${t(`menu.hw.${key}`)}</label>`;
  return `<div class="sheet-in wide" role="dialog" aria-modal="true" aria-labelledby="games-title">
    <div class="d-head simple"><h2 id="games-title">${t('menu.title')}</h2>${draft.first ? '' : `<button class="btn ghost" data-action="menu-close">${t('menu.cancel')}</button>`}</div>
    <p class="note">${esc(t('menu.lede'))}</p>
    <h3 class="menu-h">${t('menu.main')}</h3>
    ${mains}
    <h3 class="menu-h">${t('menu.own')}</h3>
    ${owned}
    <h3 class="menu-h">${t('menu.hw')}</h3>
    <div class="menu-hw">${['trade', 'gba', 'bank', 'vc'].map(hw).join('')}</div>
    <div class="row-btns end"><button class="btn primary" data-action="menu-save">${draft.first ? t('menu.start') : t('menu.save')}</button></div>
  </div>`;
}
