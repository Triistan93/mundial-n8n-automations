# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/SN79HS84IAi8ueJq'

r = requests.get(N8N_URL, headers={'X-N8N-API-KEY': API_KEY})
wf = r.json()

nodes = [
    {
        'id': 'webhook',
        'name': 'Webhook',
        'type': 'n8n-nodes-base.webhook',
        'typeVersion': 2,
        'position': [100, 300],
        'parameters': {
            'httpMethod': 'POST',
            'path': 'kb-ti-search',
            'responseMode': 'lastNode',
            'options': {}
        }
    },
    {
        'id': 'run_sql',
        'name': 'Run_SQL',
        'type': 'n8n-nodes-base.postgres',
        'typeVersion': 1,
        'position': [350, 300],
        'parameters': {
            'operation': 'executeQuery',
            'query': '={{ $json.body.query }}'
        },
        'credentials': {
            'postgres': {
                'id': 'J8q2YHlBbp4WxxV2',
                'name': 'Postgres account'
            }
        }
    },
    {
        'id': 'aggregate_rows',
        'name': 'Aggregate_Rows',
        'type': 'n8n-nodes-base.function',
        'typeVersion': 1,
        'position': [600, 300],
        'parameters': {
            'functionCode': 'const all = $input.all(); return [{ json: { count: all.length, rows: all.map(i => i.json) } }];'
        }
    }
]

connections = {
    'Webhook': {
        'main': [[{'node': 'Run_SQL', 'type': 'main', 'index': 0}]]
    },
    'Run_SQL': {
        'main': [[{'node': 'Aggregate_Rows', 'type': 'main', 'index': 0}]]
    }
}

payload = {
    'name': 'TEST_SQL_RUNNER',
    'nodes': nodes,
    'connections': connections,
    'settings': {'executionOrder': 'v1'}
}

r2 = requests.put(N8N_URL, json=payload, headers={'X-N8N-API-KEY': API_KEY})
print('Update WF:', r2.status_code)
