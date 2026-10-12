#!/usr/bin/env bash
# Full build: fetch PokéAPI data and sprites, build and validate the data, run all tests,
# then assemble the website (site/) and the single offline file (dist/living-dex.html).
# Needs: git, python3 with Pillow, node >= 20. Set UPDATE=1 to pull the latest PokéAPI data.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d pokeapi-src ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/PokeAPI/pokeapi.git pokeapi-src
  git -C pokeapi-src sparse-checkout set data/v2/csv
elif [ "${UPDATE:-0}" = 1 ]; then
  git -C pokeapi-src pull --ff-only
fi
if [ ! -d sprites-src ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/PokeAPI/sprites.git sprites-src
elif [ "${UPDATE:-0}" = 1 ]; then
  git -C sprites-src pull --ff-only
fi
# set every time, so an older checkout picks up sprite folders added later
git -C sprites-src sparse-checkout set --no-cone \
  'sprites/pokemon/versions/generation-i/red-blue/transparent/[0-9]*.png' \
  'sprites/pokemon/versions/generation-i/yellow/transparent/[0-9]*.png' \
  'sprites/pokemon/versions/generation-ii/gold/transparent/[0-9]*.png' \
  'sprites/pokemon/versions/generation-ii/crystal/transparent/[0-9]*.png' \
  'sprites/pokemon/versions/generation-iii/ruby-sapphire/[0-9]*.png' \
  'sprites/pokemon/versions/generation-iii/emerald/[0-9]*.png' \
  'sprites/pokemon/versions/generation-iii/firered-leafgreen/[0-9]*.png' \
  'sprites/pokemon/versions/generation-iv/diamond-pearl/[0-9]*.png' \
  'sprites/pokemon/versions/generation-iv/platinum/[0-9]*.png' \
  'sprites/pokemon/versions/generation-iv/heartgold-soulsilver/[0-9]*.png' \
  'sprites/pokemon/versions/generation-v/black-white/[0-9]*.png'

echo "== data";        python3 -m pipeline.build_data pokeapi-src/data/v2/csv generated
echo "== sprites";     python3 -m pipeline.build_sprites sprites-src generated
echo "== availability"; node scripts/availability.mjs generated
echo "== validate";    python3 -m pipeline.validate generated
echo "== tests";       python3 -m unittest discover -s tests
                       node --test tests/planner.test.mjs tests/text.test.mjs tests/progress.test.mjs tests/boxes.test.mjs tests/multi.test.mjs
echo "== site";        python3 -m pipeline.build_site src generated site
echo "== single file"; python3 -m pipeline.build_single src generated dist/living-dex.html
