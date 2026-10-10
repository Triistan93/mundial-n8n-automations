# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['name'] in ['PostRes_02_Prepare_Prompt', 'PostRes_03_Classify_Intent', 'PostRes_04_Parse_Classification']:
        print(f"=== {n['name']} ===")
        print(json.dumps(n['parameters'], indent=2, ensure_ascii=False))
