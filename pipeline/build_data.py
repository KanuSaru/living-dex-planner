"""Build generated/data/<game>.json for every game (Gen 1 to Gen 5, and Pokémon HOME) from PokéAPI's CSV data.

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

EVENT_METHODS = {'pokemon-ranger', 'colosseum-bonus-disc-jpn', 'colosseum-bonus-disc-us', 'pokemon-channel-pal'}
GUARANTEED = {'gift', 'gift-egg', 'static', 'roaming-grass', 'roaming-water', 'npc-trade', 'squirt-bottle',
              'pokeflute', 'wailmer-pail'} | EVENT_METHODS
ONE_TIME = {'gift', 'gift-egg', 'static', 'npc-trade', 'squirt-bottle', 'pokeflute', 'wailmer-pail'} | EVENT_METHODS
TIME_PERIODS = {'time-morning': 'm', 'time-day': 'd', 'time-night': 'n'}
TIME_GROUP, SEASON_GROUP = '2', '6'
PLATE_FOR_TYPE = {'fighting': 'fist-plate', 'flying': 'sky-plate', 'poison': 'toxic-plate', 'ground': 'earth-plate',
                  'rock': 'stone-plate', 'bug': 'insect-plate', 'ghost': 'spooky-plate', 'steel': 'iron-plate',
                  'fire': 'flame-plate', 'water': 'splash-plate', 'grass': 'meadow-plate', 'electric': 'zap-plate',
                  'psychic': 'mind-plate', 'ice': 'icicle-plate', 'dragon': 'draco-plate', 'dark': 'dread-plate'}
DRIVE_FOR_FORM = {'douse': 'douse-drive', 'shock': 'shock-drive', 'burn': 'burn-drive', 'chill': 'chill-drive'}
UNOWN_JOHTO = [('ABCDEFGHIJ', 'kabuto'), ('KLMNOPQ', 'omanyte'), ('RSTUV', 'aerodactyl'), ('WXYZ', 'hooh')]
UNOWN_GSC = [('ABCDEFGHIJK', 'kabuto'), ('LMNOPQR', 'omanyte'), ('STUVW', 'aerodactyl'), ('XYZ', 'hooh')]
UNOVA = ('unova', 'unova2')


def nat_max(game):
    return C.NAT_MAX[game['gen']]


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
        # types before a later generation changed them (Clefairy was Normal until Gen 6): {species: [(gen, [types])]}
        past = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in api.rows('pokemon_types_past'):
            p = self.pokemon.get(r['pokemon_id'])
            if p and p['is_default'] == '1' and p['species_id'] in self.species:
                past[p['species_id']][int(r['generation_id'])].append((int(r['slot']), int(r['type_id'])))
        self.types_past = {sid: sorted(by_gen.items()) for sid, by_gen in past.items()}
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

    def types_for(self, sid, gen):
        for g, types in self.types_past.get(sid, []):
            if gen <= g:
                return [t for _, t in sorted(types)]
        return [t for _, t in sorted(self.types_of[sid])]


def form_entries(shared, game_id):
    """The alternate-form rows of pokemon_forms that matter for a game, grouped by species."""
    g = C.GAMES[game_id]
    R = C.REGIONS[g['region']]
    if R.get('forms') is False:
        return {}
    home = g.get('home')
    vg_order = shared.vg_order[str(C.HOME_FORMS_UP_TO_VG if home else g['vg'])]
    top = C.NAT_MAX[5] if home else nat_max(g)
    by_species = collections.defaultdict(list)
    for f in shared.forms:
        p = shared.pokemon[f['pokemon_id']]
        sid = p['species_id']
        if sid not in shared.species or int(sid) > top or f['is_battle_only'] == '1' or f['identifier'] in C.SKIP_FORMS:
            continue
        if shared.vg_order[f['introduced_in_version_group_id']] > vg_order:
            continue
        if g['gen'] == 3 and sid == '386':
            continue  # a Gen 3 game shows Deoxys in its own form only
        if g['gen'] > 4 and f['identifier'] in C.GEN4_ONLY_FORMS:
            continue
        by_species[sid].append(f)
    return {sid: forms for sid, forms in by_species.items() if len(forms) > 1}


class GameBuilder:
    def __init__(self, shared, game_id):
        self.S = shared
        self.id = game_id
        self.g = C.GAMES[game_id]
        self.gen = self.g['gen']
        self.home = bool(self.g.get('home'))
        self.nat = nat_max(self.g)
        self.region_key = self.g['region']
        self.R = C.REGIONS[self.region_key]
        self.vg_order = shared.vg_order[str(self.g['vg'])]
        self.clock = C.CLOCKS[self.gen]
        kind = self.clock and self.clock['kind']
        if kind == 'tod':
            self.periods, self.clock_group = dict(TIME_PERIODS), TIME_GROUP
        elif kind == 'season':
            self.periods, self.clock_group = dict(C.SEASONS), SEASON_GROUP
        else:
            self.periods, self.clock_group = {None: 'a'}, None
        self.used_items, self.used_moves, self.used_locs = set(), set(), set()
        self.enc_pokemon = collections.defaultdict(dict)  # species -> {pokemon_id: lowest stage}
        self.problems = []

    # ---------------------------------------------------------------- helpers
    def loc_stage(self, ident):
        if ident in self.R['locations']:
            return self.R['locations'][ident]
        for prefix in self.R.get('location_default', ()):
            if ident.startswith(prefix):
                return self.R['location_default_stage']
        self.problems.append(f'no stage for location {ident}')
        return len(self.R['stages']) - 1

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
        st = self.R.get('cond_stage', {}).get(c['k'], st)
        if c['k'] in ('fossil', 'item'):
            iid = self.S.item_by_ident.get(c['v'])
            if iid:
                c['i'] = int(iid)
                self.used_items.add(iid)
        if c['k'] == 'key' and (self.id, c['v']) in C.OTHER_VERSION_KEY:
            ext = 'other'
        if c['k'] in ('give', 'starter-was'):
            if c['v'] == 'any-pokemon':
                c['s'] = 0
            else:
                sid = next((k for k, v in self.S.species.items() if v['identifier'] == c['v']), None)
                c['s'] = int(sid) if sid else 0
        gate = C.COND_GATE.get(c['k'])
        if gate not in self.R['gates']:
            gate = None
        return c, (0 if gate else st), ext, gate

    def method_stage(self, method):
        return max([self.R['gates'][g] for g in self.R['method_gates'].get(method, [])], default=0)

    def stages(self):
        if self.g.get('badges') == 'dp':
            return C._badge_stages(C.DP_BADGES) + self.R['stages'][len(C.DP_BADGES) + 1:]
        return self.R['stages']

    def starter_groups(self):
        return self.g.get('starters', self.R['starter_groups'])

    # ------------------------------------------------------------------ areas
    def canonical_area(self, area_id):
        """Areas PokéAPI only knows as "unknown area 53" are merged into one area per place."""
        ar = self.S.areas[area_id]
        if 'unknown' not in (ar['identifier'] or ''):
            return area_id, False
        same = [a for a in self.S.areas.values() if a['location_id'] == ar['location_id'] and 'unknown' in (a['identifier'] or '')]
        return min(same, key=lambda a: int(a['id']))['id'], True

    def build_area(self, area_id, merged=False):
        ar = self.S.areas[area_id]
        loc = self.S.locations[ar['location_id']]
        ident = loc['identifier']
        self.used_locs.add(ar['location_id'])
        prose = self.S.area_prose.get(area_id, '')
        m = re.search(r'\((.*)\)$', prose)
        if merged:
            raw = ''
        elif ar['identifier'] in l10n.SUB_EN_FORCE:
            raw = l10n.SUB_EN_FORCE[ar['identifier']]
        elif m:
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
        area_ident = None if merged else ar['identifier']
        stage = self.R['areas'].get((ident, area_ident), self.loc_stage(ident))
        out = {'id': int(area_id), 'loc': int(ar['location_id']), 'key': ident, 'st': stage}
        ag = self.R.get('area_gates', {})
        gates = ag.get((ident, area_ident or None)) or ag.get((ident, None))
        if gates:
            out['gt'] = gates
        if raw:
            out['sub'] = {'en': l10n.tidy_sub_en(raw), 'es': sub_es[:1].upper() + sub_es[1:]}
        if self.region_key == 'sinnoh':
            out['side'] = 'w' if ident in self.R['west'] else 'e'
        return out

    # ------------------------------------------------------------- encounters
    def build_encounters(self):
        S = self.S
        if self.home:
            return {}, {}
        ok_regions = C.OFF_REGION_OK.get(self.region_key)
        groups = collections.defaultdict(list)
        for e in S.api.rows('encounters'):
            if e['version_id'] != str(self.g['version']):
                continue
            area = S.areas[e['location_area_id']]
            loc = S.locations[area['location_id']]
            if loc['identifier'].startswith('unknown'):
                continue  # PokéAPI placeholder areas
            if ok_regions and loc['region_id'] and int(loc['region_id']) not in ok_regions:
                continue  # listed for this game by mistake
            sp = S.pokemon[e['pokemon_id']]['species_id']
            if int(sp) > self.nat:
                continue
            m = S.methods[S.slots[e['encounter_slot_id']]['encounter_method_id']]
            groups[(sp, e['location_area_id'], m)].append(e)

        def matches(row_conds, ctx):
            by = collections.defaultdict(set)
            for c in row_conds:
                by[S.cond_vals[c]['encounter_condition_id']].add(c)
            return all(vals & ctx for vals in by.values())

        clock_ids = {v['identifier']: v['id'] for v in S.cond_vals.values() if v['identifier'] in self.periods}
        is_clock = lambda c: S.cond_vals[c]['encounter_condition_id'] == self.clock_group  # noqa: E731

        def context(period_ident, combo=()):
            ctx = {c for c in S.defaults if not is_clock(c)}
            if period_ident:
                ctx.add(clock_ids[period_ident])
            for c in combo:
                oc = S.cond_vals[c]['encounter_condition_id']
                ctx = {x for x in ctx if S.cond_vals[x]['encounter_condition_id'] != oc}
            return ctx | set(combo)

        def rarity(rows, ctx):
            return sum(int(S.slots[r['encounter_slot_id']]['rarity']) for r in rows if matches(S.cond_map[r['id']], ctx))

        starter_of = {sp: i for i, grp in enumerate(self.starter_groups()) for sp in grp}
        out = collections.defaultdict(dict)   # species -> {(canonical area, method): item}
        areas = {}
        for (sp, a, m), rs in sorted(groups.items(), key=lambda kv: (int(kv[0][0]), int(kv[0][1]), kv[0][2])):
            if sp not in S.species:
                continue
            ca, merged = self.canonical_area(a)
            if ca not in areas:
                areas[ca] = self.build_area(ca, merged)
            item = {'a': int(ca), 'm': m, 'lv': [min(int(r['min_level']) for r in rs), max(int(r['max_level']) for r in rs)]}
            if m in GUARANTEED:
                req, st, ext, gates = [], 0, set(), set()
                for r in rs:
                    for cid in S.cond_map[r['id']]:
                        if cid in S.defaults:
                            continue
                        ident = S.cond_vals[cid]['identifier']
                        if ident in TIME_PERIODS:
                            c, cst, cext, cgate = {'k': 'time', 'v': TIME_PERIODS[ident]}, 0, None, None
                        elif ident in C.SEASONS:
                            c, cst, cext, cgate = {'k': 'season', 'v': C.SEASONS[ident]}, 0, None, None
                        else:
                            parsed = self.cond(cid)
                            if not parsed:
                                continue
                            c, cst, cext, cgate = parsed
                        if c not in req:
                            req.append(c)
                        if cgate:
                            gates.add(cgate)
                        st = max(st, cst)
                        if cext:
                            ext.add(cext)
                wd = C.EXTRA_WEEKDAY.get((self.id, int(sp), areas[ca]['key']))
                if wd and {'k': 'weekday', 'v': wd} not in req:
                    req.append({'k': 'weekday', 'v': wd})
                if m in EVENT_METHODS or (self.gen == 4 and int(sp) in C.EVENT_SPECIES) or areas[ca]['key'] in C.EVENT_LOCATIONS:
                    ext.add('event')
                item['g'] = 1
                if req:
                    item['req'] = req
                if st:
                    item['cst'] = st
                if gates:
                    item['gt'] = sorted(gates)
                if ext:
                    item['ext'] = sorted(ext)
                if m in ONE_TIME and not any(c['k'] in ('fossil', 'coins') for c in req):
                    item['one'] = 1
                if m == 'gift' and int(sp) in starter_of:
                    item['sg'] = starter_of[int(sp)]
                score = 100
            else:
                t = {k: rarity(rs, context(p)) for p, k in self.periods.items()}
                item['t'] = t
                specials = {}
                combos = {frozenset(c for c in S.cond_map[r['id']] if c not in S.defaults and not is_clock(c)) for r in rs}
                for combo in sorted(combos, key=lambda c: sorted(int(x) for x in c)):
                    if not combo:
                        continue
                    best = max(rarity(rs, context(p, combo)) for p in self.periods)
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
                        gts = sorted({p[3] for p in parsed if p[3]})
                        if gts:
                            entry['gt'] = gts
                        ext = [p[2] for p in parsed if p[2]]
                        if ext:
                            entry['ext'] = ext[0]
                        specials[key] = entry
                if specials:
                    item['sp'] = sorted(specials.values(), key=lambda s: (-s['p'], json.dumps(s['c'], sort_keys=True)))
                if self.R.get('level_hints'):
                    lv_stage = self.level_stage(item['lv'][0])
                    hint = len(self.R['stages']) - 1 if lv_stage >= len(self.R['level_caps']) - 1 else lv_stage - 1
                    if hint > areas[ca]['st']:
                        item['cst'] = hint
                score = max(list(t.values()) + [s['p'] for s in item.get('sp', [])])
            # which Pokémon (form) shows up here, for forms like Blue-Striped Basculin
            a_st = max(areas[ca]['st'], self.method_stage(m))
            for r in rs:
                pid = r['pokemon_id']
                prev = self.enc_pokemon[int(sp)].get(pid)
                self.enc_pokemon[int(sp)][pid] = a_st if prev is None else min(prev, a_st)
            key = (int(ca), m)
            prev = out[int(sp)].get(key)
            if prev is None:
                out[int(sp)][key] = (score, item)
            else:  # merged "unknown" areas: keep the better table, widen the levels
                pscore, pitem = prev
                keep = item if score > pscore else pitem
                keep['lv'] = [min(item['lv'][0], pitem['lv'][0]), max(item['lv'][1], pitem['lv'][1])]
                out[int(sp)][key] = (max(score, pscore), keep)
        return {sp: [it for _, it in d.values()] for sp, d in out.items()}, {str(k): v for k, v in areas.items()}

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
            if r.get('trade_species_id'):
                e['ts'] = int(r['trade_species_id'])
            if r['minimum_happiness']:
                e['fr'] = 1
            if r['minimum_beauty']:
                e['be'] = 1
                if not self.R['beauty']:
                    ext = 'trade'
                else:
                    st = max(st, self.R.get('beauty_stage', 2))
            if r['time_of_day']:
                e['tod'] = 'd' if r['time_of_day'] == 'day' else 'n'
                if not self.R.get('clock', True):
                    ext = 'trade'  # no clock in this game (FireRed/LeafGreen)
            if r['gender_id']:
                e['g'] = 'f' if r['gender_id'] == '1' else 'm'
            if r['relative_physical_stats']:
                e['ps'] = int(r['relative_physical_stats'])
            if e['t'] == 'trade':
                ext = 'trade'
            if (self.id, int(sid)) in C.EVO_EXT:
                ext = C.EVO_EXT[(self.id, int(sid))]
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
        out = []
        for sid, forms in sorted(form_entries(S, self.id).items(), key=lambda kv: int(kv[0])):
            forms = sorted(forms, key=lambda f: (int(f['form_order']), int(f['id'])))
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
                if self.home:
                    entry.update({'how': [{'k': 'from-games'}], 'ext': 'trade', 'dep': 0} if not default else {'how': [{'k': 'default'}]})
                else:
                    entry.update(self.form_rules(int(sid), fid, default, encounters, areas, f['pokemon_id']))
                nobox = C.NOT_BOXABLE_HOME if self.home else C.NOT_BOXABLE_GEN5 if self.gen == 5 else C.NOT_BOXABLE
                if f['identifier'] in nobox:
                    entry['nobox'] = 1
                out.append(entry)
        return out

    def xfer_in(self):
        return {'how': [{'k': 'xfer-in'}], 'ext': 'trade', 'dep': 0}

    def form_rules(self, sid, fid, default, encounters, areas, pokemon_id):
        R, game = self.R, self.id
        sinnoh = self.region_key == 'sinnoh'
        unova = self.region_key in UNOVA
        b2w2 = self.region_key == 'unova2'
        if sid == 201:
            kind = R['unown']
            if kind == 'sinnoh':
                if fid in ('exclamation', 'question'):
                    return {'how': [{'k': 'unown', 'v': 'tunnel'}], 'st': 4}
                letter = (fid or 'a').upper()
                return {'how': [{'k': 'unown', 'v': 'friend' if letter in 'FRIEND' else 'room'}], 'st': 2}
            if kind in ('johto', 'gsc'):
                if fid in ('exclamation', 'question'):
                    return {'how': [{'k': 'alph', 'v': 'report'}], 'st': 1}
                letter = (fid or 'a').upper()
                table, prefix = (UNOWN_JOHTO, 'alph') if kind == 'johto' else (UNOWN_GSC, 'alph2')
                puzzle = next(p for letters, p in table if letter in letters)
                return {'how': [{'k': prefix, 'v': puzzle}], 'st': 1}
            if kind == 'tanoby':
                return {'how': [{'k': 'tanoby'}], 'st': 9}
            return {'how': [{'k': 'default'}]} if default else self.xfer_in()
        # a form that is its own Pokémon in the encounter tables (Blue-Striped Basculin)
        seen = self.enc_pokemon.get(sid, {})
        if not default and pokemon_id in seen and pokemon_id != str(sid):
            return {'how': [{'k': 'wild'}], 'st': seen[pokemon_id], 'dep': 0}
        if sid == 550 and not default:
            return self.xfer_in()
        if sid == 412:
            return {'how': [{'k': 'cloak', 'v': fid}]}
        if sid == 413:
            return {'how': [{'k': 'evo-cloak', 'v': fid}]}
        if sid in (422, 423):
            if not sinnoh:
                return self.xfer_in()
            side = 'w' if fid == 'west' else 'e'
            def sea_stage(species):
                st = None
                for e in encounters.get(species, []):
                    a = areas[str(e['a'])]
                    if a.get('side') == side:
                        s = max([a['st'], self.method_stage(e['m'])] + [R['gates'][g] for g in a.get('gt', [])])
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
            if b2w2:
                return {'how': [{'k': 'rotom-mall'}], 'st': 6}
            if unova:
                return self.xfer_in()
            return {'how': [{'k': 'trade-in', 'v': 'platinum'}], 'ext': 'trade'}
        if sid == 487 and fid == 'origin':
            if game == 'platinum':
                return {'how': [{'k': 'griseous', 'v': 'distortion'}], 'st': 9}
            if unova:
                return self.xfer_in()
            return {'how': [{'k': 'griseous', 'v': 'sinjoh'}], 'ext': 'event'}
        if sid == 492 and fid == 'sky':
            return {'how': [{'k': 'gracidea', 'v': 'floaroma' if sinnoh else 'unova' if unova else 'goldenrod'}], 'ext': 'event'}
        if sid == 386 and fid != 'normal':
            place = 'veilstone' if sinnoh else 'nacrene' if unova else 'route-3'
            return {'how': [{'k': 'meteorite', 'v': place}], 'st': 3 if sinnoh else 9, 'ext': 'event'}
        if sid == 493 and fid != 'normal':
            plate = self.S.item_by_ident[PLATE_FOR_TYPE[fid]]
            self.used_items.add(plate)
            return {'how': [{'k': 'plate', 'i': int(plate)}], 'ext': 'event'}
        if sid == 493:
            return {'how': [{'k': 'no-plate'}]}
        if sid == 172 and fid == 'spiky-eared':
            return {'how': [{'k': 'spiky'}], 'ext': 'event'}
        if sid in (585, 586) and not default:
            return {'how': [{'k': 'season', 'v': fid}]}
        if sid in (641, 642, 645) and fid == 'therian':
            if b2w2:
                return {'how': [{'k': 'reveal-glass'}], 'st': 9}
            return {'how': [{'k': 'trade-in', 'v': 'b2w2'}], 'ext': 'trade', 'dep': 0}
        if sid == 646 and fid in ('black', 'white'):
            if b2w2:
                return {'how': [{'k': 'dna-splicers', 'v': fid}], 'st': 9}
            return {'how': [{'k': 'trade-in', 'v': 'b2w2'}], 'ext': 'trade', 'dep': 0}
        if sid == 647 and fid == 'resolute':
            return {'how': [{'k': 'secret-sword'}], 'ext': 'event'}
        if sid == 649 and fid in DRIVE_FOR_FORM:
            drive = self.S.item_by_ident[DRIVE_FOR_FORM[fid]]
            self.used_items.add(drive)
            return {'how': [{'k': 'drive', 'i': int(drive)}], 'ext': 'event'}
        return {'how': [{'k': 'default'}]}

    # ------------------------------------------------------------------ build
    def build(self, sprite_index):
        S = self.S
        encounters, areas = self.build_encounters()
        regional = S.dex_numbers[S.dexes[self.g['dex']]] if self.g['dex'] else {}
        species = []
        for sid, s in sorted(S.species.items(), key=lambda kv: int(kv[0])):
            if int(sid) > self.nat:
                continue
            n = S.sp_names[sid]
            o = {'id': int(sid), 'n': n['en']}
            if n.get('es') and n['es'] != n['en']:
                o['ne'] = n['es']
            o['ty'] = S.types_for(sid, self.gen)
            o['ch'] = int(s['evolution_chain_id'])
            if sid in regional:
                o['rd'] = regional[sid]
            if s['evolves_from_species_id'] and int(s['evolves_from_species_id']) <= self.nat:
                o['f'] = int(s['evolves_from_species_id'])
                evs = self.build_evolutions(sid)
                if evs:
                    o['ev'] = evs
            if s['is_baby'] == '1' and any(int(k) <= self.nat and v['evolves_from_species_id'] == sid for k, v in S.species.items()):
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
        max_type = 18 if self.home else 17
        types = {tid: S.type_names[tid] for tid in S.type_names if int(tid) <= max_type}

        area_list = sorted(areas.values(), key=lambda a: (a['st'], locs[str(a['loc'])]['en'], a.get('sub', {}).get('en', '')))
        R = self.R
        box_size, box_cols, box_count = C.BOXES[self.gen]
        game = {'id': self.id, 'gen': self.gen, 'name': self.g['name'], 'short': self.g['short'], 'region': self.region_key,
                'sprites': self.g['sprites'], 'natMax': self.nat, 'regionalSize': len(regional),
                'stages': self.stages(), 'dayCareStage': R['day_care_stage'], 'levelCaps': R['level_caps'],
                'starterGroups': self.starter_groups(), 'gates': R['gates'], 'methodGates': R['method_gates'],
                'methodStage': {m: self.method_stage(m) for m in R['method_gates']},
                'clock': self.clock, 'periods': list(self.periods.values()),
                'boxes': {'size': box_size, 'cols': box_cols, 'count': box_count}}
        if self.home:
            game['home'] = True
        return {
            'game': game,
            'species': species,
            'areas': area_list,
            'forms': forms,
            'names': {'loc': locs, 'item': items, 'move': moves, 'type': types},
        }


def form_sprite_files(shared, game_ids):
    """{(sprite_set, form_identifier): candidate file names} for every alternate form any game uses."""
    out = collections.OrderedDict()
    for gid in game_ids:
        g = C.GAMES[gid]
        for sid, forms in form_entries(shared, gid).items():
            for f in forms:
                p = shared.pokemon[f['pokemon_id']]
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

    # sprite indices: species 1..N at index id-1 (N = the set's last species), then forms per sprite set
    sprite_forms = form_sprite_files(shared, list(C.GAMES))
    per_set = collections.defaultdict(dict)
    for (sset, key), cands in sprite_forms.items():
        per_set[sset][key] = {'index': C.SPRITE_SETS[sset][1] + len(per_set[sset]), 'files': cands}
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
        g = C.GAMES[gid]
        entry = {'id': gid, 'gen': g['gen'], 'main': True, 'name': g['name'], 'short': g['short'], 'sprites': g['sprites']}
        if g.get('home'):
            entry['home'] = True
        index['games'].append(entry)
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
