# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
print(f"Total nodes: {len(nodes)}")
for i, n in enumerate(nodes):
    print(f"{i}: {n.get('name')} | Type: {n.get('type')}")
