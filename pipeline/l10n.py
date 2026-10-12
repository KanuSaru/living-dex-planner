"""Place-name localisation that PokéAPI lacks.

PokéAPI has no Spanish location names, so they are listed here (Spanish names as used in the
Spanish releases of the Gen 4 games, checked against WikiDex). Sub-area labels come from
PokéAPI's English area prose and are translated with SUB_ES and a few patterns.
validate.py reports any name that is missing.
"""
import re

FORM_NAME_ES = {'pichu-spiky-eared': 'Picoreja'}

LOCATION_EN_OVERRIDE = {
    'roaming-hoenn': 'Roaming Hoenn',
    'roaming-kanto': 'Roaming Kanto',
    'hoenn-pokecenter': 'Event',
    'kanto-pokecenter': 'Event',
    'roaming-sinnoh': 'Roaming Sinnoh',
    'roaming-johto': 'Roaming Johto',
    'sinnoh-pokemart': 'Event',
    'johto-pokemart': 'Event',
    'kanto-power-plant': 'Power Plant',
}

LOCATION_ES = {
    # Sinnoh
    'canalave-city': 'Ciudad Canal', 'eterna-city': 'Ciudad Vetusta', 'pastoria-city': 'Ciudad Pradera',
    'sunyshore-city': 'Ciudad Marina', 'sinnoh-pokemon-league': 'Liga Pokémon', 'oreburgh-mine': 'Mina Pirita',
    'valley-windworks': 'Valle Eólico', 'eterna-forest': 'Bosque Vetusto', 'fuego-ironworks': 'Forja Fuego',
    'mt-coronet': 'Monte Corona', 'great-marsh': 'Gran Pantano', 'solaceon-ruins': 'Ruinas Sosiego',
    'sinnoh-victory-road': 'Calle Victoria', 'ravaged-path': 'Senda Desolada', 'oreburgh-gate': 'Puerta Pirita',
    'stark-mountain': 'Montaña Dura', 'turnback-cave': 'Cueva Retorno', 'snowpoint-temple': 'Templo Puntaneva',
    'wayward-cave': 'Cueva Extravío', 'ruin-maniac-cave': 'Túnel del Ruinamaníaco',
    'maniac-tunnel': 'Túnel del Ruinamaníaco', 'trophy-garden': 'Jardín Trofeo', 'iron-island': 'Isla Hierro',
    'old-chateau': 'Vieja Mansión', 'lake-verity': 'Lago Veraz', 'lake-valor': 'Lago Valor',
    'lake-acuity': 'Lago Agudeza', 'valor-lakefront': 'Orilla Valor', 'acuity-lakefront': 'Orilla Agudeza',
    'lost-tower': 'Torre Sagrada', 'twinleaf-town': 'Pueblo Hojaverde', 'celestic-town': 'Pueblo Caelestis',
    'resort-area': 'Zona Descanso', 'oreburgh-city': 'Ciudad Pirita', 'hearthome-city': 'Ciudad Corazón',
    'veilstone-city': 'Ciudad Rocavelo', 'snowpoint-city': 'Ciudad Puntaneva', 'spear-pillar': 'Columnas Lanza',
    'floaroma-meadow': 'Prado Aromaflor', 'sendoff-spring': 'Fuente Despedida', 'flower-paradise': 'Paraíso Floral',
    'newmoon-island': 'Isla Lunanueva', 'sinnoh-hall-of-origin-1': 'Sala del Origen',
    'distortion-world': 'Mundo Distorsión', 'roaming-sinnoh': 'Errante por Sinnoh', 'sinnoh-pokemart': 'Evento',
    'jubilife-city': 'Ciudad Jubileo', 'sandgem-town': 'Pueblo Arena', 'floaroma-town': 'Pueblo Aromaflor',
    'solaceon-town': 'Pueblo Sosiego',
    # Johto
    'blackthorn-city': 'Ciudad Endrino', 'burned-tower': 'Torre Quemada', 'cherrygrove-city': 'Ciudad Cerezo',
    'cianwood-city': 'Ciudad Orquídea', 'dark-cave': 'Cueva Oscura', 'dragons-den': 'Guarida Dragón',
    'ecruteak-city': 'Ciudad Iris', 'ice-path': 'Ruta Helada', 'ilex-forest': 'Encinar',
    'lake-of-rage': 'Lago de la Furia', 'mt-mortar': 'Monte Mortero', 'mt-silver': 'Monte Plateado',
    'national-park': 'Parque Nacional', 'new-bark-town': 'Pueblo Primavera', 'olivine-city': 'Ciudad Olivo',
    'ruins-of-alph': 'Ruinas Alfa', 'slowpoke-well': 'Pozo Slowpoke', 'sprout-tower': 'Torre Bellsprout',
    'bell-tower': 'Torre Campana', 'tohjo-falls': 'Cataratas Tohjo', 'union-cave': 'Cueva Unión',
    'violet-city': 'Ciudad Malva', 'whirl-islands': 'Islas Remolino', 'azalea-town': 'Pueblo Azalea',
    'goldenrod-city': 'Ciudad Trigal', 'team-rocket-hq': 'Guarida Rocket', 'sinjoh-ruins': 'Ruinas de Sinjoh',
    'embedded-tower': 'Torre Oculta', 'roaming-johto': 'Errante por Johto', 'johto-safari-zone': 'Zona Safari',
    'safari-zone-gate': 'Entrada de la Zona Safari', 'johto-pokemart': 'Evento', 'mahogany-town': 'Pueblo Caoba',
    # Hoenn (Gen 3 Spanish releases)
    'littleroot-town': 'Villa Raíz', 'oldale-town': 'Pueblo Escaso', 'petalburg-city': 'Ciudad Petalia',
    'rustboro-city': 'Ciudad Férrica', 'dewford-town': 'Pueblo Azuliza', 'slateport-city': 'Ciudad Portual',
    'mauville-city': 'Ciudad Malvalona', 'verdanturf-town': 'Pueblo Verdegal', 'lavaridge-town': 'Pueblo Lavacalda',
    'fallarbor-town': 'Pueblo Pardal', 'fortree-city': 'Ciudad Arborada', 'lilycove-city': 'Ciudad Calagua',
    'mossdeep-city': 'Ciudad Algaria', 'sootopolis-city': 'Arrecípolis', 'pacifidlog-town': 'Pueblo Oromar',
    'ever-grande-city': 'Ciudad Colosalia', 'meteor-falls': 'Cascada Meteoro', 'rusturf-tunnel': 'Túnel Fervergal',
    'granite-cave': 'Cueva Granito', 'petalburg-woods': 'Bosque Petalia', 'jagged-pass': 'Desfiladero',
    'fiery-path': 'Senda Ígnea', 'mt-pyre': 'Monte Pírico', 'seafloor-cavern': 'Caverna Abisal',
    'cave-of-origin': 'Cueva Ancestral', 'hoenn-victory-road': 'Calle Victoria', 'shoal-cave': 'Cueva Cardumen',
    'new-mauville': 'Malvalanova', 'abandoned-ship': 'Nao Abandonada', 'sky-pillar': 'Pilar Celeste',
    'hoenn-safari-zone': 'Zona Safari', 'magma-hideout': 'Guarida del Equipo Magma', 'mirage-tower': 'Torre Espejismo',
    'desert-underpass': 'Gruta Desértica', 'artisan-cave': 'Cueva Taller', 'hoenn-altering-cave': 'Cueva Cambiante',
    'southern-island': 'Isla del Sur', 'island-cave': 'Cueva Insular', 'desert-ruins': 'Ruinas del Desierto',
    'ancient-tomb': 'Tumba Antigua', 'team-aqua-hideout': 'Guarida del Equipo Aqua',
    'team-magma-hideout': 'Guarida del Equipo Magma', 'roaming-hoenn': 'Errante por Hoenn', 'terra-cave': 'Cueva Terrena',
    'marine-cave': 'Cueva Marina', 'birth-island': 'Isla Origen', 'navel-rock': 'Roca Ombligo',
    'faraway-island': 'Isla Suprema', 'hoenn-battle-frontier': 'Frente Batalla', 'hoenn-pokecenter': 'Evento',
    'mirage-island': 'Isla Espejismo',
    # Sevii Islands and FireRed/LeafGreen-only places
    'one-island': 'Isla Prima', 'four-island': 'Isla Quarta', 'five-island': 'Isla Inta', 'mt-ember': 'Monte Ascuas',
    'berry-forest': 'Bosque Baya', 'icefall-cave': 'Cueva Glaciada', 'pattern-bush': 'Bosquejo',
    'lost-cave': 'Cueva Perdida', 'kindle-road': 'Camino Candente', 'treasure-beach': 'Playa Tesoro',
    'cape-brink': 'Cabo Extremo', 'bond-bridge': 'Puente Unión', 'three-isle-port': 'Puerto Isla Tera',
    'resort-gorgeous': 'Lugar de Recreo', 'water-labyrinth': 'Aquarinto', 'five-isle-meadow': 'Prado Isla Inta',
    'memorial-pillar': 'Pilar Recuerdo', 'outcast-island': 'Isla Aislada', 'green-path': 'Vía Verde',
    'water-path': 'Vía Acuática', 'ruin-valley': 'Valle Ruinas', 'trainer-tower': 'Torre Desafío',
    'canyon-entrance': 'Entrada al Cañón', 'sevault-canyon': 'Cañón Sétano', 'tanoby-ruins': 'Ruinas Sete',
    'monean-chamber': 'Cámara Monean', 'liptoo-chamber': 'Cámara Liptoo', 'weepth-chamber': 'Cámara Weepth',
    'dilford-chamber': 'Cámara Dilford', 'scufib-chamber': 'Cámara Scufib', 'rixy-chamber': 'Cámara Rixy',
    'viapos-chamber': 'Cámara Viapos', 'kanto-altering-cave': 'Cueva Cambiante', 'roaming-kanto': 'Errante por Kanto',
    'kanto-pokecenter': 'Evento', 'pokemon-tower': 'Torre Pokémon', 'pokemon-mansion': 'Mansión Pokémon',
    'kanto-safari-zone': 'Zona Safari', 'ss-anne': 'S.S. Anne', 'kanto-victory-road-2': 'Calle Victoria',
    'kanto-underground-path': 'Vía Subterránea',
    # Kanto
    'celadon-city': 'Ciudad Azulona', 'cerulean-city': 'Ciudad Celeste', 'cinnabar-island': 'Isla Canela',
    'digletts-cave': 'Cueva Diglett', 'fuchsia-city': 'Ciudad Fucsia', 'mt-moon': 'Monte Moon',
    'pallet-town': 'Pueblo Paleta', 'rock-tunnel': 'Túnel Roca', 'seafoam-islands': 'Islas Espuma',
    'cerulean-cave': 'Cueva Celeste', 'vermilion-city': 'Ciudad Carmín', 'kanto-victory-road-1': 'Calle Victoria',
    'viridian-city': 'Ciudad Verde', 'viridian-forest': 'Bosque Verde', 'kanto-power-plant': 'Central de Energía',
    'pewter-city': 'Ciudad Plateada', 'saffron-city': 'Ciudad Azafrán', 'lavender-town': 'Pueblo Lavanda',
}

