"""Per-game and per-region settings.

"Stage" is the planner's measure of story progress: 0 is the start of the game and each step is
roughly one gym badge. PokéAPI has no story order, so every stage below is a hand-written estimate.
Adjust them here; the validate step fails the build if an area has no stage.
"""

# ---------------------------------------------------------------- games ---
GAMES = {
    'ruby':       {'version': 7,  'vg': 5,  'gen': 3, 'name': {'en': 'Ruby', 'es': 'Rubí'},             'region': 'hoenn',  'dex': 'hoenn', 'sprites': 'pt', 'short': 'R'},
    'sapphire':   {'version': 8,  'vg': 5,  'gen': 3, 'name': {'en': 'Sapphire', 'es': 'Zafiro'},       'region': 'hoenn',  'dex': 'hoenn', 'sprites': 'pt', 'short': 'S'},
    'emerald':    {'version': 9,  'vg': 6,  'gen': 3, 'name': {'en': 'Emerald', 'es': 'Esmeralda'},    'region': 'hoenn',  'dex': 'hoenn', 'sprites': 'pt', 'short': 'E'},
    'firered':    {'version': 10, 'vg': 7,  'gen': 3, 'name': {'en': 'FireRed', 'es': 'Rojo Fuego'},   'region': 'kanto3', 'dex': 'kanto', 'sprites': 'pt', 'short': 'FR'},
    'leafgreen':  {'version': 11, 'vg': 7,  'gen': 3, 'name': {'en': 'LeafGreen', 'es': 'Verde Hoja'}, 'region': 'kanto3', 'dex': 'kanto', 'sprites': 'pt', 'short': 'LG'},
    'diamond':    {'version': 12, 'vg': 8,  'gen': 4, 'badges': 'dp', 'name': {'en': 'Diamond', 'es': 'Diamante'},     'region': 'sinnoh', 'dex': 'original-sinnoh', 'sprites': 'dp',   'short': 'D'},
    'pearl':      {'version': 13, 'vg': 8,  'gen': 4, 'badges': 'dp', 'name': {'en': 'Pearl', 'es': 'Perla'},          'region': 'sinnoh', 'dex': 'original-sinnoh', 'sprites': 'dp',   'short': 'P'},
    'platinum':   {'version': 14, 'vg': 9,  'gen': 4, 'name': {'en': 'Platinum', 'es': 'Platino'},     'region': 'sinnoh', 'dex': 'extended-sinnoh', 'sprites': 'pt',   'short': 'Pt'},
    'heartgold':  {'version': 15, 'vg': 10, 'gen': 4, 'name': {'en': 'HeartGold', 'es': 'Oro HeartGold'}, 'region': 'johto', 'dex': 'updated-johto', 'sprites': 'hgss', 'short': 'HG'},
    'soulsilver': {'version': 16, 'vg': 10, 'gen': 4, 'name': {'en': 'SoulSilver', 'es': 'Plata SoulSilver'}, 'region': 'johto', 'dex': 'updated-johto', 'sprites': 'hgss', 'short': 'SS'},
}
DEFAULT_GAME = 'platinum'

SPRITE_SETS = {
    'dp': 'diamond-pearl',
    'pt': 'platinum',
    'hgss': 'heartgold-soulsilver',
}
SPRITE_COLS = 25
SPRITE_CELL = 80
NATIONAL_MAX = 493

# Species that come only from distributions in every Gen 4 game.
EVENT_SPECIES = {491, 492, 493}
# Places only reachable with an event ticket (Gen 3)
EVENT_LOCATIONS = {'birth-island', 'navel-rock', 'faraway-island', 'southern-island', 'hoenn-pokecenter',
                   'kanto-pokecenter', 'sinnoh-pokemart', 'johto-pokemart'}

