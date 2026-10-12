"""Thin, cached reader for PokéAPI's CSV source data (data/v2/csv in the PokeAPI/pokeapi repo)."""
import csv
import functools
import os

EN, ES = '9', '7'


class PokeAPI:
    def __init__(self, csv_dir):
        if not os.path.isfile(os.path.join(csv_dir, 'pokemon_species.csv')):
            raise SystemExit(f'PokéAPI CSV folder not found: {csv_dir}')
        self.dir = csv_dir

    @functools.lru_cache(maxsize=None)
    def rows(self, name):
        with open(os.path.join(self.dir, name + '.csv'), encoding='utf-8') as f:
            return tuple(csv.DictReader(f))

    def by_id(self, name, key='id'):
        return {r[key]: r for r in self.rows(name)}

    def names(self, table, id_col, field='name', langs=(EN, ES)):
        """{id: {'en': ..., 'es': ...}} for a *_names table."""
        out = {}
        lang_key = {EN: 'en', ES: 'es'}
        for r in self.rows(table):
            if r['local_language_id'] in langs:
                out.setdefault(r[id_col], {})[lang_key[r['local_language_id']]] = r[field]
        return out
