// Turns structured data (conditions, evolutions, plan steps) into sentences in the current language.
import { getLang, t } from './i18n.js';

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

export function createText(data) {
  const N = data.names;
  const S = new Map(data.species.map((s) => [s.id, s]));
  const pick = (o) => (o ? o[getLang()] || o.en : '');

  const api = {
    game: () => pick(data.game.name),
    species: (id) => {
      const s = typeof id === 'object' ? id : S.get(id);
      if (!s) return '?';
      return getLang() === 'es' && s.ne ? s.ne : s.n;
    },
    loc: (id) => pick(N.loc[String(id)]) || '?',
    item: (id) => pick(N.item[String(id)]) || '?',
    move: (id) => pick(N.move[String(id)]) || '?',
    type: (id) => pick(N.type[String(id)]) || '?',
    areaSub: (a) => (a.sub ? pick(a.sub) : ''),
    area: (a) => (a.sub ? `${api.loc(a.loc)} · ${pick(a.sub)}` : api.loc(a.loc)),
    method: (m) => t(`method.${m}`),
    period: (p) => t(`period.${p}`),
    weekday: (w) => t(`weekday.${w}`),
    stage: (st) => pick(data.game.stages[st]) || '',
    stageTag: (st) => {
      const s = data.game.stages[st];
      return s ? (getLang() === 'es' ? s.tag_es : s.tag_en) : '';
    },
    ext: (x) => t(`ext.${x}`),
    extLong: (x) => t(`ext.long.${x}`),

    cond(c) {
      switch (c.k) {
        case 'slot2': return t('cond.slot2', { game: t(`gba.${c.v}`) });
        case 'radio': return t(`cond.radio.${c.v}`);
        case 'story': return t(`cond.story.${c.v}`);
        case 'other': return t(`cond.other.${c.v}`);
        case 'weekday': return t('cond.weekday', { day: getLang() === 'es' ? t(`weekday.${c.v}`).toLowerCase() + (c.v === 'saturday' || c.v === 'sunday' ? 's' : '') : t(`weekday.${c.v}`) });
        case 'honey': return t(`cond.honey.${c.v}`);
        case 'headbutt': return t(`cond.headbutt.${c.v}`);
        case 'coins': return t('cond.coins', { n: c.n.toLocaleString(getLang()) });
        case 'safari': return t('cond.safari', { n: c.n, kind: t(`safari.${c.v}`) });
        case 'give': return c.s ? t('cond.give', { name: api.species(c.s) }) : t('cond.give.any');
        case 'fossil': return t('cond.fossil', { item: api.item(c.i) });
        case 'item': return t('cond.item', { item: api.item(c.i) });
        case 'time': return t(`cond.time.${c.v}`);
        case 'periods': return t('periods.only', { list: c.v.map((p) => t(`period.${p}`)).join(t('periods.and')) });
        default: return t(`cond.${c.k}`);
      }
    },
    conds: (list) => (list || []).map(api.cond).join(' · '),

    evo(ev) {
      let s;
      if (ev.t === 'trade') s = t('evo.trade');
      else if (ev.t === 'item') s = t('evo.use', { item: api.item(ev.it) });
      else if (ev.t === 'shed') return t('evo.shed');
      else s = ev.lv ? t('evo.level', { lv: ev.lv }) : t('evo.levelUp');
      if (ev.fr) s += t('evo.friendship');
      if (ev.be) s += t('evo.beauty');
      if (ev.hi) s += t('evo.holding', { item: api.item(ev.hi) });
      if (ev.mv) s += t('evo.knowing', { move: api.move(ev.mv) });
      if (ev.lo) s += t('evo.at', { place: api.loc(ev.lo) });
      if (ev.pa) s += t('evo.party', { name: api.species(ev.pa) });
      if (ev.ps === 1) s += t('evo.atkGt');
      if (ev.ps === -1) s += t('evo.atkLt');
      if (ev.ps === 0) s += t('evo.atkEq');
      if (ev.g) s += t(ev.g === 'f' ? 'evo.female' : 'evo.male');
      if (ev.tod) s += t(ev.tod === 'd' ? 'evo.day' : 'evo.night');
      return s;
    },
    evoShort(ev) {
      if (ev.t === 'shed') return t('evoShort.free');
      if (ev.t === 'trade') return t('evoShort.trade');
      if (ev.t === 'item') return api.item(ev.it);
      if (ev.lv && Object.keys(ev).every((k) => ['t', 'lv', 'st', 'ext'].includes(k))) return `${t('th.lv')} ${ev.lv}`;
      if (ev.fr) return t('evoShort.friendship');
      if (ev.lv) return `${t('th.lv')} ${ev.lv}*`;
      if (ev.pa) return api.species(ev.pa);
      if (ev.mv) return api.move(ev.mv);
      if (ev.hi) return api.item(ev.hi);
      if (ev.lo) return api.loc(ev.lo);
      if (ev.be) return t('evoShort.beauty');
      return t('evoShort.special');
    },

    formHow(h) {
      switch (h.k) {
        case 'unown': return t(`form.unown.${h.v}`);
        case 'alph': return t(`form.alph.${h.v}`);
        case 'cloak': return t(`form.cloak.${h.v}`);
        case 'evo-cloak': return t('form.evo-cloak', { cloak: t(`cloak.${h.v}`) });
        case 'sea': return t(`form.sea.${h.v}`);
        case 'evo-sea': return t(`form.evo-sea.${h.v}`);
        case 'trade-in': return t(`form.trade-in.${h.v}`);
        case 'griseous': return t(`form.griseous.${h.v}`);
        case 'gracidea': return t(`form.gracidea.${h.v}`);
        case 'meteorite': return t(`form.meteorite.${h.v}`);
        case 'plate': return t('form.plate', { item: api.item(h.i) });
        default: return t(`form.${h.k}`);
      }
    },
    formName: (f) => pick(f.n),

    // a short "how" line for a catch option: method, level, chance, conditions
    catchLine(o) {
      const e = o.e;
      const parts = [api.method(e.m)];
      if (e.m !== 'npc-trade') parts.push(e.lv[0] === e.lv[1] ? `${t('th.lv')} ${e.lv[0]}` : `${t('th.lv')} ${e.lv[0]}–${e.lv[1]}`);
      if (!e.g) parts.push(`${o.p}%`);
      let line = parts.join(', ');
      const conds = [...(o.cond || [])];
      if (o.starterNote) conds.unshift({ k: o.starterNote });
      if (conds.length) line += ` · ${api.conds(conds)}`;
      return line;
    },

    // ordered steps (HTML, names in <b>) to get option o
    steps(o) {
      if (o.k === 'event') return [t('step.event', { name: esc(api.species(o.s)) })];
      if (o.k === 'catch') {
        const key = o.e.m === 'gift' || o.e.m === 'gift-egg' ? 'step.receive' : o.e.m === 'npc-trade' ? 'step.tradeFor' : 'step.catch';
        return [t(key, { name: esc(api.species(o.s)), area: esc(api.area(o.a)), how: esc(api.catchLine(o)) })];
      }
      if (o.k === 'evolve') return [...api.steps(o.parent), t('step.evolve', { name: esc(api.species(o.s)), how: esc(api.evo(o.ev)) })];
      let line = t(o.needsDitto ? 'step.breed.ditto' : 'step.breed', { name: esc(api.species(o.s)), parent: esc(api.species(o.from)) });
      if (o.incense) line += t('step.breed.incense', { item: esc(api.item(o.incense)) });
      if (o.withoutIncense) line += t('step.breed.noIncense', { item: esc(api.item(o.withoutIncense)), name: esc(api.species(o.s)) });
      return [...api.steps(o.parent), line];
    },
  };
  return api;
}
