# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions'
r = requests.get(url, headers={'X-N8N-API-KEY': API_KEY}, params={'workflowId': 'crMragbg2AOehF0d', 'limit': 3})
execs = r.json().get('data', [])
print(f"Total execs: {len(execs)}")
for e in execs:
    print(f"ID: {e.get('id')} | Status: {e.get('status')} | Mode: {e.get('mode')} | Finished: {e.get('finished')}")
    eid = e.get('id')
    det = requests.get(f"{url}/{eid}", headers={'X-N8N-API-KEY': API_KEY}, params={'includeData': 'true'}).json()
    err = det.get('data', {}).get('resultData', {}).get('error')
    if err:
        print("  ERRO:", json.dumps(err, indent=2))
    else:
        run_data = det.get('data', {}).get('resultData', {}).get('runData', {})
        print("  Nós executados com sucesso:", list(run_data.keys()))
