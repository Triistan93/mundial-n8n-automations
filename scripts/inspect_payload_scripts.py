# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}

for name in ['1. Preparar Dados Lead', 'Preparar Payload de Criação (Fallback)', 'Preparar Payload de Atualização1']:
    n = nodes.get(name)
    if n:
        print(f"=== NÓ: {name} ===")
        print(n.get('parameters', {}).get('jsCode', ''))
        print("\n" + "="*50 + "\n")
