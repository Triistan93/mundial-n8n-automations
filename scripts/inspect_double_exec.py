# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
headers = {'X-N8N-API-KEY': API_KEY}

for eid in [652341, 652376]:
    r = requests.get(f'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions/{eid}?includeData=true', headers=headers)
    ex = r.json()
    data = ex.get('data', {}).get('resultData', {}).get('runData', {})
    print(f'=== EXEC #{eid} ===')
    if '05_Filter_And_Classify_Messages' in data:
        out = data['05_Filter_And_Classify_Messages'][0].get('data', {}).get('main', [[]])[0]
        for item in out:
            j = item.get('json', {})
            print(f'  Deal #{j.get("deal_id")}: user_message="{j.get("user_message")}" | last_id={j.get("last_processed_message_id")} | new_max={j.get("new_max_id")}')
    if '08_AI_Agent_Triage_Deal' in data:
        out8 = data['08_AI_Agent_Triage_Deal'][0].get('data', {}).get('main', [[]])[0]
        for item in out8:
            print('  -> AGENT OUTPUT:', item.get('json', {}).get('output'))
    if '10_Send_Bot_Message_Chat' in data:
        out10 = data['10_Send_Bot_Message_Chat'][0].get('data', {}).get('main', [[]])[0]
        for item in out10:
            print('  -> SENT MESSAGE:', item.get('json', {}))
