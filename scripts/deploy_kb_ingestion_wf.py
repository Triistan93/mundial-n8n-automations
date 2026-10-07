# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# Load documents
with open(r"C:\mundial-n8n-automations\scripts\kb_docs_for_ingestion.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

# Embed documents in Code node as fallback so workflow can run self-contained anytime
docs_json_str = json.dumps(docs, ensure_ascii=False)

wf = {
    "name": "KB_TI_PGVECTOR_INGESTION",
    "nodes": [
        {
            "id": "trigger_manual",
            "name": "Manual_Trigger_Ingestion",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [-300, 200]
        },
        {
            "id": "trigger_webhook",
            "name": "Webhook_Ingest_KB",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [-300, 400],
            "parameters": {
                "httpMethod": "POST",
                "path": "kb-ti-ingest",
                "responseMode": "onReceived",
                "options": {}
            }
        },
        {
            "id": "node_prepare_docs",
            "name": "Prepare_KB_Documents",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [0, 300],
            "parameters": {
                "jsCode": f"""
// Se receber docs pelo webhook (body), usa eles. Senão usa o catálogo de 13 KBs embutido.
const incoming = $input.all();
if (incoming.length > 0 && incoming[0].json.body && Array.isArray(incoming[0].json.body.documents)) {{
    return incoming[0].json.body.documents.map(d => ({{ json: d }}));
}}

const defaultDocs = {docs_json_str};
return defaultDocs.map(d => ({{ json: d }}));
"""
            }
        },
        {
            "id": "node_pgvector_insert",
            "name": "Postgres_PGVector_Insert",
            "type": "@n8n/n8n-nodes-langchain.vectorStorePGVector",
            "typeVersion": 1.3,
            "position": [360, 300],
            "parameters": {
                "mode": "insert",
                "tableName": "kb_ti_conhecimento",
                "options": {}
            },
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        },
        {
            "id": "node_data_loader",
            "name": "Default_Data_Loader",
            "type": "@n8n/n8n-nodes-langchain.documentDefaultDataLoader",
            "typeVersion": 1,
            "position": [420, 500],
            "parameters": {
                "jsonMode": "expressionData",
                "jsonData": "={{ $json.text }}",
                "options": {
                    "metadata": {
                        "metadataValues": [
                            {"name": "kb_id", "value": "={{ $json.kb_id }}"},
                            {"name": "title", "value": "={{ $json.title }}"},
                            {"name": "systems", "value": "={{ $json.systems }}"},
                            {"name": "keywords", "value": "={{ $json.keywords }}"},
                            {"name": "source", "value": "={{ $json.source }}"}
                        ]
                    }
                }
            }
        },
        {
            "id": "node_text_splitter",
            "name": "Recursive_Text_Splitter",
            "type": "@n8n/n8n-nodes-langchain.textSplitterRecursiveCharacterTextSplitter",
            "typeVersion": 1,
            "position": [440, 680],
            "parameters": {
                "chunkSize": 800,
                "chunkOverlap": 120,
                "options": {}
            }
        },
        {
            "id": "node_openai_embeddings",
            "name": "Embeddings_OpenAI",
            "type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
            "typeVersion": 1.2,
            "position": [300, 500],
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
        "Manual_Trigger_Ingestion": {
            "main": [[{"node": "Prepare_KB_Documents", "type": "main", "index": 0}]]
        },
        "Webhook_Ingest_KB": {
            "main": [[{"node": "Prepare_KB_Documents", "type": "main", "index": 0}]]
        },
        "Prepare_KB_Documents": {
            "main": [[{"node": "Postgres_PGVector_Insert", "type": "main", "index": 0}]]
        },
        "Default_Data_Loader": {
            "ai_document": [[{"node": "Postgres_PGVector_Insert", "type": "ai_document", "index": 0}]]
        },
        "Recursive_Text_Splitter": {
            "ai_textSplitter": [[{"node": "Default_Data_Loader", "type": "ai_textSplitter", "index": 0}]]
        },
        "Embeddings_OpenAI": {
            "ai_embedding": [[{"node": "Postgres_PGVector_Insert", "type": "ai_embedding", "index": 0}]]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

print("Deployando workflow KB_TI_PGVECTOR_INGESTION no n8n...")
resp = requests.post(N8N_URL, headers=headers, json=wf)
print("Status code:", resp.status_code)
if resp.status_code in [200, 201]:
    wf_id = resp.json().get("id")
    print(f"Workflow criado com sucesso! ID: {wf_id}")
    
    # Ativar workflow para que o webhook funcione
    act_resp = requests.post(f"{N8N_URL}/{wf_id}/activate", headers=headers)
    print("Ativação do workflow:", act_resp.status_code)
else:
    print("Erro:", resp.text)
