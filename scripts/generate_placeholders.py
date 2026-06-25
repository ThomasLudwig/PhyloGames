#!/usr/bin/env python3
"""
Generate simple SVG placeholder icons for each order listed in icons_to_download.csv.
Usage:
  python scripts/generate_placeholders.py --csv icons_to_download.csv --outdir static/icons
"""
import argparse
import csv
import os
import unicodedata
from pathlib import Path


def normalize(name: str) -> str:
    s = name.lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = ''.join(ch if ch.isalnum() else '-' for ch in s)
    while '--' in s:
        s = s.replace('--', '-')
    s = s.strip('-')
    if not s:
        return 'generic'
    return s


def make_svg(text: str, width=128, height=128, bg='#f0f0f0', fg='#333') -> str:
    # Escape basic XML characters
    esc = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="{bg}"/>
  <text x="50%" y="50%" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{fg}" text-anchor="middle" dominant-baseline="middle">{esc}</text>
</svg>'''
    return svg


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', default='icons_to_download.csv')
    p.add_argument('--outdir', default='static/icons')
    args = p.parse_args()

    csv_path = Path(args.csv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    orders = []
    if not csv_path.exists():
        print(f'CSV {csv_path} not found')
        return

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order = (row.get('order') or '').strip()
            if order:
                orders.append(order)

    created = 0
    for order in sorted(set(orders)):
        key = normalize(order)
        filename = outdir / f"{key}.svg"
        if filename.exists():
            print(f'{filename.name} exists, skipping')
            continue
        svg = make_svg(order)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg)
        created += 1
        print(f'Created {filename}')

    print(f'Done. Created {created} placeholder icons in {outdir}')

if __name__ == '__main__':
    main()
