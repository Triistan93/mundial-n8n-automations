# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

wf = json.load(open(r'c:\mundial-n8n-automations\workflows\BITRIX_TI_AI_TRIAGE_AGENT.json', encoding='utf-8'))
nodes = {n['name']: n for n in wf['nodes']}

for k in ['14_Prepare_Timeline_And_Chat', '15_Prepare_Final_Chat', '15_Send_Final_Confirmation_To_Chat', '15_Filter_Tickets_Ready_For_IT', '15_Notify_IT_Team_Ready']:
    if k in nodes:
        print(f"=== {k} ({nodes[k].get('type')}) ===")
        print(json.dumps(nodes[k].get('parameters', {}), indent=2, ensure_ascii=False))
        print()
