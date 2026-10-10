import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

connections = wf['connections']
nodes = {n['name']: n for n in wf['nodes']}

print("--- CONNECTIONS GRAPH BY NODE ---")
for source, targets in sorted(connections.items()):
    target_list = []
    for out_type, groups in targets.items():
        for g in groups:
            for t in g:
                target_list.append(f"{t['node']} ({out_type})")
    print(f"[{source}] -> {', '.join(target_list)}")
