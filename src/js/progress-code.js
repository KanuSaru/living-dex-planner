// Compact, copyable progress codes: "LD1.<game>.<base64url bits>".
// Bit i (0-based) is species i+1 for 1..493, then one bit per alternate form in data.forms order.

const NATIONAL = 493;
const PREFIX = 'LD1';

function toB64url(bytes) {
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function fromB64url(s) {
  const b64 = s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4);
  const bin = atob(b64);
  return Uint8Array.from(bin, (c) => c.charCodeAt(0));
}

const formKeys = (data) => data.forms.filter((f) => !f.def).map((f) => f.key);

export function encodeProgress(data, caught) {
  const keys = formKeys(data);
  const bits = NATIONAL + keys.length;
  const bytes = new Uint8Array(Math.ceil(bits / 8));
  const set = (i) => { bytes[i >> 3] |= 1 << (i & 7); };
  for (let id = 1; id <= NATIONAL; id++) if (caught.has(String(id))) set(id - 1);
  keys.forEach((k, i) => { if (caught.has(k)) set(NATIONAL + i); });
  return `${PREFIX}.${data.game.id}.${toB64url(bytes)}`;
}

// Returns { game } from a code without needing the game's data, or null if it isn't a code.
export function peekProgress(code) {
  const m = String(code || '').replace(/\s+/g, '').match(/^LD1\.([a-z]+)\.([A-Za-z0-9_-]+)$/);
  return m ? { game: m[1], payload: m[2] } : null;
}

export function decodeProgress(data, code) {
  const p = peekProgress(code);
  if (!p || p.game !== data.game.id) return null;
  let bytes;
  try { bytes = fromB64url(p.payload); } catch { return null; }
  const keys = formKeys(data);
  if (bytes.length !== Math.ceil((NATIONAL + keys.length) / 8)) return null;
  const has = (i) => (bytes[i >> 3] >> (i & 7)) & 1;
  const caught = new Set();
  for (let id = 1; id <= NATIONAL; id++) if (has(id - 1)) caught.add(String(id));
  keys.forEach((k, i) => { if (has(NATIONAL + i)) caught.add(k); });
  return caught;
}
