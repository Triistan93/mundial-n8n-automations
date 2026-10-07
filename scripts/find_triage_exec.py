# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url_base = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions/'

for eid in range(535435, 535456):
    try:
        r = requests.get(f"{url_base}{eid}?includeData=true", headers={'X-N8N-API-KEY': API_KEY}, timeout=5)
        if r.status_code == 200:
            d = r.json()
            runData = d.get('data', {}).get('resultData', {}).get('runData', {})
            nodes = list(runData.keys())
            if any('15_' in n or '12_' in n or '08_' in n for n in nodes):
                print(f"Execution {eid} ({d.get('startedAt')}):")
                print("  Nodes:", nodes)
                # Print output of 08 or 11 or 15
                if '11_B01_Priority_And_Payload' in runData:
                    print("  11_B01 output:", json.dumps(runData['11_B01_Priority_And_Payload'], ensure_ascii=False)[:300])
                if '15_Send_Final_Confirmation_To_Chat' in runData:
                    print("  15_Send output:", json.dumps(runData['15_Send_Final_Confirmation_To_Chat'], ensure_ascii=False)[:300])
    except Exception as e:
        pass
