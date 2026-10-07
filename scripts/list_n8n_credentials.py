# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/credentials'
r = requests.get(url, headers={'X-N8N-API-KEY': API_KEY})
creds = r.json().get('data', [])
print(f"Total de credenciais cadastradas: {len(creds)}")
for c in creds:
    print(f"ID: {c.get('id')} | Type: {c.get('type')} | Name: {c.get('name')}")
