import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A_SPRINT1.json'
with open(path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}
node_names = set(nodes.keys())

pattern = re.compile(r"\$\(['\"]([^'\"]+)['\"]\)")
broken_refs = set()

for name, node in nodes.items():
    node_str = json.dumps(node, ensure_ascii=False)
    matches = pattern.findall(node_str)
    for ref in matches:
        if ref not in node_names:
            broken_refs.add((name, ref))

print(f"Total nodes: {len(nodes)}")
print(f"Total broken references found: {len(broken_refs)}")
for source, ref in sorted(broken_refs):
    print(f"  Node '{source}' references nonexistent node: '{ref}'")

if len(broken_refs) == 0:
    print("\n🎉 PERFECT: ZERO BROKEN NODE REFERENCES!")
