"""Build a compact Platinum living-dex dataset (data.json) from PokéAPI's CSV source data.

Usage: python3 build_data.py <pokeapi>/data/v2/csv data.json
"""
import csv, json, sys, collections, os, re

D = sys.argv[1]  # path to pokeapi data/v2/csv
OUT = sys.argv[2]
EN = '9'
PT_VERSION, PT_VG_ORDER = '14', 13

def rows(name):
    with open(os.path.join(D, name + '.csv'), encoding='utf-8') as f:
        return list(csv.DictReader(f))

species = {r['id']: r for r in rows('pokemon_species') if int(r['generation_id']) <= 4}
sp_name = {r['pokemon_species_id']: r['name'] for r in rows('pokemon_species_names') if r['local_language_id'] == EN}
pokemon = {r['id']: r for r in rows('pokemon')}
type_name = {r['type_id']: r['name'] for r in rows('type_names') if r['local_language_id'] == EN}
item_name = {r['item_id']: r['name'] for r in rows('item_names') if r['local_language_id'] == EN}
move_name = {r['move_id']: r['name'] for r in rows('move_names') if r['local_language_id'] == EN}
loc_name = {r['location_id']: r['name'] for r in rows('location_names') if r['local_language_id'] == EN}
locations = {r['id']: r for r in rows('locations')}
areas_raw = {r['id']: r for r in rows('location_areas')}
vg_order = {r['id']: int(r['order']) for r in rows('version_groups')}
slots = {r['id']: r for r in rows('encounter_slots')}
methods = {r['id']: r['identifier'] for r in rows('encounter_methods')}
cond_vals = {r['id']: r for r in rows('encounter_condition_values')}
cond_prose = {r['encounter_condition_value_id']: r['name'] for r in rows('encounter_condition_value_prose') if r['local_language_id'] == EN}
chains = {r['id']: r for r in rows('evolution_chains')}

# Types (default form)
types = collections.defaultdict(list)
for r in rows('pokemon_types'):
    p = pokemon.get(r['pokemon_id'])
    if p and p['is_default'] == '1' and p['species_id'] in species:
        types[p['species_id']].append((int(r['slot']), type_name[r['type_id']]))

# Platinum regional dex (extended-sinnoh, id 6)
sinnoh_no = {r['species_id']: int(r['pokedex_number']) for r in rows('pokemon_dex_numbers') if r['pokedex_id'] == '6'}

