# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
conns = wf.get('connections', {})

functional_nodes = [n for n in nodes if not n.get('type', '').endswith('stickyNote')]
sticky_nodes = [n for n in nodes if n.get('type', '').endswith('stickyNote')]

print(f"Total functional nodes: {len(functional_nodes)}")
print(f"Total sticky notes: {len(sticky_nodes)}")

print("\n=== LISTA DE TODOS OS NÓS FUNCIONAIS ===")
for i, n in enumerate(functional_nodes):
    name = n['name']
    ntype = n['type']
    pos = n.get('position', [0, 0])
    print(f"{i+1:02d}. [{pos[0]:6d}, {pos[1]:5d}] {name} ({ntype})")
