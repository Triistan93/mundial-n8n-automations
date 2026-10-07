# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows'

r = requests.get(URL, headers={'X-N8N-API-KEY': API_KEY})
wfs = r.json().get('data', [])
print(f"Total workflows no n8n: {len(wfs)}")
for w in wfs:
    print(f"ID: {w.get('id')} | Active: {w.get('active')} | Name: {w.get('name')}")
