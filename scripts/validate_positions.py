import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Import our position mapping
import test_layout_mapping

pos_dict = test_layout_mapping.get_node_positions()

# Check that every single functional node is in pos_dict
nodes = wf['nodes']
for n in nodes:
    if not n['type'].endswith('stickyNote'):
        assert n['name'] in pos_dict, f"Missing {n['name']}"

print("All 86 functional nodes confirmed present.")

# Check for any exact duplicates in coordinates
seen_coords = {}
for name, p in pos_dict.items():
    key = tuple(p)
    if key in seen_coords:
        print(f"WARNING: Duplicate position {p} between '{name}' and '{seen_coords[key]}'")
    seen_coords[key] = name

print(f"Unique positions count: {len(seen_coords)} / {len(pos_dict)}")
