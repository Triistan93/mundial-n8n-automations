# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

conns = wf.get('connections', {})
for src, targets in conns.items():
    if any(k in src for k in ['04_', '05_', '06_', '07_', '08_', 'PostRes', '01_']):
        print(f"Source: {src}")
        for branch, dest_list in targets.items():
            for dest in dest_list:
                for d in dest:
                    print(f"  --> [{branch}] {d.get('node')}")
