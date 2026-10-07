# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('C:/mundial-n8n-automations/workflows/current_c0F2GUMFm2BI94UG.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes_to_check = [
    '11_B01_Priority_And_Payload',
    '11_Fetch_Deal_For_Description',
    '12_Prepare_Deal_Update_Payload',
    '12_Update_Deal_CRM_Bitrix',
    '14_Prepare_Timeline_And_Chat',
    '15_Prepare_Final_Chat',
    '15_Send_Final_Confirmation_To_Chat',
    '16_Prepare_Complete_Session',
    '16_Mark_Session_Completed_Postgres'
]

for n in wf.get('nodes', []):
    if n['name'] in nodes_to_check:
        print(f"==================== {n['name']} ====================")
        print("Type:", n.get('type'))
        params = n.get('parameters', {})
        for k, v in params.items():
            print(f"[{k}]:")
            if isinstance(v, str):
                print(v[:500])
            else:
                print(json.dumps(v, ensure_ascii=False)[:300])
        print("\n")

print("--- CONNECTIONS AROUND 15 ---")
for k, v in wf.get('connections', {}).items():
    if '14_' in k or '15_' in k or '16_' in k:
        print(k, "->", v)
