# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

wf = {
    "name": "TEST_PGVECTOR_SEARCH",
    "nodes": [
        {
            "id": "search_webhook",
            "name": "Search_Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [-300, 300],
            "parameters": {
                "httpMethod": "POST",
                "path": "kb-ti-search",
                "responseMode": "lastNode",
                "options": {}
            }
        },
        {
            "id": "pgvector_retrieve",
            "name": "Postgres_PGVector_Retrieve",
            "type": "@n8n/n8n-nodes-langchain.vectorStorePGVector",
            "typeVersion": 1.3,
            "position": [0, 300],
            "parameters": {
                "mode": "retrieve",
                "tableName": "kb_ti_conhecimento",
                "topK": 3,
                "prompt": "={{ $json.body.query || $json.query }}"
            },
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        },
        {
            "id": "openai_embed_search",
            "name": "Embeddings_OpenAI",
            "type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
            "typeVersion": 1.2,
            "position": [0, 500],
            "parameters": {
                "options": {}
            },
            "credentials": {
                "openAiApi": {
                    "id": "zJ462uvngfWgM0PB",
                    "name": "OpenAi account 3"
                }
            }
        }
    ],
    "connections": {
        "Search_Webhook": {
            "main": [[{"node": "Postgres_PGVector_Retrieve", "type": "main", "index": 0}]]
        },
        "Embeddings_OpenAI": {
            "ai_embedding": [[{"node": "Postgres_PGVector_Retrieve", "type": "ai_embedding", "index": 0}]]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

print("Deployando TEST_PGVECTOR_SEARCH no n8n...")
resp = requests.post(N8N_URL, headers=headers, json=wf)
print("Status:", resp.status_code)
if resp.status_code in [200, 201]:
    wf_id = resp.json().get("id")
    print("Workflow ID:", wf_id)
    act = requests.post(f"{N8N_URL}/{wf_id}/activate", headers=headers)
    print("Ativação:", act.status_code)
else:
    print("Erro:", resp.text)
