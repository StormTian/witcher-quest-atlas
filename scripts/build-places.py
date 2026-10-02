"""Join frozen bilingual game-map labels, retaining provenance and explicit aliases."""
from pathlib import Path
import json, hashlib, re, unicodedata, xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
src = root / 'evidence/localization/tiva'
region = {'WO': ('w', 'white-orchard'), 'NO': ('v', 'velen'), 'VE': ('v', 'velen'),
          'SK': ('s', 'skellige'), 'KM': ('k', 'kaer-morhen'), 'TO': ('t', 'toussaint')}
aliases = {'Bald Mountain': 'Road to Bald Mountain',
           'Nilfgaardian Army Group': "Nilfgaardian Army Group 'Center' Camp",
           'Orphans of Crookback Bog': 'The Orphans of Crookback Bog',
           'Temerian Parison Hideout': 'Temerian Partisan Hideout',
           'Vacant estate': 'Moldavie Residence', 'Pali Gap Coast': 'The Pali Gap Coast',
           'Termes Palace Ruins': 'Termes Palace Runins', 'Lower City': 'San Sebastian',
           "The Gran'place": "Gran'Place", 'The Morhen Eye': 'Bastion',
           'Outpost ruins': 'Ruined Watchtower', 'Morhen Mine dam': 'Iron Mine',
           'The Lake House': 'Lakeside Hut'}
def norm(s):
    return ''.join(c.lower() for c in unicodedata.normalize('NFD', s) if c.isascii() and c.isalnum())

catalog = {}
for r in 'wvskt':
    en = json.loads((src / f'en-{r}.json').read_text())['signpost']['label']
    zh = json.loads((src / f'zh-simplified-{r}.json').read_text())['signpost']['label']
    catalog[r] = {norm(v): (v, zh[k], k) for k, v in en.items()}
# The bilingual source accidentally repeats Eldberg's label for Elverum.
catalog['s'][norm('Elverum Lighthouse')] = ('Elverum Lighthouse', '艾孚鲁灯塔', 'elverumLighthouse')
data = json.loads((root / 'dist/data.json').read_text())
roads = [(w.get('code'), p.findtext('name'))
         for w in ET.parse(root / 'evidence/upstream/Witcher3MapViewer/MapPins.xml').getroot().findall('world')
         for p in w.findall('mappin') if p.get('type') == 'RoadSign']
assert len(roads) == len(data['landmarks']) == 227
entries = []
for (world, original), p in zip(roads, data['landmarks']):
    r, reg = region[world]
    assert p['region'] == reg
    english, chinese, key = catalog[r][norm(aliases.get(original, original))]
    assert re.search('[\u4e00-\u9fff]', chinese) and not re.search('[A-Za-z]', chinese)
    entries.append({'key': reg + '|' + p['name'], 'name': chinese, 'original': original,
                    'sourceName': english, 'sourceKey': f'{r}:signpost.label.{key}',
                    'source': f'https://www.tivaprojects.com/witcher3map/files/locales/zh/{r}.json',
                    'aliased': original in aliases})
out = {'date': '2026-10-02', 'entries': entries,
       'method': '公开游戏中文地图的中英路标对照；繁体中文逐字转简，保留原文与来源。',
       'limits': '不是直接从官方简中语言文件导出；没有逐项实机比对。官中繁、简版本可能有不同用词。',
       'corrections': [{'name': '艾孚鲁灯塔', 'source': 'https://witcher.huijiwiki.com/wiki/艾孚鲁灯塔',
                        'detail': '修正社区中文地图把 Elverum 与 Eldberg 两座灯塔写成同名的问题。'}],
       'sourceHashes': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(src.glob('*.json'))}}
(root / 'dist/places-zh.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'localizedRoadSigns': len(entries), 'englishFallbacks': 0}))
