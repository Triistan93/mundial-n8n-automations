# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/uRjdQlM8edLyKmQO'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

r = requests.get(url, headers=headers).json()

for n in r.get('nodes', []):
    if n['name'] == 'Bitrix_Update_Deal_Stage':
        n['parameters']['jsonBody'] = "={{ JSON.stringify({\n  id: $json.deal_id,\n  fields: {\n    STAGE_ID: $json.target_stage,\n    UF_CRM_TI_RESPONSIBLE: $json.user_id\n  }\n}) }}"

deploy_payload = {
    "name": r["name"],
    "nodes": r["nodes"],
    "connections": r["connections"],
    "settings": r.get("settings", {})
}

resp = requests.put(url, headers=headers, json=deploy_payload)
print("Update BITRIX_TI_PURCHASE_APPROVAL_HANDLER status:", resp.status_code)
