# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['name'] == '11_B01_Priority_And_Payload':
        print(n['parameters']['functionCode'])
