import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT_LIVE.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf['nodes']
connections = wf['connections']

print(f"Total nodes: {len(nodes)}")

# Print nodes grouped by X coordinate range
nodes_sorted = sorted(nodes, key=lambda n: (n['position'][0], n['position'][1]))

for i, n in enumerate(nodes_sorted):
    ntype = n['type']
    nname = n['name']
    pos = n['position']
    print(f"{i+1:02d}. [{pos[0]:5d}, {pos[1]:5d}] '{nname}' ({ntype})")
