#!/usr/bin/env python3
"""Genera menu.json (copia di riserva same-origin) leggendo da Supabase.

Ordina le voci per ordine-categoria (tabella menu_categorie), poi per nome
categoria, poi per ordine/nome della voce — così la copia statica rispetta lo
stesso ordine del menù live. Usato sia in locale sia dal workflow GitHub.
"""
import json
import os
import urllib.request

URL = os.environ.get('SUPABASE_URL', 'https://nkxsnjogaslhkgtglkuw.supabase.co')
KEY = os.environ['SUPABASE_ANON_KEY']


def get(path):
    req = urllib.request.Request(URL + path, headers={'apikey': KEY})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    items = get('/rest/v1/menu_items?select=*')
    cats = get('/rest/v1/menu_categorie?select=nome,ordine')

    if not isinstance(items, list) or len(items) == 0:
        raise SystemExit('menu_items vuoto o non valido: non aggiorno menu.json')

    order = {c['nome']: c['ordine'] for c in cats}
    BIG = 10 ** 9
    items.sort(key=lambda x: (
        order.get(x['categoria'], BIG),
        x['categoria'],
        x.get('ordine') or 0,
        x['nome'],
    ))

    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f'menu.json scritto: {len(items)} voci, {len(order)} categorie')


if __name__ == '__main__':
    main()
