# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}
conns = wf.get('connections', {})

roteador = nodes.get('Roteador de Saída')
if roteador:
    print("=== REGRAS DO ROTEADOR DE SAÍDA ===")
    print(json.dumps(roteador.get('parameters', {}), indent=2, ensure_ascii=False))

print("\n=== CONEXÕES A PARTIR DO ROTEADOR DE SAÍDA ===")
if 'Roteador de Saída' in conns:
    for branch_type, branch_list in conns['Roteador de Saída'].items():
        print(f"Tipo: {branch_type}")
        for idx, target_group in enumerate(branch_list):
            targets = [t.get('node') for t in target_group]
            print(f"  Regra/Saída [{idx}]: {targets}")

# Also check Formatar Output do Agente
fmt = nodes.get('Formatar Output do Agente')
if fmt:
    print("\n=== CÓDIGO DO NÓ FORMATAR OUTPUT DO AGENTE ===")
    print(fmt.get('parameters', {}).get('jsCode', ''))
