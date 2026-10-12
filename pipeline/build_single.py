"""Build one self-contained HTML file with every game, sprite sheet and script inlined. It works offline
from disk and is what gets published as a Claude artifact.

Usage: python3 -m pipeline.build_single [src] [generated] [out.html] [--fragment]
--fragment leaves out <!doctype>/<html>/<head>/<body> for hosts that add their own skeleton.
"""
import base64
import json
import os
import re
import sys

from .bundle import bundle


def _json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def _bytes(path):
    with open(path, 'rb') as f:
        return f.read()



def script_json(id_, obj):
    text = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return f'<script type="application/json" id="{id_}">{text}</script>'


def main(argv):
    fragment = '--fragment' in argv
    args = [a for a in argv if a != '--fragment']
    src, gen, out = (args + ['src', 'generated', 'dist/living-dex.html'][len(args):])[:3]
    html = _text(os.path.join(src, 'index.html'))
    css = _text(os.path.join(src, 'css', 'app.css'))
    js = bundle(os.path.join(src, 'js'), 'app.js').replace('</script', '<\\/script')
    svg = _text(os.path.join(src, 'icons', 'icon.svg')).strip()
    icon = 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()

    index = _json(os.path.join(gen, 'data', 'index.json'))
    embeds = [script_json('ld-index', index)]
    for g in index['games']:
        embeds.append(script_json(f'ld-data-{g["id"]}', _json(os.path.join(gen, 'data', f'{g["id"]}.json'))))
    avail_path = os.path.join(gen, 'data', 'availability.json')
    if os.path.exists(avail_path):
        embeds.append(script_json('ld-avail', _json(avail_path)))
    sprites = {}
    for g in index['games']:
        sset = g['sprites']
        if sset not in sprites:
            raw = _bytes(os.path.join(gen, 'sprites', f'{sset}.webp'))
            sprites[sset] = 'data:image/webp;base64,' + base64.b64encode(raw).decode()
    embeds.append(script_json('ld-sprites', sprites))

    # drop the website-only links (manifest, icons, external css/js) and inline instead
    html = re.sub(r'\s*<link rel="(manifest|apple-touch-icon)"[^>]*>', '', html)
    html = re.sub(r'<link rel="icon"[^>]*>', f'<link rel="icon" href="{icon}">', html)
    html = html.replace('<link rel="stylesheet" href="css/app.css">', f'<style>\n{css}\n</style>')
    html = html.replace('<script type="module" src="js/app.js"></script>', '\n'.join(embeds) + f'\n<script>\n{js}\n</script>')
    if fragment:
        head = re.search(r'<head>(.*?)</head>', html, re.S).group(1)
        body = re.search(r'<body>(.*?)</body>', html, re.S).group(1)
        head = re.sub(r'\s*<meta (charset|name="viewport")[^>]*>', '', head)
        html = head.strip() + '\n' + body.strip() + '\n'
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'single file: {out}, {os.path.getsize(out) // 1024} KB')


if __name__ == '__main__':
    main(sys.argv[1:])
