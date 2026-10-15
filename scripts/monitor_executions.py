import requests
import json
import time

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
headers = {'X-N8N-API-KEY': API_KEY}

print("Checking latest executions...")
r = requests.get('https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions?workflowId=c0F2GUMFm2BI94UG&limit=5', headers=headers)
executions = r.json().get('data', [])
for ex in executions:
    print(f"ID: {ex.get('id')}, Status: {ex.get('status')}, Mode: {ex.get('mode')}, Started: {ex.get('startedAt')}, Finished: {ex.get('stoppedAt')}")
