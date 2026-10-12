"""Build pipeline for the Living Dex Planner.

Modules:
    pokeapi     -- reads PokéAPI's CSV source data
    config      -- per-game and per-region settings (stages, methods, conditions, forms)
    l10n        -- Spanish place names and sub-area labels that PokéAPI does not provide
    build_data  -- writes generated/data/<game>.json
    build_sprites -- writes generated/sprites/<set>.webp
    validate    -- data checks that fail the build
    build_site  -- assembles the deployable site/
    build_single -- assembles the single-file offline page
"""
