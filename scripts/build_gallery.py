#!/usr/bin/env python3
"""Genera le miniature della galleria e il manifesto gallery.json.

Scansiona assets/<cartelle per anno>, crea miniature in assets/thumbs/<anno>/
(lato lungo max 640px) e scrive gallery.json con, per ogni anno, l'elenco delle
foto { full, thumb } e una cover. Le foto piene restano gli originali (usate solo
nel visualizzatore a schermo intero). Rilanciabile: rigenera solo ciò che manca.
"""
import json
import os
import re

from PIL import Image, ImageOps

ASSETS = 'assets'
THUMBS = os.path.join(ASSETS, 'thumbs')
MAX_SIDE = 640
QUALITY = 75
EXTS = ('.jpg', '.jpeg', '.png')


def year_of(folder_name):
    m = re.search(r'(20\d{2})', folder_name)
    return m.group(1) if m else folder_name


def make_thumb(src, dst):
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        im = im.convert('RGB')
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
        im.save(dst, 'JPEG', quality=QUALITY, optimize=True, progressive=True)


def main():
    years = []
    for entry in sorted(os.listdir(ASSETS)):
        folder = os.path.join(ASSETS, entry)
        if not os.path.isdir(folder) or entry == 'thumbs':
            continue
        year = year_of(entry)
        files = sorted(
            f for f in os.listdir(folder)
            if f.lower().endswith(EXTS) and not f.lower().startswith('thumbs.db')
        )
        if not files:
            continue
        photos = []
        for f in files:
            src = os.path.join(folder, f)
            thumb_name = os.path.splitext(f)[0] + '.jpg'
            dst = os.path.join(THUMBS, year, thumb_name)
            make_thumb(src, dst)
            photos.append({
                'full': f'{ASSETS}/{entry}/{f}',
                'thumb': f'{THUMBS}/{year}/{thumb_name}'.replace('\\', '/'),
            })
        years.append({
            'year': year,
            'count': len(photos),
            'cover': photos[0]['thumb'],
            'photos': photos,
        })
        print(f'  {year}: {len(photos)} foto')

    # più recenti in cima
    years.sort(key=lambda y: y['year'], reverse=True)
    with open('gallery.json', 'w', encoding='utf-8') as fp:
        json.dump({'years': years}, fp, ensure_ascii=False, indent=1)
    total = sum(y['count'] for y in years)
    print(f'gallery.json scritto: {len(years)} anni, {total} foto totali')


if __name__ == '__main__':
    main()
