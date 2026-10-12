"""Pack sprites into one WebP sheet per sprite set (Diamond/Pearl, Platinum, HeartGold/SoulSilver).

Layout: 25 columns of 80x80 cells. Species 1..493 sit at index id-1; alternate forms follow,
in the order listed in generated/sprite-manifest.json.

Usage: python3 -m pipeline.build_sprites <PokeAPI/sprites checkout> generated
"""
import json
import os
import sys

from PIL import Image

from . import config as C


def _json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1)



def build_sheet(src_dir, forms, out_path):
    total = C.NATIONAL_MAX + len(forms)
    rows = (total + C.SPRITE_COLS - 1) // C.SPRITE_COLS
    cell = C.SPRITE_CELL
    sheet = Image.new('RGBA', (C.SPRITE_COLS * cell, rows * cell), (0, 0, 0, 0))
    missing = []

    def paste(index, path):
        im = Image.open(path).convert('RGBA')
        if im.size != (cell, cell):
            im = im.resize((cell, cell), Image.NEAREST)
        sheet.paste(im, ((index % C.SPRITE_COLS) * cell, (index // C.SPRITE_COLS) * cell))

    for sid in range(1, C.NATIONAL_MAX + 1):
        path = os.path.join(src_dir, f'{sid}.png')
        if os.path.exists(path):
            paste(sid - 1, path)
        else:
            missing.append(f'{sid}.png')
    for key, info in forms.items():
        path = next((os.path.join(src_dir, f) for f in info['files'] if os.path.exists(os.path.join(src_dir, f))), None)
        if path:
            paste(info['index'], path)
        else:
            missing.append(f'{key} ({" / ".join(info["files"])})')
    sheet.save(out_path, lossless=True, quality=100, method=6)
    return missing


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    sprites_repo, out_dir = argv
    manifest = _json(os.path.join(out_dir, 'sprite-manifest.json'))
    os.makedirs(os.path.join(out_dir, 'sprites'), exist_ok=True)
    report = {}
    for sset, folder in C.SPRITE_SETS.items():
        src = os.path.join(sprites_repo, 'sprites', 'pokemon', 'versions', 'generation-iv', folder)
        out = os.path.join(out_dir, 'sprites', f'{sset}.webp')
        missing = build_sheet(src, manifest.get(sset, {}), out)
        report[sset] = missing
        print(f'{sset}: {os.path.getsize(out) // 1024} KB, {len(missing)} missing')
    _write_json(os.path.join(out_dir, 'sprite-problems.json'), report)


if __name__ == '__main__':
    main(sys.argv[1:])
