"""Per-game and per-region settings.

"Stage" is the planner's measure of story progress: 0 is the start of the game and each step is
roughly one gym badge. PokéAPI has no story order, so every stage below is a hand-written estimate.
Adjust them here; the validate step fails the build if an area has no stage.
"""

# ---------------------------------------------------------------- games ---
# Every game can be the main game (where the living dex lives). 'home' is Pokémon HOME: no encounters of
# its own, everything comes from the other games through the transfer chain.
GAMES = {
    'red':        {'version': 1,  'vg': 1,  'gen': 1, 'name': {'en': 'Red', 'es': 'Rojo'},               'region': 'kanto1', 'dex': 'kanto', 'sprites': 'rb', 'short': 'R'},
    'blue':       {'version': 2,  'vg': 1,  'gen': 1, 'name': {'en': 'Blue', 'es': 'Azul'},              'region': 'kanto1', 'dex': 'kanto', 'sprites': 'rb', 'short': 'B'},
    'yellow':     {'version': 3,  'vg': 2,  'gen': 1, 'name': {'en': 'Yellow', 'es': 'Amarillo'},        'region': 'kanto1', 'dex': 'kanto', 'sprites': 'y',  'short': 'Y', 'starters': []},
    'gold':       {'version': 4,  'vg': 3,  'gen': 2, 'name': {'en': 'Gold', 'es': 'Oro'},               'region': 'johto2', 'dex': 'original-johto', 'sprites': 'gs', 'short': 'G'},
    'silver':     {'version': 5,  'vg': 3,  'gen': 2, 'name': {'en': 'Silver', 'es': 'Plata'},           'region': 'johto2', 'dex': 'original-johto', 'sprites': 'gs', 'short': 'S'},
    'crystal':    {'version': 6,  'vg': 4,  'gen': 2, 'name': {'en': 'Crystal', 'es': 'Cristal'},        'region': 'johto2', 'dex': 'original-johto', 'sprites': 'c',  'short': 'C'},
    'ruby':       {'version': 7,  'vg': 5,  'gen': 3, 'name': {'en': 'Ruby', 'es': 'Rubí'},             'region': 'hoenn',  'dex': 'hoenn', 'sprites': 'rs', 'short': 'R'},
    'sapphire':   {'version': 8,  'vg': 5,  'gen': 3, 'name': {'en': 'Sapphire', 'es': 'Zafiro'},       'region': 'hoenn',  'dex': 'hoenn', 'sprites': 'rs', 'short': 'S'},
    'emerald':    {'version': 9,  'vg': 6,  'gen': 3, 'name': {'en': 'Emerald', 'es': 'Esmeralda'},    'region': 'hoenn',  'dex': 'hoenn', 'sprites': 'e',  'short': 'E'},
    'firered':    {'version': 10, 'vg': 7,  'gen': 3, 'name': {'en': 'FireRed', 'es': 'Rojo Fuego'},   'region': 'kanto3', 'dex': 'kanto', 'sprites': 'frlg', 'short': 'FR'},
    'leafgreen':  {'version': 11, 'vg': 7,  'gen': 3, 'name': {'en': 'LeafGreen', 'es': 'Verde Hoja'}, 'region': 'kanto3', 'dex': 'kanto', 'sprites': 'frlg', 'short': 'LG'},
    'diamond':    {'version': 12, 'vg': 8,  'gen': 4, 'badges': 'dp', 'name': {'en': 'Diamond', 'es': 'Diamante'},     'region': 'sinnoh', 'dex': 'original-sinnoh', 'sprites': 'dp',   'short': 'D'},
    'pearl':      {'version': 13, 'vg': 8,  'gen': 4, 'badges': 'dp', 'name': {'en': 'Pearl', 'es': 'Perla'},          'region': 'sinnoh', 'dex': 'original-sinnoh', 'sprites': 'dp',   'short': 'P'},
    'platinum':   {'version': 14, 'vg': 9,  'gen': 4, 'name': {'en': 'Platinum', 'es': 'Platino'},     'region': 'sinnoh', 'dex': 'extended-sinnoh', 'sprites': 'pt',   'short': 'Pt'},
    'heartgold':  {'version': 15, 'vg': 10, 'gen': 4, 'name': {'en': 'HeartGold', 'es': 'Oro HeartGold'}, 'region': 'johto', 'dex': 'updated-johto', 'sprites': 'hgss', 'short': 'HG'},
    'soulsilver': {'version': 16, 'vg': 10, 'gen': 4, 'name': {'en': 'SoulSilver', 'es': 'Plata SoulSilver'}, 'region': 'johto', 'dex': 'updated-johto', 'sprites': 'hgss', 'short': 'SS'},
    'black':      {'version': 17, 'vg': 11, 'gen': 5, 'name': {'en': 'Black', 'es': 'Negro'},          'region': 'unova',  'dex': 'original-unova', 'sprites': 'bw', 'short': 'B'},
    'white':      {'version': 18, 'vg': 11, 'gen': 5, 'name': {'en': 'White', 'es': 'Blanco'},         'region': 'unova',  'dex': 'original-unova', 'sprites': 'bw', 'short': 'W'},
    'black2':     {'version': 21, 'vg': 14, 'gen': 5, 'name': {'en': 'Black 2', 'es': 'Negro 2'},      'region': 'unova2', 'dex': 'updated-unova',  'sprites': 'bw', 'short': 'B2'},
    'white2':     {'version': 22, 'vg': 14, 'gen': 5, 'name': {'en': 'White 2', 'es': 'Blanco 2'},     'region': 'unova2', 'dex': 'updated-unova',  'sprites': 'bw', 'short': 'W2'},
    'home':       {'version': None, 'vg': 14, 'gen': 9, 'home': True, 'name': {'en': 'Pokémon HOME', 'es': 'Pokémon HOME'}, 'region': 'home', 'dex': None, 'sprites': 'home', 'short': 'HOME'},
}
DEFAULT_GAME = 'platinum'

