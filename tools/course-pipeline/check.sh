#!/bin/bash
# The checks to run after every edit to index.html: extract the inline scripts, node --check, eslint no-undef, and a scan for code
# swallowed by a // comment (a comment put in the middle of a one-line statement comments out everything after it).
set -e
cd "$(dirname "$0")/../.."
T=${TMPDIR:-/tmp}/ssg-check; mkdir -p "$T"
python3 - "$T" <<'P'
import re,sys
s=open('index.html').read()
open(sys.argv[1]+'/s9.js','w').write('\n;\n'.join(re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>',s,re.S)))
bad=0
for i,l in enumerate(s.split('\n'),1):
    if l.strip().startswith('//') or '//' not in l or len(l)>5000: continue
    c=re.split(r'(?<![:"\'])//',l,maxsplit=1)
    if len(c)>1 and re.search(r';\s*[A-Za-z_\$][\w\.\[\]]*\s*(\(|=[^=])[^;]*;',c[1]): print('code after a // comment? line',i,':',c[1][:120].strip()); bad=1
sys.exit(bad)
P
node --check "$T/s9.js"
for f in data-*.js; do node --check "$f"; done
npx --yes eslint@8 --no-eslintrc --env browser,es2022 --parser-options=ecmaVersion:2022 --global THREE,mqtt --rule 'no-undef:error' "$T/s9.js"
echo 'index.html: all checks passed'