# Expected minimum sizes; validate.py fails the build if the data drops below these.
EXPECT = {
    'ruby':       {'species_with_encounters': 120, 'areas': 95,  'regional': 202},
    'sapphire':   {'species_with_encounters': 120, 'areas': 95,  'regional': 202},
    'emerald':    {'species_with_encounters': 145, 'areas': 105, 'regional': 202},
    'firered':    {'species_with_encounters': 130, 'areas': 125, 'regional': 151},
    'leafgreen':  {'species_with_encounters': 130, 'areas': 125, 'regional': 151},
    'diamond':    {'species_with_encounters': 270, 'areas': 150, 'regional': 151},
    'pearl':      {'species_with_encounters': 270, 'areas': 150, 'regional': 151},
    'platinum':   {'species_with_encounters': 280, 'areas': 155, 'regional': 210},
    'heartgold':  {'species_with_encounters': 275, 'areas': 160, 'regional': 256},
    'soulsilver': {'species_with_encounters': 275, 'areas': 160, 'regional': 256},
}

# --------------------------------------------------------------- regions ---
# Diamond and Pearl visit the gyms in a different order from Platinum
DP_BADGES = [('Coal', 'Lignito'), ('Forest', 'Bosque'), ('Cobble', 'Adoquín'), ('Fen', 'Ciénaga'),
             ('Relic', 'Reliquia'), ('Mine', 'Mina'), ('Icicle', 'Carámbano'), ('Beacon', 'Faro')]
SINNOH_BADGES = [('Coal', 'Lignito'), ('Forest', 'Bosque'), ('Relic', 'Reliquia'), ('Cobble', 'Adoquín'),
                 ('Fen', 'Ciénaga'), ('Mine', 'Mina'), ('Icicle', 'Carámbano'), ('Beacon', 'Faro')]
HOENN_BADGES = [('Stone', 'Piedra'), ('Knuckle', 'Puño'), ('Dynamo', 'Dinamo'), ('Heat', 'Calor'),
                ('Balance', 'Equilibrio'), ('Feather', 'Pluma'), ('Mind', 'Mente'), ('Rain', 'Lluvia')]
KANTO_BADGES = [('Boulder', 'Roca'), ('Cascade', 'Cascada'), ('Thunder', 'Trueno'), ('Rainbow', 'Arcoíris'),
                ('Soul', 'Alma'), ('Marsh', 'Pantano'), ('Volcano', 'Volcán'), ('Earth', 'Tierra')]
JOHTO_BADGES = [('Zephyr', 'Céfiro'), ('Hive', 'Colmena'), ('Plain', 'Planicie'), ('Fog', 'Niebla'),
                ('Storm', 'Tormenta'), ('Mineral', 'Mineral'), ('Glacier', 'Glaciar'), ('Rising', 'Dragón')]


def _badge_stages(badges):
    out = [{'en': 'Start', 'es': 'Inicio', 'tag_en': 'From the start', 'tag_es': 'Desde el principio', 'pips': 0}]
    for i, (en, es) in enumerate(badges, 1):
        out.append({'en': f'{i} badge' + ('s' if i > 1 else ''), 'es': f'{i} medalla' + ('s' if i > 1 else ''),
                    'tag_en': f'{en} Badge', 'tag_es': f'Medalla {es}', 'pips': i})
    return out


