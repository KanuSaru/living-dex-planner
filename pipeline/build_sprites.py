"""Pack sprites into one WebP sheet per sprite set (one or two per generation, and one for Pokémon HOME).

Layout: 25 columns of square cells. Species 1..N sit at index id-1 (N = the last species the set covers);
alternate forms follow, in the order listed in generated/sprite-manifest.json. Each set keeps its native
pixel size; every sprite is cropped to the set's shared bounding box so no space is wasted.

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


def build_sheet(src_dir, last, forms, out_path):
    files = {sid - 1: os.path.join(src_dir, f'{sid}.png') for sid in range(1, last + 1)}
    missing = [f'{i + 1}.png' for i, p in files.items() if not os.path.exists(p)]
    files = {i: p for i, p in files.items() if os.path.exists(p)}
    for key, info in forms.items():
        path = next((os.path.join(src_dir, f) for f in info['files'] if os.path.exists(os.path.join(src_dir, f))), None)
        if path:
            files[info['index']] = path
        else:
            missing.append(f'{key} ({" / ".join(info["files"])})')
    images = {i: Image.open(p).convert('RGBA') for i, p in files.items()}
    # a square crop around everything any sprite in the set draws, centred on the canvas
    size = max(im.size[0] for im in images.values())
    lo, hi = size, 0
    for im in images.values():
        box = im.getbbox()
        if box:
            off = (size - im.size[0]) // 2
            lo = min(lo, box[0] + off, box[1] + off)
            hi = max(hi, box[2] + off, box[3] + off)
    half = max(size / 2 - lo, hi - size / 2)
    cell = int(2 * half + 0.999) + (int(2 * half + 0.999) % 2)
    start = (size - cell) // 2
    total = max([last] + [info['index'] + 1 for info in forms.values()])
    rows = (total + C.SPRITE_COLS - 1) // C.SPRITE_COLS
    sheet = Image.new('RGBA', (C.SPRITE_COLS * cell, rows * cell), (0, 0, 0, 0))
    for i, im in images.items():
        off = (size - im.size[0]) // 2
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        canvas.paste(im, (off, off))
        tile = canvas.crop((start, start, start + cell, start + cell))
        sheet.paste(tile, ((i % C.SPRITE_COLS) * cell, (i // C.SPRITE_COLS) * cell))
    sheet.save(out_path, lossless=True, quality=100, method=6)
    return missing, cell


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    sprites_repo, out_dir = argv
    manifest = _json(os.path.join(out_dir, 'sprite-manifest.json'))
    os.makedirs(os.path.join(out_dir, 'sprites'), exist_ok=True)
    report = {}
    for sset, (folder, last) in C.SPRITE_SETS.items():
        src = os.path.join(sprites_repo, 'sprites', 'pokemon', 'versions', folder)
        out = os.path.join(out_dir, 'sprites', f'{sset}.webp')
        missing, cell = build_sheet(src, last, manifest.get(sset, {}), out)
        report[sset] = missing
        print(f'{sset}: {cell}px cells, {os.path.getsize(out) // 1024} KB, {len(missing)} missing')
    _write_json(os.path.join(out_dir, 'sprite-problems.json'), report)


if __name__ == '__main__':
    main(sys.argv[1:])
