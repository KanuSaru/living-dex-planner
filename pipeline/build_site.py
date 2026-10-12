"""Assemble the deployable static website in site/.

    site/index.html, css/, js/ (ES modules), icons/, manifest.webmanifest, sw.js
    site/data/<game>.json, index.json, availability.json
    site/sprites/<set>.webp

Usage: python3 -m pipeline.build_site [src] [generated] [site]
"""
import hashlib
import json
import os
import shutil
import sys

from PIL import Image, ImageDraw


def _text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def _bytes(path):
    with open(path, 'rb') as f:
        return f.read()


ICON_BG, ICON_FG = (27, 30, 44, 255), (226, 179, 84, 255)


def draw_icon(size, path, maskable=False):
    """Raster version of src/icons/icon.svg: a 3x3 grid of boxes, seven filled."""
    im = Image.new('RGBA', (size, size), ICON_BG if maskable else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = size / 64
    inset = 0.1 * size if maskable else 0
    scale = (size - 2 * inset) / size
    if not maskable:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=14 * s, fill=ICON_BG)
    def box(x, y, filled):
        x0, y0 = inset + x * s * scale, inset + y * s * scale
        x1, y1 = x0 + 12 * s * scale, y0 + 12 * s * scale
        if filled:
            d.rounded_rectangle([x0, y0, x1, y1], radius=3 * s * scale, fill=ICON_FG)
        else:
            w = max(1, round(2.5 * s * scale))
            d.rounded_rectangle([x0 + w / 2, y0 + w / 2, x1 - w / 2, y1 - w / 2], radius=2.5 * s * scale, outline=ICON_FG, width=w)
    cells = [(10, 10), (26, 10), (42, 10), (10, 26), (26, 26), (42, 26), (10, 42), (26, 42), (42, 42)]
    for i, (x, y) in enumerate(cells):
        box(x, y, i < 7)
    im.save(path)


MANIFEST = {
    'name': 'Living Dex Planner',
    'short_name': 'Living Dex',
    'description': 'Living dex planner for the Pokémon games from Red and Blue to Black 2 and White 2, and Pokémon HOME.',
    'start_url': './',
    'scope': './',
    'display': 'standalone',
    'background_color': '#13121b',
    'theme_color': '#13121b',
    'icons': [
        {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
        {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
        {'src': 'icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        {'src': 'icons/icon.svg', 'sizes': 'any', 'type': 'image/svg+xml'},
    ],
}


def main(argv):
    src, gen, out = (argv + ['src', 'generated', 'site'][len(argv):])[:3]
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    shutil.copy(os.path.join(src, 'index.html'), os.path.join(out, 'index.html'))
    shutil.copytree(os.path.join(src, 'css'), os.path.join(out, 'css'))
    shutil.copytree(os.path.join(src, 'js'), os.path.join(out, 'js'))
    shutil.copytree(os.path.join(src, 'icons'), os.path.join(out, 'icons'))
    draw_icon(192, os.path.join(out, 'icons', 'icon-192.png'))
    draw_icon(512, os.path.join(out, 'icons', 'icon-512.png'))
    draw_icon(512, os.path.join(out, 'icons', 'icon-maskable-512.png'), maskable=True)
    with open(os.path.join(out, 'manifest.webmanifest'), 'w', encoding='utf-8') as f:
        json.dump(MANIFEST, f, ensure_ascii=False, indent=1)
    shutil.copytree(os.path.join(gen, 'data'), os.path.join(out, 'data'))
    shutil.copytree(os.path.join(gen, 'sprites'), os.path.join(out, 'sprites'))
    open(os.path.join(out, '.nojekyll'), 'w').close()

    files, digest = [], hashlib.sha256()
    for dirpath, _, names in os.walk(out):
        for n in sorted(names):
            p = os.path.join(dirpath, n)
            rel = os.path.relpath(p, out).replace(os.sep, '/')
            if rel in ('.nojekyll', 'sw.js'):
                continue
            files.append(rel)
            digest.update(rel.encode())
            digest.update(_bytes(p))
    files.sort()
    # precache the app itself; each game's data and sprite sheet are cached the first time you open that game
    per_game = lambda f: f.startswith('sprites/') or (f.startswith('data/') and f not in ('data/index.json', 'data/availability.json'))  # noqa: E731
    precache = ['./'] + [f for f in files if not per_game(f)]
    sw = _text(os.path.join(src, 'sw.js'))
    sw = sw.replace('__VERSION__', digest.hexdigest()[:12]).replace('__PRECACHE__', json.dumps(precache, indent=1))
    with open(os.path.join(out, 'sw.js'), 'w', encoding='utf-8') as f:
        f.write(sw)
    size = sum(os.path.getsize(os.path.join(out, f)) for f in files)
    print(f'site: {len(files)} files, {size // 1024} KB, cache version {digest.hexdigest()[:12]}')


if __name__ == '__main__':
    main(sys.argv[1:])