_ROUTE = re.compile(r'^(?:sinnoh|johto|kanto|hoenn)-(?:sea-)?route-(\d+)$')


def location_es(identifier):
    m = _ROUTE.match(identifier)
    if m:
        return f'Ruta {m.group(1)}'
    return LOCATION_ES.get(identifier)


def location_en(identifier, pokeapi_name):
    return LOCATION_EN_OVERRIDE.get(identifier, pokeapi_name)


# English sub-area labels for areas whose PokéAPI prose has no "(...)" part, keyed by area identifier.
SUB_EN_BY_IDENT = {
    'department-store-5f': 'Department Store 5F', 'desert': 'Desert', 'forest': 'Forest', 'marshland': 'Marshland',
    'meadow': 'Meadow', 'mountain': 'Mountain', 'peak': 'Peak', 'plains': 'Plains', 'rocky-beach': 'Rocky Beach',
    'savannah': 'Savannah', 'swamp': 'Swamp', 'wasteland': 'Wasteland', 'wetland': 'Wetland',
    'game-corner': 'Game Corner', 'gym': 'Gym', 'magnet-train-station': 'Magnet Train Station',
    'mt-moon-square': 'Mt. Moon Square', 'oreburgh-mining-museum': 'Mining Museum',
    'pewter-museum-of-science': 'Museum of Science', 'prize-corner': 'Prize Corner', 'silph-co': 'Silph Co.',
    'ss-anne-dock': 'S.S. Anne dock', 'eterna-condominiums': 'Eterna Condominiums', 'cavern': 'Cavern',
    'entrance': 'Entrance', 'inside': 'Main cavern', 'celadon-mansion': 'Celadon Mansion', 'summit': 'Summit',
    'fighting-dojo': 'Fighting Dojo', 'silph-co-7f': 'Silph Co. 7F', 'b2f': 'B2F', 'b3f': 'B3F',
    'high-tide': 'High tide', 'low-tide': 'Low tide', 'apex': 'Top', 'area-1': 'Area 1', 'area-2': 'Area 2', 'area-3': 'Area 3',
    'area-4': 'Area 4', 'area-5': 'Area 5', 'area-6': 'Area 6', 'area': '',
}

