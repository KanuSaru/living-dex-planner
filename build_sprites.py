"""Pack the 493 Platinum sprites from the PokeAPI/sprites repo into one WebP sheet (25 columns, 80x80 cells)."""
import sys
from PIL import Image

src = sys.argv[1].rstrip('/') + '/'   # .../sprites/pokemon/versions/generation-iv/platinum
out = sys.argv[2] if len(sys.argv) > 2 else 'sheet.webp'
COLS, CELL, COUNT = 25, 80, 493

sheet = Image.new('RGBA', (COLS * CELL, ((COUNT + COLS - 1) // COLS) * CELL), (0, 0, 0, 0))
for i in range(1, COUNT + 1):
    im = Image.open(f'{src}{i}.png').convert('RGBA')
    sheet.paste(im, (((i - 1) % COLS) * CELL, ((i - 1) // COLS) * CELL))
sheet.save(out, lossless=True, quality=100, method=6)
print('wrote', out)
