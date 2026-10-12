# -*- coding: utf-8 -*-
import json
import sys
import requests

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
WORKFLOW_ID = '5pFwAtQWvsuhyxO0'
N8N_URL = f'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/{WORKFLOW_ID}'

homolog_file = 'c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_HOMOLOG.json'
with open(homolog_file, 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf['nodes']}

# Adiciona continueOnFail nos nós de envio WhatsApp para não travar homologação
for name in ['Enviar MSG (Continua o Papo)', 'Enviar MSG Final']:
    if name in nodes:
        nodes[name]['onError'] = 'continueRegularOutput'
        print(f"Adicionada tolerância a falhas no nó: {name}")

# Salva arquivo local
with open(homolog_file, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

# Deploy to n8n API
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}

headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}
r = requests.put(N8N_URL, json=payload, headers=headers)
print(f"Deploy no n8n ({WORKFLOW_ID}): HTTP {r.status_code}")
