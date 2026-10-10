# -*- coding: utf-8 -*-
import requests
import json
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'
dialog_id = 'chat855770'
file_id = 7163904

# 1. Get download URL
r1 = requests.get(webhook + 'im.v2.File.download', params={'dialogId': dialog_id, 'fileId': file_id})
download_url = r1.json().get('result', {}).get('downloadUrl')
print("Download URL obtained:", bool(download_url))

# 2. Download binary
r2 = requests.get(download_url)
print("Binary downloaded:", r2.status_code, len(r2.content), "bytes")
b64_image = base64.b64encode(r2.content).decode('utf-8')

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
        'id': 'prep_vision',
        'name': 'Prep_Vision',
        'type': 'n8n-nodes-base.function',
        'typeVersion': 1,
        'position': [350, 300],
        'parameters': {
            'functionCode': '''
            const item = $input.first().json;
            const b64 = item.body?.b64 || item.b64;
            return [{
                json: {
                    model: "gpt-4o-mini",
                    messages: [
                        {
                            role: "system",
                            content: "Voce e um assistente de OCR de TI para a Mundial Honda. Descreva brevemente o que ve na imagem."
                        },
                        {
                            role: "user",
                            content: [
                                { type: "text", text: "O que ha nesta imagem?" },
                                { type: "image_url", image_url: { url: "data:image/png;base64," + b64 } }
                            ]
                        }
                    ],
                    max_tokens: 100
                }
            }];
            '''
        }
    },
    {
        'id': 'call_openai',
        'name': 'Call_OpenAI',
        'type': 'n8n-nodes-base.httpRequest',
        'typeVersion': 4.2,
        'position': [600, 300],
        'parameters': {
            'method': 'POST',
            'url': 'https://api.openai.com/v1/chat/completions',
            'authentication': 'predefinedCredentialType',
            'nodeCredentialType': 'openAiApi',
            'sendBody': True,
            'specifyBody': 'json',
            'jsonBody': '={{ JSON.stringify($json) }}',
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
    'Webhook': {'main': [[{'node': 'Prep_Vision', 'type': 'main', 'index': 0}]]},
    'Prep_Vision': {'main': [[{'node': 'Call_OpenAI', 'type': 'main', 'index': 0}]]}
}

payload = {
    'name': 'TEST_OPENAI_VISION',
    'nodes': nodes,
    'connections': connections,
    'settings': {'executionOrder': 'v1'}
}

r_up = requests.put(N8N_URL, json=payload, headers={'X-N8N-API-KEY': API_KEY})
print('Update WF status:', r_up.status_code)

r_call = requests.post('https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search', json={'b64': b64_image})
print('Vision Call status:', r_call.status_code)
res = r_call.json()
print('Vision Response:', res.get('choices', [{}])[0].get('message', {}).get('content'))
