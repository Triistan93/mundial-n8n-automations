# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/SN79HS84IAi8ueJq'

r = requests.get(N8N_URL, headers={'X-N8N-API-KEY': API_KEY})
wf = r.json()
payload = {
    'name': 'TEST_SQL_RUNNER',
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}
for n in payload['nodes']:
    if n['name'] == 'Run_SQL':
        n['parameters']['query'] = '={{ $json.body.query }}'

r = requests.put(N8N_URL, json=payload, headers={'X-N8N-API-KEY': API_KEY})
print('Update WF:', r.status_code)
