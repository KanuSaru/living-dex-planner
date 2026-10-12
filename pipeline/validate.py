"""Data checks that fail the build. Run after build_data and build_sprites.

Usage: python3 -m pipeline.validate generated
Exit code 1 when any check fails, so CI never deploys broken or shrunken data.
"""
import json
import os
import sys

from . import config as C


def _json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


KNOWN_METHODS = {'walk', 'surf', 'old-rod', 'good-rod', 'super-rod', 'rock-smash', 'headbutt', 'honey-tree',
                 'gift', 'gift-egg', 'static', 'roaming-grass', 'roaming-water', 'npc-trade', 'pokemon-ranger',
                 'feebas-tile-fishing', 'pokeflute', 'squirt-bottle', 'seaweed', 'devon-scope', 'wailmer-pail',
                 'colosseum-bonus-disc-jpn', 'colosseum-bonus-disc-us', 'pokemon-channel-pal',
                 'headbutt-low', 'headbutt-normal', 'headbutt-high', 'dark-grass', 'grass-spots', 'cave-spots',
                 'bridge-spots', 'surf-spots', 'super-rod-spots', 'hidden-grotto'}
KNOWN_COND = {'swarm', 'radar', 'slot2', 'radio', 'natdex', 'story', 'other', 'weekday', 'honey', 'marsh', 'backlot',
              'contest', 'coins', 'headbutt', 'safari', 'give', 'fossil', 'item', 'time', 'tv', 'starter-was', 'season', 'key'}
KNOWN_FORM_HOW = {'unown', 'alph', 'cloak', 'evo-cloak', 'sea', 'evo-sea', 'trade-in', 'rotom-room', 'griseous',
                  'gracidea', 'meteorite', 'plate', 'no-plate', 'spiky', 'default', 'alph2', 'tanoby', 'xfer-in',
                  'wild', 'rotom-mall', 'season', 'reveal-glass', 'dna-splicers', 'secret-sword', 'drive', 'from-games'}
KNOWN_EXT = {'trade', 'gba', 'event', 'other', 'vc'}


