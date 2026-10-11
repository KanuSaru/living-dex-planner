"""Build a deployable static website in site/: index.html (data inlined) + sheet.webp served as its own cached file.

Usage: python3 build_site.py [template.html] [data.json] [sheet.webp] [site]
"""
import os, shutil, sys

args = sys.argv[1:] + ['template.html', 'data.json', 'sheet.webp', 'site'][len(sys.argv) - 1:]
template, data, sprites, out = args[:4]
os.makedirs(out, exist_ok=True)

t = open(template, encoding='utf-8').read()
d = open(data, encoding='utf-8').read().replace('</', '<\\/')

head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Plan a Pokémon Platinum living dex: every route, level, encounter rate and evolution for all 493 Pokémon, ordered into the fastest catch route.">
<meta property="og:title" content="Platinum Living Dex">
<meta property="og:description" content="Every route, level, encounter rate and evolution in Pokémon Platinum, ordered into the fastest living dex route.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#e7e9ef" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#13121b" media="(prefers-color-scheme: dark)">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='14' fill='%23e7e9ef' stroke='%231b1e2c' stroke-width='3'/%3E%3Cpath d='M2 16h28' stroke='%231b1e2c' stroke-width='3'/%3E%3Cpath d='M2 16a14 14 0 0 1 28 0z' fill='%239a6a12' stroke='%231b1e2c' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='4.5' fill='%23e7e9ef' stroke='%231b1e2c' stroke-width='3'/%3E%3C/svg%3E">
<link rel="preload" href="sheet.webp" as="image" type="image/webp">
<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
'''
page = head + t.replace('__DATA__', d).replace('url(__SPRITE__)', 'url(sheet.webp)') + '\n</body>\n</html>\n'
open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page)
shutil.copy(sprites, os.path.join(out, 'sheet.webp'))
open(os.path.join(out, '.nojekyll'), 'w').close()
print('wrote', out + '/index.html', 'and', out + '/sheet.webp')
