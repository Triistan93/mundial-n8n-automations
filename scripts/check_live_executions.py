# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions'
r = requests.get(url, params={'workflowId': 'c0F2GUMFm2BI94UG', 'limit': 8}, headers={'X-N8N-API-KEY': API_KEY})
for e in r.json().get('data', []):
    print(f"ID: {e['id']} | Status: {e['status']} | Mode: {e['mode']} | CreatedAt: {e['createdAt']}")
