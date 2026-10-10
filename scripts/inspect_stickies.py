import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['type'].endswith('stickyNote'):
        p = n.get('parameters', {})
        print(f"Name: {n['name']}")
        print(f"Content:\n{p.get('content', '')}")
        print(f"Color: {p.get('color')} | Size: {p.get('width')}x{p.get('height')}\n" + "-"*40)
