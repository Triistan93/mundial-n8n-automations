# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
for n in nodes:
    if 'PostRes' in n['name']:
        print(f"=== {n['name']} ({n['type']}) ===")
        params = n.get('parameters', {})
        if 'functionCode' in params:
            print(params['functionCode'][:500])
        elif 'prompt' in params:
            print(params['prompt'][:500])
        elif 'query' in params:
            print(params['query'])
        print("------------------------------------------")
