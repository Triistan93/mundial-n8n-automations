# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}

targets = [
    '01_Strict_Gate_Cat160_Pilot',
    '01_If_Is_Duplicate',
    '02_Reserve_Deal_Session_Atomic',
    '03_Create_CRM_Card_Chat',
    '11_B01_Priority_And_Payload',
    '14_Prepare_Timeline_And_Chat'
]

for t in targets:
    n = nodes.get(t)
    if n:
        print(f"=== {t} ({n.get('type')}) ===")
        params = n.get('parameters', {})
        if 'functionCode' in params:
            print("functionCode:\n", params['functionCode'][:600])
        elif 'query' in params:
            print("query:\n", params['query'])
        elif 'url' in params:
            print("url:\n", params['url'])
            if 'queryParameters' in params:
                print("queryParams:\n", json.dumps(params['queryParameters'], indent=2)[:300])
        print("----------------------------------------")