SUB_ES = {
    '0–9 different Unown caught': '0–9 Unown distintos capturados',
    '10–25 different Unown caught': '10–25 Unown distintos capturados',
    '26+ different Unown caught': '26 o más Unown distintos capturados',
    '1F from exterior': '1F desde el exterior', '1F top': '1F parte alta',
    '2F left room': '2F sala izquierda', '2F leftmost room': '2F sala del extremo izquierdo',
    '2F middle room': '2F sala central', '2F private room': '2F sala privada', '2F right room': '2F sala derecha',
    '2F rightmost room': '2F sala del extremo derecho', '4F small room': '4F sala pequeña',
    "Bill's house": 'Casa de Bill', 'Blackthorn City entrance': 'Entrada de Ciudad Endrino',
    'Cianwood City': 'Ciudad Orquídea', 'Groudon’s room': 'Sala de Groudon', 'Kyogre’s room': 'Sala de Kyogre',
    'Rayquaza’s room': 'Sala de Rayquaza', 'Heatran Chamber': 'Cámara de Heatran', 'Island House': 'Casa de la isla',
    "Kirk's house": 'Casa de Kirk', 'Lower Cave': 'Cueva inferior', 'Upper Cave': 'Cueva superior',
    'Northwest House': 'Casa del noroeste', 'Poke Mart': 'Tienda Pokémon', 'Pokemon Center': 'Centro Pokémon',
    'Violet City entrance': 'Entrada de Ciudad Malva',
    'after Galactic intervention': 'tras la intervención del Equipo Galaxia',
    'before Galactic intervention': 'antes de la intervención del Equipo Galaxia',
    'after pillar 3': 'tras el pilar 3', 'before pillar 1': 'antes del pilar 1',
    'between pillars 1 and 2': 'entre los pilares 1 y 2', 'between pillars 2 and 3': 'entre los pilares 2 y 3',
    'pillar 1': 'pilar 1', 'pillar 2': 'pilar 2', 'pillar 3': 'pilar 3', 'cave gate': 'entrada de la cueva',
    'dining room': 'comedor', 'entrance': 'entrada', 'Entrance': 'Entrada', 'exterior blizzard': 'exterior, ventisca',
    'exterior snowfall': 'exterior, nevada', 'inside': 'interior', 'inside B1F': 'interior B1F',
    'inside cave': 'dentro de la cueva', 'inside exit': 'interior, salida', 'mountainside': 'ladera',
    'north gate': 'puerta norte', 'outside': 'exterior', 'roof': 'tejado', 'top': 'cima', 'west gate': 'puerta oeste',
    'Desert': 'Desierto', 'Forest': 'Bosque', 'Marshland': 'Marisma', 'Meadow': 'Pradera', 'Mountain': 'Montaña',
    'Peak': 'Cumbre', 'Plains': 'Llanura', 'Rocky Beach': 'Playa rocosa', 'Savannah': 'Sabana', 'Swamp': 'Pantano',
    'Wasteland': 'Páramo', 'Wetland': 'Humedal', 'Department Store 5F': 'Centro Comercial 5F',
    'Game Corner': 'Casino', 'Gym': 'Gimnasio', 'Magnet Train Station': 'Estación del Magnetotrén',
    'Mt. Moon Square': 'Plaza Monte Moon', 'Mining Museum': 'Museo de la Mina', 'Museum of Science': 'Museo de Ciencias',
    'Prize Corner': 'Tienda de premios', 'Silph Co.': 'Silph S.A.', 'S.S. Anne dock': 'Muelle del S.S. Anne',
    'Eterna Condominiums': 'Bloque de pisos', 'Cavern': 'Caverna', 'Main cavern': 'Caverna principal',
    '1F, cave behind team rocket': '1F, cueva tras el Team Rocket', '1F/small room': '1F, sala pequeña',
    'Area 1, east': 'Zona 1, este', 'Area 2, north': 'Zona 2, norte', 'Area 3, west': 'Zona 3, oeste',
    'Cinnabar Island': 'Isla Canela', 'NE/acro bike area': 'NE, zona de la bici acrobática',
    'NW/mach bike area': 'NO, zona de la bici de carreras', 'SE': 'SE', 'SW': 'SO', "Steven's house": 'Casa de Máximo',
    'apex': 'cima', 'Top': 'Cima', 'back': 'fondo', 'back/small room': 'fondo, sala pequeña', 'cave': 'cueva',
    'celadon mansion': 'Mansión Azulona', 'Celadon Mansion': 'Mansión Azulona', 'expansion north': 'ampliación norte',
    'expansion south': 'ampliación sur', 'fighting dojo': 'Dojo Karate', 'Fighting Dojo': 'Dojo Karate',
    'high tide': 'marea alta', 'High tide': 'Marea alta', 'low tide': 'marea baja', 'Low tide': 'Marea baja',
    'item rooms': 'salas de objetos', 'middle': 'centro', 'silph co 7f': 'Silph S.A. 7F', 'Silph Co. 7F': 'Silph S.A. 7F',
    'summit': 'cima', 'Summit': 'Cima', 'underwater': 'bajo el agua', 'waterfall': 'cascada',
    'interior A': 'interior A', 'interior B': 'interior B', 'interior C': 'interior C', 'interior D': 'interior D',
}
_DIR_ES = {'north': 'norte', 'south': 'sur', 'east': 'este', 'west': 'oeste'}
_FLOOR = re.compile(r'^([Bb]?\d+[Ff])(?: ([A-E]|left|right))?$')
_LETTER = re.compile(r'^[A-I]$')
_ROOM = re.compile(r'^room (\d+)$')
_ROAD_ONLY = re.compile(r'^Road (\d+)$')
_TOWARDS = re.compile(r'^(north|south|east|west), towards (.+)$')
_ROAD = re.compile(r'^1F Road (\d+)$')
_AREA = re.compile(r'^Area (\d)$')