# highest National Dex number per generation; HOME holds every species
NAT_MAX = {1: 151, 2: 251, 3: 386, 4: 493, 5: 649, 9: 1025}
NATIONAL_MAX = 1025

# Sprite sets: folder under sprites/pokemon/versions/ (or sprites/pokemon/) and how many species they cover.
SPRITE_SETS = {
    'rb':   ('generation-i/red-blue/transparent', 151),
    'y':    ('generation-i/yellow/transparent', 151),
    'gs':   ('generation-ii/gold/transparent', 251),
    'c':    ('generation-ii/crystal/transparent', 251),
    'rs':   ('generation-iii/ruby-sapphire', 386),
    'e':    ('generation-iii/emerald', 386),
    'frlg': ('generation-iii/firered-leafgreen', 386),
    'dp':   ('generation-iv/diamond-pearl', 493),
    'pt':   ('generation-iv/platinum', 493),
    'hgss': ('generation-iv/heartgold-soulsilver', 493),
    'bw':   ('generation-v/black-white', 649),
    'home': ('generation-v/black-white', 1025),
}
SPRITE_COLS = 25

# PC boxes per generation: (slots per box, columns, number of boxes)
BOXES = {1: (20, 5, 12), 2: (20, 5, 14), 3: (30, 6, 14), 4: (30, 6, 18), 5: (30, 6, 24), 9: (30, 6, 200)}

# In-game clock: Gen 2 and Gen 4 have morning/day/night, Gen 5 has seasons, Gen 1 and Gen 3 have neither for encounters.
CLOCKS = {
    1: None,
    2: {'kind': 'tod', 'hours': [4, 10, 18]},
    3: None,
    4: {'kind': 'tod', 'hours': [4, 10, 20]},
    5: {'kind': 'season'},
    9: None,
}

