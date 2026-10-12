# -*- coding: utf-8 -*-
import json
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

creds_found = {}
for p in glob.glob('c:/mundial-n8n-automations/workflows/*.json'):
    if 'JARVIS' in p: continue
    try:
        with open(p, 'r', encoding='utf-8') as f:
            d = json.load(f)
            for n in d.get('nodes', []):
                if 'credentials' in n and n['credentials']:
                    for ctype, cdata in n['credentials'].items():
                        creds_found.setdefault(ctype, set()).add((cdata.get('id'), cdata.get('name')))
    except Exception as e:
        pass

print("=== CREDENCIAIS EFETIVAMENTE UTILIZADAS EM PRODUÇÃO NO N8N ===")
for ctype, cset in creds_found.items():
    print(f"\nTipo: {ctype}")
    for cid, cname in cset:
        print(f"  - ID: {cid} | Nome: {cname}")
