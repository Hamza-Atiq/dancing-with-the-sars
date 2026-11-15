"""Draw the three charts used in README.md as standalone SVG files.

Every number is read from result files, none is typed here:
  docs/story/story.json      built by scripts/site_assets.py
  data/rtc/rtc_patch.json    Sentinel-1 patch brightness (scripts/s1_rtc.py; local, optional)
Output: previews/readme_controls.svg, previews/readme_year.svg, previews/readme_brightness.svg

Run: C:/Users/HP/anaconda3/python.exe scripts/readme_figures.py
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'previews'
BG, INK, DIM, HOT, BLUE = '#0b1216', '#e8eef0', '#8fa0a8', '#f0a63a', '#86b7c9'
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
FONT = 'font-family="Segoe UI,Helvetica,Arial,sans-serif"'


def d8(s):
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def text(x, y, s, size=15, fill=INK, anchor='start', weight=400):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {FONT}>{s}</text>'


def line(x1, y1, x2, y2, stroke=DIM, w=1, op=1.0):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}" stroke-opacity="{op}"/>'


def circle(x, y, r, fill, op=1.0, stroke='none'):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}"/>'


def save(name, w, h, title, parts):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
           f'<title>{title}</title><rect width="{w}" height="{h}" fill="{BG}"/>' + ''.join(parts) + '</svg>')
    (OUT / name).write_text(svg, encoding='utf-8')
    print(name, len(svg) // 1024, 'KB')


def controls(D):
    k, W, H, L, R, base = D['key_pair'], 1000, 330, 40, 70, 270
    top = 6.2
    x = lambda v: L + v / top * (W - L - R)
    p = [text(L, 34, f"Same 12 days, {k['controls_n']} other slopes and the Langtang patch", 20, INK, weight=600),
         text(L, 58, 'Size of the step in the 14 to 26 July 2026 radar pair. Each dot is one slope.', 14, DIM),
         line(L, base, W - R, base)]
    for t in range(7):
        p += [line(x(t), base, x(t), base + 6), text(x(t), base + 26, f'{t} cm' if t == 6 else str(t), 14, DIM, 'middle')]
    counts = {}
    for v in D['controls_cm']:
        counts[round(v / 0.06)] = counts.get(round(v / 0.06), 0) + 1
    step = min(6.4, (base - 7 - 80) / max(1, max(counts.values()) - 1))   # tallest column stops below the subtitle
    bins = {}
    for v in D['controls_cm']:
        b = round(v / 0.06)
        bins[b] = bins.get(b, 0) + 1
        p.append(circle(x(b * 0.06), base - 7 - (bins[b] - 1) * step, min(2.7, step / 2.2), BLUE, 0.75))
    cm = k['control_max_cm']
    p += [line(x(cm), base - 50, x(cm), base, DIM), text(x(cm) + 7, base - 40, f'largest of the others: {cm:.1f} cm', 14, DIM),
          circle(x(k['langtang_cm']), base - 13, 11, HOT),
          text(x(k['langtang_cm']), base - 36, 'Langtang patch', 14, INK, 'middle'),
          text(x(k['langtang_cm']), base - 56, f"{k['langtang_cm']:.1f} cm", 24, HOT, 'middle', 600)]
    save('readme_controls.svg', W, H, f"{k['controls_n']} comparable slopes stay below {cm:.1f} cm; the Langtang patch shows {k['langtang_cm']:.1f} cm", p)


def year(D):
    rows, W, H, L, R, T, B = D['rows'], 1000, 360, 50, 20, 90, 50
    t0, t1 = d8(rows[0]['start']), d8(rows[-1]['end'])
    col = d8(D['collapse_utc'][:10].replace('-', ''))
    x = lambda d: L + (d - t0).days / (t1 - t0).days * (W - L - R)
    y = lambda v: T + (6.5 - v) / 6.5 * (H - T - B)
    n_read = sum(1 for r in rows if r['resolved'])
    p = [text(L, 34, f'One year on the patch: {len(rows)} radar pairs, {n_read} readable', 20, INK, weight=600),
         text(L, 58, 'Filled: a reading we trust. Hollow: unreadable, drawn at zero so no pair is hidden.', 14, DIM),
         f'<rect x="{x(date(2026, 7, 27)):.1f}" y="{T}" width="{x(date(2026, 8, 10)) - x(date(2026, 7, 27)):.1f}" height="{H - T - B}" fill="{INK}" fill-opacity="0.1"/>']
    for v in (0, 2, 4, 6):
        p += [line(L, y(v), W - R, y(v), DIM, 1, 0.45), text(L - 8, y(v) + 5, f'{v} cm' if v == 6 else str(v), 13, DIM, 'end')]
    m = date(2025, 12, 1)
    while m < t1:
        p += [line(x(m), H - B, x(m), H - B + 6), text(x(m), H - B + 24, MONTHS[m.month - 1] + (' 2026' if m.month == 1 else ''), 13, DIM)]
        m = date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    for r in rows:
        cx = (x(d8(r['start'])) + x(d8(r['end']))) / 2
        v, key = min(6.3, abs(r['cm'])), r['pair'] == D['key_pair']['pair']
        if r['resolved']:
            p += [line(cx, y(0), cx, y(v), HOT if key else INK, 3 if key else 1.5), circle(cx, y(v), 8 if key else 4.5, HOT if key else INK)]
            if key:
                p.append(text(cx - 14, y(v) + 5, f'14 to 26 July: {v:.1f} cm', 15, INK, 'end', 600))
        else:
            p.append(circle(cx, y(0), 4, 'none', 1, DIM))
    p += [line(x(col), T - 10, x(col), H - B, HOT, 2), text(x(col) + 7, T + 2, 'collapse', 14, HOT),
          text(x(date(2026, 8, 3)), T - 8, 'no data', 12, DIM, 'middle'), text(x(date(2026, 5, 1)), y(0) - 14, 'unreadable', 13, DIM, 'middle')]
    save('readme_year.svg', W, H, 'Step on the patch in every radar pair, November 2025 to October 2026', p)


def brightness(D):
    rf = ROOT / 'data/rtc/rtc_patch.json'
    if not rf.exists():
        print('readme_brightness.svg skipped: data/rtc/rtc_patch.json not present')
        return
    R = [r for r in json.loads(rf.read_text()) if 'start' in r and r.get('change_db') is not None]
    tracks = {}
    for r in R:
        s = tracks.setdefault(r['track'], {})
        s[r['start']], s[r['end']] = r['patch_db_start'], r['patch_db_end']
    W, H, L, Rm, T, B = 1000, 360, 60, 30, 90, 50
    alld = sorted(d for s in tracks.values() for d in s)
    t0, t1 = d8(alld[0]), d8(alld[-1])
    col = d8(D['collapse_utc'][:10].replace('-', ''))
    lo, hi = -20.0, -4.0
    x = lambda d: L + (d - t0).days / (t1 - t0).days * (W - L - Rm)
    y = lambda v: T + (hi - v) / (hi - lo) * (H - T - B)
    acr = D['sentinel1_brightness']['across']
    drops = ' and '.join(f"{abs(a['change_db']):.1f} dB" for a in acr)
    p = [text(L, 34, f'Sentinel-1 brightness of the patch: ordinary before, {drops} darker after', 20, INK, weight=600),
         text(L, 58, 'Median radar brightness of the same patch pixels on the two tracks that can see it, 2026.', 14, DIM)]
    for v in (-20, -16, -12, -8, -4):
        p += [line(L, y(v), W - Rm, y(v), DIM, 1, 0.45), text(L - 8, y(v) + 5, f'{v} dB' if v == -4 else str(v), 13, DIM, 'end')]
    m = date(t0.year, t0.month, 1)
    while m < t1:
        if m >= t0:
            p += [line(x(m), H - B, x(m), H - B + 6), text(x(m), H - B + 24, MONTHS[m.month - 1], 13, DIM)]
        m = date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    for i, (name, s) in enumerate(sorted(tracks.items())):
        c = (BLUE, INK)[i % 2]
        pts = [(x(d8(k)), y(max(lo, min(hi, v)))) for k, v in sorted(s.items())]
        p.append(f'<polyline fill="none" stroke="{c}" stroke-width="2" points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + '"/>')
        p += [circle(a, b, 4, c) for a, b in pts]
        p += [line(W - 250, 78 + i * 20 - 5, W - 225, 78 + i * 20 - 5, c, 2), text(W - 218, 78 + i * 20, 'track ' + name, 13, DIM)]
    p += [line(x(col), T - 10, x(col), H - B, HOT, 2), text(x(col) + 7, T + 2, 'collapse', 14, HOT)]
    save('readme_brightness.svg', W, H, 'Radar brightness of the patch on two Sentinel-1 tracks, May to November 2026', p)


if __name__ == '__main__':
    D = json.loads((ROOT / 'docs/story/story.json').read_text())
    controls(D)
    year(D)
    brightness(D)
