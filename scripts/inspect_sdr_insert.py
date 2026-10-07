# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/yYXjxaOaYVgFZbdG2I3FY'
wf = requests.get(url, headers={'X-N8N-API-KEY': API_KEY}).json()

for n in wf['nodes']:
    name = n.get('name', '').lower()
    t = n.get('type', '').lower()
    if 'insert' in name or 'loader' in t or 'splitter' in t:
        print(f"=== Node: {n.get('name')} ({n.get('type')}) ===")
        print(json.dumps(n, indent=2))
