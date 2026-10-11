#!/usr/bin/env bash
# Full rebuild: fetch PokéAPI source data + sprites, build data.json and sheet.webp, assemble the page.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d pokeapi-src ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/PokeAPI/pokeapi.git pokeapi-src
  git -C pokeapi-src sparse-checkout set data/v2/csv
fi
if [ ! -d sprites-src ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/PokeAPI/sprites.git sprites-src
  git -C sprites-src sparse-checkout set --no-cone 'sprites/pokemon/versions/generation-iv/platinum/[0-9]*.png'
fi

python3 build_data.py pokeapi-src/data/v2/csv data.json
python3 build_sprites.py sprites-src/sprites/pokemon/versions/generation-iv/platinum sheet.webp
python3 assemble.py template.html data.json sheet.webp platinum-living-dex.html
python3 build_site.py template.html data.json sheet.webp site
