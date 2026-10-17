"""Package the verified static site and bind it to an exact Git source commit."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess


root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', required=True, type=Path, help='A new output directory')
parser.add_argument('--repository', default=os.environ.get('GITHUB_REPOSITORY'))
args = parser.parse_args()
if not args.repository or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repository):
    parser.error('Set --repository owner/name or GITHUB_REPOSITORY')


def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=root, text=True).strip()


source_commit = git('rev-parse', 'HEAD')
if os.environ.get('GITHUB_SHA') and os.environ['GITHUB_SHA'] != source_commit:
    raise SystemExit('The checked-out commit differs from GITHUB_SHA')
status = subprocess.check_output(
    ['git', 'status', '--porcelain=v1', '--untracked-files=normal', '-z'], cwd=root
).decode()
dirty_paths = [entry[3:] for entry in status.split('\0') if entry]
if dirty_paths:
    generated_reports = {
        'evidence/asset-report-validation.json', 'evidence/browser-validation.json',
        'evidence/catalog-browser-validation.json', 'evidence/catalog-validation.json',
        'evidence/data-logic-validation.json', 'evidence/exploration-browser-validation.json',
        'evidence/exploration-data-validation.json', 'evidence/guidance-browser-validation.json',
        'evidence/guidance-validation.json', 'evidence/landmark-validation.json',
        'evidence/navigation-validation.json', 'evidence/progress-validation.json',
        'dist/validation.json', 'dist/validation-report.md',
    }

    def generated_path(path):
        return (
            path in generated_reports
            or (path.startswith('dist/checks/') and path.count('/') >= 2)
            or (posixpath.dirname(path) == 'evidence' and path.endswith('.png')
                and 'failure' not in posixpath.basename(path).lower())
        )

    unexpected = [path for path in dirty_paths if not generated_path(path)]
    if (os.environ.get('GITHUB_ACTIONS') != 'true' or not os.environ.get('GITHUB_SHA')
            or unexpected):
        details = ', '.join(unexpected or dirty_paths)
        raise SystemExit(f'Only CI-generated validation outputs may be uncommitted: {details}')

dist = root / 'dist'
output = args.output.resolve()
if output.exists() or output == root or dist in output.parents or root / 'evidence' in output.parents:
    raise SystemExit('Use a new output directory outside dist/ and evidence/')

inputs = json.loads((root / 'scripts/runtime-inputs.json').read_text())
hashes = {name: hashlib.sha256((dist / name).read_bytes()).hexdigest() for name in inputs}
validation = json.loads((dist / 'validation.json').read_text())
if validation['status'] != 'pass' or validation['runtimeInputHashes'] != hashes:
    raise SystemExit('The passing verification report must match the current runtime files')
for name in validation['evidence'].values():
    if name:
        report = json.loads((dist / name).read_text())
        if report['status'] != 'pass':
            raise SystemExit(f'A published verification result failed: {name}')
        if 'runtimeInputHashes' in report and report['runtimeInputHashes'] != hashes:
            raise SystemExit(f'A published browser result is stale: {name}')

files = sorted(path for path in dist.rglob('*') if path.is_file())
tree_hash = hashlib.sha256()
for path in files:
    if path.is_symlink():
        raise SystemExit(f'Pages does not accept symbolic links: {path.relative_to(dist)}')
    tree_hash.update(path.relative_to(dist).as_posix().encode() + b'\0')
    tree_hash.update(hashlib.sha256(path.read_bytes()).digest())

repository_url = f'https://github.com/{args.repository}'
version = {
    'schemaVersion': 1,
    'hosting': 'github-pages',
    'repository': args.repository,
    'repositoryURL': repository_url,
    'sourceCommit': source_commit,
    'sourceURL': f'{repository_url}/commit/{source_commit}',
    'builtAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'workflowRunURL': (f'{repository_url}/actions/runs/{os.environ["GITHUB_RUN_ID"]}'
                       if os.environ.get('GITHUB_RUN_ID') else None),
    'staticSourceFiles': len(files),
    'staticTreeSha256': tree_hash.hexdigest(),
    'runtimeInputHashes': hashes,
    'verification': {
        'status': validation['status'],
        'passed': validation['automatedChecksPassed'],
        'executedAt': validation['executedAt'],
        'reportSha256': hashlib.sha256((dist / 'validation.json').read_bytes()).hexdigest(),
    },
}
shutil.copytree(dist, output)
(output / '.nojekyll').write_text('Static site; no Jekyll processing.\n')
(output / 'version.json').write_text(json.dumps(version, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output': str(output), 'sourceCommit': source_commit,
                  'staticSourceFiles': len(files), 'verifiedChecks': version['verification']['passed']}))
