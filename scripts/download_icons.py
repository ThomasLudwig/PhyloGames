#!/usr/bin/env python3
"""
Download group images listed in a CSV to `static/icons/` and record attributions.
CSV columns: order,image_url,license,author (header required)

Usage:
  python scripts/download_icons.py --csv icons_to_download.csv --outdir static/icons
  python scripts/download_icons.py --csv icons_to_download.csv --outdir static/icons --force

If `--csv` is absent, the script will create a template named `icons_to_download.csv` containing unique orders found in
`species_taxonomy_with_ott.csv` (no URLs filled) so you can add URLs and metadata.
"""

import argparse
import csv
import os
import sys
import unicodedata
import urllib.request
import urllib.parse
import mimetypes
from pathlib import Path


def normalize(name: str) -> str:
    s = name.lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    # replace non-alnum by dash
    s = ''.join(ch if ch.isalnum() else '-' for ch in s)
    # collapse dashes
    while '--' in s:
        s = s.replace('--', '-')
    s = s.strip('-')
    if not s:
        return 'generic'
    return s


def ensure_outdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def guess_extension(url, headers):
    # Try from url path
    parsed = urllib.parse.urlparse(url)
    root, ext = os.path.splitext(parsed.path)
    if ext and len(ext) <= 5:
        return ext.lower()
    # Fallback to content-type header
    ctype = headers.get('Content-Type') or headers.get('content-type')
    if ctype:
        ext = mimetypes.guess_extension(ctype.split(';')[0].strip())
        if ext:
            return ext
    return '.bin'


def download(url, dest_path, timeout=30):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            headers = r.headers
            # if dest_path has no extension, try to guess
            if dest_path.suffix == '':
                ext = guess_extension(url, headers)
                dest_path = dest_path.with_suffix(ext)
            # write bytes
            with open(dest_path, 'wb') as f:
                f.write(data)
            return dest_path, headers
    except Exception as e:
        return None, str(e)


def create_template(csv_path: Path):
    # extract unique orders from species_taxonomy_with_ott.csv if available
    src = Path('species_taxonomy_with_ott.csv')
    orders = set()
    if src.exists():
        with open(src, encoding='utf-8') as f:
            header = f.readline()
            for line in f:
                cols = line.strip().split(',')
                if len(cols) >= 6:
                    ord_name = cols[5].strip()
                    if ord_name:
                        orders.add(ord_name)
    orders = sorted(orders)
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['order', 'image_url', 'license', 'author'])
        for o in orders:
            writer.writerow([o, '', '', ''])
    print(f'Template CSV created at {csv_path}. Fill the image_url and metadata then re-run the script.')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', default='icons_to_download.csv', help='CSV with columns order,image_url,license,author')
    p.add_argument('--outdir', default='static/icons', help='Output directory for downloaded images')
    p.add_argument('--force', action='store_true', help='Overwrite existing files')
    p.add_argument('--timeout', type=int, default=30, help='Timeout for downloads (seconds)')
    args = p.parse_args()

    csv_path = Path(args.csv)
    outdir = Path(args.outdir)
    ensure_outdir(outdir)

    if not csv_path.exists():
        create_template(csv_path)
        sys.exit(0)

    attributions = []

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            order = (row.get('order') or '').strip()
            url = (row.get('image_url') or '').strip()
            license = (row.get('license') or '').strip()
            author = (row.get('author') or '').strip()

            if not order:
                print(f'Row {i}: missing order, skipping')
                continue

            key = normalize(order)
            if not url:
                print(f'Row {i} ({order}): no URL, skipping')
                continue

            # determine tentative filename
            parsed = urllib.parse.urlparse(url)
            _, ext = os.path.splitext(parsed.path)
            if ext and len(ext) <= 5:
                filename = f"{key}{ext.lower()}"
            else:
                # unknown ext, try .png then guess after download
                filename = f"{key}"

            dest = outdir / filename
            if dest.exists() and not args.force:
                print(f'{order}: file exists as {dest.name}, skipping (use --force to overwrite)')
                attributions.append((order, dest.name, url, license, author))
                continue

            print(f'{order}: downloading {url} -> {dest.name}')
            saved, info = download(url, dest, timeout=args.timeout)
            if saved:
                print(f'  saved as {saved.name}')
                attributions.append((order, saved.name, url, license, author))
            else:
                print(f'  ERROR downloading {order}: {info}')

    # write ATTRIBUTIONS.md
    attr_file = outdir / 'ATTRIBUTIONS.md'
    with open(attr_file, 'w', encoding='utf-8') as f:
        f.write('# Icon Attributions\n\n')
        f.write('| order | filename | source_url | license | author |\n')
        f.write('|---|---|---|---|---|\n')
        for order, filename, url, license, author in attributions:
            f.write(f'| {order} | {filename} | {url} | {license} | {author} |\n')

    print(f'Download complete. Attributions saved to {attr_file}')


if __name__ == '__main__':
    main()
