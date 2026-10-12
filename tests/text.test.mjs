import { test } from 'node:test';
import assert from 'node:assert/strict';
import { STRINGS, setLang } from '../src/js/i18n.js';
import { createText } from '../src/js/text.js';
import { createPlanner } from '../src/js/planner.js';
import { GAMES, loadGame } from './helpers.mjs';

const BAD = /⟨|undefined|null|NaN|\[object|\{\w+\}/;

test('English and Spanish have the same interface strings', () => {
  const en = Object.keys(STRINGS.en).sort();
  const es = Object.keys(STRINGS.es).sort();
  assert.deepEqual(es.filter((k) => !en.includes(k)), [], 'keys only in Spanish');
  assert.deepEqual(en.filter((k) => !es.includes(k)), [], 'keys only in English');
  for (const k of en) {
    const params = (s) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort().join(',');
    assert.equal(params(STRINGS.es[k]), params(STRINGS.en[k]), `placeholders differ for ${k}`);
  }
});

// Renders every condition, evolution, form method, area name and plan step in every game and language.
for (const lang of ['en', 'es']) {
  test(`every label renders in ${lang}`, () => {
    setLang(lang);
    for (const id of GAMES) {
      const data = loadGame(id);
      const T = createText(data);
      const P = createPlanner(data);
      const check = (s, where) => assert.ok(!BAD.test(s), `${id}/${lang} ${where}: "${s}"`);
      check(T.game(), 'game name');
      for (const a of data.areas) check(T.area(a), `area ${a.key}`);
      data.game.stages.forEach((_, i) => { check(T.stage(i), 'stage'); check(T.stageTag(i), 'stage tag'); });
      for (const s of data.species) {
        check(T.species(s), `species ${s.id}`);
        for (const ty of s.ty) check(T.type(ty), `type of ${s.n}`);
        for (const e of s.e || []) {
          check(T.method(e.m), `method ${e.m}`);
          for (const c of e.req || []) check(T.cond(c), `${s.n} requirement`);
          for (const sp of e.sp || []) check(T.conds(sp.c), `${s.n} special`);
          for (const x of e.ext || []) check(T.ext(x), `${s.n} ext`);
        }
        for (const ev of s.ev || []) { check(T.evo(ev), `${s.n} evolution`); check(T.evoShort(ev), `${s.n} short evolution`); }
        for (const o of P.options(s.id)) {
          for (const step of T.steps(o)) check(step, `${s.n} step`);
          if (o.ext) { check(T.ext(o.ext), 'ext'); check(T.extLong(o.ext), 'ext long'); }
        }
      }
      for (const f of data.forms) {
        check(T.formName(f), `form ${f.key}`);
        for (const h of f.how) check(T.formHow(h), `form ${f.key} method`);
      }
    }
    setLang('en');
  });
}

test('evolution sentences read naturally', () => {
  const data = loadGame('platinum');
  const T = createText(data);
  const S = new Map(data.species.map((s) => [s.id, s]));
  setLang('en');
  assert.equal(T.evo(S.get(445).ev[0]), 'Level 48');
  assert.equal(T.evo(S.get(470).ev[0]), 'Level up at Eterna Forest');
  assert.equal(T.evo(S.get(242).ev[0]), 'Level up with high friendship');
  setLang('es');
  assert.equal(T.evo(S.get(445).ev[0]), 'Nivel 48');
  assert.equal(T.evo(S.get(470).ev[0]), 'Subir de nivel en Bosque Vetusto');
  setLang('en');
});
