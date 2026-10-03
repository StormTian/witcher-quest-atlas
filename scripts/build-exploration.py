"""Build reviewed exploration layers, keeping original and mapped variant IDs."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/upstream/Witcher3MapViewer/MapPins.xml'
SOURCE_COMMIT = 'fb674dbff7df087d0a45f9b3938ba6d5317295af'
SOURCE_URL = f'https://github.com/reubengann/Witcher3MapViewer/blob/{SOURCE_COMMIT}/Witcher3MapViewer/MapPins.xml'
REGIONS = {'WO': 'white-orchard', 'NO': 'velen', 'SK': 'skellige', 'KM': 'kaer-morhen', 'TO': 'toussaint'}
SETTINGS = {'WO': (.000038, 60, 19.2), 'NO': (.000114, 968.6, 706.4), 'SK': (.000164, 209.9, 305.7), 'KM': (.0000568, 10.1, 244.2), 'TO': (.0000897, -153.3, -717.7)}
CATEGORIES = {
    'PlaceOfPower': {'id': 'power', 'name': '魔力之所', 'symbol': '✧', 'description': '探索魔力之所的位置。部分地点可能受任务阶段或入口条件影响，请结合游戏内情况确认。'},
    'NoticeBoard': {'id': 'board', 'name': '告示板', 'symbol': '≡', 'description': '查看当地告示与任务线索。这里标的是告示板位置，不代表当前剧情阶段已有全部告示或可接任务。'},
    'PlayerStash': {'id': 'stash', 'name': '储藏箱', 'symbol': '▣', 'description': '玩家储藏箱的位置。是否已开放取决于剧情与当地状态；地图不读取存档，无法判断当前可用性。'},
}
CATEGORIES.update({
    'Merchant': {'id': 'merchant', 'name': '商人与草药师', 'symbol': '¤', 'description': '社区来源登记的商人或草药师位置。不是完整商人名单，不推断当前库存或开放状态。'},
    'Blacksmith': {'id': 'blacksmith', 'name': '铁匠', 'symbol': '⚒', 'description': '社区来源登记的铁匠位置。工匠等级、营业时间及任务解锁须在游戏内确认。'},
    'Armorer': {'id': 'armorer', 'name': '护甲匠', 'symbol': '▧', 'description': '社区来源登记的护甲匠位置。不能仅凭标记推断师匠能力或当前可用性。'},
    'GwentPlayer': {'id': 'gwent-player', 'name': '昆特对手', 'symbol': '♠', 'description': '来源登记的昆特对战入口；不代表完整对手、独特卡牌或任何阶段均可对战。'},
    'GwentSeller': {'id': 'gwent-seller', 'name': '昆特售牌者', 'symbol': '♣', 'description': '来源登记的售牌入口；卡牌库存及错过条件尚未逐卡核对。'},
    'MonsterNest': {'id': 'nest', 'name': '怪物巢穴', 'symbol': '◉', 'description': '社区来源记录的怪物巢穴位置。清理状态由你记录，地图不会读取游戏存档。'},
    'RescuingTown': {'id': 'abandoned', 'name': '废弃地点', 'symbol': '⌂', 'description': '社区来源的清理／救援地点。原始类型 RescuingTown，未逐点确认清理后的商人与人口变化。'},
    'TreasureHuntMappin': {'id': 'treasure-point', 'name': '宝藏与战利品', 'symbol': '◆', 'description': '隐藏宝藏、守卫宝藏或战利品的社区候选位置；保留原始类型，不把资源点当成独立寻宝任务。'},
    'Contraband': {'id': 'smuggler', 'name': '走私品', 'symbol': '▱', 'description': '社区来源登记的走私品候选位置；通常需要自行探索水域，不提供未经验证的抵达路线。'},
    'Entrance': {'id': 'entrance', 'name': '洞穴入口', 'symbol': '∩', 'description': '只标社区记录的入口候选位置；没有洞穴内部底图，不代表通道一定开放或可连通。'},
})
CATEGORIES['Herbalist'] = CATEGORIES['Merchant']
CATEGORIES['BossAndTreasure'] = CATEGORIES['TreasureHuntMappin']
CATEGORIES['SpoilsOfWar'] = CATEGORIES['TreasureHuntMappin']
# This source key belongs to a separate scene, outside the supported Toussaint tiles.
DEFERRED = {'TO|NoticeBoard|q704_ft_fairy_tale_noticeboard': '来源标识为童话世界独立场景，且坐标在陶森特区域底图范围外；没有对应场景底图，暂缓展示。'}


def transform(world, xy):
    scale, origin_x, origin_y = SETTINGS[world]
    x, y = (xy[0] - origin_x) / scale, (xy[1] - origin_y) / scale
    return [math.degrees(2 * math.atan(math.exp(y / 6378137)) - math.pi / 2), math.degrees(x / 6378137)]


def build():
    xml = ET.parse(SOURCE).getroot()
    id_map = json.loads((ROOT / 'evidence/exploration-id-map.json').read_text())['entries']
    landmarks = json.loads((ROOT / 'dist/data.json').read_text())['landmarks']
    points, seen, raw_counts, duplicates, deferred, ledger = [], {}, Counter(), [], [], []
    for world in xml.findall('world'):
        code = world.get('code')
        roads = [(node.findtext('name', ''), [float(node.find('position').get(axis)) for axis in ['x', 'y']])
                 for node in world.findall('mappin') if node.get('type') == 'RoadSign']
        for index, node in enumerate(world.findall('mappin')):
            source_type = node.get('type')
            if source_type not in CATEGORIES:
                continue
            raw_counts[source_type] += 1
            category = CATEGORIES[source_type]
            source_key = node.findtext('internalname', '').strip()
            key = '|'.join([code, source_type, source_key])
            override = id_map.get(key + '|' + str(index))
            if override:
                assert override['sourceName'] == node.findtext('name', ''), f'ID migration needs review: {key}/{index}'
            stable_key = override['stableKey'] if override else key
            if not source_key and not override:
                raise ValueError(f'Missing curated ID mapping: {code}/{index}')
            xy = [float(node.find('position').get(axis)) for axis in ['x', 'y']]
            record = {'world': code, 'sourceType': source_type, 'sourceKey': key, 'sourceIndex': index}
            if key in DEFERRED:
                deferred.append({'sourceKey': key, 'sourceIndex': index, 'gameXY': xy, 'reason': DEFERRED[key]})
                ledger.append({**record, 'action': 'defer', 'reason': DEFERRED[key]})
                continue
            if stable_key in seen:
                if seen[stable_key]['gameXY'] != xy:
                    raise ValueError(f'Conflicting source positions: {key}')
                duplicates.append({'sourceKey': key, 'sourceIndex': index, 'keptPointId': seen[stable_key]['id'], 'reason': '同一来源标识与坐标的重复记录，合并为一个点位。'})
                ledger.append({**record, 'action': 'merge', 'pointId': seen[stable_key]['id']})
                continue
            latlng = transform(code, xy)
            if not (-85.0512 <= latlng[0] <= 85.0512 and -180 <= latlng[1] <= 180):
                raise ValueError(f'Point outside supported map bounds: {key}')
            _, near_xy = min(roads, key=lambda road: sum((a - b) ** 2 for a, b in zip(road[1], xy)))
            near_latlng = transform(code, near_xy)
            nearby = next(road for road in landmarks if road['region'] == REGIONS[code]
                          and all(abs(a - b) < 1e-8 for a, b in zip(road['latlng'], near_latlng)))
            point = {
                'id': 'p-' + code.lower() + '-' + category['id'] + '-' + hashlib.sha256(stable_key.encode()).hexdigest()[:16],
                'type': category['id'], 'title': category['name'], 'region': REGIONS[code],
                'gameXY': xy, 'latlng': latlng, 'precision': 'community',
                'sourceKey': key, 'sourceName': node.findtext('name', '').strip(),
                'sourceType': source_type, 'stableSourceKey': stable_key,
                'sourceIndex': index, 'sourceCommit': SOURCE_COMMIT,
                'nearbyLandmark': nearby,
                'description': category['description'],
                'availability': '当前来源仅给出位置，没有可解析的完整开放条件；尚未逐点实机复核。',
                'sources': [{'label': '社区地图点位来源', 'url': SOURCE_URL}],
            }
            points.append(point)
            seen[stable_key] = point
            ledger.append({**record, 'action': 'include', 'pointId': point['id']})
    counts = Counter(point['type'] for point in points)
    manifest = json.loads((ROOT / 'evidence/exploration-round3-manifest.json').read_text())
    assert sum(raw_counts.values()) == manifest['rawRecords']
    assert dict(counts) == manifest['expectedCounts']
    output = {
        'meta': {'schemaVersion': 1, 'date': '2026-10-03', 'sourceCommit': SOURCE_COMMIT,
                 'sourceSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                 'coordinateSystem': '与现有区域底图同源的游戏 XY 校准坐标；不是现实地理经纬度。',
                 'scope': '基础设施、昆特入口、探索资源及洞穴入口的冻结社区记录；不是全游戏探索点或商人完整性证明。',
                 'rawRecords': sum(raw_counts.values()), 'rawCounts': dict(raw_counts),
                 'included': len(points), 'duplicates': duplicates, 'deferred': deferred,
                 'ledger': ledger, 'idMapping': 'source-key with explicit curated variants; no coordinate IDs',
                 'limits': ['来源坐标尚未逐点实机复核。', '最近路标按游戏 XY 直线距离选择，只作为方位参考，不代表可步行到达的路线。', '点位显示不代表其任务、告示或设施已在当前存档中开放。']},
        'categories': [{**category, 'defaultEnabled': category['id'] in ['power','board','stash'], 'count': counts[category['id']]} for category in {c['id']: c for c in CATEGORIES.values()}.values()],
        'points': points,
    }
    path = ROOT / 'dist/exploration.json'
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'included': len(points), 'counts': dict(counts), 'duplicates': len(duplicates), 'deferred': len(deferred)}, ensure_ascii=False))


if __name__ == '__main__':
    build()