# ---------- Story-progress estimate (badges needed; 9 = post-game / National Dex) ----------
LOC_STAGE = {
    'twinleaf-town': 0, 'sinnoh-route-201': 0, 'lake-verity': 0, 'sinnoh-route-202': 0, 'sinnoh-route-203': 0,
    'oreburgh-gate': 0, 'oreburgh-mine': 0, 'sinnoh-route-204': 0, 'oreburgh-city': 1, 'ravaged-path': 1,
    'floaroma-meadow': 1, 'sinnoh-route-205': 1, 'valley-windworks': 1, 'eterna-forest': 1, 'eterna-city': 1,
    'sinnoh-route-211': 1, 'old-chateau': 2, 'sinnoh-route-206': 2, 'wayward-cave': 2, 'sinnoh-route-207': 2,
    'mt-coronet': 2, 'sinnoh-route-208': 2, 'hearthome-city': 2, 'sinnoh-route-209': 2, 'lost-tower': 2,
    'solaceon-ruins': 2, 'sinnoh-route-210': 2, 'sinnoh-route-215': 3, 'veilstone-city': 3,
    'sinnoh-route-214': 4, 'ruin-maniac-cave': 4, 'maniac-tunnel': 4, 'valor-lakefront': 4, 'sinnoh-route-213': 4,
    'pastoria-city': 4, 'great-marsh': 4, 'sinnoh-route-212': 4, 'trophy-garden': 4,
    'celestic-town': 5, 'sinnoh-route-218': 5, 'canalave-city': 5, 'iron-island': 5, 'sinnoh-route-219': 5,
    'sinnoh-sea-route-220': 5, 'sinnoh-route-221': 5, 'fuego-ironworks': 5,
    'lake-valor': 6, 'sinnoh-route-216': 6, 'sinnoh-route-217': 6, 'acuity-lakefront': 6, 'snowpoint-city': 6,
    'lake-acuity': 6, 'spear-pillar': 7, 'distortion-world': 7, 'sinnoh-route-222': 7, 'sunyshore-city': 7,
    'roaming-sinnoh': 7, 'sinnoh-sea-route-223': 8, 'sinnoh-victory-road': 8, 'sinnoh-pokemon-league': 8,
    'snowpoint-temple': 9, 'sinnoh-route-224': 9, 'sinnoh-route-225': 9, 'sinnoh-sea-route-226': 9,
    'sinnoh-route-227': 9, 'sinnoh-route-228': 9, 'sinnoh-route-229': 9, 'sinnoh-sea-route-230': 9,
    'stark-mountain': 9, 'resort-area': 9, 'sendoff-spring': 9, 'turnback-cave': 9, 'newmoon-island': 9,
    'flower-paradise': 9, 'sinnoh-hall-of-origin-1': 9, 'sinnoh-pokemart': 9,
}
AREA_STAGE = {  # (location, area) overrides
    ('sinnoh-route-204', 'north-towards-floaroma-town'): 1, ('oreburgh-gate', 'b1f'): 1,
    ('mt-coronet', '1f-route-211'): 1, ('mt-coronet', 'b1f'): 5, ('mt-coronet', '1f-route-216'): 6,
    ('mt-coronet', '2f'): 6, ('mt-coronet', '3f'): 7, ('mt-coronet', '4f'): 7, ('mt-coronet', '4f-small-room'): 7,
    ('mt-coronet', '5f'): 7, ('mt-coronet', '6f'): 7, ('mt-coronet', 'exterior-snowfall'): 7,
    ('mt-coronet', 'exterior-blizzard'): 7, ('mt-coronet', '1f-from-exterior'): 7,
    ('sinnoh-route-210', 'west-towards-celestic-town'): 5, ('sinnoh-route-211', 'east-towards-celestic-town'): 5,
    ('lake-verity', 'after-galactic-intervention'): 7, ('lake-acuity', 'cavern'): 7, ('lake-valor', 'cavern'): 7,
    ('eterna-city', 'eterna-condominiums'): 1, ('stark-mountain', 'heatran-chamber'): 9,
}
METHOD_STAGE = {'surf': 5, 'good-rod': 2, 'super-rod': 9, 'honey-tree': 1, 'feebas-tile-fishing': 5}
METHOD_LABEL = {
    'walk': 'Grass / cave', 'surf': 'Surfing', 'old-rod': 'Old Rod', 'good-rod': 'Good Rod', 'super-rod': 'Super Rod',
    'honey-tree': 'Honey tree', 'gift': 'Gift', 'gift-egg': 'Gift egg', 'static': 'Static encounter',
    'roaming-grass': 'Roaming (land)', 'roaming-water': 'Roaming (water)', 'npc-trade': 'In-game trade',
    'pokemon-ranger': 'Pokémon Ranger egg (event)', 'feebas-tile-fishing': 'Feebas tiles (any rod)',
}
GUARANTEED = {'gift', 'gift-egg', 'static', 'roaming-grass', 'roaming-water', 'npc-trade', 'pokemon-ranger'}
# Conditions that change availability; value -> (short label, stage, external requirement)
COND = {
    'swarm-yes': ('Swarm', 9, None), 'radar-on': ('Poké Radar', 9, None),
    'slot2-ruby': ('Ruby in GBA slot', 9, 'GBA game'), 'slot2-sapphire': ('Sapphire in GBA slot', 9, 'GBA game'),
    'slot2-emerald': ('Emerald in GBA slot', 9, 'GBA game'), 'slot2-firered': ('FireRed in GBA slot', 9, 'GBA game'),
    'slot2-leafgreen': ('LeafGreen in GBA slot', 9, 'GBA game'),
    'story-progress-national-dex': ('National Dex', 9, None), 'story-progress-hall-of-fame': ('After Hall of Fame', 9, None),
    'story-progress-oak-eterna-city': ('After talking to Oak in Eterna', 9, None),
    'story-progress-beat-galactic-coronet': ('After Spear Pillar', 7, None),
    'story-progress-cure-eldritch-nightmares': ("Cure Eldritch's son (needs Lunar Wing)", 9, None),
    'other-talk-to-cynthias-grandmother': ("Talk to Cynthia's grandmother", 9, None),
    'story-progress-defeat-jupiter': ('After beating Jupiter', 2, None),
    'story-progress-beat-team-galactic-iron-island': ('After Iron Island with Riley', 5, None),
    'story-progress-defeat-mars': ('After beating Mars · Fridays', 1, None),
    'other-regirock-regice-registeel-in-party': ('Regirock, Regice & Registeel in party', 9, 'Other games'),
    'other-giratina-not-caught-in-distortion-world': ('If Giratina was not caught before', 9, None),
    'item-adamant-orb': ('Adamant Orb in bag', 9, None), 'item-lustrous-orb': ('Lustrous Orb in bag', 9, None),
    'item-odd-keystone': ('Odd Keystone', 2, None), 'other-talked-to-32-people-underground': ('Talk to 32 people Underground', 2, None),
    'backlot-mentioned': ('Mr. Backlot daily Pokémon', 9, None),
    'honey-tree-group-a': ('Honey tree · group A', 1, None), 'honey-tree-group-b': ('Honey tree · group B', 1, None),
    'honey-tree-group-c': ('Special honey trees only', 1, None),
}
for v in cond_vals.values():
    i = v['identifier']
    if i.startswith('item-') and i.endswith('fossil') or i == 'item-old-amber':
        COND[i] = ('Fossil: ' + cond_prose.get(v['id'], i).replace('Have ', '').replace(' in bag', ''), 1, None)
    if i.startswith('trade-'):
        COND[i] = ('Give ' + i[6:].replace('-', ' ').title(), 0, None)
    if i.startswith('great-marsh-daily-slot-') and i != 'great-marsh-daily-slot-none':
        COND[i] = ('Great Marsh daily rotation', 4, None)
