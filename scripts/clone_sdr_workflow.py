# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_BASE = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows'

# Load canonical SDR workflow with Bento Grid layout
with open('c:/mundial-n8n-automations/workflows/canonical/SDR_Mundial_Motos_Unificado.json', 'r', encoding='utf-8') as f:
    prod_wf = json.load(f)

# Clone object
clone_wf = {
    'name': '[HOMOLOG] SDR - Mundial Motos (Unificado)',
    'nodes': prod_wf['nodes'],
    'connections': prod_wf['connections'],
    'settings': prod_wf.get('settings', {})
}

# Update Webhook path to avoid collision with production 'testesdr'
for n in clone_wf['nodes']:
    if n['name'] == 'Webhook' and n['type'] == 'n8n-nodes-base.webhook':
        n['parameters']['path'] = 'testesdr-homolog'
        print("Webhook path ajustado para: 'testesdr-homolog'")

headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}
r = requests.post(N8N_BASE, json=clone_wf, headers=headers)

if r.status_code in [200, 201]:
    data = r.json()
    new_id = data.get('id')
    print(f"\nSUCESSO: Fluxo de homologação criado!")
    print(f"Nome: {data.get('name')}")
    print(f"Novo Workflow ID: {new_id}")
    print(f"Link no n8n: https://sophia-n8nsophia.timft8.easypanel.host/workflow/{new_id}")
    
    # Save local file
    homolog_file = 'c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_HOMOLOG.json'
    with open(homolog_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Salvo localmente em: {homolog_file}")
    
    # Activate clone
    r_act = requests.post(f"{N8N_BASE}/{new_id}/activate", headers=headers)
    print(f"Ativação do clone: HTTP {r_act.status_code}")
else:
    print(f"Erro ao criar clone: {r.status_code} - {r.text}")
    sys.exit(1)
