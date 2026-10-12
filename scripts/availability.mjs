// Writes generated/data/availability.json: for every species, how each game can get it.
// Uses the same planner as the site, so the "In other Gen 4 games" chips always agree with each game's plan.
// Usage: node scripts/availability.mjs generated
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { createPlanner } from '../src/js/planner.js';

const out = process.argv[2] || 'generated';
const index = JSON.parse(readFileSync(join(out, 'data', 'index.json'), 'utf8'));
const result = {};
for (const g of index.games) {
  const data = JSON.parse(readFileSync(join(out, 'data', `${g.id}.json`), 'utf8'));
  const P = createPlanner(data);
  for (const s of data.species) {
    const b = P.best(s.id);
    if (!b) continue;
    // an unchosen starter is still yours to pick in that game
    const value = b.ext && b.ext !== 'starter' ? `${b.k}:${b.ext}` : b.k;
    (result[s.id] ||= {})[g.id] = value;
  }
}
writeFileSync(join(out, 'data', 'availability.json'), JSON.stringify(result));
console.log(`availability: ${Object.keys(result).length} species across ${index.games.length} games`);