REGIONS = {
    'sinnoh': {
        'id': 4,
        'stages': _badge_stages(SINNOH_BADGES) + [
            {'en': 'Post-game', 'es': 'Posjuego', 'tag_en': 'National Dex', 'tag_es': 'Pokédex Nacional', 'pips': 8, 'post': True}],
        # highest level of the gym leader's ace before each badge, then the League
        'level_caps': [14, 22, 26, 32, 37, 41, 44, 50, 62],
        'day_care_stage': 2,         # Solaceon Town
        'use_item_stage': 1,         # evolution stones: Underground (Explorer Kit in Eterna City)
        'held_item_stage': 4,        # Oval Stone, Razor Claw/Fang, Dusk/Dawn Stone etc.
        'beauty': True,              # Poffins exist (Milotic)
        'starter_groups': [[387, 390, 393]],
        # field moves and key items, with the stage (badge) at which you normally have them
        'gates': {'rock-smash': 1, 'cut': 2, 'surf': 5, 'strength': 6, 'rock-climb': 7, 'waterfall': 8,
                  'old-rod': 0, 'good-rod': 2, 'super-rod': 9, 'honey': 1, 'poke-radar': 9, 'national-dex': 9},
        'method_gates': {'surf': ['surf'], 'old-rod': ['old-rod'], 'good-rod': ['good-rod'], 'super-rod': ['super-rod'],
                         'honey-tree': ['honey'], 'feebas-tile-fishing': ['surf', 'old-rod']},
        'area_gates': {
            ('sinnoh-route-221', None): ['surf'], ('fuego-ironworks', None): ['surf'],
            ('lake-acuity', 'cavern'): ['surf'], ('lake-valor', 'cavern'): ['surf'],
            ('sinnoh-victory-road', None): ['surf', 'waterfall'], ('sinnoh-pokemon-league', None): ['surf', 'waterfall'],
            ('stark-mountain', 'inside'): ['strength'], ('stark-mountain', 'heatran-chamber'): ['strength'],
            ('old-chateau', None): ['cut'], ('oreburgh-gate', 'b1f'): ['rock-smash'],
            ('mt-coronet', '4f'): ['rock-climb', 'strength'], ('mt-coronet', '4f-small-room'): ['rock-climb', 'strength'],
            ('mt-coronet', '5f'): ['rock-climb', 'strength'], ('mt-coronet', '6f'): ['rock-climb', 'strength'],
            ('mt-coronet', 'exterior-snowfall'): ['rock-climb', 'strength'],
            ('mt-coronet', 'exterior-blizzard'): ['rock-climb', 'strength'],
        },
        'locations': {
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
        },
        'areas': {
            ('sinnoh-route-204', 'north-towards-floaroma-town'): 1, ('oreburgh-gate', 'b1f'): 1,
            ('mt-coronet', '1f-route-211'): 1, ('mt-coronet', 'b1f'): 5, ('mt-coronet', '1f-route-216'): 6,
            ('mt-coronet', '2f'): 6, ('mt-coronet', '3f'): 7, ('mt-coronet', '4f'): 7, ('mt-coronet', '4f-small-room'): 7,
            ('mt-coronet', '5f'): 7, ('mt-coronet', '6f'): 7, ('mt-coronet', 'exterior-snowfall'): 7,
            ('mt-coronet', 'exterior-blizzard'): 7, ('mt-coronet', '1f-from-exterior'): 7,
            ('sinnoh-route-210', 'west-towards-celestic-town'): 5, ('sinnoh-route-211', 'east-towards-celestic-town'): 5,
            ('lake-verity', 'after-galactic-intervention'): 7, ('lake-acuity', 'cavern'): 7, ('lake-valor', 'cavern'): 7,
            ('eterna-city', 'eterna-condominiums'): 1,
        },
        # Shellos / Gastrodon: places west of Mt. Coronet give the West Sea form
        'west': {'sinnoh-route-201', 'sinnoh-route-202', 'sinnoh-route-203', 'sinnoh-route-204', 'sinnoh-route-205',
                 'sinnoh-route-206', 'sinnoh-route-207', 'sinnoh-route-218', 'sinnoh-route-219', 'sinnoh-sea-route-220',
                 'sinnoh-route-221', 'valley-windworks', 'fuego-ironworks', 'canalave-city', 'twinleaf-town',
                 'oreburgh-city', 'eterna-city', 'floaroma-meadow', 'iron-island', 'lake-verity'},
        'unown': 'sinnoh',
    },
    'hoenn': {
        'id': 3,
        'stages': _badge_stages(HOENN_BADGES) + [
            {'en': 'Post-game', 'es': 'Posjuego', 'tag_en': 'After the Elite Four', 'tag_es': 'Tras el Alto Mando', 'pips': 8, 'post': True}],
        'level_caps': [15, 19, 24, 29, 31, 33, 42, 46, 58],
        'day_care_stage': 2,         # Route 117
        'use_item_stage': 3,
        'held_item_stage': 4,
        'beauty': True, 'beauty_stage': 5,   # Pokéblocks
        'clock': True,
        'forms': False,
        'starter_groups': [[252, 255, 258]],
        'gates': {'cut': 1, 'rock-smash': 3, 'strength': 4, 'surf': 5, 'dive': 7, 'waterfall': 8,
                  'mach-bike': 2, 'acro-bike': 2, 'devon-scope': 5, 'wailmer-pail': 5,
                  'old-rod': 1, 'good-rod': 3, 'super-rod': 6, 'national-dex': 9},
        'method_gates': {'surf': ['surf'], 'old-rod': ['old-rod'], 'good-rod': ['good-rod'], 'super-rod': ['super-rod'],
                         'rock-smash': ['rock-smash'], 'seaweed': ['surf', 'dive'], 'devon-scope': ['devon-scope'],
                         'wailmer-pail': ['wailmer-pail'], 'feebas-tile-fishing': ['surf', 'old-rod']},
        'area_gates': {
            ('pacifidlog-town', None): ['surf'], ('sootopolis-city', None): ['surf', 'dive'],
            ('seafloor-cavern', None): ['surf', 'dive'], ('cave-of-origin', None): ['surf', 'dive'],
            ('shoal-cave', None): ['surf'], ('abandoned-ship', None): ['surf'], ('new-mauville', None): ['surf'],
            ('sky-pillar', None): ['surf'], ('mirage-island', None): ['surf'], ('island-cave', None): ['surf'],
            ('hoenn-victory-road', None): ['surf', 'waterfall'], ('meteor-falls', 'back'): ['surf', 'waterfall'],
            ('meteor-falls', 'backsmall-room'): ['surf', 'waterfall'], ('granite-cave', 'b1f'): ['mach-bike'],
            ('hoenn-safari-zone', 'nwmach-bike-area'): ['mach-bike'], ('hoenn-safari-zone', 'neacro-bike-area'): ['acro-bike'],
        },
        'locations': {
            'littleroot-town': 0, 'hoenn-route-101': 0, 'hoenn-route-103': 0, 'hoenn-route-102': 0, 'petalburg-city': 0,
            'hoenn-route-104': 0, 'petalburg-woods': 0, 'rustboro-city': 0,
            'hoenn-route-116': 1, 'rusturf-tunnel': 1, 'dewford-town': 1, 'granite-cave': 1, 'hoenn-route-106': 1,
            'hoenn-route-107': 1, 'hoenn-route-109': 1, 'slateport-city': 1,
            'hoenn-route-110': 2, 'mauville-city': 2, 'hoenn-route-117': 2, 'verdanturf-town': 2, 'hoenn-route-111': 2,
            'hoenn-route-112': 2, 'fiery-path': 2, 'hoenn-route-113': 2, 'fallarbor-town': 2, 'hoenn-route-114': 2,
            'meteor-falls': 2, 'hoenn-route-115': 2, 'jagged-pass': 2, 'lavaridge-town': 2,
            'hoenn-route-118': 3,
            'mirage-tower': 4,
            'hoenn-route-105': 5, 'hoenn-route-108': 5, 'abandoned-ship': 5, 'hoenn-route-119': 5, 'fortree-city': 5,
            'hoenn-route-120': 5, 'hoenn-route-121': 5, 'hoenn-safari-zone': 5, 'lilycove-city': 5, 'mt-pyre': 5,
            'hoenn-route-122': 5, 'hoenn-route-123': 5, 'new-mauville': 5,
            'magma-hideout': 6, 'team-aqua-hideout': 6, 'team-magma-hideout': 6,
            'hoenn-route-124': 6, 'hoenn-route-125': 6, 'hoenn-route-126': 6, 'hoenn-route-127': 6, 'hoenn-route-128': 6,
            'mossdeep-city': 6, 'shoal-cave': 6,
            'seafloor-cavern': 7, 'sootopolis-city': 7, 'cave-of-origin': 7, 'hoenn-route-129': 7, 'hoenn-route-130': 7,
            'hoenn-route-131': 7, 'pacifidlog-town': 7, 'hoenn-route-132': 7, 'hoenn-route-133': 7, 'hoenn-route-134': 7,
            'sky-pillar': 7,
            'ever-grande-city': 8, 'hoenn-victory-road': 8,
            'artisan-cave': 9, 'desert-underpass': 9, 'hoenn-altering-cave': 9, 'island-cave': 9, 'desert-ruins': 9,
            'ancient-tomb': 9, 'terra-cave': 9, 'marine-cave': 9, 'hoenn-battle-frontier': 9, 'southern-island': 9,
            'birth-island': 9, 'navel-rock': 9, 'faraway-island': 9, 'hoenn-pokecenter': 9, 'mirage-island': 9,
            'roaming-hoenn': 9,
        },
        'areas': {},
        'west': set(),
        'unown': None,
    },
    'kanto3': {
        'id': 1,
        'stages': _badge_stages(KANTO_BADGES) + [
            {'en': 'Post-game', 'es': 'Posjuego', 'tag_en': 'National Dex and Sevii Islands 4–7', 'tag_es': 'Pokédex Nacional e Islas Sete 4–7', 'pips': 8, 'post': True}],
        'level_caps': [14, 21, 24, 29, 43, 43, 47, 50, 63],
        'day_care_stage': 9,         # the Route 5 Day-Care doesn't breed; Four Island's does
        'use_item_stage': 3,
        'held_item_stage': 5,
        'beauty': False,
        'clock': False,              # no clock: Espeon and Umbreon can't evolve
        'forms': False,
        'starter_groups': [[1, 4, 7]],
        'gates': {'cut': 2, 'strength': 4, 'surf': 5, 'rock-smash': 7, 'waterfall': 9, 'poke-flute': 4,
                  'silph-scope': 4, 'old-rod': 2, 'good-rod': 5, 'super-rod': 5, 'national-dex': 9},
        'method_gates': {'surf': ['surf'], 'old-rod': ['old-rod'], 'good-rod': ['good-rod'], 'super-rod': ['super-rod'],
                         'rock-smash': ['rock-smash'], 'pokeflute': ['poke-flute']},
        'area_gates': {
            ('kanto-route-9', None): ['cut'], ('kanto-route-10', None): ['cut'], ('rock-tunnel', None): ['cut'],
            ('pokemon-tower', None): ['silph-scope'], ('seafoam-islands', None): ['surf', 'strength'],
            ('cinnabar-island', None): ['surf'], ('kanto-power-plant', None): ['surf'], ('cerulean-cave', None): ['surf'],
            ('kanto-victory-road-2', None): ['strength'], ('mt-ember', 'summit'): ['strength', 'rock-smash'],
        },
        'locations': {
            'pallet-town': 0, 'kanto-route-1': 0, 'viridian-city': 0, 'kanto-route-22': 0, 'kanto-route-2': 0,
            'viridian-forest': 0, 'pewter-city': 0,
            'kanto-route-3': 1, 'mt-moon': 1, 'kanto-route-4': 1, 'cerulean-city': 1,
            'kanto-route-24': 2, 'kanto-route-25': 2, 'kanto-route-5': 2, 'kanto-route-6': 2, 'vermilion-city': 2,
            'ss-anne': 2, 'digletts-cave': 2, 'kanto-route-11': 2, 'kanto-route-9': 2, 'kanto-route-10': 2,
            'rock-tunnel': 2, 'kanto-underground-path': 2,
            'kanto-route-8': 3, 'kanto-route-7': 3, 'celadon-city': 3, 'lavender-town': 3,
            'pokemon-tower': 4, 'kanto-route-12': 4, 'kanto-route-13': 4, 'kanto-route-14': 4, 'kanto-route-15': 4,
            'kanto-route-16': 4, 'kanto-route-17': 4, 'kanto-route-18': 4,
            'fuchsia-city': 5, 'kanto-safari-zone': 5, 'saffron-city': 5, 'kanto-sea-route-19': 5,
            'kanto-sea-route-20': 5, 'kanto-sea-route-21': 5, 'seafoam-islands': 5, 'cinnabar-island': 5,
            'pokemon-mansion': 5, 'kanto-power-plant': 5,
            'one-island': 7, 'kindle-road': 7, 'treasure-beach': 7, 'mt-ember': 7, 'cape-brink': 7, 'bond-bridge': 7,
            'three-isle-port': 7, 'berry-forest': 7,
            'kanto-route-23': 8, 'kanto-victory-road-2': 8,
            'four-island': 9, 'icefall-cave': 9, 'five-island': 9, 'resort-gorgeous': 9, 'water-labyrinth': 9,
            'five-isle-meadow': 9, 'memorial-pillar': 9, 'outcast-island': 9, 'green-path': 9, 'water-path': 9,
            'ruin-valley': 9, 'trainer-tower': 9, 'canyon-entrance': 9, 'sevault-canyon': 9, 'tanoby-ruins': 9,
            'pattern-bush': 9, 'lost-cave': 9, 'kanto-altering-cave': 9, 'cerulean-cave': 9, 'roaming-kanto': 9,
            'birth-island': 9, 'navel-rock': 9, 'kanto-pokecenter': 9,
        },
        'location_default': ('monean-chamber', 'liptoo-chamber', 'weepth-chamber', 'dilford-chamber', 'scufib-chamber',
                             'rixy-chamber', 'viapos-chamber'),
        'location_default_stage': 9,
        'areas': {},
        'west': set(),
        'unown': None,
    },
    'johto': {
        'id': 2,
        'stages': _badge_stages(JOHTO_BADGES) + [
            {'en': 'Kanto', 'es': 'Kanto', 'tag_en': 'After the Elite Four', 'tag_es': 'Tras el Alto Mando', 'pips': 8, 'post': True},
            {'en': '16 badges', 'es': '16 medallas', 'tag_en': 'After all 16 badges and Red', 'tag_es': 'Tras 16 medallas y Rojo', 'pips': 8, 'post': True}],
        'level_caps': [13, 17, 19, 25, 31, 35, 35, 41, 50, 65],
        'day_care_stage': 2,         # Route 34
        'use_item_stage': 3,         # stones: Bug-Catching Contest, Pokéathlon Dome, Ruins of Alph
        'held_item_stage': 6,
        'beauty': False,             # no Poffins or contests: Milotic needs Diamond, Pearl or Platinum
        'starter_groups': [[152, 155, 158], [1, 4, 7], [252, 255, 258]],
        'gates': {'cut': 2, 'headbutt': 2, 'strength': 3, 'rock-smash': 3, 'squirt-bottle': 3, 'surf': 4,
                  'whirlpool': 7, 'waterfall': 8, 'old-rod': 1, 'good-rod': 3, 'super-rod': 9, 'poke-flute': 9,
                  'national-dex': 9},
        'method_gates': {'surf': ['surf'], 'old-rod': ['old-rod'], 'good-rod': ['good-rod'], 'super-rod': ['super-rod'],
                         'headbutt': ['headbutt'], 'rock-smash': ['rock-smash'], 'pokeflute': ['poke-flute'],
                         'squirt-bottle': ['squirt-bottle']},
        'area_gates': {
            ('cianwood-city', None): ['surf'], ('whirl-islands', None): ['surf', 'whirlpool'],
            ('dragons-den', None): ['surf', 'whirlpool'], ('tohjo-falls', None): ['surf', 'waterfall'],
            ('johto-route-27', None): ['surf'], ('kanto-route-27', None): ['surf'], ('kanto-route-26', None): ['surf'],
            ('seafoam-islands', None): ['surf', 'strength'], ('cinnabar-island', None): ['surf'],
            ('cerulean-cave', None): ['surf'], ('johto-route-47', None): ['surf'], ('johto-route-48', None): ['surf'],
            ('johto-safari-zone', None): ['surf'], ('safari-zone-gate', None): ['surf'],
            ('kanto-victory-road-1', None): ['surf', 'waterfall'],
        },
        'locations': {
            'new-bark-town': 0, 'johto-route-29': 0, 'cherrygrove-city': 0, 'johto-route-30': 0, 'johto-route-31': 0,
            'violet-city': 0, 'sprout-tower': 0, 'dark-cave': 0, 'johto-route-46': 0,
            'johto-route-32': 1, 'ruins-of-alph': 1, 'union-cave': 1, 'johto-route-33': 1, 'azalea-town': 1, 'slowpoke-well': 1,
            'ilex-forest': 2, 'johto-route-34': 2, 'goldenrod-city': 2, 'johto-route-35': 2, 'national-park': 2, 'johto-route-36': 2,
            'johto-route-37': 3, 'ecruteak-city': 3, 'burned-tower': 3, 'johto-route-38': 3, 'johto-route-39': 3, 'olivine-city': 3,
            'johto-route-42': 3, 'mt-mortar': 3, 'johto-route-43': 3, 'lake-of-rage': 3,
            'johto-sea-route-40': 4, 'johto-sea-route-41': 4, 'cianwood-city': 4, 'johto-route-27': 4,
            'johto-route-47': 5, 'johto-route-48': 5, 'johto-safari-zone': 5, 'safari-zone-gate': 5,
            'team-rocket-hq': 6,
            'johto-route-44': 7, 'ice-path': 7, 'blackthorn-city': 7, 'johto-route-45': 7, 'whirl-islands': 7, 'bell-tower': 7,
            'roaming-johto': 3,
            'dragons-den': 8, 'tohjo-falls': 8, 'kanto-route-26': 8, 'kanto-route-27': 4, 'kanto-victory-road-1': 8,
            'mt-silver': 10, 'kanto-route-28': 10, 'cerulean-cave': 10, 'embedded-tower': 10, 'sinjoh-ruins': 10,
            'johto-pokemart': 9,
        },
        # every other Kanto location
        'location_default': ('kanto-', 'pallet-town', 'viridian-', 'pewter-city', 'cerulean-city', 'vermilion-city',
                             'lavender-town', 'celadon-city', 'fuchsia-city', 'saffron-city', 'cinnabar-island',
                             'digletts-cave', 'mt-moon', 'rock-tunnel', 'seafoam-islands'),
        'location_default_stage': 9,
        'areas': {
            ('dark-cave', 'blackthorn-city-entrance'): 7, ('union-cave', 'b2f'): 4, ('mt-mortar', 'b1f'): 4,
            ('whirl-islands', 'b3f'): 8, ('bell-tower', 'roof'): 8, ('slowpoke-well', 'b2f'): 3,
        },
        'west': set(),
        'unown': 'johto',
    },
}

