"""Inject data.json and the sprite sheet into template.html to produce a single self-contained page."""
import base64, sys

template, data, sprites, out = (sys.argv[1:5] + ['template.html', 'data.json', 'sheet.webp', 'platinum-living-dex.html'][len(sys.argv) - 1:])[:4]
t = open(template, encoding='utf-8').read()
d = open(data, encoding='utf-8').read().replace('</', '<\\/')  # keep "</" from closing the <script> tag
s = 'data:image/webp;base64,' + base64.b64encode(open(sprites, 'rb').read()).decode()
open(out, 'w', encoding='utf-8').write(t.replace('__DATA__', d).replace('__SPRITE__', s))
print('wrote', out)
