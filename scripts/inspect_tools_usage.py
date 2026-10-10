# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows'

r = requests.get(url, headers={'X-N8N-API-KEY': API_KEY})
wfs = r.json().get('data', [])

for w in wfs:
    rw = requests.get(f"{url}/{w['id']}", headers={'X-N8N-API-KEY': API_KEY})
    for n in rw.json().get('nodes', []):
        t = n.get('type', '')
        if 'toolhttprequest' in t.lower() or 'toolworkflow' in t.lower():
            print(f"WF: {w['name']} ({w['id']}) | Node: {n.get('name')} | Type: {t}")
            print(json.dumps(n, indent=2)[:500])
            print("------------------------------------------")
