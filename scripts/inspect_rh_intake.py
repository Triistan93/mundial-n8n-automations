# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for n in wf.get('nodes', []):
    if n['name'] in ['Webhook', 'JID', 'Entrada', '[IF] Triagem: Receptivo vs Ativo', 'RECEPTIVO']:
        print(f"=== {n['name']} ({n['type']}) ===")
        print(json.dumps(n.get('parameters', {}), indent=2, ensure_ascii=False)[:300])
