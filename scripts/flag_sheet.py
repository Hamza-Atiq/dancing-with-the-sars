"""Contact sheets of the eye-check chips (scripts/flag_check.py chips) -> data/flagcheck/chips/sheet_a.png, sheet_b.png."""
from pathlib import Path
from PIL import Image, ImageDraw

D = Path(__file__).resolve().parents[1] / 'data/flagcheck/chips'
fs = sorted(D.glob('[0-9][0-9]_*.png'))
W, H = 606, 300
for part, sub in (('a', fs[:10]), ('b', fs[10:])):
    sheet = Image.new('RGB', (2 * W + 10, 5 * (H + 22)), 'white'); d = ImageDraw.Draw(sheet)
    for k, f in enumerate(sub):
        x, y = (k % 2) * (W + 10), (k // 2) * (H + 22)
        sheet.paste(Image.open(f), (x, y + 20)); d.text((x + 4, y + 4), f.stem + '   left: Oct 2025   right: Oct 2026', fill='black')
    sheet.save(D / f'sheet_{part}.png')
print(len(fs))
