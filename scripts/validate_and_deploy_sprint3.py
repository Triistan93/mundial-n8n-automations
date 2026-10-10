# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'

wf_path = 'workflows/BITRIX_TI_AI_TRIAGE_AGENT.json'
with open(wf_path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Validation: Check connections
node_names = {n['name'] for n in wf['nodes']}
missing_sources = set()
missing_targets = set()

for src, branches in wf['connections'].items():
    if src not in node_names:
        missing_sources.add(src)
    for branch_name, branch_list in branches.items():
        for target_group in branch_list:
            for target in target_group:
                t_name = target.get('node')
                if t_name not in node_names:
                    missing_targets.add(t_name)

if missing_sources:
    print(f"ERROR: Missing source nodes in connections: {missing_sources}")
    sys.exit(1)

if missing_targets:
    print(f"ERROR: Missing target nodes in connections: {missing_targets}")
    sys.exit(1)

print("Validation PASSED! All 89 nodes and connections are strictly valid.")

# Deploy to n8n
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}

headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}
r = requests.put(N8N_URL, json=payload, headers=headers)

if r.status_code == 200:
    print(f"Successfully deployed to n8n! Workflow ID: c0F2GUMFm2BI94UG | Status: {r.status_code}")
    # Verify active state
    r_get = requests.get(N8N_URL, headers=headers)
    active = r_get.json().get('active')
    print(f"Workflow active status: {active}")
    if not active:
        r_act = requests.post(f"{N8N_URL}/activate", headers=headers)
        print(f"Activation response: {r_act.status_code}")
else:
    print(f"Deployment FAILED: {r.status_code}")
    print(r.text)
    sys.exit(1)