# ------------------------------------------------------------ conditions ---
# Every encounter condition value the games use must be handled here or validate.py fails.
# kind -> (stage per region, external requirement)
COND_DEFAULT_IDS = {'story-progress-before-national-dex', 'great-marsh-daily-slot-none', 'backlot-not-mentioned',
                    'johto-safari-blocks-inactive', 'bug-catching-contest-no'}

STORY_STAGE = {
    'beat-elite-four-round-two': 9,
    # Sinnoh
    'defeat-jupiter': 2, 'defeat-mars': 1, 'beat-galactic-coronet': 7, 'beat-team-galactic-iron-island': 5,
    'cure-eldritch-nightmares': 9, 'oak-eterna-city': 9, 'hall-of-fame': 9, 'national-dex': 9,
    # Johto
    'zephyr-badge': 1, 'awakened-beasts': 3, 'beat-red': 10, 'receive-tm-from-claire': 8,
    'returned-machine-part': 9, 'vermilion-copycat': 9,
}
OTHER_STAGE = {
    'talked-to-32-people-underground': (2, None),
    'regirock-regice-registeel-in-party': (9, 'other'),
    'giratina-not-caught-in-distortion-world': (9, None),
    'talk-to-cynthias-grandmother': (9, None),
    'correct-password': (1, None),
    'event-arceus-in-party': (10, 'event'),
    'received-kanto-starter': (10, None),
    'snorlax-11-beat-league': (9, None),
    'first-party-pokemon-high-friendship': (0, None),
}
ITEM_STAGE = {'odd-keystone': 2, 'adamant-orb': 9, 'lustrous-orb': 9}
FOSSIL_STAGE = {'sinnoh': 1, 'johto': 9, 'hoenn': 4, 'kanto3': 5}


