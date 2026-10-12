// PC box layout (pure, no DOM). Box sizes differ by generation: Gen 1 and 2 boxes hold 20 Pokémon (shown 5 × 4),
// Gen 3 to 5 and Pokémon HOME hold 30 in 6 columns × 5 rows. Each game's data file says which.

export const BOX_SIZE = 30;
export const BOX_COLS = 6;
export const BOX_COUNT = 18;

// { size, cols, count } for a game
export function boxShape(data) {
  return { size: BOX_SIZE, cols: BOX_COLS, count: BOX_COUNT, ...((data && data.game && data.game.boxes) || {}) };
}

// slots in dex order for the chosen scope; forms (when included) follow their species
export function boxSlots(data, { scope = 'regional', includeForms = false } = {}) {
  let list = data.species.filter((s) => scope === 'national' || s.rd != null);
  if (scope !== 'national') list = [...list].sort((a, b) => a.rd - b.rd);
  const forms = new Map();
  if (includeForms) {
    for (const f of data.forms || []) {
      if (f.def || f.nobox) continue;
      if (!forms.has(f.sp)) forms.set(f.sp, []);
      forms.get(f.sp).push(f);
    }
  }
  const slots = [];
  for (const s of list) {
    slots.push({ key: String(s.id), sp: s.id, no: scope === 'national' ? s.id : s.rd });
    for (const f of forms.get(s.id) || []) slots.push({ key: f.key, sp: s.id, form: f, no: scope === 'national' ? s.id : s.rd });
  }
  return slots;
}

// group slots into boxes; `start` is the first box number to use (1-based)
export function layoutBoxes(slots, { start = 1, size = BOX_SIZE } = {}) {
  const boxes = [];
  for (let i = 0; i < slots.length; i += size) {
    boxes.push({ n: start + boxes.length, slots: slots.slice(i, i + size) });
  }
  return boxes;
}

// where a key goes: { box, slot (1-based), row, col } or null
export function positionOf(slots, key, { start = 1, size = BOX_SIZE, cols = BOX_COLS } = {}) {
  const i = slots.findIndex((s) => s.key === String(key));
  if (i < 0) return null;
  const slot = (i % size) + 1;
  return { box: start + Math.floor(i / size), slot, row: Math.ceil(slot / cols), col: ((slot - 1) % cols) + 1 };
}
