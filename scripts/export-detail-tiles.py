"""Export higher native zooms from the same frozen map revision, in compact WebP."""
from pathlib import Path
import json, sqlite3, io, hashlib, argparse
from PIL import Image

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=Path('/private/tmp/witcher-map-research/Witcher3MapViewer/Witcher3MapViewer/Maps'))
source = parser.parse_args().source
hashes = json.loads((root / 'evidence/source-hashes.json').read_text())
manifest = json.loads((root / 'evidence/map-manifest.json').read_text())
for code, name in [('NO', 'VelenNovigrad'), ('SK', 'Skellige'), ('KM', 'KaerMorhen'), ('TO', 'Toussaint')]:
    db = source / (name + '.mbtiles')
    assert hashlib.sha256(db.read_bytes()).hexdigest() == hashes[f'Witcher3MapViewer/Maps/{name}.mbtiles'], name
    con = sqlite3.connect(db)
    for z, x, y, data in con.execute('select zoom_level,tile_column,tile_row,tile_data from tiles where zoom_level>=4'):
        dest = root / f'dist/assets/tiles/{code}/{z}/{x}/{2**z-1-y}.webp'
        dest.parent.mkdir(parents=True, exist_ok=True)
        Image.open(io.BytesIO(data)).save(dest, 'WEBP', quality=88, method=6)
    con.close()
    manifest[code]['maxNativeZoom'] = 5
    manifest[code]['recommendedMaxZoom'] = 5.5
    manifest[code]['detailTemplate'] = code + '/{z}/{x}/{y}.webp'
    manifest[code]['detailEncoding'] = 'WebP quality 88; original 256-pixel native z4 and z5 tiles, TMS rows converted to XYZ'
manifest['WO']['recommendedMaxZoom'] = 4.5
for code, m in manifest.items():
    files = sorted((root / f'dist/assets/tiles/{code}').rglob('*.*'))
    m['fileCount'] = len(files)
    m['bytes'] = sum(f.stat().st_size for f in files)
    m['directory'] = f'dist/assets/tiles/{code}'
(root / 'evidence/map-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tiles': sum(m['fileCount'] for m in manifest.values()), 'bytes': sum(m['bytes'] for m in manifest.values())}))