def check_game(gid, d, errors):
    exp = C.EXPECT[gid]
    err = lambda msg: errors.append(f'{gid}: {msg}')  # noqa: E731
    species = d['species']
    top = C.NAT_MAX[C.GAMES[gid]['gen']]
    if len(species) != top or [s['id'] for s in species] != list(range(1, top + 1)) or d['game']['natMax'] != top:
        err(f'expected species 1..{top}, got {len(species)}')
    ids = {s['id'] for s in species}
    for s in species:
        for key in ('f', 'pa', 'ts'):
            refs = [s.get(key)] if key == 'f' else [ev.get(key) for ev in s.get('ev', [])]
            for r in refs:
                if r is not None and r not in ids:
                    err(f'{s["n"]}: {key} points to species {r}, which is not in this game')
    if len(d['game']['periods']) not in (1, 3, 4):
        err(f'unexpected periods {d["game"]["periods"]}')
    with_enc = sum(1 for s in species if s.get('e'))
    if with_enc < exp['species_with_encounters']:
        err(f'only {with_enc} species have encounters (expected at least {exp["species_with_encounters"]})')
    if len(d['areas']) < exp['areas']:
        err(f'only {len(d["areas"])} areas (expected at least {exp["areas"]})')
    regional = sum(1 for s in species if 'rd' in s)
    if regional != exp['regional'] or d['game']['regionalSize'] != exp['regional']:
        err(f'regional dex has {regional} entries (expected {exp["regional"]})')

    names = d['names']
    max_stage = len(d['game']['stages']) - 1
    areas = {a['id']: a for a in d['areas']}
    for a in d['areas']:
        if not 0 <= a['st'] <= max_stage:
            err(f'area {a["key"]} has stage {a["st"]} outside 0..{max_stage}')
        loc = names['loc'].get(str(a['loc']))
        if not loc or not loc.get('en') or not loc.get('es'):
            err(f'area {a["key"]} has no English/Spanish location name')
        if 'sub' in a and (not a['sub'].get('en') or not a['sub'].get('es')):
            err(f'area {a["key"]} sub-area label incomplete')

    gates = d['game'].get('gates', {})
    for a in d['areas']:
        for g in a.get('gt', []):
            if g not in gates:
                err(f'area {a["key"]} uses unknown gate {g}')
    for m, gs in d['game'].get('methodGates', {}).items():
        for g in gs:
            if g not in gates:
                err(f'method {m} uses unknown gate {g}')

    def check_cond(c, where):
        if c.get('k') not in KNOWN_COND:
            err(f'{where}: unknown condition {c}')
        if c.get('k') in ('fossil', 'item') and str(c.get('i')) not in names['item']:
            err(f'{where}: condition item {c} has no name')

    for s in species:
        for e in s.get('e', []):
            where = f'{s["n"]} @ area {e["a"]}'
            if e['a'] not in areas:
                err(f'{where}: unknown area')
            if e['m'] not in KNOWN_METHODS:
                err(f'{where}: unknown method {e["m"]}')
            if not e.get('g') and set(e.get('t', {})) != set(d['game']['periods']):
                err(f'{where}: wild encounter rates don\'t match the game\'s periods')
            for c in e.get('req', []):
                check_cond(c, where)
            for g in e.get('gt', []) + [g for sp in e.get('sp', []) for g in sp.get('gt', [])]:
                if g not in gates:
                    err(f'{where}: unknown gate {g}')
            for sp in e.get('sp', []):
                for c in sp['c']:
                    check_cond(c, where)
                if sp.get('ext') and sp['ext'] not in KNOWN_EXT:
                    err(f'{where}: unknown external requirement {sp["ext"]}')
            for x in e.get('ext', []):
                if x not in KNOWN_EXT:
                    err(f'{where}: unknown external requirement {x}')
        for ev in s.get('ev', []):
            where = f'{s["n"]} evolution'
            if ev['t'] not in ('level', 'trade', 'item', 'shed'):
                err(f'{where}: unknown trigger {ev["t"]}')
            for key, table in (('it', 'item'), ('hi', 'item'), ('mv', 'move'), ('lo', 'loc')):
                if key in ev and str(ev[key]) not in names[table]:
                    err(f'{where}: {table} {ev[key]} has no name')
        if 'inc' in s and str(s['inc']) not in names['item']:
            err(f'{s["n"]}: incense item has no name')

    for f in d['forms']:
        for h in f['how']:
            if h['k'] not in KNOWN_FORM_HOW:
                err(f'form {f["key"]}: unknown method {h}')
            if h['k'] in ('plate', 'drive') and str(h['i']) not in names['item']:
                err(f'form {f["key"]}: plate has no name')
        if not f['n'].get('en') or not f['n'].get('es'):
            err(f'form {f["key"]}: missing name')
        if f.get('ext') and f['ext'] not in KNOWN_EXT:
            err(f'form {f["key"]}: unknown external requirement')
    # every multi-form species must have exactly one default form
    defaults = {}
    for f in d['forms']:
        defaults[f['sp']] = defaults.get(f['sp'], 0) + f['def']
    for sp, n in defaults.items():
        if n != 1:
            err(f'species {sp} has {n} default forms')


def main(argv):
    out_dir = argv[0] if argv else 'generated'
    errors = []
    for name in ('build-problems.json', 'sprite-problems.json'):
        path = os.path.join(out_dir, name)
        if not os.path.exists(path):
            errors.append(f'{name} missing: run build_data and build_sprites first')
            continue
        problems = _json(path)
        if isinstance(problems, dict):
            problems = [f'{k}: missing sprite {v}' for k, vs in problems.items() for v in vs]
        errors += problems
    for gid in C.GAMES:
        path = os.path.join(out_dir, 'data', f'{gid}.json')
        if not os.path.exists(path):
            errors.append(f'{gid}: data file missing')
            continue
        d = _json(path)
        check_game(gid, d, errors)
        sheet = os.path.join(out_dir, 'sprites', f'{d["game"]["sprites"]}.webp')
        if not os.path.exists(sheet):
            errors.append(f'{gid}: sprite sheet {sheet} missing')
    if errors:
        print(f'Data validation failed ({len(errors)} problems):')
        for e in errors[:200]:
            print('  -', e)
        sys.exit(1)
    print('Data validation passed for', ', '.join(C.GAMES))


if __name__ == '__main__':
    main(sys.argv[1:])
