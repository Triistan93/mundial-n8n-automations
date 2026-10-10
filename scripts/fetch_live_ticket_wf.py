import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'

headers = {'X-N8N-API-KEY': API_KEY}
r = requests.get(N8N_URL, headers=headers)

if r.status_code == 200:
    data = r.json()
    print(f"Downloaded workflow: {data.get('name')} | ID: {data.get('id')}")
    print(f"Active: {data.get('active')}")
    print(f"Total nodes: {len(data.get('nodes', []))}")
    with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT_LIVE.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Saved to workflows/BITRIX_TI_AI_TRIAGE_AGENT_LIVE.json")
else:
    print(f"Error fetching workflow: {r.status_code} - {r.text}")
