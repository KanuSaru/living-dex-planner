// Loads the generated data once for every test file. Run the data build first (./build.sh does).
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dataDir = join(root, 'generated', 'data');

export const GAMES = ['ruby', 'sapphire', 'emerald', 'firered', 'leafgreen', 'diamond', 'pearl', 'platinum', 'heartgold', 'soulsilver'];
export const GEN4 = ['diamond', 'pearl', 'platinum', 'heartgold', 'soulsilver'];
const cache = new Map();

export function loadGame(id) {
  if (!cache.has(id)) {
    const path = join(dataDir, `${id}.json`);
    if (!existsSync(path)) throw new Error(`Missing ${path}. Run the data build first (./build.sh or python3 -m pipeline.build_data).`);
    cache.set(id, JSON.parse(readFileSync(path, 'utf8')));
  }
  return cache.get(id);
}

export const areaKey = (data, id) => data.areas.find((a) => a.id === id).key;
