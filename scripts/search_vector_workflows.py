# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows'
wfs = requests.get(url, headers={'X-N8N-API-KEY': API_KEY}).json().get('data', [])

print("Buscando workflows com Vector Store ou Embeddings...")
for w in wfs:
    wid = w.get('id')
    w_detail = requests.get(f'{url}/{wid}', headers={'X-N8N-API-KEY': API_KEY}).json()
    for n in w_detail.get('nodes', []):
        t = n.get('type', '')
        if 'vector' in t.lower() or 'embedding' in t.lower():
            print(f"WF: '{w.get('name')}' ({wid}) -> Node: '{n.get('name')}' ({t}) | Creds: {n.get('credentials')}")