TIME = {'time-morning': 'm', 'time-day': 'd', 'time-night': 'n'}
DEFAULTS = {v['id'] for v in cond_vals.values() if v['is_default'] == '1'}
for v in cond_vals.values():
    if v['identifier'] in ('great-marsh-daily-slot-none', 'backlot-not-mentioned', 'story-progress-before-national-dex'):
        DEFAULTS.add(v['id'])

def pretty_area(loc_id, ident):
    base = loc_name.get(loc_id) or locations[loc_id]['identifier'].replace('-', ' ').title()
    if not ident:
        return base, ''
    words = []
    for w in ident.split('-'):
        if re.fullmatch(r'b?\d+f', w): words.append(w.upper())
        elif w in ('route',): words.append('Route')
        else: words.append(w)
    sub = ' '.join(words)
    sub = sub[0].upper() + sub[1:]
    return base, sub

area_prose = {r['location_area_id']: r['name'] for r in rows('location_area_prose') if r['local_language_id'] == EN}
cmap = collections.defaultdict(list)
for r in rows('encounter_condition_value_map'):
    cmap[r['encounter_id']].append(r['encounter_condition_value_id'])

enc = [r for r in rows('encounters') if r['version_id'] == PT_VERSION]
groups = collections.defaultdict(list)  # (species, area, method) -> rows
areas_used = set()
for e in enc:
    sp = pokemon[e['pokemon_id']]['species_id']
    m = methods[slots[e['encounter_slot_id']]['encounter_method_id']]
    groups[(sp, e['location_area_id'], m)].append(e)
    areas_used.add(e['location_area_id'])

def matches(row_conds, context):
    by = collections.defaultdict(set)
    for c in row_conds:
        by[cond_vals[c]['encounter_condition_id']].add(c)
    return all(vals & context for vals in by.values())

def context_for(time_ident, override=None):
    ctx = set(DEFAULTS)
    tid = next(v['id'] for v in cond_vals.values() if v['identifier'] == time_ident)
    ctx = {c for c in ctx if cond_vals[c]['encounter_condition_id'] != '2'} | {tid}
    if override:
        oc = cond_vals[override]['encounter_condition_id']
        ctx = {c for c in ctx if cond_vals[c]['encounter_condition_id'] != oc} | {override}
    return ctx

