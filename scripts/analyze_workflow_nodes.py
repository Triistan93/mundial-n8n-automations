import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf['nodes']
connections = wf['connections']

print(f"Total nodes: {len(nodes)}")

# Trace execution paths from triggers
# The entry point is Webhook
for i, n in enumerate(nodes):
    ntype = n.get('type')
    nname = n.get('name')
    disabled = n.get('disabled', False)
    print(f"{i+1:02d}. [{ntype}] '{nname}' {'(DISABLED)' if disabled else ''}")
