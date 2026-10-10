import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes_by_name = {n['name']: n for n in wf['nodes']}
connections = wf['connections']

# Find all paths from Webhook
visited = set()
def trace_from(name, depth=0):
    if name in visited and depth > 10:
        return
    # print('  '*depth + f'-> {name}')
    visited.add(name)
    if name in connections:
        for out_type, conns in connections[name].items():
            for group in conns:
                for target in group:
                    trace_from(target['node'], depth+1)

trace_from('Webhook')

all_functional = [n['name'] for n in wf['nodes'] if not n['type'].endswith('stickyNote')]
unreached = [n for n in all_functional if n not in visited]

print(f"Total functional nodes: {len(all_functional)}")
print(f"Reached from Webhook: {len(visited)}")
print(f"Unreached nodes ({len(unreached)}):")
for u in unreached:
    print(f" - {u} ({nodes_by_name[u]['type']})")

