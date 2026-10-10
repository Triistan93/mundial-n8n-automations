# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1'
headers = {'X-N8N-API-KEY': API_KEY}

tag_id = 'LqCvrBiHyqG4x9ug' # Central TI

target_workflows = [
    'c0F2GUMFm2BI94UG', # BITRIX_TI_AI_TRIAGE_AGENT
    'PdpgXjbRMygjaL25', # BITRIX_TI_DIAGNOSTIC_TOOLS
    'SN79HS84IAi8ueJq', # TEST_SQL_RUNNER
    'crMragbg2AOehF0d', # KB_TI_PGVECTOR_INGESTION
    'uRjdQlM8edLyKmQO', # BITRIX_TI_PURCHASE_APPROVAL_HANDLER
]

print("Applying tag 'Central TI' to all 5 workflows...")
for w_id in target_workflows:
    r = requests.put(f'{url}/workflows/{w_id}/tags', json=[{'id': tag_id}], headers=headers)
    print(f"Workflow {w_id} - Tag status: {r.status_code}")
    
    r2 = requests.get(f'{url}/workflows/{w_id}', headers=headers)
    wf_data = r2.json()
    t_names = [t.get('name') for t in wf_data.get('tags', [])]
    print(f"  -> Nome: {wf_data.get('name')} | Tags: {t_names}")
