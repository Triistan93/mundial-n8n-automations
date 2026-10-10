# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/SN79HS84IAi8ueJq'

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
        'id': 'openai_test',
        'name': 'OpenAI_Test',
        'type': 'n8n-nodes-base.httpRequest',
        'typeVersion': 4.2,
        'position': [350, 300],
        'parameters': {
            'method': 'POST',
            'url': 'https://api.openai.com/v1/chat/completions',
            'authentication': 'predefinedCredentialType',
            'nodeCredentialType': 'openAiApi',
            'sendBody': True,
            'specifyBody': 'json',
            'jsonBody': json.dumps({
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": "Teste rápido de conexão n8n e OpenAI. Responda apenas: CONECTADO COM SUCESSO."}
                ],
                "max_tokens": 20
            }),
            'options': {}
        },
        'credentials': {
            'openAiApi': {
                'id': 'zJ462uvngfWgM0PB',
                'name': 'OpenAi account 3'
            }
        }
    }
]

connections = {
    'Webhook': {
        'main': [[{'node': 'OpenAI_Test', 'type': 'main', 'index': 0}]]
    }
}

payload = {
    'name': 'TEST_OPENAI_CALL',
    'nodes': nodes,
    'connections': connections,
    'settings': {'executionOrder': 'v1'}
}

r = requests.put(N8N_URL, json=payload, headers={'X-N8N-API-KEY': API_KEY})
print('Update WF:', r.status_code)

url = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
r2 = requests.post(url, json={})
print('OpenAI Call Result:', r2.status_code, r2.text)
