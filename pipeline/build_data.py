"""Build generated/data/<game>.json for every Gen 4 game from PokéAPI's CSV data.

Usage: python3 -m pipeline.build_data <pokeapi>/data/v2/csv generated [game ...]
"""
import collections
import json
import os
import re
import subprocess
import sys

from . import config as C
from . import l10n
from .pokeapi import EN, ES, PokeAPI

GUARANTEED = {'gift', 'gift-egg', 'static', 'roaming-grass', 'roaming-water', 'npc-trade', 'pokemon-ranger',
              'squirt-bottle', 'pokeflute'}
ONE_TIME = {'gift', 'gift-egg', 'static', 'npc-trade', 'pokemon-ranger', 'squirt-bottle', 'pokeflute'}
PERIODS = {'time-morning': 'm', 'time-day': 'd', 'time-night': 'n'}
PLATE_FOR_TYPE = {'fighting': 'fist-plate', 'flying': 'sky-plate', 'poison': 'toxic-plate', 'ground': 'earth-plate',
                  'rock': 'stone-plate', 'bug': 'insect-plate', 'ghost': 'spooky-plate', 'steel': 'iron-plate',
                  'fire': 'flame-plate', 'water': 'splash-plate', 'grass': 'meadow-plate', 'electric': 'zap-plate',
                  'psychic': 'mind-plate', 'ice': 'icicle-plate', 'dragon': 'draco-plate', 'dark': 'dread-plate'}
UNOWN_JOHTO = [('ABCDEFGHIJ', 'kabuto'), ('KLMNOPQ', 'omanyte'), ('RSTUV', 'aerodactyl'), ('WXYZ', 'hooh')]


class Shared:
    """Tables that are the same for every game."""

    def __init__(self, api):
        self.api = api
        self.species = {r['id']: r for r in api.rows('pokemon_species') if int(r['id']) <= C.NATIONAL_MAX}
        self.sp_names = api.names('pokemon_species_names', 'pokemon_species_id')
        self.pokemon = api.by_id('pokemon')
        self.types = {r['id']: r['identifier'] for r in api.rows('types')}
        self.type_names = api.names('type_names', 'type_id')
        self.items = api.by_id('items')
        self.item_by_ident = {r['identifier']: r['id'] for r in api.rows('items')}
        self.item_names = api.names('item_names', 'item_id')
        self.move_names = api.names('move_names', 'move_id')
        self.locations = api.by_id('locations')
        self.loc_names = api.names('location_names', 'location_id', langs=(EN,))
        self.areas = api.by_id('location_areas')
        self.area_prose = {r['location_area_id']: r['name'] for r in api.rows('location_area_prose')
                           if r['local_language_id'] == EN}
        self.vg_order = {r['id']: int(r['order']) for r in api.rows('version_groups')}
        self.slots = api.by_id('encounter_slots')
        self.methods = {r['id']: r['identifier'] for r in api.rows('encounter_methods')}
        self.cond_vals = api.by_id('encounter_condition_values')
        self.cond_map = collections.defaultdict(list)
        for r in api.rows('encounter_condition_value_map'):
            self.cond_map[r['encounter_id']].append(r['encounter_condition_value_id'])
        self.defaults = {v['id'] for v in self.cond_vals.values()
                         if v['is_default'] == '1' or v['identifier'] in C.COND_DEFAULT_IDS}
        self.chains = api.by_id('evolution_chains')
        self.dexes = {r['identifier']: r['id'] for r in api.rows('pokedexes')}
        self.dex_numbers = collections.defaultdict(dict)
        for r in api.rows('pokemon_dex_numbers'):
            self.dex_numbers[r['pokedex_id']][r['species_id']] = int(r['pokedex_number'])
        self.types_of = collections.defaultdict(list)
        for r in api.rows('pokemon_types'):
            p = self.pokemon.get(r['pokemon_id'])
            if p and p['is_default'] == '1' and p['species_id'] in self.species:
                self.types_of[p['species_id']].append((int(r['slot']), int(r['type_id'])))
        self.egg_groups = collections.defaultdict(set)
        for r in api.rows('pokemon_egg_groups'):
            self.egg_groups[r['species_id']].add(r['egg_group_id'])
        self.evolutions = collections.defaultdict(list)
        for r in api.rows('pokemon_evolution'):
            self.evolutions[r['evolved_species_id']].append(r)
        self.forms = api.rows('pokemon_forms')
        self.form_names = api.names('pokemon_form_names', 'pokemon_form_id', field='form_name')
        # English location name -> Spanish, for "south, towards Jubilife City" style labels
        self.en_to_es = {}
        for lid, loc in self.locations.items():
            en = self.loc_names.get(lid, {}).get('en')
            es = l10n.location_es(loc['identifier'])
            if en and es:
                self.en_to_es[en] = es