# Species that come only from distributions in every Gen 4 game.
EVENT_SPECIES = {491, 492, 493}
# Places only reachable with an event ticket
EVENT_LOCATIONS = {'birth-island', 'navel-rock', 'faraway-island', 'southern-island', 'hoenn-pokecenter',
                   'kanto-pokecenter', 'sinnoh-pokemart', 'johto-pokemart', 'liberty-garden'}

# Expected minimum sizes; validate.py fails the build if the data drops below these.
EXPECT = {
    'red':        {'species_with_encounters': 100, 'areas': 60,  'regional': 151},
    'blue':       {'species_with_encounters': 100, 'areas': 60,  'regional': 151},
    'yellow':     {'species_with_encounters': 100, 'areas': 60,  'regional': 151},
    'gold':       {'species_with_encounters': 140, 'areas': 110, 'regional': 251},
    'silver':     {'species_with_encounters': 140, 'areas': 110, 'regional': 251},
    'crystal':    {'species_with_encounters': 160, 'areas': 110, 'regional': 251},
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
    'black':      {'species_with_encounters': 230, 'areas': 70,  'regional': 156},
    'white':      {'species_with_encounters': 230, 'areas': 70,  'regional': 156},
    'black2':     {'species_with_encounters': 285, 'areas': 110, 'regional': 301},
    'white2':     {'species_with_encounters': 285, 'areas': 110, 'regional': 301},
    'home':       {'species_with_encounters': 0,   'areas': 0,   'regional': 0},
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
        'unown': 'tanoby',
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

BW_BADGES = [('Trio', 'Trío'), ('Basic', 'Base'), ('Insect', 'Élitro'), ('Bolt', 'Voltio'), ('Quake', 'Temblor'),
             ('Jet', 'Jet'), ('Freeze', 'Candelizo'), ('Legend', 'Leyenda')]
B2W2_BADGES = [('Basic', 'Base'), ('Toxic', 'Ponzoña'), ('Insect', 'Élitro'), ('Bolt', 'Voltio'), ('Quake', 'Temblor'),
               ('Jet', 'Jet'), ('Legend', 'Leyenda'), ('Wave', 'Ola')]
POST_LEAGUE = {'en': 'Post-game', 'es': 'Posjuego', 'tag_en': 'After the Elite Four', 'tag_es': 'Tras el Alto Mando', 'pips': 8, 'post': True}

# Red, Blue and Yellow
REGIONS['kanto1'] = {
    'id': 1,
    'stages': _badge_stages(KANTO_BADGES) + [POST_LEAGUE],
    'level_caps': [14, 21, 24, 29, 43, 43, 47, 50, 65],
    'day_care_stage': None,      # the Route 5 Day Care raises Pokémon but there are no eggs in Gen 1
    'use_item_stage': 3,         # Celadon Department Store
    'held_item_stage': 9,
    'beauty': False,
    'clock': False,
    'forms': False,
    'starter_groups': [[1, 4, 7]],
    'gates': {'cut': 2, 'strength': 5, 'surf': 5, 'old-rod': 2, 'good-rod': 4, 'super-rod': 4,
              'poke-flute': 4, 'silph-scope': 4},
    'method_gates': {'surf': ['surf'], 'old-rod': ['old-rod'], 'good-rod': ['good-rod'], 'super-rod': ['super-rod'],
                     'pokeflute': ['poke-flute']},
    'area_gates': {
        ('kanto-route-9', None): ['cut'], ('kanto-route-10', None): ['cut'], ('rock-tunnel', None): ['cut'],
        ('pokemon-tower', None): ['silph-scope'], ('seafoam-islands', None): ['surf', 'strength'],
        ('cinnabar-island', None): ['surf'], ('pokemon-mansion', None): ['surf'], ('kanto-power-plant', None): ['surf'],
        ('cerulean-cave', None): ['surf'], ('kanto-victory-road-2', None): ['strength'],
        ('kanto-sea-route-19', None): ['surf'], ('kanto-sea-route-20', None): ['surf'],
    },
    'locations': {
        'pallet-town': 0, 'kanto-route-1': 0, 'viridian-city': 0, 'kanto-route-22': 0, 'kanto-route-2': 0,
        'viridian-forest': 0, 'pewter-city': 0,
        'kanto-route-3': 1, 'mt-moon': 1, 'kanto-route-4': 1, 'cerulean-city': 1,
        'kanto-route-24': 2, 'kanto-route-25': 2, 'kanto-route-5': 2, 'kanto-route-6': 2, 'vermilion-city': 2,
        'digletts-cave': 2, 'kanto-route-11': 2, 'kanto-route-9': 2, 'kanto-route-10': 2, 'rock-tunnel': 2,
        'kanto-underground-path': 2,
        'kanto-route-8': 3, 'kanto-route-7': 3, 'celadon-city': 3, 'lavender-town': 3,
        'pokemon-tower': 4, 'kanto-route-12': 4, 'kanto-route-13': 4, 'kanto-route-14': 4, 'kanto-route-15': 4,
        'kanto-route-16': 4, 'kanto-route-17': 4, 'kanto-route-18': 4, 'fuchsia-city': 4, 'kanto-safari-zone': 4,
        'saffron-city': 5, 'kanto-sea-route-19': 5, 'kanto-sea-route-20': 5, 'kanto-sea-route-21': 5,
        'seafoam-islands': 5, 'cinnabar-island': 5, 'pokemon-mansion': 5, 'kanto-power-plant': 5,
        'kanto-route-23': 8, 'kanto-victory-road-2': 8,
        'cerulean-cave': 9,
    },
    'areas': {('kanto-route-4', 'pokemon-center'): 1},
    'west': set(),
    'unown': None,
}

# Gold, Silver and Crystal: Johto as in HeartGold/SoulSilver, without the HGSS-only places and items
REGIONS['johto2'] = dict(REGIONS['johto'],
    level_caps=[9, 16, 20, 25, 30, 35, 35, 40, 50, 81],
    starter_groups=[[152, 155, 158]],
    gates={'cut': 2, 'headbutt': 2, 'strength': 3, 'rock-smash': 3, 'squirt-bottle': 3, 'surf': 4,
           'whirlpool': 7, 'waterfall': 8, 'old-rod': 1, 'good-rod': 3, 'super-rod': 9, 'poke-flute': 9,
           'time-capsule': 3},
    method_gates={'surf': ['surf'], 'old-rod': ['old-rod'], 'good-rod': ['good-rod'], 'super-rod': ['super-rod'],
                  'headbutt-low': ['headbutt'], 'headbutt-normal': ['headbutt'], 'headbutt-high': ['headbutt'],
                  'rock-smash': ['rock-smash'], 'pokeflute': ['poke-flute'], 'squirt-bottle': ['squirt-bottle']},
    cond_stage={'swarm': 0},     # Gen 2 swarms come from phone calls during the story
    unown='gsc',
)

UNOVA_GATES_METHODS = {'surf': ['surf'], 'surf-spots': ['surf'], 'super-rod': ['super-rod'],
                       'super-rod-spots': ['super-rod']}

# Black and White
REGIONS['unova'] = {
    'id': 5,
    'stages': _badge_stages(BW_BADGES) + [
        {'en': 'Post-game', 'es': 'Posjuego', 'tag_en': 'After the Hall of Fame', 'tag_es': 'Tras el Salón de la Fama', 'pips': 8, 'post': True}],
    'level_caps': [14, 20, 23, 27, 31, 35, 39, 43, 54],
    'day_care_stage': 1,         # Route 3
    'use_item_stage': 3,
    'held_item_stage': 5,
    'beauty': False,             # no contests: Milotic needs a Prism Scale trade
    'clock': True,
    'starter_groups': [[495, 498, 501]],
    # Gen 5 needs no badges for field moves: these are the points where you get each HM or item
    'gates': {'cut': 1, 'strength': 4, 'surf': 6, 'waterfall': 6, 'dive': 9, 'super-rod': 9, 'poke-transfer': 9},
    'method_gates': UNOVA_GATES_METHODS,
    'area_gates': {
        ('unova-route-17', None): ['surf'], ('unova-route-18', None): ['surf'], ('p2-laboratory', None): ['surf'],
        ('undella-bay', None): ['surf'],
    },
    'locations': {
        'nuvema-town': 0, 'unova-route-1': 0, 'accumula-town': 0, 'unova-route-2': 0, 'striaton-city': 0, 'dreamyard': 0,
        'unova-route-3': 1, 'wellspring-cave': 1, 'nacrene-city': 1,
        'pinwheel-forest': 2, 'skyarrow-bridge': 2, 'castelia-city': 2,
        'unova-route-4': 3, 'desert-resort': 3, 'relic-castle': 3, 'nimbasa-city': 3, 'anville-town': 3,
        'unova-route-5': 4, 'driftveil-drawbridge': 4, 'driftveil-city': 4, 'cold-storage': 4, 'unova-route-16': 4,
        'lostlorn-forest': 4,
        'unova-route-6': 5, 'chargestone-cave': 5, 'mistralton-city': 5, 'unova-route-7': 5, 'celestial-tower': 5,
        'unova-route-17': 6, 'unova-route-18': 6, 'p2-laboratory': 6, 'mistralton-cave': 6, 'guidance-chamber': 6,
        'twist-mountain': 6, 'icirrus-city': 6,
        'dragonspiral-tower': 7, 'unova-route-8': 7, 'moor-of-icirrus': 7, 'tubeline-bridge': 7, 'unova-route-9': 7,
        'opelucid-city': 7,
        'unova-route-10': 8, 'unova-victory-road': 8, 'ns-castle': 8, 'trial-chamber': 8,
        'unova-route-11': 9, 'village-bridge': 9, 'unova-route-12': 9, 'lacunosa-town': 9, 'unova-route-13': 9,
        'giant-chasm': 9, 'undella-town': 9, 'undella-bay': 9, 'unova-route-14': 9, 'abundant-shrine': 9,
        'unova-route-15': 9, 'marvelous-bridge': 9, 'challengers-cave': 9, 'liberty-garden': 9,
    },
    'areas': {('pinwheel-forest', 'rumination-field'): 6},
    'west': set(),
    'unown': None,
    # Black and White reopen early places in the post-game with much stronger Pokémon (dark grass, rippling water):
    # wild encounters far above the gym levels count as later in the story
    'level_hints': True,
}

# Black 2 and White 2: the old Unova areas open after the Hall of Fame (Skyarrow Bridge is closed until then)
REGIONS['unova2'] = dict(REGIONS['unova'],
    stages=_badge_stages(B2W2_BADGES) + [REGIONS['unova']['stages'][-1]],
    level_caps=[13, 18, 24, 30, 33, 39, 48, 51, 59],
    day_care_stage=9,            # Route 3, past Skyarrow Bridge
    gates={'cut': 1, 'strength': 2, 'surf': 5, 'dive': 6, 'waterfall': 8, 'super-rod': 9, 'poke-transfer': 9},
    area_gates={('unova-route-17', None): ['surf'], ('unova-route-18', None): ['surf'], ('p2-laboratory', None): ['surf'],
                ('undella-bay', None): ['surf'], ('underground-ruins', None): ['surf']},
    locations={
        'aspertia-city': 0, 'unova-route-19': 0, 'floccesy-town': 0, 'unova-route-20': 0, 'floccesy-ranch': 0,
        'virbank-city': 1, 'virbank-complex': 1,
        'castelia-city': 2, 'castelia-sewers': 2,
        'unova-route-4': 3, 'desert-resort': 3, 'relic-castle': 3, 'nimbasa-city': 3, 'anville-town': 3,
        'unova-route-16': 3, 'lostlorn-forest': 3,
        'unova-route-5': 4, 'driftveil-drawbridge': 4, 'driftveil-city': 4,
        'relic-passage': 5, 'unova-route-6': 5, 'mistralton-cave': 5, 'chargestone-cave': 5, 'mistralton-city': 5,
        'unova-route-7': 5, 'celestial-tower': 5,
        'lentimas-town': 6, 'strange-house': 6, 'reversal-mountain': 6, 'undella-town': 6, 'undella-bay': 6,
        'unova-route-13': 6, 'lacunosa-town': 6, 'unova-route-12': 6, 'village-bridge': 6, 'unova-route-11': 6,
        'opelucid-city': 6, 'unova-route-9': 6,
        'humilau-city': 7, 'unova-route-22': 7,
        'unova-route-21': 8, 'seaside-cave': 8, 'giant-chasm': 8, 'unova-route-23': 8, 'unova-victory-road-2': 8,
        'unova-victory-road': 8,
        'clay-tunnel': 9, 'underground-ruins': 9, 'rocky-mountain-room': 9, 'glacier-room': 9, 'iron-room': 9,
        'unova-route-14': 9, 'abundant-shrine': 9, 'unova-route-15': 9, 'marvelous-bridge': 9, 'unova-route-8': 9,
        'moor-of-icirrus': 9, 'icirrus-city': 9, 'dragonspiral-tower': 9, 'twist-mountain': 9, 'pinwheel-forest': 9,
        'nacrene-city': 9, 'unova-route-3': 9, 'wellspring-cave': 9, 'striaton-city': 9, 'dreamyard': 9,
        'unova-route-2': 9, 'accumula-town': 9, 'unova-route-1': 9, 'unova-route-17': 9, 'unova-route-18': 9,
        'p2-laboratory': 9, 'nuvema-town': 9, 'nature-sanctuary': 9, 'guidance-chamber': 9,
    },
    areas={('giant-chasm', 'forest'): 9, ('giant-chasm', 'forest-cave'): 9, ('giant-chasm', 'hidden-grotto'): 9,
           ('reversal-mountain', 'b1f'): 9},
)

# Pokémon HOME: storage only. Everything arrives from your games.
REGIONS['home'] = {
    'id': None,
    'stages': [{'en': 'Any time', 'es': 'En cualquier momento', 'tag_en': 'Pokémon HOME', 'tag_es': 'Pokémon HOME', 'pips': 0}],
    'level_caps': [], 'day_care_stage': None, 'use_item_stage': 0, 'held_item_stage': 0, 'beauty': False,
    'clock': False, 'starter_groups': [], 'gates': {}, 'method_gates': {}, 'area_gates': {}, 'locations': {},
    'areas': {}, 'west': set(), 'unown': None,
}

# Places in another region that PokéAPI lists for a game by mistake
OFF_REGION_OK = {'kanto1': {1}, 'johto2': {1, 2}, 'unova': {5}, 'unova2': {5}}

# ------------------------------------------------------------ conditions ---
# Every encounter condition value the games use must be handled here or validate.py fails.
# kind -> (stage per region, external requirement)
COND_DEFAULT_IDS = {'story-progress-before-national-dex', 'great-marsh-daily-slot-none', 'backlot-not-mentioned',
                    'johto-safari-blocks-inactive', 'bug-catching-contest-no',
                    # a second chance at a legendary you knocked out: not a separate way to get it
                    'special-encounter-couldnt-capture-before'}
SEASONS = {'season-spring': 'sp', 'season-summer': 'su', 'season-autumn': 'au', 'season-winter': 'wi'}

STORY_STAGE = {
    'beat-elite-four-round-two': 9,
    # Sinnoh
    'defeat-jupiter': 2, 'defeat-mars': 1, 'beat-galactic-coronet': 7, 'beat-team-galactic-iron-island': 5,
    'cure-eldritch-nightmares': 9, 'oak-eterna-city': 9, 'hall-of-fame': 9, 'national-dex': 9,
    # Johto
    'zephyr-badge': 1, 'awakened-beasts': 3, 'beat-red': 10, 'receive-tm-from-claire': 8,
    'returned-machine-part': 9, 'vermilion-copycat': 9,
    # Unova
    'juniper-cave-of-being': 9, 'quake-badge': 5, 'defeated-ghetsis': 9,
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
    'virtual-console': (9, 'vc'),            # Crystal's GS Ball event, only in the 3DS Virtual Console release
    'captured-reshiram-or-zekrom': (9, None),
}
ITEM_STAGE = {'odd-keystone': 2, 'adamant-orb': 9, 'lustrous-orb': 9, 'ice-key': 9, 'iron-key': 9, 'lunar-wing': 9,
              'light-stone': 9, 'dark-stone': 9}
FOSSIL_STAGE = {'sinnoh': 1, 'johto': 9, 'hoenn': 4, 'kanto3': 5, 'kanto1': 5, 'johto2': 9, 'unova': 3, 'unova2': 3}
# Black 2 unlocks the Iron Key (Registeel) and White 2 the Iceberg Key (Regice); the other key comes from the
# other version through the Key System.
OTHER_VERSION_KEY = {('black2', 'ice-key'), ('white2', 'iron-key')}


def parse_condition(ident, region):
    """Map a PokéAPI encounter condition value to (cond, stage, ext). Returns None for defaults/time."""
    if ident in COND_DEFAULT_IDS or ident.startswith('time-') or ident in SEASONS:
        return None
    if ident == 'defeated-ghetsis':
        return {'k': 'story', 'v': ident}, STORY_STAGE[ident], None
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
        if key in ('ice-key', 'iron-key'):
            return {'k': 'key', 'v': key}, ITEM_STAGE[key], None
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
SKIP_FORMS = {'arceus-unknown', 'castform', 'cherrim-overcast',
              # gender differences, not forms
              'frillish-male', 'frillish-female', 'jellicent-male', 'jellicent-female'}
# Spiky-eared Pichu can't leave Gen 4 (Poké Transfer refuses it)
GEN4_ONLY_FORMS = {'pichu-spiky-eared'}
# Forms that revert when deposited in the PC in Gen 4, so they can't be part of a living dex box.
NOT_BOXABLE = {'shaymin-sky'}
# Gen 5: Deerling and Sawsbuck follow the season, and a fused Kyurem uses up your Reshiram or Zekrom
NOT_BOXABLE_GEN5 = {'deerling-summer', 'deerling-autumn', 'deerling-winter', 'sawsbuck-summer', 'sawsbuck-autumn',
                    'sawsbuck-winter', 'kyurem-black', 'kyurem-white', 'shaymin-sky'}
# Pokémon HOME strips held items and refuses fused Pokémon, so these forms can't be stored there
NOT_BOXABLE_HOME = {'shaymin-sky', 'kyurem-black', 'kyurem-white', 'giratina-origin'} | {
    f'arceus-{t}' for t in ('fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel', 'fire', 'water',
                            'grass', 'electric', 'psychic', 'ice', 'dragon', 'dark')} | {
    f'genesect-{d}' for d in ('douse', 'shock', 'burn', 'chill')}
# HOME tracks forms up to Black 2 / White 2 for now (version group 14)
HOME_FORMS_UP_TO_VG = 14
# Evolutions that one game blocks: (game, species) -> external requirement.
# Yellow's starter Pikachu refuses the Thunder Stone and there is no other Pikachu to catch.
EVO_EXT = {('yellow', 26): 'trade'}
