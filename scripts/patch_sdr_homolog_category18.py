# -*- coding: utf-8 -*-
import json
import requests

WORKFLOW_FILE = "c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_HOMOLOG.json"
N8N_WORKFLOW_ID = "5pFwAtQWvsuhyxO0"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU"
N8N_BASE_URL = "https://sophia-n8nsophia.timft8.easypanel.host/api/v1"

with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
    wf = json.load(f)

for node in wf.get("nodes", []):
    if node["name"] == "Montar URL de Busca":
        old_js = node["parameters"]["jsCode"]
        new_js = """const isolarData = $('Garantir Contato com Chat na Linha').first().json;
const ids = isolarData.contactIds || [];
const dadosLead = $('1. Preparar Dados Lead').first().json;
const categoriaSDR = Number(dadosLead.CategoriaBitrix || 18);

const baseUrl = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.deal.list.json";

// Busca Específica no Funil SDR: Seleciona APENAS cards da Categoria 18 (Vendas Outras Mídias)
const params = {
    "filter[CATEGORY_ID]": categoriaSDR,
    "select[0]": "ID",
    "select[1]": "TITLE",
    "select[2]": "STAGE_ID",
    "select[3]": "CATEGORY_ID",
    "select[4]": "STAGE_SEMANTIC_ID",
    "order[ID]": "DESC"
};

if (!ids.length) {
    params["filter[ID]"] = 0;
} else {
    ids.forEach((id, index) => {
        params[`filter[CONTACT_ID][${index}]`] = id;
    });
}

const queryString = Object.entries(params)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join("&");

return [
    {
        json: {
            ...isolarData,
            finalUrl: `${baseUrl}?${queryString}`
        }
    }
];"""
        node["parameters"]["jsCode"] = new_js
        print("Montar URL de Busca atualizado com sucesso!")

with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

# Deploy para o n8n
headers = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "name": wf.get("name", "[HOMOLOG] SDR - Mundial Motos (Unificado)"),
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

r = requests.put(f"{N8N_BASE_URL}/workflows/{N8N_WORKFLOW_ID}", headers=headers, json=payload)
print(f"Deploy no n8n: HTTP {r.status_code}")
if r.status_code == 200:
    print("Workflow de Homologação atualizado no n8n com sucesso!")
else:
    print("Erro no deploy:", r.text[:300])
