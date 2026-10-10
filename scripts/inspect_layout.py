import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

xs = [n['position'][0] for n in wf['nodes']]
ys = [n['position'][1] for n in wf['nodes']]

print(f"Total nodes: {len(wf['nodes'])}")
print(f"X span: {min(xs)} to {max(xs)} (total width: {max(xs) - min(xs)})")
print(f"Y span: {min(ys)} to {max(ys)} (total height: {max(ys) - min(ys)})")

print("\n--- STICKY NOTES ATUAIS ---")
for n in wf['nodes']:
    if n['type'].endswith('stickyNote'):
        p = n['position']
        params = n.get('parameters', {})
        w = params.get('width')
        h = params.get('height')
        c = params.get('color')
        content = params.get('content', '')
        first_line = content.split('\n')[0] if content else ''
        print(f"Sticky: '{n['name']}' pos: {p} size: {w}x{h} color: {c} | title: {first_line}")
