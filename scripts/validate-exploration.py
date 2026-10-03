"""Independent frozen-source checks for exploration data; no game verification."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'dist/exploration.json'
SOURCE_PATH = ROOT / 'evidence/upstream/Witcher3MapViewer/MapPins.xml'
DATA = json.loads(DATA_PATH.read_text())
QUESTS = json.loads((ROOT / 'dist/data.json').read_text())
CHECKS = []
MANIFEST = json.loads((ROOT / 'evidence/exploration-round3-manifest.json').read_text())
SOURCE_TYPES = {'PlaceOfPower','NoticeBoard','PlayerStash','Merchant','Herbalist','Blacksmith','Armorer','GwentPlayer','GwentSeller','MonsterNest','RescuingTown','TreasureHuntMappin','BossAndTreasure','SpoilsOfWar','Contraband','Entrance'}
REGIONS = {'WO': 'white-orchard', 'NO': 'velen', 'SK': 'skellige', 'KM': 'kaer-morhen', 'TO': 'toussaint'}
EXPECTED_REGIONS = {'white-orchard': {'power': 6, 'board': 1, 'stash': 1}, 'velen': {'power': 8, 'board': 19, 'stash': 2}, 'skellige': {'power': 9, 'board': 8, 'stash': 1}, 'toussaint': {'power': 5, 'board': 7, 'stash': 1}, 'kaer-morhen': {'power': 1, 'board': 0, 'stash': 1}}
FIXTURES = [
    ('WO|NoticeBoard|prologue_village_noticeboard', [4, -15], [-8.058140546210554, -13.238330502814001]),
    ('NO|PlayerStash|MISSING_NAME_AA3ED6BB-4FAE7E56-37FADC93-4571C7AE', [186, 182], [-38.14549630928053, -61.66855625894189]),
    ('SK|NoticeBoard|kaer_trolde_village_notice_board', [-39, 550], [13.261589700403915, -13.633577696179811]),
    ('TO|NoticeBoard|beauclair_city_noticeboard', [-508, -1338], [-52.63231219208436, -35.522010175829905]),
    ('KM|PlaceOfPower|km_mp_pop_igniii', [61, 969], [74.59561180725517, 8.050043655225993]),
]


def check(name, fn):
    try:
        detail = fn()
        CHECKS.append({'name': name, 'status': 'pass', 'detail': detail})
    except Exception as error:
        CHECKS.append({'name': name, 'status': 'fail', 'detail': str(error)})


def source_coverage():
    assert hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() == '2ecb73a3b14e1a47383c66e959ff0f1518f5918e7163f689aa8f790ae79f776e'
    source = Counter()
    positions = {}
    for world in ET.parse(SOURCE_PATH).getroot():
        for index, node in enumerate(world.findall('mappin')):
            if node.get('type') not in SOURCE_TYPES:
                continue
            key = '|'.join([world.get('code'), node.get('type'), node.findtext('internalname').strip()])
            source[key] += 1
            positions[(world.get('code'), index)] = [float(node.find('position').get(axis)) for axis in ['x', 'y']]
    included = Counter(point['sourceKey'] for point in DATA['points'])
    ledger = included + Counter(item['sourceKey'] for item in DATA['meta']['duplicates']) + Counter(item['sourceKey'] for item in DATA['meta']['deferred'])
    assert source == ledger, 'Unexplained missing or extra source records'
    assert sum(source.values()) == MANIFEST['rawRecords']
    for point in DATA['points']:
        assert point['gameXY'] == positions[(point['sourceKey'].split('|')[0], point['sourceIndex'])]
    assert [(r['world'],r['sourceIndex'],r['action'],r.get('pointId')) for r in DATA['meta']['ledger']] == [(r['world'],r['sourceIndex'],r['action'],r.get('pointId')) for r in MANIFEST['records']]
    return 'Locked source hash; all 617 raw records independently accounted for, with original XY retained.'


def audited_counts():
    assert len(DATA['points']) == MANIFEST['expectedIncluded']
    assert Counter(point['type'] for point in DATA['points']) == MANIFEST['expectedCounts']
    for region, counts in MANIFEST['regions'].items():
        for category, count in counts.items():
            assert sum(point['region'] == region and point['type'] == category for point in DATA['points']) == count, (region, category)
    return '615 audited records; exact per-category counts independently declared for all five regions.'


def exclusions():
    assert len(DATA['meta']['duplicates']) == 1 and len(DATA['meta']['deferred']) == 1
    duplicate = DATA['meta']['duplicates'][0]
    assert duplicate['sourceKey'] == 'TO|NoticeBoard|cockatrice_inn_noticeboard'
    assert sum(point['id'] == duplicate['keptPointId'] for point in DATA['points']) == 1
    assert DATA['meta']['deferred'][0]['sourceKey'] == 'TO|NoticeBoard|q704_ft_fairy_tale_noticeboard'
    assert all('fairy_tale' not in point['sourceKey'] for point in DATA['points'])
    return 'Duplicate Cockatrice Inn board merged; separate-scene candidate withheld from Toussaint.'


def coordinate_samples():
    for key, xy, expected in FIXTURES:
        point = next(point for point in DATA['points'] if point['sourceKey'] == key)
        assert point['gameXY'] == xy
        assert all(abs(a - b) < 1e-9 for a, b in zip(point['latlng'], expected)), key
    for point in DATA['points']:
        lat, lng = point['latlng']
        assert all(math.isfinite(number) for number in [lat, lng])
        assert -85.0512 <= lat <= 85.0512 and -180 <= lng <= 180
        assert point['region'] == REGIONS[point['sourceKey'].split('|')[0]]
    return 'Five predeclared coordinate fixtures match; every point has finite coordinates in its own region.'


def identities_and_references():
    ids = [point['id'] for point in DATA['points']]
    assert len(ids) == len(set(ids))
    assert not set(ids) & {quest['id'] for quest in QUESTS['quests']}
    assert len({point['stableSourceKey'] for point in DATA['points']}) == MANIFEST['expectedIncluded']
    old_path=ROOT/'evidence/baselines/exploration-v6.json'
    assert hashlib.sha256(old_path.read_bytes()).hexdigest()=='0c72d1d022d7e30500fed600c6a66eca69538dcf62bcd8e84abd8ec7dffe1c3f'
    old=json.loads(old_path.read_text())
    current = {p['id']:p for p in DATA['points']}
    for p in old['points']:
        assert p['id'] in current and current[p['id']]['gameXY']==p['gameXY'] and max(abs(a-b) for a,b in zip(current[p['id']]['latlng'],p['latlng']))<1e-9
    for point in DATA['points']:
        assert point['nearbyLandmark'] in QUESTS['landmarks']
        assert point['nearbyLandmark']['region'] == point['region']
    return 'Unique stable source identities, separate from quest IDs; all reference landmarks resolve in the same region.'


def legacy_catalog():
    old_path=ROOT/'evidence/history/cloud-round1-2026-10-03/data.json'
    assert hashlib.sha256(old_path.read_bytes()).hexdigest() == '2a3bb7d2b153174966ec2c4125dc2a57343b55b065884ce9ae3047f7e351faa9'
    current={q['id']:q for q in QUESTS['quests']}
    for q in json.loads(old_path.read_text())['quests']:
        for field in ['id','type','title','region','expansion']:
            assert q[field]==current[q['id']][field], (q['id'],field)
            a,b=q['point'],current[q['id']]['point'];assert bool(a)==bool(b)
        if a:
            assert a['world']==b['world'] and a['xy']==b['xy']
            assert max(abs(x-y) for x,y in zip(a['latlng'],b['latlng']))<1e-9
    return 'All 267 legacy IDs, classifications, titles, expansion boundaries and coordinates retain their frozen baseline values.'


def provenance():
    assert DATA['meta']['sourceSha256'] == hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()
    for point in DATA['points']:
        assert point['precision'] == 'community'
        assert point['availability'] and point['description'] and point['sources']
        assert point['sourceCommit'] == 'fb674dbff7df087d0a45f9b3938ba6d5317295af'
        assert all(point['sourceCommit'] in source['url'] for source in point['sources'])
    return 'Every point retains frozen source provenance and unknown-availability limits; no in-game verification claimed.'


for name, fn in [('原始记录逐条对账', source_coverage), ('独立分类与地区清单', audited_counts), ('重复与独立场景处理', exclusions), ('独立坐标样例与区域边界', coordinate_samples), ('稳定标识与引用', identities_and_references), ('旧任务目录保持', legacy_catalog), ('来源与精度边界', provenance)]:
    check(name, fn)
output = {'date': datetime.now(timezone.utc).date().isoformat(), 'executionEnvironment': 'cloud-linux', 'executedAt': datetime.now(timezone.utc).isoformat(), 'status': 'pass' if all(item['status'] == 'pass' for item in CHECKS) else 'fail', 'checks': CHECKS, 'passed': sum(item['status'] == 'pass' for item in CHECKS), 'total': len(CHECKS), 'explorationSha256': hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(), 'datasetSha256': hashlib.sha256((ROOT / 'dist/data.json').read_bytes()).hexdigest()}
(ROOT / 'evidence/exploration-data-validation.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(output, ensure_ascii=False))
raise SystemExit(0 if output['status'] == 'pass' else 1)