def sub_es(sub_en, en_to_es_location):
    """Translate an English sub-area label. Returns None if no rule applies."""
    if sub_en in SUB_ES:
        return SUB_ES[sub_en]
    m = _FLOOR.match(sub_en)
    if m:
        side = {'left': 'izquierda', 'right': 'derecha'}.get(m.group(2), m.group(2))
        return m.group(1).upper() + (f' {side}' if side else '')
    if _LETTER.match(sub_en):
        return sub_en
    m = _ROOM.match(sub_en)
    if m:
        return f'sala {m.group(1)}'
    m = _ROAD_ONLY.match(sub_en)
    if m:
        return f'Ruta {m.group(1)}'
    m = _TOWARDS.match(sub_en)
    if m and m.group(2) in en_to_es_location:
        return f'{_DIR_ES[m.group(1)]}, hacia {en_to_es_location[m.group(2)]}'
    m = _ROAD.match(sub_en)
    if m:
        return f'1F, Ruta {m.group(1)}'
    m = _AREA.match(sub_en)
    if m:
        return f'Zona {m.group(1)}'
    return None


def tidy_sub_en(sub):
    sub = re.sub(r'^1F Road (\d+)$', r'1F, Route \1', sub)
    sub = re.sub(r'^Road (\d+)$', r'Route \1', sub)
    sub = re.sub(r'^([bB]?\d+)f$', lambda m: m.group(1).upper() + 'F', sub)
    sub = sub.replace('/', ', ').replace('silph co 7f', 'Silph Co. 7F').replace('team rocket', 'Team Rocket')
    sub = sub.replace('Poke Mart', 'Poké Mart').replace('Pokemon Center', 'Pokémon Center')
    return sub[:1].upper() + sub[1:]
