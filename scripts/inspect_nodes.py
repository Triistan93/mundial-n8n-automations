# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('C:/mundial-n8n-automations/workflows/current_c0F2GUMFm2BI94UG.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

target_nodes = [
    '11_B01_Priority_And_Payload',
    '12_Prepare_Deal_Update_Payload',
    '15_Prepare_Final_Chat',
    '15_Send_Final_Confirmation_To_Chat'
]

for n in wf.get('nodes', []):
    if n['name'] in target_nodes:
        print(f"==================== {n['name']} ({n['type']}) ====================")
        params = n.get('parameters', {})
        if 'functionCode' in params:
            print("--- FUNCTION CODE ---")
            print(params['functionCode'])
        elif 'jsCode' in params:
            print("--- JS CODE ---")
            print(params['jsCode'])
        else:
            print(json.dumps(params, indent=2, ensure_ascii=False))
        print("\n")
