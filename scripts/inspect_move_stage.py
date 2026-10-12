# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}

for name in ['Normalizar IDs Finais', 'IF: Há etapa de destino?', 'Mover Card de Etapa']:
    n = nodes.get(name)
    if n:
        print(f"=== {name} ===")
        print(json.dumps(n.get('parameters', {}), indent=2, ensure_ascii=False))