areas_out = {}
for a in areas_used:
    ar = areas_raw[a]; loc = locations[ar['location_id']]
    base, sub = pretty_area(ar['location_id'], ar['identifier'])
    pr = area_prose.get(a, '')
    mm = re.search(r'\((.*)\)$', pr)
    if mm and sub:
        sub = mm.group(1).replace('Road ', 'Route ')
        sub = sub[0].upper() + sub[1:]
    if a == '1213': base, sub = 'Event', 'Manaphy egg via Pokémon Ranger'
    sub = {'Eterna condominiums': 'Eterna Condominiums', 'Oreburgh mining museum': 'Mining Museum'}.get(sub, sub)
    stage = AREA_STAGE.get((loc['identifier'], ar['identifier']), LOC_STAGE.get(loc['identifier']))
    if stage is None:
        print('NO STAGE', loc['identifier'], ar['identifier']); stage = 9
    areas_out[a] = {'id': int(a), 'loc': base, 'sub': sub, 'st': stage, 'key': loc['identifier']}

enc_out = collections.defaultdict(list)
for (sp, a, m), rs in groups.items():
    if sp not in species: continue
    lv = [min(int(r['min_level']) for r in rs), max(int(r['max_level']) for r in rs)]
    item = {'a': int(a), 'm': m, 'lv': lv}
    if m in GUARANTEED:
        req = []
        for r in rs:
            for c in cmap[r['id']]:
                if c in DEFAULTS: continue
                ident = cond_vals[c]['identifier']
                lab = COND.get(ident, (cond_prose.get(c, ident), 0, None))
                if lab not in req: req.append(lab)
        item['g'] = 1
        if m in ('gift', 'gift-egg', 'static', 'npc-trade') and not any(x[0].startswith('Fossil') for x in req) and not (sp == '425'):
            item['one'] = 1
        if sp in ('387', '390', '393') and m == 'gift':
            item['starter'] = 1
        item['req'] = [x[0] for x in req]
        item['cst'] = max([x[1] for x in req], default=0)
        ext = [x[2] for x in req if x[2]]
        if m == 'pokemon-ranger' or sp in ('491', '492', '493'): ext.append('Event')
        if ext: item['ext'] = sorted(set(ext))
    else:
        t = {}
        for k, ti in TIME.items():
            ctx = context_for(k)
            t[ti] = sum(int(slots[r['encounter_slot_id']]['rarity']) for r in rs if matches(cmap[r['id']], ctx))
        item['t'] = t
        specials = {}
        combos = {frozenset(c for c in cmap[r['id']] if c not in DEFAULTS and cond_vals[c]['encounter_condition_id'] != '2') for r in rs}
        for combo in sorted(combos, key=lambda c: sorted(int(x) for x in c)):
            if not combo: continue
            best = 0
            for k in TIME:
                ctx = context_for(k)
                for c in combo:
                    oc = cond_vals[c]['encounter_condition_id']
                    ctx = {x for x in ctx if cond_vals[x]['encounter_condition_id'] != oc}
                ctx |= combo
                best = max(best, sum(int(slots[r['encounter_slot_id']]['rarity']) for r in rs if matches(cmap[r['id']], ctx)))
            labs = [COND.get(cond_vals[c]['identifier'], (cond_prose.get(c, cond_vals[c]['identifier']), 0, None)) for c in sorted(combo, key=int)]
            # 'National Dex' is implied by most of the other post-game labels; keep it only when alone
            if len(labs) > 1: labs = [l for l in labs if l[0] != 'National Dex'] or labs
            if best > max(t.values()):
                key = ' + '.join(l[0] for l in labs)
                if key not in specials or specials[key]['p'] < best:
                    specials[key] = {'c': key, 'p': best, 'st': max(l[1] for l in labs)}
                    ext = [l[2] for l in labs if l[2]]
                    if ext: specials[key]['ext'] = ext[0]
        if specials: item['sp'] = sorted(specials.values(), key=lambda s: (-s['p'], s['c']))
    enc_out[sp].append(item)

# ---------- Evolutions valid in Platinum ----------
ev_rows = collections.defaultdict(list)
for r in rows('pokemon_evolution'):
    s = r['evolved_species_id']
    if s not in species or not r['version_group_id']: continue
    if vg_order[r['version_group_id']] > PT_VG_ORDER: continue
    if r['location_id'] and locations[r['location_id']]['region_id'] != '4': continue
    ev_rows[s].append(r)

