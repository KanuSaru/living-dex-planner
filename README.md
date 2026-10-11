# Platinum Living Dex

A single-page planner for completing a living dex in Pokémon Platinum. It shows every place a Pokémon appears (levels, morning/day/night rates, special conditions) and its evolution family, and builds a route plan that picks the earliest way to get each one by catching, evolving or breeding.

## Files

| File | What it does |
|---|---|
| `build.sh` | Full rebuild: downloads the source data, then runs the three scripts below |
| `build_data.py` | Reads PokéAPI's CSV source data and writes `data.json` (Platinum encounters, evolutions valid in gen 4, names, types, Sinnoh dex numbers, estimated badge stage per area) |
| `build_sprites.py` | Packs the 493 Platinum sprites into one `sheet.webp` (25 columns × 80 px) |
| `template.html` | The page itself: HTML, CSS and the planner logic in plain JavaScript |
| `assemble.py` | Embeds `data.json` and `sheet.webp` into the template, producing one offline file `platinum-living-dex.html` |
| `build_site.py` | Builds the deployable website in `site/` (`index.html` + `sheet.webp`, with page metadata and favicon) |
| `.github/workflows/deploy.yml` | Rebuilds and publishes `site/` to GitHub Pages on each push and monthly |
| `data.json`, `sheet.webp`, `platinum-living-dex.html` | Prebuilt outputs |

## Rebuild

Needs Python 3, Pillow (`pip install pillow`) and git.

```bash
./build.sh
```

The script sparse-clones only what it needs from GitHub:
- `PokeAPI/pokeapi` → `data/v2/csv` (the same data pokeapi.co serves)
- `PokeAPI/sprites` → `sprites/pokemon/versions/generation-iv/platinum`

Then open `platinum-living-dex.html` in a browser. It works offline.

## Using the live API instead

The page uses PokéAPI's source CSVs rather than calling `https://pokeapi.co/api/v2/` at runtime. That makes it load instantly and work offline, and avoids hundreds of requests per visit. The same data is available from these endpoints:

- `/version/platinum` (id 14) and `/location-area/{id}` (`pokemon_encounters` → `version_details` filtered to `platinum`)
- `/pokemon-species/{id}` → `evolution_chain` → `/evolution-chain/{id}`
- `/pokedex/extended-sinnoh` for Platinum's regional dex numbers

## Notes

- Badge estimates (`LOC_STAGE`, `AREA_STAGE`, `METHOD_STAGE`, `COND` in `build_data.py`) are hand-written approximations of Platinum's story order; adjust them to taste.
- Evolution rules come from `pokemon_evolution.csv` rows introduced in Platinum or earlier, keeping only Sinnoh locations, so Leafeon, Glaceon, Magnezone and Probopass use their gen 4 methods.
- Boxed Pokémon and your starter choice are saved in the browser's localStorage.

## Deploy as a website

`./build.sh` writes a ready-to-host folder, `site/` (about 37 KB gzipped HTML plus a 328 KB sprite sheet). It is fully static, so any static host works.

**GitHub Pages (automatic rebuilds)**
1. Create a GitHub repository and push this folder to its `main` branch.
2. In the repository, open Settings → Pages and set Source to **GitHub Actions**.
3. The included workflow builds and deploys on every push, and once a month to pick up PokéAPI data fixes. The site appears at `https://<user>.github.io/<repo>/`.

**Netlify or Cloudflare Pages (no Git needed)**
Run `./build.sh` locally, then drag the `site/` folder into Netlify Drop (app.netlify.com/drop) or a Cloudflare Pages direct upload.

**Custom domain**
Add the domain in the host's settings and create the DNS record it asks for (a CNAME to `<user>.github.io`, or the record Netlify or Cloudflare shows). HTTPS is issued automatically.

Sprites and Pokémon names are Nintendo / GAME FREAK property. Fan sites like this are common, but keep it non-commercial and keep the footer credit.
