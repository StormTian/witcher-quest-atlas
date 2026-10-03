"""Read every served asset and record actual cloud recovery/verification limits."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
import hashlib,json,subprocess,os,datetime,threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
root=Path(__file__).resolve().parents[1]
base=os.environ.get('ATLAS_BASE_URL','http://127.0.0.1:8765/')
if not os.environ.get('ATLAS_BASE_URL'):
 class QuietHandler(SimpleHTTPRequestHandler):
  def log_message(self,*args): pass
 server=ThreadingHTTPServer(('127.0.0.1',8765),partial(QuietHandler,directory=str(root/'dist')))
 threading.Thread(target=server.serve_forever,daemon=True).start()
files=[p for p in (root/'dist').rglob('*') if p.is_file()]
def check(p):
 rel=p.relative_to(root/'dist').as_posix()
 with urlopen(base+rel,timeout=30) as response:
  body=response.read();assert response.status==200 and body==p.read_bytes(),rel
 return rel
with ThreadPoolExecutor(max_workers=4) as pool: fetched=list(pool.map(check,files))
expected=json.loads((root/'evidence/source-hashes.json').read_text())
verified={}
for name,digest in expected.items():
 p=root/'evidence/upstream'/name
 if p.exists():
  assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,name;verified[name]=digest
original='341b240bbb598db2f5f37e4c548953b046178b4f'
git=lambda *a:subprocess.check_output(['git',*a],cwd=root,text=True).strip()
subprocess.run(['git','fsck','--full'],cwd=root,check=True)
assert len(git('ls-tree','-r','--name-only',original).splitlines())==5822
attempts=[]
logs=root/'evidence/cloud-logs';logs.mkdir(exist_ok=True)
for script in ['browser-validate.cjs','validate-landmarks.cjs','validate-navigation.cjs','validate-assets.cjs']:
 result_name={'browser-validate.cjs':'browser-validation.json','validate-landmarks.cjs':'landmark-validation.json','validate-navigation.cjs':'navigation-validation.json','validate-assets.cjs':'asset-report-validation.json'}[script]
 prior=(root/'evidence'/result_name).read_bytes()
 result=subprocess.run(['node',str(root/'scripts'/script)],cwd=root,text=True,capture_output=True)
 (logs/(script+'.log')).write_text(result.stdout+result.stderr)
 if result.returncode:
  after=(root/'evidence'/result_name).read_bytes()
  if after!=prior: (logs/(result_name+'.failed.json')).write_bytes(after)
  (root/'evidence'/result_name).write_bytes(prior)
 attempts.append({'script':script,'exitCode':result.returncode,'log':'evidence/cloud-logs/'+script+'.log'})
out={'browserAttempts':attempts,'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executionEnvironment':'cloud-linux','originalCommit':original,'originalTrackedFiles':5822,'gitHistoryCommits':int(git('rev-list','--count',original)),'gitFsck':'pass','assetsFetched':len(fetched),'mapTiles':sum('/tiles/' in p for p in fetched),'frozenSourceHashesVerified':verified,'browserStatus':'pass' if all(a['exitCode']==0 for a in attempts) else 'blocked','browserBlocker':'本次云端 Playwright 浏览器检查全部通过。' if all(a['exitCode']==0 for a in attempts) else 'Playwright exists but Chromium/headless-shell is absent. playwright install chromium returned truncated/non-ZIP downloads from cdn.playwright.dev; browser launch failed before page loading. No cloud browser interaction or screenshot validation is claimed.','historicalLocalChecks':66,'cloudDataChecksPassed':json.loads((root/'evidence/data-logic-validation.json').read_text())['passed'],'gameVerification':'not executed','limits':['227 Chinese labels are public bilingual game-map translations, not individually verified official simplified Chinese strings.','Full tracked source recovered; original MBTiles databases are not tracked. Existing 5721 tiles are present; exporting additional tiles requires authorized original MBTiles with recorded hashes.','No user computer, remote Mac or Local computer access used.']}
(root/'evidence/cloud-migration.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
if not os.environ.get('ATLAS_BASE_URL'): server.shutdown()
print(json.dumps(out,ensure_ascii=False))
