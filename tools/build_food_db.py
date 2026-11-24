#!/usr/bin/env python3
"""Baut die Offline-Lebensmittel-Datenbank für Fitness-Multiversum.

Quellen:
  * Open Food Facts (ODbL) – alle Produkte, die in Deutschland, Österreich oder der Schweiz verkauft werden
  * Schweizer Nährwertdatenbank (BLV, Quellenangabe erforderlich) – Grundnahrungsmittel

Ausgabe (Ordner out/):
  foods-N.tsv.gz  – Produkte, eine Zeile pro Produkt (Spalten siehe COLS), nach Beliebtheit sortiert
  generic.tsv.gz  – Grundnahrungsmittel
  meta.json       – Datum, Anzahl, Dateien, Quellen

Aufruf: build_food_db.py [--off DATEI_ODER_URL] [--ch DATEI_ODER_URL] [--max N]
"""
import argparse, csv, gzip, io, json, os, re, sys, time, urllib.request

OFF_URL = 'https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz'
CH_URL = 'https://naehrwertdaten.ch/wp-content/uploads/2023/08/Schweizer_Nahrwertdatenbank.xlsx'
COUNTRIES = ('en:germany', 'en:austria', 'en:switzerland')
COLS = ['code', 'name', 'brand', 'kcal', 'p', 'c', 'f', 'sugar', 'fiber', 'salt', 'sg', 'sl', 'ns', 'nova', 'rank']
PART_LINES = 120000
DE_WORDS = re.compile(r"[äöüß]|\b(mit|und|ohne|aus|für|vollkorn\w*|schoko\w*|milch\w*|käse\w*|brot\w*|brötchen|wurst\w*|joghurt|quark|nudeln|sahne|butter\w*|kartoffel\w*|hähnchen\w*|huhn|rind\w*|schwein\w*|fisch\w*|gemüse\w*|obst|apfel\w*|saft\w*|getränk\w*|zucker\w*|mehl|haferflocken|müsli|keks\w*|kuchen|fruchtgummi|gummibär\w*|bier|mineralwasser|frischkäse|aufschnitt|schinken|salami|senf|soße|sauce hollandaise|gewürz\w*|nuss\w*|erdnuss\w*|riegel|eis|feinkost|salat\w*|suppe|tee|kaffee|leicht|natur|klassik|original)\b", re.I)
OTHER_WORDS = re.compile(r"[éèêàâçùûôîœ]|\b(au|aux|avec|sans|de|du|des|le|la|les|et|chocolat|lait|noir|blé|fromage|pain|sucre|jus|fraise|pomme|poulet|beurre|biscuits?|céréales|nature|the|of|with|and|con|di|della|y|sin|leche|met|zonder|en)\b", re.I)

def num(v):
    if v is None: return None
    s = str(v).strip().replace(',', '.')
    if not s: return None
    s = re.sub(r'^[<>~≈]\s*', '', s)
    try: x = float(s)
    except ValueError: return None
    return x if x == x and abs(x) < 1e6 else None

def fmt(x, d=1):
    if x is None: return ''
    r = round(x, d)
    return str(int(r)) if r == int(r) else str(r)

def clean(s, n=90):
    return re.sub(r'\s+', ' ', str(s or '').replace('\t', ' ')).strip()[:n]

