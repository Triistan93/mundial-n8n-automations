import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "X-N8N-API-KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU"
}

url = "https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions/563289?includeData=true"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

run_data = data.get('data', {}).get('resultData', {}).get('runData', {})
print("Nodes executed in 563289:")
for k in run_data.keys():
    print(f" - {k}")

if 'AI Agent' in run_data:
    print("\nAI Agent output:")
    print(json.dumps(run_data['AI Agent'][0]['data']['main'], indent=2, ensure_ascii=False))

if 'Formatar Output do Agente' in run_data:
    print("\nFormatar Output do Agente:")
    print(json.dumps(run_data['Formatar Output do Agente'][0]['data']['main'], indent=2, ensure_ascii=False))