class GameBuilder:
    def __init__(self, shared, game_id):
        self.S = shared
        self.id = game_id
        self.g = C.GAMES[game_id]
        self.region_key = self.g['region']
        self.R = C.REGIONS[self.region_key]
        self.vg_order = shared.vg_order[str(self.g['vg'])]
        self.used_items, self.used_moves, self.used_locs = set(), set(), set()
        self.problems = []

    # ---------------------------------------------------------------- helpers
    def loc_stage(self, ident):
        if ident in self.R['locations']:
            return self.R['locations'][ident]
        for prefix in self.R.get('location_default', ()):
            if ident.startswith(prefix):
                return self.R['location_default_stage']
        self.problems.append(f'no stage for location {ident}')
        return 9

    def level_stage(self, level):
        for i, cap in enumerate(self.R['level_caps']):
            if level <= cap:
                return i
        return len(self.R['level_caps'])

    def cond(self, value_id):
        ident = self.S.cond_vals[value_id]['identifier']
        try:
            parsed = C.parse_condition(ident, self.region_key)
        except KeyError:
            self.problems.append(f'unhandled encounter condition {ident}')
            return None
        if parsed is None:
            return None
        c, st, ext = parsed
        if c['k'] in ('fossil', 'item'):
            iid = self.S.item_by_ident.get(c['v'])
            if iid:
                c['i'] = int(iid)
                self.used_items.add(iid)
        if c['k'] == 'give':
            if c['v'] == 'any-pokemon':
                c['s'] = 0
            else:
                sid = next((k for k, v in self.S.species.items() if v['identifier'] == c['v']), None)
                c['s'] = int(sid) if sid else 0
        return c, st, ext

    # ------------------------------------------------------------------ areas
    def build_area(self, area_id):
        ar = self.S.areas[area_id]
        loc = self.S.locations[ar['location_id']]
        ident = loc['identifier']
        self.used_locs.add(ar['location_id'])
        prose = self.S.area_prose.get(area_id, '')
        m = re.search(r'\((.*)\)$', prose)
        if m:
            raw = m.group(1)
        elif ar['identifier']:
            raw = l10n.SUB_EN_BY_IDENT.get(ar['identifier'])
            if raw is None:
                self.problems.append(f'no English label for area {ident}/{ar["identifier"]}')
                raw = ar['identifier'].replace('-', ' ')
        else:
            raw = ''
        sub_es = l10n.sub_es(raw, self.S.en_to_es) if raw else ''
        if sub_es is None:
            self.problems.append(f'no Spanish label for sub-area "{raw}"')
            sub_es = raw
        stage = self.R['areas'].get((ident, ar['identifier']), self.loc_stage(ident))
        out = {'id': int(area_id), 'loc': int(ar['location_id']), 'key': ident, 'st': stage}
        if raw:
            out['sub'] = {'en': l10n.tidy_sub_en(raw), 'es': sub_es[:1].upper() + sub_es[1:]}
        if self.region_key == 'sinnoh':
            out['side'] = 'w' if ident in self.R['west'] else 'e'
        return out

    # ------------------------------------------------------------- encounters
    def build_encounters(self):
        S = self.S
        groups = collections.defaultdict(list)
        for e in S.api.rows('encounters'):
            if e['version_id'] != str(self.g['version']):
                continue
            area = S.areas[e['location_area_id']]
            if S.locations[area['location_id']]['identifier'].startswith('unknown'):
                continue  # PokéAPI placeholder areas
            sp = S.pokemon[e['pokemon_id']]['species_id']
            m = S.methods[S.slots[e['encounter_slot_id']]['encounter_method_id']]
            groups[(sp, e['location_area_id'], m)].append(e)

        def matches(row_conds, ctx):
            by = collections.defaultdict(set)
            for c in row_conds:
                by[S.cond_vals[c]['encounter_condition_id']].add(c)
            return all(vals & ctx for vals in by.values())

        time_ids = {v['identifier']: v['id'] for v in S.cond_vals.values() if v['identifier'] in PERIODS}

        def context(period_ident, combo=()):
            ctx = {c for c in S.defaults if S.cond_vals[c]['encounter_condition_id'] != '2'}
            ctx.add(time_ids[period_ident])
            for c in combo:
                oc = S.cond_vals[c]['encounter_condition_id']
                ctx = {x for x in ctx if S.cond_vals[x]['encounter_condition_id'] != oc}
            return ctx | set(combo)

        def rarity(rows, ctx):
            return sum(int(S.slots[r['encounter_slot_id']]['rarity']) for r in rows if matches(S.cond_map[r['id']], ctx))

        starter_of = {sp: i for i, grp in enumerate(self.R['starter_groups']) for sp in grp}
        out = collections.defaultdict(list)
        areas = {}
        for (sp, a, m), rs in sorted(groups.items(), key=lambda kv: (int(kv[0][0]), int(kv[0][1]), kv[0][2])):
            if sp not in S.species:
                continue
            if a not in areas:
                areas[a] = self.build_area(a)
            item = {'a': int(a), 'm': m, 'lv': [min(int(r['min_level']) for r in rs), max(int(r['max_level']) for r in rs)]}
            if m in GUARANTEED:
                req, st, ext = [], 0, set()
                for r in rs:
                    for cid in S.cond_map[r['id']]:
                        if cid in S.defaults:
                            continue
                        ident = S.cond_vals[cid]['identifier']
                        if ident in PERIODS:
                            c, cst, cext = {'k': 'time', 'v': PERIODS[ident]}, 0, None
                        else:
                            parsed = self.cond(cid)
                            if not parsed:
                                continue
                            c, cst, cext = parsed
                        if c not in req:
                            req.append(c)
                        st = max(st, cst)
                        if cext:
                            ext.add(cext)
                wd = C.EXTRA_WEEKDAY.get((self.id, int(sp), areas[a]['key']))
                if wd and {'k': 'weekday', 'v': wd} not in req:
                    req.append({'k': 'weekday', 'v': wd})
                if m == 'pokemon-ranger' or int(sp) in C.EVENT_SPECIES:
                    ext.add('event')
                item['g'] = 1
                if req:
                    item['req'] = req
                if st:
                    item['cst'] = st
                if ext:
                    item['ext'] = sorted(ext)
                if m in ONE_TIME and not any(c['k'] in ('fossil', 'coins') for c in req):
                    item['one'] = 1
                if m == 'gift' and int(sp) in starter_of:
                    item['sg'] = starter_of[int(sp)]
            else:
                t = {k: rarity(rs, context(p)) for p, k in PERIODS.items()}
                item['t'] = t
                specials = {}
                combos = {frozenset(c for c in S.cond_map[r['id']] if c not in S.defaults
                                    and S.cond_vals[c]['encounter_condition_id'] != '2') for r in rs}
                for combo in sorted(combos, key=lambda c: sorted(int(x) for x in c)):
                    if not combo:
                        continue
                    best = max(rarity(rs, context(p, combo)) for p in PERIODS)
                    if best <= max(t.values()):
                        continue
                    parsed = [self.cond(c) for c in sorted(combo, key=int)]
                    parsed = [p for p in parsed if p]
                    if not parsed:
                        continue
                    if len(parsed) > 1:  # "National Dex" is implied by the other post-game conditions
                        parsed = [p for p in parsed if p[0]['k'] != 'natdex'] or parsed
                    conds = [p[0] for p in parsed]
                    key = json.dumps(conds, sort_keys=True)
                    if key not in specials or specials[key]['p'] < best:
                        entry = {'c': conds, 'p': best, 'st': max(p[1] for p in parsed)}
                        ext = [p[2] for p in parsed if p[2]]
                        if ext:
                            entry['ext'] = ext[0]
                        specials[key] = entry
                if specials:
                    item['sp'] = sorted(specials.values(), key=lambda s: (-s['p'], json.dumps(s['c'], sort_keys=True)))
            out[int(sp)].append(item)
        return out, areas

    # ------------------------------------------------------------- evolutions
    def build_evolutions(self, sid):
        S = self.S
        rows = []
        for r in S.evolutions.get(sid, []):
            if not r['version_group_id'] or S.vg_order[r['version_group_id']] > self.vg_order:
                continue
            if r['location_id'] and S.locations[r['location_id']]['region_id'] != str(self.R['id']):
                continue
            rows.append(r)
        out, seen = [], set()
        trig = {'1': 'level', '2': 'trade', '3': 'item', '4': 'shed'}
        for r in rows:
            e = {'t': trig.get(r['evolution_trigger_id'], 'other')}
            st, ext = 0, None
            if r['minimum_level']:
                e['lv'] = int(r['minimum_level'])
            if r['trigger_item_id']:
                e['it'] = int(r['trigger_item_id'])
                self.used_items.add(r['trigger_item_id'])
                st = max(st, self.R['use_item_stage'])
            if r['held_item_id']:
                e['hi'] = int(r['held_item_id'])
                self.used_items.add(r['held_item_id'])
                if e['t'] != 'trade':
                    st = max(st, self.R['held_item_stage'])
            if r['known_move_id']:
                e['mv'] = int(r['known_move_id'])
                self.used_moves.add(r['known_move_id'])
            if r['location_id']:
                e['lo'] = int(r['location_id'])
                self.used_locs.add(r['location_id'])
                st = max(st, self.loc_stage(S.locations[r['location_id']]['identifier']))
            if r['party_species_id']:
                e['pa'] = int(r['party_species_id'])
            if r['minimum_happiness']:
                e['fr'] = 1
            if r['minimum_beauty']:
                e['be'] = 1
                if not self.R['beauty']:
                    ext = 'trade'
                else:
                    st = max(st, 2)
            if r['time_of_day']:
                e['tod'] = 'd' if r['time_of_day'] == 'day' else 'n'
            if r['gender_id']:
                e['g'] = 'f' if r['gender_id'] == '1' else 'm'
            if r['relative_physical_stats']:
                e['ps'] = int(r['relative_physical_stats'])
            if e['t'] == 'trade':
                ext = 'trade'
            if st:
                e['st'] = st
            if ext:
                e['ext'] = ext
            key = json.dumps(e, sort_keys=True)
            if key not in seen:
                seen.add(key)
                out.append(e)
        return out

    # ------------------------------------------------------------------ forms
    def build_forms(self, encounters, areas, sprite_index):
        S = self.S
        by_species = collections.defaultdict(list)
        for f in S.forms:
            p = S.pokemon[f['pokemon_id']]
            sid = p['species_id']
            if sid not in S.species or f['is_battle_only'] == '1' or f['identifier'] in C.SKIP_FORMS:
                continue
            if S.vg_order[f['introduced_in_version_group_id']] > self.vg_order:
                continue
            by_species[sid].append(f)
        out = []
        for sid, forms in sorted(by_species.items(), key=lambda kv: int(kv[0])):
            if len(forms) < 2:
                continue
            forms.sort(key=lambda f: (int(f['form_order']), int(f['id'])))
            for f in forms:
                p = S.pokemon[f['pokemon_id']]
                default = p['is_default'] == '1' and f['is_default'] == '1'
                fid = f['form_identifier']
                names = S.form_names.get(f['id'], {})
                en = names.get('en') or S.sp_names[sid]['en']
                es = names.get('es') or l10n.FORM_NAME_ES.get(f['identifier']) or en
                if default and (es.startswith('Forma de ') or not names.get('en')):
                    en = es = S.sp_names[sid]['en'] if not fid else en
                entry = {'key': f['identifier'], 'sp': int(sid), 'fid': fid, 'n': {'en': en, 'es': es},
                         'spr': sprite_index.get(f['identifier'], int(sid) - 1), 'def': 1 if default else 0,
                         'dep': int(sid)}
                entry.update(self.form_rules(int(sid), fid, default, encounters, areas))
                if f['identifier'] in C.NOT_BOXABLE:
                    entry['nobox'] = 1
                out.append(entry)
        return out

    def form_rules(self, sid, fid, default, encounters, areas):
        R, game = self.R, self.id
        sinnoh = self.region_key == 'sinnoh'
        if sid == 201:
            if R['unown'] == 'sinnoh':
                if fid in ('exclamation', 'question'):
                    return {'how': [{'k': 'unown', 'v': 'tunnel'}], 'st': 4}
                letter = (fid or 'a').upper()
                return {'how': [{'k': 'unown', 'v': 'friend' if letter in 'FRIEND' else 'room'}], 'st': 2}
            if fid in ('exclamation', 'question'):
                return {'how': [{'k': 'alph', 'v': 'report'}], 'st': 1}
            letter = (fid or 'a').upper()
            puzzle = next(p for letters, p in UNOWN_JOHTO if letter in letters)
            return {'how': [{'k': 'alph', 'v': puzzle}], 'st': 1}
        if sid == 412:
            return {'how': [{'k': 'cloak', 'v': fid}]}
        if sid == 413:
            return {'how': [{'k': 'evo-cloak', 'v': fid}]}
        if sid in (422, 423):
            side = 'w' if fid == 'west' else 'e'
            def sea_stage(species):
                st = None
                for e in encounters.get(species, []):
                    a = areas[str(e['a'])]
                    if a.get('side') == side:
                        s = max(a['st'], R['method_stage'].get(e['m'], 0))
                        st = s if st is None else min(st, s)
                return st
            how, stages = [], []
            shellos = sea_stage(422)
            if sid == 422:
                if shellos is not None:
                    how.append({'k': 'sea', 'v': fid})
                    stages.append(shellos)
            else:
                if shellos is not None:
                    how.append({'k': 'evo-sea', 'v': fid})
                    stages.append(max(shellos, self.level_stage(30)))
                gas = sea_stage(423)
                if gas is not None:
                    how.append({'k': 'sea', 'v': fid})
                    stages.append(gas)
            if not how:
                return {'how': [{'k': 'trade-in', 'v': 'sinnoh'}], 'ext': 'trade', 'dep': 0}
            return {'how': how, 'st': min(stages), 'dep': 0}
        if sid == 479 and fid:
            if game == 'platinum':
                return {'how': [{'k': 'rotom-room'}], 'st': 2, 'ext': 'event'}
            return {'how': [{'k': 'trade-in', 'v': 'platinum'}], 'ext': 'trade'}
        if sid == 487 and fid == 'origin':
            if game == 'platinum':
                return {'how': [{'k': 'griseous', 'v': 'distortion'}], 'st': 9}
            return {'how': [{'k': 'griseous', 'v': 'sinjoh'}], 'ext': 'event'}
        if sid == 492 and fid == 'sky':
            return {'how': [{'k': 'gracidea', 'v': 'floaroma' if sinnoh else 'goldenrod'}], 'ext': 'event'}
        if sid == 386 and fid != 'normal':
            return {'how': [{'k': 'meteorite', 'v': 'veilstone' if sinnoh else 'route-3'}],
                    'st': 3 if sinnoh else 9, 'ext': 'event'}
        if sid == 493 and fid != 'normal':
            plate = self.S.item_by_ident[PLATE_FOR_TYPE[fid]]
            self.used_items.add(plate)
            return {'how': [{'k': 'plate', 'i': int(plate)}], 'ext': 'event'}
        if sid == 493:
            return {'how': [{'k': 'no-plate'}]}
        if sid == 172 and fid == 'spiky-eared':
            return {'how': [{'k': 'spiky'}], 'ext': 'event'}
        return {'how': [{'k': 'default'}]}

    # ------------------------------------------------------------------ build
    def build(self, sprite_index):
        S = self.S
        encounters, areas = self.build_encounters()
        dex_id = S.dexes[self.g['dex']]
        regional = S.dex_numbers[dex_id]
        species = []
        for sid, s in sorted(S.species.items(), key=lambda kv: int(kv[0])):
            n = S.sp_names[sid]
            o = {'id': int(sid), 'n': n['en']}
            if n.get('es') and n['es'] != n['en']:
                o['ne'] = n['es']
            o['ty'] = [t for _, t in sorted(S.types_of[sid])]
            o['ch'] = int(s['evolution_chain_id'])
            if sid in regional:
                o['rd'] = regional[sid]
            if s['evolves_from_species_id']:
                o['f'] = int(s['evolves_from_species_id'])
                evs = self.build_evolutions(sid)
                if evs:
                    o['ev'] = evs
            if s['is_baby'] == '1':
                o['baby'] = 1
                inc = S.chains[s['evolution_chain_id']]['baby_trigger_item_id']
                if inc:
                    o['inc'] = int(inc)
                    self.used_items.add(inc)
            if '15' in S.egg_groups[sid] and s['is_baby'] != '1':
                o['noegg'] = 1
            if '13' in S.egg_groups[sid]:
                o['ditto'] = 1
            o['gr'] = int(s['gender_rate'])
            if s['is_legendary'] == '1':
                o['leg'] = 1
            if s['is_mythical'] == '1':
                o['myth'] = 1
            if int(sid) in encounters:
                o['e'] = sorted(encounters[int(sid)], key=lambda x: (areas[str(x['a'])]['st'], x['a'], x['m']))
            species.append(o)

        forms = self.build_forms(encounters, areas, sprite_index)

        locs = {}
        for lid in sorted(self.used_locs, key=int):
            ident = S.locations[lid]['identifier']
            en = l10n.location_en(ident, S.loc_names.get(lid, {}).get('en') or ident.replace('-', ' ').title())
            es = l10n.location_es(ident)
            if not es:
                self.problems.append(f'no Spanish name for location {ident}')
                es = en
            locs[lid] = {'en': en, 'es': es}
        items = {}
        for iid in sorted(self.used_items, key=int):
            nm = S.item_names.get(str(iid), {})
            if not nm.get('en') or not nm.get('es'):
                self.problems.append(f'missing name for item {iid}')
            items[str(iid)] = {'en': nm.get('en', ''), 'es': nm.get('es', nm.get('en', ''))}
        moves = {mid: S.move_names[mid] for mid in sorted(self.used_moves, key=int)}
        types = {tid: S.type_names[tid] for tid in S.type_names if int(tid) <= 17}

        area_list = sorted(areas.values(), key=lambda a: (a['st'], locs[str(a['loc'])]['en'], a.get('sub', {}).get('en', '')))
        R = self.R
        return {
            'game': {'id': self.id, 'name': self.g['name'], 'short': self.g['short'], 'region': self.region_key,
                     'sprites': self.g['sprites'], 'regionalSize': len(regional),
                     'stages': R['stages'], 'dayCareStage': R['day_care_stage'], 'levelCaps': R['level_caps'],
                     'starterGroups': R['starter_groups'], 'methodStage': R['method_stage']},
            'species': species,
            'areas': area_list,
            'forms': forms,
            'names': {'loc': locs, 'item': items, 'move': moves, 'type': types},
        }


