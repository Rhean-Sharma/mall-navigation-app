#!/usr/bin/env python3
"""Assemble index.html from app_template.html + assets/data.json + assets/map_embed.webp.

Run from the repo root:  python3 tools/assemble.py
"""
import json, base64, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
data = json.load(open(root / 'assets' / 'data.json'))
for k in ('suites', 'entries'):
    data.pop(k, None)
tpl = open(root / 'tools' / 'app_template.html').read()
img = base64.b64encode(open(root / 'assets' / 'map_embed.webp', 'rb').read()).decode()
content = tpl.replace('__DATA__', json.dumps(data, separators=(',', ':'))) \
             .replace('__MAPIMG__', 'data:image/webp;base64,' + img)
full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '</head>\n<body>\n' + content + '\n</body>\n</html>\n')
open(root / 'index.html', 'w').write(full)
print('wrote index.html', (root / 'index.html').stat().st_size, 'bytes')
