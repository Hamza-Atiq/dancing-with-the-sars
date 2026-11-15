"""Keep downloading the Sentinel-1 results until all are on disk, then measure the patch.

Safe to start again at any time (finished files are skipped). Only one copy should run.
Log: data/s1_finish.log     Run: C:/Users/HP/anaconda3/python.exe scripts/s1_finish.py
"""
import glob
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 24

for attempt in range(60):
    n = len(glob.glob(str(ROOT / 'data/s1/*.zip')))
    print(time.strftime('%H:%M'), 'have', n, 'of', EXPECTED, flush=True)
    if n >= EXPECTED:
        break
    subprocess.run([sys.executable, '-u', 'scripts/s1_hyp3.py', 'download'], cwd=ROOT)
    time.sleep(30)
if len(glob.glob(str(ROOT / 'data/s1/*.zip'))) >= EXPECTED:
    r = subprocess.run([sys.executable, 'scripts/s1_patch.py'], cwd=ROOT, capture_output=True, text=True)
    (ROOT / 'data/s1/s1_patch_table.txt').write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    print('measured; table in data/s1/s1_patch_table.txt', flush=True)
else:
    print('gave up before all files arrived', flush=True)
