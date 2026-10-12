import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "X-N8N-API-KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU"
}

url = "https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions?workflowId=8OvNSMmZFZWxiW9A&limit=20"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

for item in data.get('data', []):
    eid = item['id']
    u = f"https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions/{eid}?includeData=true"
    r = urllib.request.Request(u, headers=headers)
    with urllib.request.urlopen(r) as rep:
        edata = json.loads(rep.read().decode('utf-8'))
    run_data = edata.get('data', {}).get('resultData', {}).get('runData', {})
    has_create = 'Criar Novo Deal' in run_data or 'Atualizar Deal Existente' in run_data or 'Bitrix: Criar Deal (Contato Novo)1' in run_data or 'Bitrix: Criar Deal (Contato Existente)1' in run_data
    if has_create:
        print(f"\nExecution {eid} ({item.get('startedAt')}):")
        for node in ['Criar Novo Deal', 'Atualizar Deal Existente', 'Bitrix: Criar Deal (Contato Novo)1', 'Bitrix: Criar Deal (Contato Existente)1']:
            if node in run_data:
                print(f"  Ran {node}:")
                print(json.dumps(run_data[node][0]['data']['main'], indent=2, ensure_ascii=False)[:500])
        if 'Formatar Output do Agente' in run_data:
            print("  Agent Formatted Output:")
            print(json.dumps(run_data['Formatar Output do Agente'][0]['data']['main'], indent=2, ensure_ascii=False)[:500])
