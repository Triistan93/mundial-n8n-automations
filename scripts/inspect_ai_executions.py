import requests
import json

api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions'
r = requests.get(url, headers={'X-N8N-API-KEY': api_key}, params={'workflowId': 'c0F2GUMFm2BI94UG', 'limit': 20})
execs = r.json().get('data', [])

print(f"Total executions fetched: {len(execs)}")
for e in execs:
    eid = e.get('id')
    detail = requests.get(f'{url}/{eid}', headers={'X-N8N-API-KEY': api_key}, params={'includeData': 'true'}).json()
    rd = detail.get('data', {}).get('resultData', {}).get('runData', {})
    
    if '08_AI_Agent_Triage_Deal' in rd:
        print(f"\n=== Exec {eid} (AI Agent) ===")
        ai_in = rd.get('07_Prepare_AI_Deal_Input', [{}])[0].get('data', {}).get('main', [[]])[0]
        ai_out = rd.get('08_AI_Agent_Triage_Deal', [{}])[0].get('data', {}).get('main', [[]])[0]
        for item in ai_in:
            print("USER INPUT:", item.get('json', {}).get('full_user_input'))
        for item in ai_out:
            out_txt = item.get('json', {}).get('output') or item.get('json', {}).get('text')
            print("AI OUTPUT:\n", out_txt)
            
    if '14_Add_Timeline_Milestone_Comment' in rd:
        print(f"\n=== Exec {eid} (Timeline Milestone) ===")
        tl_items = rd.get('14_Add_Timeline_Milestone_Comment', [{}])[0].get('data', {}).get('main', [[]])[0]
        for t in tl_items:
            print("Timeline comment response:", t.get('json'))