TRIG = {'1': 'level-up', '2': 'trade', '3': 'use-item', '4': 'shed'}
def describe(r, parent):
    trig = TRIG.get(r['evolution_trigger_id'], 'other')
    parts, stage, ext, lvl = [], 0, None, None
    if trig == 'trade':
        parts.append('Trade'); ext = 'Trade'
        if r['held_item_id']: parts.append('holding ' + item_name[r['held_item_id']])
    elif trig == 'use-item':
        parts.append('Use ' + item_name[r['trigger_item_id']]); stage = 1
    elif trig == 'shed':
        parts.append('Spare party slot + Poké Ball when Nincada reaches Lv. 20'); lvl = 20
    else:
        if r['minimum_level']:
            lvl = int(r['minimum_level']); parts.append(f'Level {lvl}')
        else:
            parts.append('Level up')
        if r['minimum_happiness']: parts.append('with high friendship')
        if r['minimum_beauty']: parts.append('with max Beauty (Poffins)')
        if r['held_item_id']: parts.append('holding ' + item_name[r['held_item_id']]); stage = max(stage, 4)
        if r['known_move_id']: parts.append('knowing ' + move_name[r['known_move_id']])
        if r['location_id']:
            lid = r['location_id']; parts.append('at ' + loc_name.get(lid, locations[lid]['identifier']))
            stage = max(stage, LOC_STAGE.get(locations[lid]['identifier'], 0))
        if r['party_species_id']: parts.append('with ' + sp_name[r['party_species_id']] + ' in party')
        if r['relative_physical_stats']:
            parts.append({'1': '(Atk > Def)', '-1': '(Atk < Def)', '0': '(Atk = Def)'}[r['relative_physical_stats']])
    if r['gender_id']: parts.append('(female)' if r['gender_id'] == '1' else '(male)')
    if r['time_of_day']: parts.append({'day': 'during the day', 'night': 'at night'}.get(r['time_of_day'], r['time_of_day']))
    text = ' '.join(parts).replace('Level up at daytime', 'Level up during the day')
    return {'txt': text, 'st': stage, 'ext': ext, 'lv': lvl}

INCENSE = {}
for cid, c in chains.items():
    if c['baby_trigger_item_id']:
        INCENSE[cid] = item_name[c['baby_trigger_item_id']]

sp_out = []
for sid, s in sorted(species.items(), key=lambda kv: int(kv[0])):
    evo = None
    if s['evolves_from_species_id'] and ev_rows.get(sid):
        seen, opts = set(), []
        for r in ev_rows[sid]:
            d = describe(r, s['evolves_from_species_id'])
            if d['txt'] in seen: continue
            seen.add(d['txt']); opts.append(d)
        evo = opts
    o = {
        'id': int(sid), 'n': sp_name[sid], 'ty': [t for _, t in sorted(types[sid])],
        'g': int(s['generation_id']), 'ch': int(s['evolution_chain_id']),
    }
    if sid in sinnoh_no: o['sn'] = sinnoh_no[sid]
    if s['evolves_from_species_id']: o['f'] = int(s['evolves_from_species_id'])
    if evo: o['ev'] = evo
    if s['is_baby'] == '1':
        o['baby'] = 1
        inc = INCENSE.get(s['evolution_chain_id'])
        if inc: o['inc'] = inc
    if s['is_legendary'] == '1': o['leg'] = 1
    if s['is_mythical'] == '1': o['myth'] = 1
    if sid in ('132', '201', '144', '145', '146', '150', '151', '243', '244', '245', '249', '250', '251', '377', '378', '379', '380', '381', '382', '383', '384', '385', '386', '480', '481', '482', '483', '484', '485', '486', '487', '488', '489', '490', '491', '492', '493'):
        o['nobreed'] = 1
    if sid in enc_out: o['e'] = sorted(enc_out[sid], key=lambda x: (areas_out[str(x['a'])]['st'], x['a']))
    sp_out.append(o)

json.dump({'species': sp_out, 'areas': sorted(areas_out.values(), key=lambda a: (a['st'], a['loc'], a['sub'])),
           'methods': METHOD_LABEL, 'methodStage': METHOD_STAGE},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('species', len(sp_out), 'with encounters', sum(1 for s in sp_out if 'e' in s), 'areas', len(areas_out))
print('bytes', os.path.getsize(OUT))
