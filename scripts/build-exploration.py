"""Build the first exploration layers from frozen community map records."""
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
# This source key belongs to a separate scene, outside the supported Toussaint tiles.
DEFERRED = {'TO|NoticeBoard|q704_ft_fairy_tale_noticeboard': '来源标识为童话世界独立场景，且坐标在陶森特区域底图范围外；没有对应场景底图，暂缓展示。'}


def transform(world, xy):
    scale, origin_x, origin_y = SETTINGS[world]
    x, y = (xy[0] - origin_x) / scale, (xy[1] - origin_y) / scale
    return [math.degrees(2 * math.atan(math.exp(y / 6378137)) - math.pi / 2), math.degrees(x / 6378137)]


def build():
    xml = ET.parse(SOURCE).getroot()
    landmarks = json.loads((ROOT / 'dist/data.json').read_text())['landmarks']
    points, seen, raw_counts, duplicates, deferred = [], {}, Counter(), [], []
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
            if not source_key:
                raise ValueError(f'Missing stable source key: {code}/{index}')
            key = '|'.join([code, source_type, source_key])
            xy = [float(node.find('position').get(axis)) for axis in ['x', 'y']]
            if key in DEFERRED:
                deferred.append({'sourceKey': key, 'sourceIndex': index, 'gameXY': xy, 'reason': DEFERRED[key]})
                continue
            if key in seen:
                if seen[key]['gameXY'] != xy:
                    raise ValueError(f'Conflicting source positions: {key}')
                duplicates.append({'sourceKey': key, 'sourceIndex': index, 'keptPointId': seen[key]['id'], 'reason': '同一来源标识与坐标的重复记录，合并为一个点位。'})
                continue
            latlng = transform(code, xy)
            if not (-85.0512 <= latlng[0] <= 85.0512 and -180 <= latlng[1] <= 180):
                raise ValueError(f'Point outside supported map bounds: {key}')
            _, near_xy = min(roads, key=lambda road: sum((a - b) ** 2 for a, b in zip(road[1], xy)))
            near_latlng = transform(code, near_xy)
            nearby = next(road for road in landmarks if road['region'] == REGIONS[code]
                          and all(abs(a - b) < 1e-8 for a, b in zip(road['latlng'], near_latlng)))
            point = {
                'id': 'p-' + code.lower() + '-' + category['id'] + '-' + hashlib.sha256(key.encode()).hexdigest()[:16],
                'type': category['id'], 'title': category['name'], 'region': REGIONS[code],
                'gameXY': xy, 'latlng': latlng, 'precision': 'community',
                'sourceKey': key, 'sourceName': node.findtext('name', '').strip(),
                'sourceIndex': index, 'sourceCommit': SOURCE_COMMIT,
                'nearbyLandmark': nearby,
                'description': category['description'],
                'availability': '当前来源仅给出位置，没有可解析的完整开放条件；尚未逐点实机复核。',
                'sources': [{'label': '社区地图点位来源', 'url': SOURCE_URL}],
            }
            points.append(point)
            seen[key] = point
    counts = Counter(point['type'] for point in points)
    assert sum(raw_counts.values()) == 72
    assert dict(counts) == {'power': 29, 'board': 35, 'stash': 6}
    output = {
        'meta': {'schemaVersion': 1, 'date': '2026-10-03', 'sourceCommit': SOURCE_COMMIT,
                 'sourceSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                 'coordinateSystem': '与现有区域底图同源的游戏 XY 校准坐标；不是现实地理经纬度。',
                 'scope': '首批魔力之所、告示板、储藏箱；不是全游戏探索点完整性证明。',
                 'rawRecords': sum(raw_counts.values()), 'rawCounts': dict(raw_counts),
                 'included': len(points), 'duplicates': duplicates, 'deferred': deferred,
                 'limits': ['来源坐标尚未逐点实机复核。', '最近路标按游戏 XY 直线距离选择，只作为方位参考，不代表可步行到达的路线。', '点位显示不代表其任务、告示或设施已在当前存档中开放。']},
        'categories': [{**category, 'count': counts[category['id']]} for category in CATEGORIES.values()],
        'points': points,
    }
    path = ROOT / 'dist/exploration.json'
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'included': len(points), 'counts': dict(counts), 'duplicates': len(duplicates), 'deferred': len(deferred)}, ensure_ascii=False))


if __name__ == '__main__':
    build()
