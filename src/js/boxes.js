// PC box layout (pure, no DOM). Gen 4 boxes hold 30 Pokémon in 6 columns × 5 rows; the games have 18 boxes.

export const BOX_SIZE = 30;
export const BOX_COLS = 6;
export const BOX_COUNT = 18;

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
export function layoutBoxes(slots, { start = 1 } = {}) {
  const boxes = [];
  for (let i = 0; i < slots.length; i += BOX_SIZE) {
    boxes.push({ n: start + boxes.length, slots: slots.slice(i, i + BOX_SIZE) });
  }
  return boxes;
}

// where a key goes: { box, slot (1-30), row (1-5), col (1-6) } or null
export function positionOf(slots, key, { start = 1 } = {}) {
  const i = slots.findIndex((s) => s.key === String(key));
  if (i < 0) return null;
  const slot = (i % BOX_SIZE) + 1;
  return { box: start + Math.floor(i / BOX_SIZE), slot, row: Math.ceil(slot / BOX_COLS), col: ((slot - 1) % BOX_COLS) + 1 };
}
