# -*- coding: utf-8 -*-
import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/JARVIS_KyGWXLxc08bemhEk.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
connections = wf.get('connections', {})

print('=== WORKFLOW OVERVIEW ===')
print('ID:', wf.get('id'))
print('Name:', wf.get('name'))
print('Active:', wf.get('active'))
print('Total Nodes:', len(nodes))

type_counts = Counter(n.get('type') for n in nodes)
print('\n=== NODE TYPES COUNTER ===')
for t, c in type_counts.most_common():
    print(f'  {t}: {c}')

# Triggers
triggers = []
for n in nodes:
    t_type = n.get('type', '').lower()
    if 'trigger' in t_type or 'webhook' in t_type or 'schedule' in t_type or 'poll' in t_type:
        triggers.append(n)
print('\n=== TRIGGERS ===')
for tr in triggers:
    print(f"  Name: {tr.get('name')}, Type: {tr.get('type')}, Disabled: {tr.get('disabled', False)}")

# Credentials
creds_used = {}
for n in nodes:
    if 'credentials' in n:
        for k, v in n['credentials'].items():
            creds_used.setdefault(k, []).append((n['name'], v))
print('\n=== CREDENTIALS REFERENCED ===')
for k, v in creds_used.items():
    print(f"  {k}: {len(v)} nodes (Exemplo: {v[0]})")

# Integrity
node_names = {n['name'] for n in nodes}
missing_src = set()
missing_tgt = set()
for src, branches in connections.items():
    if src not in node_names:
        missing_src.add(src)
    for b_name, b_list in branches.items():
        for tg in b_list:
            for t in tg:
                t_name = t.get('node')
                if t_name not in node_names:
                    missing_tgt.add(t_name)

print('\n=== INTEGRITY CHECK ===')
print('Missing sources in connections:', missing_src if missing_src else 'None (OK)')
print('Missing targets in connections:', missing_tgt if missing_tgt else 'None (OK)')

# Nodes with no incoming connections (excluding triggers and stickies)
nodes_with_inputs = set()
for src, branches in connections.items():
    for b_name, b_list in branches.items():
        for tg in b_list:
            for t in tg:
                nodes_with_inputs.add(t.get('node'))

trigger_names = {tr.get('name') for tr in triggers}
sticky_names = {n.get('name') for n in nodes if n.get('type') == 'n8n-nodes-base.stickyNote'}

orphan_nodes = []
for n in nodes:
    name = n.get('name')
    if name not in nodes_with_inputs and name not in trigger_names and name not in sticky_names:
        orphan_nodes.append((name, n.get('type')))

print('\n=== ORPHAN NODES (No input connection) ===')
for name, ntype in orphan_nodes:
    print(f"  - {name} ({ntype})")

# Sticky notes
stickies = [n for n in nodes if n.get('type') == 'n8n-nodes-base.stickyNote']
print(f'\n=== STICKY NOTES ({len(stickies)}) ===')
for s in stickies:
    first_line = s.get('parameters', {}).get('content', '').split('\n')[0]
    print(f"  - {s.get('name')}: {first_line}")
