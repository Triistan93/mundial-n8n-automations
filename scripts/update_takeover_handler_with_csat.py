# -*- coding: utf-8 -*-
"""
Atualiza o workflow BITRIX_TI_TICKET_TAKEOVER_HANDLER (bf78RZqHZe5gjk9E)
adicionando o endpoint de votação de satisfação 1-clique (/webhook/ti-csat-vote).
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_BASE = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

wf_id = 'bf78RZqHZe5gjk9E'
r = requests.get(f"{N8N_BASE}/workflows/{wf_id}", headers=headers).json()

nodes = r['nodes']
connections = r['connections']

# Adiciona nós de CSAT se não existirem
csat_nodes = [
    {
        "id": "wh_csat_vote",
        "name": "Webhook_CSAT_Vote",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [-300, 650],
        "parameters": {
            "httpMethod": "GET",
            "path": "ti-csat-vote",
            "responseMode": "responseNode",
            "options": {}
        }
    },
    {
        "id": "code_parse_csat",
        "name": "Parse_CSAT_Params",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-60, 650],
        "parameters": {
            "jsCode": """
const query = $input.first().json.query || {};
const dealId = Number(query.deal_id);
let rating = parseInt(query.rating || query.stars || 5, 10);
if (isNaN(rating) || rating < 1) rating = 1;
if (rating > 5) rating = 5;

if (!dealId) {
  throw new Error("Parâmetro 'deal_id' é obrigatório.");
}

const starsStr = '⭐'.repeat(rating);
const labels = {
  5: 'Excelente',
  4: 'Muito Bom',
  3: 'Regular',
  2: 'Ruim',
  1: 'Precisa Melhorar'
};

return [{
  json: {
    deal_id: dealId,
    rating: rating,
    stars_str: starsStr,
    rating_label: labels[rating] || 'Avaliado'
  }
}];
"""
        }
    },
    {
        "id": "pg_insert_csat",
        "name": "Insert_CSAT_Database",
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 1,
        "position": [180, 650],
        "onError": "continueRegularOutput",
        "parameters": {
            "operation": "executeQuery",
            "query": "INSERT INTO ticket_csat_ratings (deal_id, requester_user_id, rating, feedback_text, created_at) VALUES ({{ $json.deal_id }}, COALESCE((SELECT requester_user_id FROM ticket_bot_sessions WHERE deal_id = {{ $json.deal_id }}), 32598), {{ $json.rating }}, 'Avaliação 1-clique via chat', NOW()) RETURNING id;",
            "additionalFields": {}
        },
        "credentials": {
            "postgres": {
                "id": "J8q2YHlBbp4WxxV2",
                "name": "Postgres account"
            }
        }
    },
    {
        "id": "http_csat_timeline",
        "name": "Bitrix_CSAT_Timeline",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [420, 650],
        "onError": "continueRegularOutput",
        "parameters": {
            "method": "POST",
            "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.timeline.comment.add",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({\n  fields: {\n    ENTITY_ID: $('Parse_CSAT_Params').first().json.deal_id,\n    ENTITY_TYPE: 'deal',\n    COMMENT: $('Parse_CSAT_Params').first().json.stars_str + ' **AVALIAÇÃO DE ATENDIMENTO (CSAT) REGISTRADA!**\\n\\n• **Nota:** ' + $('Parse_CSAT_Params').first().json.rating + '/5 (' + $('Parse_CSAT_Params').first().json.rating_label + ')\\n• **Origem:** Votação rápida de 1 clique no chat\\n\\n✅ *Registrado na base de qualidade de TI.*'\n  }\n}) }}",
            "options": {}
        }
    },
    {
        "id": "code_csat_html",
        "name": "Generate_CSAT_HTML",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [660, 650],
        "parameters": {
            "jsCode": """
const ctx = $('Parse_CSAT_Params').first().json;
const dealUrl = `https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${ctx.deal_id}/`;

const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Obrigado pela sua Avaliação! - Central de TI Mundial</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #0f172a;
      color: #f8fafc;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 16px;
    }
    .card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 32px;
      max-width: 480px;
      width: 100%;
      text-align: center;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .stars {
      font-size: 40px;
      margin-bottom: 12px;
      letter-spacing: 4px;
    }
    h1 {
      font-size: 22px;
      margin: 0 0 12px;
      color: #f8fafc;
    }
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      background: #10b98122;
      color: #10b981;
      border: 1px solid #10b98144;
      margin-bottom: 16px;
    }
    p {
      color: #94a3b8;
      font-size: 15px;
      line-height: 1.6;
      margin: 0 0 24px;
    }
    .footer {
      margin-top: 24px;
      font-size: 12px;
      color: #64748b;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="stars">${ctx.stars_str}</div>
    <div class="badge">NOTA ${ctx.rating}/5 — ${ctx.rating_label.toUpperCase()}</div>
    <h1>Avaliação Registrada!</h1>
    <p>Muito obrigado pelo seu feedback sobre o atendimento do chamado <strong>#${ctx.deal_id}</strong>. Sua avaliação foi salva com sucesso e ajuda a equipe de TI a melhorar continuamente o suporte da Mundial!</p>
    <div class="footer">Central de TI — Concessionárias Mundial Honda</div>
  </div>
</body>
</html>`;

return [{
  json: {
    html: html
  }
}];
"""
        }
    },
    {
        "id": "resp_csat_webhook",
        "name": "Respond_CSAT_Webhook",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.1,
        "position": [900, 650],
        "parameters": {
            "respondWith": "text",
            "responseBody": "={{ $json.html }}",
            "options": {
                "responseHeaders": {
                    "entries": [
                        {"name": "Content-Type", "value": "text/html; charset=utf-8"}
                    ]
                }
            }
        }
    }
]

# Atualiza ou adiciona nós de CSAT
existing_node_map = {n['name']: n for n in nodes}
for cn in csat_nodes:
    if cn['name'] in existing_node_map:
        existing_node_map[cn['name']]['parameters'] = cn['parameters']
        existing_node_map[cn['name']]['onError'] = cn.get('onError', 'continueRegularOutput')
    else:
        nodes.append(cn)

# Conexões do fluxo CSAT
connections["Webhook_CSAT_Vote"] = {"main": [[{"node": "Parse_CSAT_Params", "type": "main", "index": 0}]]}
connections["Parse_CSAT_Params"] = {"main": [[{"node": "Insert_CSAT_Database", "type": "main", "index": 0}]]}
connections["Insert_CSAT_Database"] = {"main": [[{"node": "Bitrix_CSAT_Timeline", "type": "main", "index": 0}]]}
connections["Bitrix_CSAT_Timeline"] = {"main": [[{"node": "Generate_CSAT_HTML", "type": "main", "index": 0}]]}
connections["Generate_CSAT_HTML"] = {"main": [[{"node": "Respond_CSAT_Webhook", "type": "main", "index": 0}]]}

payload = {
    "name": r["name"],
    "nodes": nodes,
    "connections": connections,
    "settings": r.get("settings", {})
}

put_resp = requests.put(f"{N8N_BASE}/workflows/{wf_id}", headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Workflow BITRIX_TI_TICKET_TAKEOVER_HANDLER atualizado com CSAT Vote com sucesso!")
    # Exporta backup local
    open(r'c:\mundial-n8n-automations\workflows\BITRIX_TI_TICKET_TAKEOVER_HANDLER.json', 'w', encoding='utf-8').write(
        json.dumps(put_resp.json(), indent=2, ensure_ascii=False)
    )
else:
    print(f"Erro ao atualizar: {put_resp.status_code} - {put_resp.text}")
    sys.exit(1)
