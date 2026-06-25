#!/usr/bin/env python3
"""
Fill `icons_to_download.csv` by searching Wikimedia Commons for a representative image per order.
Updates rows with empty `image_url` using the first suitable File found in namespace 6.

Usage:
  python scripts/fill_icons_wikimedia.py --csv icons_to_download.csv

Note: Uses the Wikimedia Commons API (no external dependencies).
"""
import argparse
import csv
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_ENDPOINT = 'https://commons.wikimedia.org/w/api.php'
DEFAULT_THUMB_WIDTH = 220


def commons_search_file(order, limit=5, thumb_width=DEFAULT_THUMB_WIDTH):
    # search files (namespace 6) with the order name and request thumbnail info
    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrnamespace': 6,
        'gsrsearch': order,
        'gsrlimit': str(limit),
        'prop': 'imageinfo',
        'iiprop': 'url|extmetadata',
        'iiurlwidth': str(thumb_width)
    }
    url = API_ENDPOINT + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'ArbrePhylo/1.0 (contact)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def choose_best_image(api_json):
    if 'query' not in api_json:
        return None
    pages = api_json['query'].get('pages', {})
    # iterate pages in arbitrary order, prefer those with thumbnail info + license
    for pid, page in pages.items():
        iinfo = page.get('imageinfo')
        if not iinfo:
            continue
        info = iinfo[0]
        thumburl = info.get('thumburl')
        url = thumburl or info.get('url')
        em = info.get('extmetadata', {})
        license = em.get('LicenseShortName', {}).get('value') if em.get('LicenseShortName') else None
        artist = em.get('Artist', {}).get('value') if em.get('Artist') else None
        credit = em.get('Credit', {}).get('value') if em.get('Credit') else None
        artist_text = artist or credit
        if url:
            return url, license or '', artist_text or ''
    return None


def update_csv(csv_path: Path):
    rows = []
    changed = False
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    for idx, row in enumerate(rows):
        order = (row.get('order') or '').strip()
        if not order:
            continue
        if (row.get('image_url') or '').strip():
            continue
        print(f'Searching Commons for: {order}')
        # retry with exponential backoff on failures (handle 429)
        max_attempts = 6
        delay = 2
        for attempt in range(1, max_attempts + 1):
            try:
                # gentle request pacing
                time.sleep(random.uniform(0.5, 1.5))
                api = commons_search_file(order, limit=5)
                pick = choose_best_image(api)
                if pick:
                    url, license, author = pick
                    print(f'  Found: {url} (license={license})')
                    row['image_url'] = url
                    row['license'] = license
                    row['author'] = author
                    changed = True
                    # persist CSV immediately to avoid losing progress
                    tmp = csv_path.with_suffix('.tmp.csv')
                    with open(tmp, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for r in rows:
                            writer.writerow(r)
                    tmp.replace(csv_path)
                    print(f'  Wrote progress to {csv_path}')
                else:
                    print('  No suitable image found')
                break
            except urllib.error.HTTPError as e:
                retry_after = e.headers.get('Retry-After') if e.headers else None
                print(f'  Attempt {attempt} error: HTTP {e.code}')
                if e.code == 429 and attempt < max_attempts:
                    wait = int(retry_after) if retry_after and retry_after.isdigit() else delay * (2 ** (attempt - 1))
                    wait += random.uniform(1, 3)
                    print(f'  Rate limited, sleeping {wait:.1f}s then retrying...')
                    time.sleep(wait)
                    continue
                else:
                    print('  Error while searching:', e)
                    break
            except urllib.error.URLError as e:
                print(f'  Attempt {attempt} error: URL error {e.reason}')
                if attempt < max_attempts:
                    wait = delay * (2 ** (attempt - 1)) + random.uniform(1, 3)
                    print(f'  Sleeping {wait:.1f}s then retrying...')
                    time.sleep(wait)
                    continue
                else:
                    print('  Error while searching:', e)
                    break
            except Exception as e:
                print(f'  Attempt {attempt} error: {e}')
                if attempt < max_attempts:
                    wait = delay * (2 ** (attempt - 1)) + random.uniform(1, 3)
                    print(f'  Sleeping {wait:.1f}s then retrying...')
                    time.sleep(wait)
                    continue
                else:
                    print('  Error while searching:', e)
                    break
        # be more gentle with API
        time.sleep(2)

    if changed:
        # write to a temp file then replace
        tmp = csv_path.with_suffix('.tmp.csv')
        with open(tmp, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        tmp.replace(csv_path)
        print(f'Updated {csv_path} with found image URLs.')
    else:
        print('No updates made to CSV.')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', default='icons_to_download.csv')
    args = p.parse_args()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f'{csv_path} not found')
        return
    update_csv(csv_path)

if __name__ == '__main__':
    main()
