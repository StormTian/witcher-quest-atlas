"""Attach independently authored Chinese story notes to stable catalogue IDs."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / 'dist/data.json'
    data = json.loads(path.read_text())
    text = (ROOT / 'content/quest-stories.tsv').read_text()
    references = json.loads((ROOT / 'content/quest-story-sources.json').read_text())
    stories = {}
    for number, line in enumerate(text.splitlines(), 1):
        row = line.split('|')
        if len(row) != 3:
            raise ValueError(f'Story row {number}: expected ID, introduction, plot')
        qid, intro, plot = row
        if qid in stories or len(intro) < 15 or len(plot) < 30:
            raise ValueError(f'Invalid or duplicate story: {qid}')
        stories[qid] = {'intro': intro, 'plot': plot, 'source': references['quests'][qid]['url']}
    ids = {q['id'] for q in data['quests']}
    if set(stories) != ids or set(references['quests']) != ids:
        raise ValueError('Story notes, source references and catalogue IDs must match exactly')
    for quest in data['quests']:
        quest['story'] = stories[quest['id']]
    data['meta']['stories'] = {
        'count': len(stories), 'date': references['date'],
        'method': '独立撰写中文简介与剧情经过；逐任务附参考来源，非游戏日志全文翻译。',
        'spoilers': '仅简介默认显示，任务经过使用逐任务／全局剧透控制。',
        'limits': '剧情摘要不代表已核对全部分支，也不等于逐任务游戏实机验证。',
        'contentSha256': hashlib.sha256(text.encode()).hexdigest(),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f'Attached {len(stories)} story introductions and spoiler-protected plots')


if __name__ == '__main__':
    main()
