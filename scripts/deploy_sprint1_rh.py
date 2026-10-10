import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "X-N8N-API-KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU",
    "Content-Type": "application/json"
}

# Load updated workflow
with open(r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A_SPRINT1.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

# n8n update expects: name, nodes, connections, settings
update_payload = {
    "name": wf.get("name", "Agente RH Com correções"),
    "nodes": wf.get("nodes", []),
    "connections": wf.get("connections", {}),
    "settings": wf.get("settings", {})
}

url = "https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/8OvNSMmZFZWxiW9A"
data = json.dumps(update_payload).encode('utf-8')

req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("✅ Workflow updated successfully via n8n API!")
        print(f"ID: {res.get('id')}")
        print(f"Name: {res.get('name')}")
        print(f"Active: {res.get('active')}")
        print(f"Nodes count: {len(res.get('nodes', []))}")
        print(f"Updated at: {res.get('updatedAt')}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"❌ Failed to update workflow: HTTP {e.code} - {err_body}")
