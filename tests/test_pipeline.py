"""Checks on the build pipeline and the data it produced. Run: python3 -m unittest discover -s tests"""
import copy
import json
import os
import unittest

from pipeline import config as C
from pipeline import l10n, validate
from pipeline.bundle import bundle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, 'generated')


def load(game):
    with open(os.path.join(GEN, 'data', f'{game}.json'), encoding='utf-8') as f:
        return json.load(f)


class ConditionParsing(unittest.TestCase):
    def test_known_conditions(self):
        self.assertEqual(C.parse_condition('swarm-yes', 'sinnoh')[0], {'k': 'swarm'})
        self.assertEqual(C.parse_condition('slot2-ruby', 'sinnoh'), ({'k': 'slot2', 'v': 'ruby'}, 9, 'gba'))
        self.assertEqual(C.parse_condition('johto-safari-blocks-peak-min-21', 'johto')[0], {'k': 'safari', 'v': 'peak', 'n': 21})
        self.assertEqual(C.parse_condition('item-helix-fossil', 'johto')[1], 9)
        self.assertIsNone(C.parse_condition('time-night', 'sinnoh'))
        self.assertIsNone(C.parse_condition('story-progress-before-national-dex', 'sinnoh'))

    def test_unknown_condition_raises(self):
        with self.assertRaises(KeyError):
            C.parse_condition('story-progress-something-new', 'sinnoh')


class Localisation(unittest.TestCase):
    def test_spanish_sub_areas(self):
        en_to_es = {'Jubilife City': 'Ciudad Jubileo'}
        self.assertEqual(l10n.sub_es('south, towards Jubilife City', en_to_es), 'sur, hacia Ciudad Jubileo')
        self.assertEqual(l10n.sub_es('B1F left', en_to_es), 'B1F izquierda')
        self.assertEqual(l10n.sub_es('1F Road 207', en_to_es), '1F, Ruta 207')
        self.assertIsNone(l10n.sub_es('somewhere new', en_to_es))

    def test_routes(self):
        self.assertEqual(l10n.location_es('sinnoh-sea-route-230'), 'Ruta 230')
        self.assertEqual(l10n.location_es('kanto-route-1'), 'Ruta 1')


class GeneratedData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(os.path.join(GEN, 'data', 'platinum.json')):
            raise unittest.SkipTest('run the data build first')

    def test_validation_passes(self):
        for gid in C.GAMES:
            errors = []
            validate.check_game(gid, load(gid), errors)
            self.assertEqual(errors, [], gid)

    def test_validation_catches_shrunken_or_broken_data(self):
        d = load('platinum')
        broken = copy.deepcopy(d)
        broken['species'] = broken['species'][:400]
        broken['areas'][0]['st'] = 42
        broken['species'][399]['e'] = [{'a': 1, 'm': 'teleport', 'lv': [1, 1], 't': {'m': 1, 'd': 1, 'n': 1}}]
        errors = []
        validate.check_game('platinum', broken, errors)
        text = '\n'.join(errors)
        self.assertIn('expected species', text)
        self.assertIn('outside', text)
        self.assertIn('unknown method teleport', text)

    def test_regional_dex_sizes(self):
        self.assertEqual(load('platinum')['game']['regionalSize'], 210)
        self.assertEqual(load('diamond')['game']['regionalSize'], 151)
        self.assertEqual(load('heartgold')['game']['regionalSize'], 256)

    def test_version_exclusives(self):
        has = lambda g, sid: any(s['id'] == sid and s.get('e') for s in load(g)['species'])  # noqa: E731
        self.assertTrue(has('heartgold', 56))   # Mankey
        self.assertFalse(has('soulsilver', 56))
        self.assertTrue(has('soulsilver', 52))  # Meowth
        self.assertFalse(has('heartgold', 52))

    def test_forms(self):
        pt = {f['key']: f for f in load('platinum')['forms']}
        self.assertEqual(sum(1 for k in pt if k.startswith('unown-')), 28)
        self.assertIn('rotom-heat', pt)
        self.assertEqual(pt['shaymin-sky'].get('nobox'), 1)
        self.assertNotIn('castform-sunny', pt)
        self.assertNotIn('arceus-unknown', pt)
        dp = {f['key'] for f in load('diamond')['forms']}
        self.assertNotIn('rotom-heat', dp)
        hg = {f['key'] for f in load('heartgold')['forms']}
        self.assertIn('pichu-spiky-eared', hg)

    def test_gen3_games(self):
        self.assertEqual(load('emerald')['game']['regionalSize'], 202)
        self.assertEqual(load('firered')['game']['regionalSize'], 151)
        self.assertEqual(load('emerald')['forms'], [])
        espeon = next(s for s in load('firered')['species'] if s['id'] == 196)
        self.assertTrue(all(ev.get('ext') == 'trade' for ev in espeon['ev']), 'no clock in FireRed')
        deoxys = next(s for s in load('emerald')['species'] if s['id'] == 386)
        self.assertTrue(all('event' in e.get('ext', []) for e in deoxys['e']), 'Birth Island needs an event ticket')

    def test_index_marks_main_games(self):
        with open(os.path.join(GEN, 'data', 'index.json'), encoding='utf-8') as f:
            index = json.load(f)
        mains = sorted(g['id'] for g in index['games'] if g['main'])
        self.assertEqual(mains, ['diamond', 'heartgold', 'pearl', 'platinum', 'soulsilver'])
        self.assertEqual(len(index['games']), 10)

    def test_drifloon_friday_in_platinum(self):
        drifloon = next(s for s in load('platinum')['species'] if s['id'] == 425)
        self.assertIn({'k': 'weekday', 'v': 'friday'}, drifloon['e'][0]['req'])


class Bundler(unittest.TestCase):
    def test_bundles_the_app(self):
        js = bundle(os.path.join(ROOT, 'src', 'js'), 'app.js')
        self.assertIn("__m['planner.js']", js)
        self.assertNotRegex(js, r'(?m)^\s*(import|export)\s')
        self.assertLess(js.index("__m['i18n.js'] ="), js.index("__m['app.js'] ="))


if __name__ == '__main__':
    unittest.main()
