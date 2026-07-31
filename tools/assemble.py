#!/usr/bin/env python3
"""Assemble index.html from app_template.html + assets/data.json + assets/basemap.json.

Run from the repo root:  python3 tools/assemble.py
"""
import json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
data = json.load(open(root / 'assets' / 'data.json'))
data.pop('entries', None)
data['basemap'] = json.load(open(root / 'assets' / 'basemap.json'))
tpl = open(root / 'tools' / 'app_template.html').read()
content = tpl.replace('__DATA__', json.dumps(data, separators=(',', ':')))
full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '</head>\n<body>\n' + content + '\n</body>\n</html>\n')
open(root / 'index.html', 'w').write(full)
print('wrote index.html', (root / 'index.html').stat().st_size, 'bytes')
