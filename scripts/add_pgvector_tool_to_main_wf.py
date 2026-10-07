# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

canonical_path = r"C:\mundial-n8n-automations\workflows\canonical\BITRIX_TI_AI_TRIAGE_AGENT.json"
with open(canonical_path, "r", encoding="utf-8") as f:
    wf = json.load(f)

# 1. Check if tool already exists
existing_names = [n.get("name") for n in wf["nodes"]]
if "KB_TI_PGVector_Tool" in existing_names:
    print("KB_TI_PGVector_Tool já existe no workflow. Pulando adição de nós.")
else:
    # 2. Add KB_TI_PGVector_Tool node
    kb_tool_node = {
        "parameters": {
            "mode": "retrieve-as-tool",
            "toolDescription": "Base de conhecimento oficial de TI da Concessionária Mundial Honda. Contém tutoriais, regras de negócio e procedimentos técnicos para MicroWork Cloud (ERP/DMS), RENAVE & ATPV, Bitrix24, Portais Honda (WebPeças, IHS), Plataforma FANDI, Impressoras e Scanners, Redes e Wi-Fi, Computador e E-mails. Use sempre para consultar o procedimento oficial antes de orientar o colaborador.",
            "tableName": "kb_ti_conhecimento",
            "topK": 3,
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.vectorStorePGVector",
        "typeVersion": 1.3,
        "position": [600, 560],
        "id": "node_kb_pgvector_tool",
        "name": "KB_TI_PGVector_Tool",
        "credentials": {
            "postgres": {
                "id": "J8q2YHlBbp4WxxV2",
                "name": "Postgres account"
            }
        }
    }

    # 3. Add Embeddings_OpenAI_KB node
    kb_embeddings_node = {
        "parameters": {
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
        "typeVersion": 1.2,
        "position": [600, 740],
        "id": "node_kb_embeddings_tool",
        "name": "Embeddings_OpenAI_KB",
        "credentials": {
            "openAiApi": {
                "id": "zJ462uvngfWgM0PB",
                "name": "OpenAi account 3"
            }
        }
    }

    wf["nodes"].append(kb_tool_node)
    wf["nodes"].append(kb_embeddings_node)

    # 4. Add connections
    if "KB_TI_PGVector_Tool" not in wf["connections"]:
        wf["connections"]["KB_TI_PGVector_Tool"] = {
            "ai_tool": [
                [
                    {
                        "node": "08_AI_Agent_Triage_Deal",
                        "type": "ai_tool",
                        "index": 0
                    }
                ]
            ]
        }
    if "Embeddings_OpenAI_KB" not in wf["connections"]:
        wf["connections"]["Embeddings_OpenAI_KB"] = {
            "ai_embedding": [
                [
                    {
                        "node": "KB_TI_PGVector_Tool",
                        "type": "ai_embedding",
                        "index": 0
                    }
                ]
            ]
        }

    print("Nós e conexões adicionados com sucesso.")

# 5. Update systemMessage in 08_AI_Agent_Triage_Deal to explicitly mention the tool
tool_guidance = """
# FERRAMENTAS DISPONÍVEIS:
1. Tool_Think_Deal: Use para estruturar seu raciocínio lógico antes de emitir a resposta final.
2. KB_TI_PGVector_Tool: BASE VETORIAL DE CONHECIMENTO OFICIAL DA CONCESSIONÁRIA MUNDIAL HONDA.
   - Use SEMPRE esta ferramenta para buscar procedimentos oficiais de atendimento ao receber qualquer problema relatado (MicroWork, RENAVE, Bitrix, Portais Honda, FANDI, Impressora, Rede, Computador, E-mail, Senhas).
   - Use o conteúdo retornado pela busca vetorial para orientar testes L1 precisos ao usuário.
"""

for n in wf["nodes"]:
    if n.get("name") == "08_AI_Agent_Triage_Deal":
        sm = n["parameters"]["options"]["systemMessage"]
        if "KB_TI_PGVector_Tool" not in sm:
            # Insert guidance right after the header
            header_target = "# PAPEL E OBJETIVO PRINCIPAL:\n"
            if header_target in sm:
                idx = sm.find(header_target) + len(header_target)
                sm = sm[:idx] + tool_guidance + "\n" + sm[idx:]
            else:
                sm = tool_guidance + "\n" + sm
            n["parameters"]["options"]["systemMessage"] = sm
            print("SystemMessage atualizado com diretrizes da ferramenta vetorial.")
        break

# 6. Save locally
with open(canonical_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print(f"Salvo arquivo canônico atualizado em {canonical_path}")

# 7. Deploy to n8n
deploy_payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

resp = requests.put(N8N_URL, headers=headers, json=deploy_payload)
print("Status do deploy no n8n:", resp.status_code)
if resp.status_code == 200:
    print("Workflow principal de atendimento atualizado com a ferramenta RAG!")
else:
    print("Erro no deploy:", resp.text)
