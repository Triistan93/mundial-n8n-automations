# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
for n in nodes:
    if n.get('name') in ['04_Fetch_Chat_Messages_Bitrix', '05_Filter_And_Classify_Messages', '07_Prepare_AI_Deal_Input', '08_AI_Agent_Triage_Deal']:
        print(f"=== NODE: {n.get('name')} ===")
        print(json.dumps(n, indent=2, ensure_ascii=False)[:2000])
        print("\n----------------------------------------\n")