def form_sprite_files(shared, game_ids):
    """[(sprite_set, form_identifier, candidate file names)] for every form any game uses."""
    out = collections.OrderedDict()
    for gid in game_ids:
        g = C.GAMES[gid]
        vg_order = shared.vg_order[str(g['vg'])]
        for f in shared.forms:
            p = shared.pokemon[f['pokemon_id']]
            sid = p['species_id']
            if sid not in shared.species or f['is_battle_only'] == '1' or f['identifier'] in C.SKIP_FORMS:
                continue
            if shared.vg_order[f['introduced_in_version_group_id']] > vg_order:
                continue
            if p['is_default'] == '1' and f['is_default'] == '1':
                continue
            cands = [f'{sid}-{f["form_identifier"]}.png']
            if f['pokemon_id'] != sid:
                cands.append(f'{f["pokemon_id"]}.png')
            out[(g['sprites'], f['identifier'])] = cands
    return out


def pokeapi_revision(csv_dir):
    try:
        return subprocess.run(['git', '-C', csv_dir, 'log', '-1', '--format=%h %cs'], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return 'unknown'


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    csv_dir, out_dir = argv[0], argv[1]
    games = argv[2:] or list(C.GAMES)
    api = PokeAPI(csv_dir)
    shared = Shared(api)
    os.makedirs(os.path.join(out_dir, 'data'), exist_ok=True)

    # sprite indices: base species 1..493 at index id-1, then forms per sprite set
    sprite_forms = form_sprite_files(shared, list(C.GAMES))
    per_set = collections.defaultdict(dict)
    for (sset, key), cands in sprite_forms.items():
        per_set[sset][key] = {'index': C.NATIONAL_MAX + len(per_set[sset]), 'files': cands}
    with open(os.path.join(out_dir, 'sprite-manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(per_set, f, indent=1, sort_keys=True)

    rev = pokeapi_revision(csv_dir)
    problems = []
    index = {'games': [], 'default': C.DEFAULT_GAME, 'pokeapi': rev}
    for gid in games:
        gb = GameBuilder(shared, gid)
        sprite_index = {k: v['index'] for k, v in per_set[C.GAMES[gid]['sprites']].items()}
        data = gb.build(sprite_index)
        data['meta'] = {'pokeapi': rev}
        path = os.path.join(out_dir, 'data', f'{gid}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        problems += [f'{gid}: {p}' for p in dict.fromkeys(gb.problems)]
        index['games'].append({'id': gid, 'name': C.GAMES[gid]['name'], 'short': C.GAMES[gid]['short'],
                               'sprites': C.GAMES[gid]['sprites']})
        print(f'{gid}: {sum(1 for s in data["species"] if "e" in s)} species with encounters, '
              f'{len(data["areas"])} areas, {len(data["forms"])} forms, {os.path.getsize(path) // 1024} KB')
    with open(os.path.join(out_dir, 'data', 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(out_dir, 'build-problems.json'), 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=1, ensure_ascii=False)
    if problems:
        print(f'{len(problems)} data problems recorded; validate.py will report them')


if __name__ == '__main__':
    main(sys.argv[1:])
