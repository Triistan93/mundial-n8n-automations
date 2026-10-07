# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

wf = json.load(open(r'C:\mundial-n8n-automations\workflows\canonical\BITRIX_TI_AI_TRIAGE_AGENT.json', encoding='utf-8'))
for n in wf['nodes']:
    if n.get('name') in ['08_AI_Agent_Triage_Deal', 'Tool_Think_Deal', 'OpenAI_Chat_Model_Deal', 'Redis_Deal_Chat_Memory']:
        print(f"{n.get('name')}: position = {n.get('position')}, type = {n.get('type')}")
