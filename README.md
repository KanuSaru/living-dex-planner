# Living Dex Planner

A living dex planner for every Pokémon game from **Red and Blue to Black 2 and White 2**, and for **Pokémon HOME**, built from [PokéAPI](https://pokeapi.co/) data. For every Pokémon it shows every place it appears (levels, morning/day/night rates, special conditions), its evolution family, and its alternate forms. It also builds a route plan that picks the earliest way to get each one: catch it, evolve it or breed it.

## Features

- **Every game from Gen 1 to Gen 5, and HOME.** Red, Blue, Yellow, Gold, Silver, Crystal, Ruby, Sapphire, Emerald, FireRed, LeafGreen, Diamond, Pearl, Platinum, HeartGold, SoulSilver, Black, White, Black 2 and White 2 can each be your main game, or pick Pokémon HOME for a full National Dex (1,025 species). Each main game keeps its own boxes, starter choice and progress.
- **The real transfer chain.** Whatever your main game can't get is planned in the other games you own and moved the way the games allow: trades within a generation (with trade evolutions), the Time Capsule between Gen 1 and Gen 2 (only the first 151 go back), Pal Park from Gen 3 to Gen 4, Poké Transfer from Gen 4 to Gen 5, and Poké Transporter and Pokémon Bank from Gen 5 (or the 3DS Virtual Console Gen 1 and 2 games) to HOME. A Pokémon can pass through several of your games, for example Emerald → Pal Park → Platinum → Poké Transfer → Black 2. Each step says what it needs: two systems, a DS with a GBA slot, a 3DS, the National Dex or the Hall of Fame.
- **PC boxes.** Your boxes laid out in dex order with each generation's box size (20 per box in Gen 1 and 2, 30 in 6 × 5 from Gen 3 and in HOME), optional form slots and a choice of starting box. Tap a slot to mark it boxed; each Pokémon's detail panel shows its box, row and column.
- **Route plan.** Catches are grouped by place and ordered by story progress, with copy counts ("×3" means catch three and evolve the extras). Shedinja doesn't cost an extra Nincada, and one-time gifts show how many you'll need to breed. In Gen 1, where there are no eggs, a one-time gift covers one Pokémon only, so the plan sends the rest of the family to your other games.
- **Where I am now.** Pick your badge count to see what you can get now, dim what comes later, and optionally hide it. Field moves and key items are ticked from your badges and can be changed.
- **Catch right now.** Uses your device clock and each game's own rules: morning, day and night in Gen 2 (night from 18:00) and Gen 4 (night from 20:00), the four seasons in Gen 5 (spring in January, May and September, and so on), plus weekday events like Friday Lapras and the Bug-Catching Contest days.
- **Forms.** Unown letters (with each game's puzzles or chambers), Burmy and Wormadam cloaks, Shellos and Gastrodon seas, Rotom appliances, Giratina Origin, Shaymin Sky, Deoxys, Arceus plates, Spiky-eared Pichu, Basculin stripes, Deerling and Sawsbuck seasons, the Forces of Nature, Kyurem, Keldeo and Genesect, each with how to get it in the selected game and whether it can stay in a box.
- **English and Spanish.** Pokémon, item, move and form names come from PokéAPI. Spanish place names are in `pipeline/l10n.py`, checked against WikiDex.
- **Sync.** Copy a short code or link with your progress and paste it on another device, or save and load it as a file.
- **Offline app.** Once loaded, the site works without internet for the games you've opened, and can be installed as an app (look for the "Install app" button, or your browser's install option).
- **In other games.** For each Pokémon, the detail panel shows which other games can get it, grouped by generation.

## Project layout

| Path | What it is |
|---|---|
| `pipeline/config.py` | Per-game and per-region settings: story stages, HM and rod stages, condition rules, form rules |
| `pipeline/l10n.py` | Spanish place names and sub-area labels |
| `pipeline/build_data.py` | PokéAPI CSVs → `generated/data/<game>.json` (structured, language-neutral) |
| `pipeline/build_sprites.py` | One sprite sheet per sprite set (one or two per generation, and one for HOME), forms included |
| `pipeline/validate.py` | Data checks that fail the build: species and area counts, stages, names in both languages, every condition and method handled, sprites present |
| `pipeline/build_site.py` | Assembles `site/`: pages, data, sprites, icons, manifest and the offline service worker |
| `pipeline/build_single.py`, `pipeline/bundle.py` | One self-contained `dist/living-dex.html` with everything inlined |
| `scripts/availability.mjs` | Runs the planner over every game to fill the "In other games" chips |
| `src/index.html`, `src/css/app.css` | Page shell and styles |
| `src/js/planner.js` | Planner logic (pure, no DOM): best route, plan groups, catch-right-now, forms |
| `src/js/text.js`, `src/js/i18n.js` | Sentences and interface strings in English and Spanish |
| `src/js/store.js`, `src/js/progress-code.js` | Saved state and sync codes |
| `src/js/boxes.js` | PC box layout and slot positions (pure) |
| `src/js/multi.js` | The transfer chain: picks the best game for each Pokémon across the games you own and the moves to get it to your main game (pure) |
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

- Story stages ("≈ badges needed") are estimates, set in `pipeline/config.py`. In Black and White, wild Pokémon far above the gym levels (the post-game dark grass and rippling water in early places) count as later in the story.
- Spanish place names follow the Spanish (Spain) releases of each game.
- PokéAPI's encounter data for Gen 1 to Gen 5 is close to complete; Gen 6 and later games (X and Y onward) are not included yet, so HOME lists species from #650 on as not obtainable with your games.
- Events, the Pokéwalker, Pokémon Dream Radar and Colosseum/XD are listed as external requirements rather than planned.
- Sprites and Pokémon names are Nintendo / Creatures / GAME FREAK property. This is a non-commercial fan project; keep the footer credit.
