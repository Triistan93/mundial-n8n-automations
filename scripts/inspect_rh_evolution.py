# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for n in wf.get('nodes', []):
    name = n.get('name', '')
    url = n.get('parameters', {}).get('url', '')
    if 'evolution' in n.get('type', '').lower() or 'whatsapp' in name.lower() or 'enviar msg' in name.lower():
        print(f"=== {name} ===")
        print(f"Type: {n.get('type')}")
        print(f"Credentials: {n.get('credentials')}")
        print(f"Params: {json.dumps(n.get('parameters', {}), indent=2, ensure_ascii=False)[:300]}")
