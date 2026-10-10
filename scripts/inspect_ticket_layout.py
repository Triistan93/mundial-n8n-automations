import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf['nodes']
xs = [n['position'][0] for n in nodes]
ys = [n['position'][1] for n in nodes]

print(f"Total nodes: {len(nodes)}")
print(f"X span: {min(xs)} to {max(xs)} (total width: {max(xs) - min(xs)})")
print(f"Y span: {min(ys)} to {max(ys)} (total height: {max(ys) - min(ys)})")

print("\n--- STICKY NOTES ATUAIS ---")
stickies = [n for n in nodes if n['type'].endswith('stickyNote')]
print(f"Total sticky notes: {len(stickies)}")
for n in stickies:
    p = n['position']
    params = n.get('parameters', {})
    w = params.get('width')
    h = params.get('height')
    c = params.get('color')
    content = params.get('content', '')
    first_line = content.split('\n')[0] if content else ''
    print(f"Sticky: '{n['name']}' pos: {p} size: {w}x{h} color: {c} | title: {first_line}")
