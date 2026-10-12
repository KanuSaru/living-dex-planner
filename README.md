# Platinum Living Dex

A living dex planner for Pokémon **Diamond, Pearl, Platinum, HeartGold and SoulSilver**, built from [PokéAPI](https://pokeapi.co/) data. For every Pokémon it shows every place it appears (levels, morning/day/night rates, special conditions), its evolution family, and its alternate forms. It also builds a route plan that picks the earliest way to get each one: catch it, evolve it or breed it.

## Features

- **Five games.** Switch between them in the header. Each game keeps its own boxes, starter choice and progress.
- **PC boxes.** Your boxes laid out in dex order, 30 per box (6 × 5), with optional form slots and a choice of starting box. Tap a slot to mark it boxed; each Pokémon's detail panel shows its box, row and column.
- **Route plan.** Catches are grouped by place and ordered by story progress, with copy counts ("×3" means catch three and evolve the extras). Shedinja doesn't cost an extra Nincada, and one-time gifts show how many you'll need to breed.
- **Where I am now.** Pick your badge count to see what you can get now, dim what comes later, and optionally hide it.
- **Catch right now.** Uses your device clock (Gen 4 periods: morning 4–10, day 10–20, night 20–4) and weekday to list everything you still need that appears at this moment, including Friday-only Drifloon and Lapras and the Bug-Catching Contest days.
- **Forms.** Unown letters, Burmy and Wormadam cloaks, Shellos and Gastrodon seas, Rotom appliances, Giratina Origin, Shaymin Sky, Deoxys, Arceus plates and Spiky-eared Pichu, each with how to get it in the selected game.
- **English and Spanish.** Pokémon, item, move and form names come from PokéAPI. Spanish place names are in `pipeline/l10n.py`, checked against WikiDex.
- **Sync.** Copy a short code or link with your progress and paste it on another device, or save and load it as a file.
- **Offline app.** Once loaded, the site works without internet and can be installed as an app (look for the "Install app" button, or your browser's install option).
- **In other Gen 4 games.** For each Pokémon, the detail panel shows which other games can get it.

## Project layout

| Path | What it is |
|---|---|
| `pipeline/config.py` | Per-game and per-region settings: story stages, HM and rod stages, condition rules, form rules |
| `pipeline/l10n.py` | Spanish place names and sub-area labels |
| `pipeline/build_data.py` | PokéAPI CSVs → `generated/data/<game>.json` (structured, language-neutral) |
| `pipeline/build_sprites.py` | One sprite sheet per sprite set (DP, Pt, HGSS), forms included |
| `pipeline/validate.py` | Data checks that fail the build: species and area counts, stages, names in both languages, every condition and method handled, sprites present |
| `pipeline/build_site.py` | Assembles `site/`: pages, data, sprites, icons, manifest and the offline service worker |
| `pipeline/build_single.py`, `pipeline/bundle.py` | One self-contained `dist/living-dex.html` with everything inlined |
| `scripts/availability.mjs` | Runs the planner over every game to fill the "In other Gen 4 games" chips |
| `src/index.html`, `src/css/app.css` | Page shell and styles |
| `src/js/planner.js` | Planner logic (pure, no DOM): best route, plan groups, catch-right-now, forms |
| `src/js/text.js`, `src/js/i18n.js` | Sentences and interface strings in English and Spanish |
| `src/js/store.js`, `src/js/progress-code.js` | Saved state and sync codes |
| `src/js/boxes.js` | PC box layout and slot positions (pure) |
| `src/js/views/*.js`, `src/js/app.js` | The tabs, detail panel, sync panel and the controller |
| `tests/` | Node tests for the planner, text and codes; Python tests for the pipeline |

## Build and test

Needs git, Python 3 with Pillow (`pip install pillow`) and Node 20 or newer. There are no npm packages to install.

```bash
./build.sh            # fetch data, build, validate, test, assemble site/ and dist/
UPDATE=1 ./build.sh   # same, but pull the latest PokéAPI data first
python3 -m http.server -d site 8000   # preview at http://localhost:8000
```

`build.sh` stops at the first failure, so a data change in PokéAPI that drops encounters, adds an unknown condition or leaves a place without a Spanish name never reaches the live site.

## Deploy

The included GitHub Actions workflow builds, tests and publishes to GitHub Pages on every push to `main`, and once a month. Pull requests only build and test. In the repository, **Settings → Pages → Source** must be **GitHub Actions**.

## Notes

- Story stages ("≈ badges needed") are estimates, set in `pipeline/config.py`.
- Spanish place names follow the Spanish releases of the Gen 4 games.
- Events, Pal Park, the Pokéwalker and trades are listed as external requirements rather than planned.
- Sprites and Pokémon names are Nintendo / Creatures / GAME FREAK property. This is a non-commercial fan project; keep the footer credit.
