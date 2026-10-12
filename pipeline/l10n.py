"""Place-name localisation that PokéAPI lacks.

PokéAPI has no Spanish location names, so they are listed here (Spanish names as used in the
Spanish releases of the Gen 4 games, checked against WikiDex). Sub-area labels come from
PokéAPI's English area prose and are translated with SUB_ES and a few patterns.
validate.py reports any name that is missing.
"""
import re

FORM_NAME_ES = {'pichu-spiky-eared': 'Picoreja'}

LOCATION_EN_OVERRIDE = {
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
    # Kanto
    'celadon-city': 'Ciudad Azulona', 'cerulean-city': 'Ciudad Celeste', 'cinnabar-island': 'Isla Canela',
    'digletts-cave': 'Cueva Diglett', 'fuchsia-city': 'Ciudad Fucsia', 'mt-moon': 'Monte Moon',
    'pallet-town': 'Pueblo Paleta', 'rock-tunnel': 'Túnel Roca', 'seafoam-islands': 'Islas Espuma',
    'cerulean-cave': 'Cueva Celeste', 'vermilion-city': 'Ciudad Carmín', 'kanto-victory-road-1': 'Calle Victoria',
    'viridian-city': 'Ciudad Verde', 'viridian-forest': 'Bosque Verde', 'kanto-power-plant': 'Central de Energía',
    'pewter-city': 'Ciudad Plateada', 'saffron-city': 'Ciudad Azafrán', 'lavender-town': 'Pueblo Lavanda',
}

_ROUTE = re.compile(r'^(?:sinnoh|johto|kanto)-(?:sea-)?route-(\d+)$')


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
    'entrance': 'Entrance', 'inside': 'Main cavern', 'area-1': 'Area 1', 'area-2': 'Area 2', 'area-3': 'Area 3',
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
    'interior A': 'interior A', 'interior B': 'interior B', 'interior C': 'interior C', 'interior D': 'interior D',
}
_DIR_ES = {'north': 'norte', 'south': 'sur', 'east': 'este', 'west': 'oeste'}
_FLOOR = re.compile(r'^(B?\d+F)(?: ([A-E]|left|right))?$')
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
        return m.group(1) + (f' {side}' if side else '')
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
    sub = sub.replace('Poke Mart', 'Poké Mart').replace('Pokemon Center', 'Pokémon Center')
    return sub[:1].upper() + sub[1:]