def parse_condition(ident, region):
    """Map a PokéAPI encounter condition value to (cond, stage, ext). Returns None for defaults/time."""
    if ident in COND_DEFAULT_IDS or ident.startswith('time-'):
        return None
    if ident == 'swarm-yes':
        return {'k': 'swarm'}, 9, None
    if ident == 'radar-on':
        return {'k': 'radar'}, 9, None
    if ident.startswith('slot2-'):
        return {'k': 'slot2', 'v': ident[6:]}, 9, 'gba'
    if ident.startswith('radio-'):
        return {'k': 'radio', 'v': ident[6:]}, 9, None
    if ident == 'story-progress-national-dex':
        return {'k': 'natdex'}, 9, None
    if ident.startswith('story-progress-'):
        key = ident[len('story-progress-'):]
        if key not in STORY_STAGE:
            raise KeyError(ident)
        return {'k': 'story', 'v': key}, STORY_STAGE[key], None
    if ident.startswith('other-'):
        key = ident[6:]
        if key not in OTHER_STAGE:
            raise KeyError(ident)
        st, ext = OTHER_STAGE[key]
        return {'k': 'other', 'v': key}, st, ext
    if ident.startswith('weekday-'):
        return {'k': 'weekday', 'v': ident[8:]}, 0, None
    if ident.startswith('honey-tree-group-'):
        return {'k': 'honey', 'v': ident[-1]}, 1, None
    if ident.startswith('great-marsh-daily-slot-'):
        return {'k': 'marsh'}, 4, None
    if ident == 'backlot-mentioned':
        return {'k': 'backlot'}, 9, None
    if ident == 'bug-catching-contest-yes':
        return {'k': 'contest'}, 2, None
    if ident.startswith('coins-'):
        return {'k': 'coins', 'n': int(ident[6:])}, 2, None
    if ident.startswith('headbutt-tree-'):
        return {'k': 'headbutt', 'v': ident[len('headbutt-tree-'):]}, 2, None
    if ident.startswith('johto-safari-blocks-'):
        kind, _, n = ident[len('johto-safari-blocks-'):].partition('-min-')
        return {'k': 'safari', 'v': kind, 'n': int(n)}, 5, None
    if ident == 'first-party-pokemon-high-friendship':
        return {'k': 'other', 'v': ident}, 0, None
    if ident.startswith('tv-option-'):
        return {'k': 'tv', 'v': ident[len('tv-option-'):]}, 9, None
    if ident.startswith('starter-'):
        return {'k': 'starter-was', 'v': ident[8:]}, 0, None
    if ident.startswith('trade-'):
        return {'k': 'give', 'v': ident[6:]}, 0, None
    if ident.startswith('item-'):
        key = ident[5:]
        if key.endswith('fossil') or key == 'old-amber':
            return {'k': 'fossil', 'v': key}, FOSSIL_STAGE[region], None
        if key not in ITEM_STAGE:
            raise KeyError(ident)
        return {'k': 'item', 'v': key}, ITEM_STAGE[key], None
    raise KeyError(ident)


# Conditions that are really "have this item or unlock": they lock by gate instead of by story stage
COND_GATE = {'radar': 'poke-radar', 'natdex': 'national-dex', 'swarm': 'national-dex', 'slot2': 'national-dex',
             'radio': 'national-dex', 'backlot': 'national-dex', 'honey': 'honey'}

# Weekday rules PokéAPI is missing for some games: (game, species, location) -> weekday
EXTRA_WEEKDAY = {('platinum', 425, 'valley-windworks'): 'friday'}

# ----------------------------------------------------------------- forms ---
# Forms that exist only in battle are skipped automatically (is_battle_only in PokéAPI).
SKIP_FORMS = {'arceus-unknown', 'castform', 'cherrim-overcast'}
# Forms that revert when deposited in the PC in Gen 4, so they can't be part of a living dex box.
NOT_BOXABLE = {'shaymin-sky'}