def norm(s):
    s = s.lower()
    for a, b in (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss')): s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

def opener(src):
    if src.startswith('http'):
        req = urllib.request.Request(src, headers={'User-Agent': 'FitnessMultiversum-DB/1.0 (privat)'})
        return urllib.request.urlopen(req, timeout=120)
    return open(src, 'rb')

def plausible(kcal, p, c, f, alc):
    if kcal is None or p is None or c is None or f is None: return False
    if not (0 <= kcal <= 950 and 0 <= p <= 100 and 0 <= c <= 100 and 0 <= f <= 100): return False
    if p + c + f > 105: return False
    if alc and alc > 0: return True
    est = 4 * p + 4 * c + 9 * f
    return abs(est - kcal) <= max(60, 0.45 * kcal)

def read_off(src, max_n):
    csv.field_size_limit(1 << 30)
    raw = opener(src)
    txt = io.TextIOWrapper(gzip.GzipFile(fileobj=raw) if src.endswith('.gz') or src.startswith('http') else raw, encoding='utf-8', errors='replace', newline='')
    rd = csv.reader(txt, delimiter='\t', quoting=csv.QUOTE_NONE)
    head = next(rd); ix = {h: i for i, h in enumerate(head)}
    def g(row, k):
        i = ix.get(k)
        return row[i] if i is not None and i < len(row) else ''
    out, seen, n, t0 = [], set(), 0, time.time()
    for row in rd:
        n += 1
        if n % 500000 == 0: print(f'  … {n:,} Zeilen gelesen, {len(out):,} übernommen ({time.time() - t0:.0f} s)', flush=True)
        ct = g(row, 'countries_tags')
        if not any(c in ct for c in COUNTRIES): continue
        name = clean(g(row, 'product_name_de') or g(row, 'product_name') or g(row, 'generic_name'))
        if len(name) < 2: continue
        kcal = num(g(row, 'energy-kcal_100g'))
        if kcal is None:
            kj = num(g(row, 'energy_100g')) or num(g(row, 'energy-kj_100g'))
            kcal = kj / 4.184 if kj is not None else None
        p, c, f = num(g(row, 'proteins_100g')), num(g(row, 'carbohydrates_100g')), num(g(row, 'fat_100g'))
        if not plausible(kcal, p, c, f, num(g(row, 'alcohol_100g'))): continue
        code = re.sub(r'\D', '', g(row, 'code'))
        brand = clean(g(row, 'brands').split(',')[0], 40)
        key = (norm(name), norm(brand), round(kcal))
        if key in seen: continue
        seen.add(key)
        sq = num(g(row, 'serving_quantity'))
        sl = clean(re.sub(r'\s*\(.*?\)', '', g(row, 'serving_size')), 24) if sq and 0 < sq <= 2000 else ''
        scans = num(g(row, 'unique_scans_n')) or 0
        comp = num(g(row, 'completeness')) or 0
        ns = g(row, 'nutriscore_grade').strip().lower()
        nova = g(row, 'nova_group').strip()
        lang = g(row, 'lang').strip().lower()
        tags = [x for x in ct.split(',') if x]
        dach_only = bool(tags) and all(x in COUNTRIES for x in tags)
        de_n, ot_n = len(DE_WORDS.findall(name)), len(OTHER_WORDS.findall(name))
        mult = 1.0
        if g(row, 'product_name_de') or lang == 'de': mult *= 10
        if de_n > ot_n: mult *= 10
        elif ot_n > de_n: mult *= 0.15
        if dach_only: mult *= 3
        if code.startswith(('40', '41', '42', '43', '440')): mult *= 2
        prio = (scans + 1) * mult
        out.append((prio, comp, [code, name, brand, fmt(kcal, 0), fmt(p), fmt(c), fmt(f), fmt(num(g(row, 'sugars_100g'))), fmt(num(g(row, 'fiber_100g'))), fmt(num(g(row, 'salt_100g')), 2), fmt(sq, 0) if sl else '', sl, ns if ns in 'abcde' and len(ns) == 1 else '', nova if nova in ('1', '2', '3', '4') else '']))
    print(f'Open Food Facts: {n:,} Zeilen, {len(out):,} passende Produkte (behalte max. {max_n:,})', flush=True)
    out.sort(key=lambda x: (-x[0], -x[1]))
    if max_n and len(out) > max_n: out = out[:max_n]
    rows = []
    for r, (_, _, rec) in enumerate(out): rows.append(rec + [str(r)])
    return rows

def read_ch(src):
    try:
        import openpyxl
    except ImportError:
        print('openpyxl fehlt – Schweizer Datenbank übersprungen'); return []
    data = opener(src).read()
    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hi = None
    for i, r in enumerate(rows[:30]):
        cells = [str(x or '').lower() for x in r]
        if any('name' == x.strip() or x.startswith('name') for x in cells) and any('kcal' in x for x in cells): hi = i; break
    if hi is None: raise RuntimeError('Kopfzeile nicht gefunden')
    head = [str(x or '').lower().strip() for x in rows[hi]]
    def col(*keys, exclude=()):
        for i, h in enumerate(head):
            if any(k in h for k in keys) and not any(e in h for e in exclude): return i
        return None
    ci = {'name': col('name'), 'kcal': col('kcal'), 'p': col('protein', 'eiweiss'), 'c': col('kohlenhydrat', exclude=('ableitung', 'quelle')), 'f': col('fett, total', 'fett total', 'fett'),
          'sugar': col('zucker'), 'fiber': col('nahrungsfaser', 'ballaststoff'), 'salt': col('salz')}
    if ci['name'] is None or ci['kcal'] is None: raise RuntimeError('Spalten nicht gefunden: ' + repr(head[:12]))
    out = []
    for r in rows[hi + 1:]:
        v = lambda k: num(r[ci[k]]) if ci[k] is not None and ci[k] < len(r) else None
        name = clean(r[ci['name']] if ci['name'] < len(r) else '')
        kcal, p, c, f = v('kcal'), v('p'), v('c'), v('f')
        if len(name) < 2 or kcal is None: continue
        p, c, f = p or 0, c or 0, f or 0
        out.append(['', name, '', fmt(kcal, 0), fmt(p), fmt(c), fmt(f), fmt(v('sugar')), fmt(v('fiber')), fmt(v('salt'), 2), '', '', '', '', str(len(out))])
    print(f'Schweizer Nährwertdatenbank: {len(out):,} Lebensmittel', flush=True)
    return out

def write_gz(path, rows):
    with gzip.open(path, 'wt', encoding='utf-8', compresslevel=9) as f:
        for r in rows: f.write('\t'.join(r) + '\n')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--off', default=OFF_URL); ap.add_argument('--ch', default=CH_URL)
    ap.add_argument('--max', type=int, default=300000); ap.add_argument('--out', default='out')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    meta = {'date': time.strftime('%Y-%m-%d'), 'cols': COLS, 'parts': [], 'count': 0, 'generic': None, 'genericCount': 0,
            'sources': ['Open Food Facts (ODbL) – openfoodfacts.org', 'Schweizer Nährwertdatenbank (BLV) – naehrwertdaten.ch']}
    try:
        ch = read_ch(a.ch)
        if ch: write_gz(os.path.join(a.out, 'generic.tsv.gz'), ch); meta['generic'] = 'generic.tsv.gz'; meta['genericCount'] = len(ch)
    except Exception as e:
        print('Schweizer Datenbank übersprungen:', e, flush=True)
    rows = read_off(a.off, a.max)
    for i in range(0, len(rows), PART_LINES):
        fn = f'foods-{i // PART_LINES + 1}.tsv.gz'
        write_gz(os.path.join(a.out, fn), rows[i:i + PART_LINES])
        meta['parts'].append({'file': fn, 'bytes': os.path.getsize(os.path.join(a.out, fn))})
    meta['count'] = len(rows)
    meta['bytes'] = sum(p['bytes'] for p in meta['parts']) + (os.path.getsize(os.path.join(a.out, 'generic.tsv.gz')) if meta['generic'] else 0)
    with open(os.path.join(a.out, 'meta.json'), 'w', encoding='utf-8') as f: json.dump(meta, f, ensure_ascii=False, indent=1)
    print(json.dumps(meta, ensure_ascii=False, indent=1))
    if len(rows) < 1000: sys.exit('Zu wenige Produkte – Abbruch')

if __name__ == '__main__':
    main()
