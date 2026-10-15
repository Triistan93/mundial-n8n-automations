# -*- coding: utf-8 -*-
"""
Deploy do Workflow BITRIX_TI_TICKET_TAKEOVER_HANDLER no n8n.
Gerencia os cliques nos botões 'Aceitar Chamado' e 'Colocar na Fila',
atribuindo o técnico, mudando a etapa para 'C160:PREPARATION',
notificando o chat e travando o silêncio da Sophia AI (HUMAN_TAKEOVER).
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_BASE = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

workflow_data = {
    "name": "BITRIX_TI_TICKET_TAKEOVER_HANDLER",
    "nodes": [
        {
            "id": "wh_takeover",
            "name": "Webhook_Ticket_Action",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [-300, 300],
            "parameters": {
                "httpMethod": "GET",
                "path": "ti-ticket-action",
                "responseMode": "responseNode",
                "options": {}
            }
        },
        {
            "id": "code_parse",
            "name": "Parse_Action_Params",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [-60, 300],
            "parameters": {
                "jsCode": """
const query = $input.first().json.query || {};
const dealId = Number(query.deal_id);
const action = String(query.action || '').toLowerCase();
const userId = Number(query.user_id || query.user || 352678);

if (!dealId) {
  throw new Error("Parâmetro 'deal_id' é obrigatório.");
}

const isAccept = action === 'accept';
const targetStage = isAccept ? 'C160:PREPARATION' : 'C160:UC_JIOBG8';
const statusLabel = isAccept ? 'EM ATENDIMENTO' : 'NA FILA DA TI';
const actionEmoji = isAccept ? '👨‍💻' : '⏳';

return [{
  json: {
    deal_id: dealId,
    action: action,
    is_accept: isAccept,
    target_stage: targetStage,
    status_label: statusLabel,
    action_emoji: actionEmoji,
    user_id: userId
  }
}];
"""
            }
        },
        {
            "id": "pg_tech_lookup",
            "name": "Lookup_Technician_Name",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [180, 300],
            "parameters": {
                "operation": "executeQuery",
                "query": "SELECT COALESCE(NULLIF(TRIM(name || ' ' || last_name), ''), full_name, 'Técnico de TI') as tech_name, SPLIT_PART(TRIM(name), ' ', 1) as first_name FROM bitrix_users_cache WHERE user_id = {{ $json.user_id }};",
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
            "id": "code_merge_data",
            "name": "Merge_Context",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [420, 300],
            "parameters": {
                "jsCode": """
const params = $('Parse_Action_Params').first().json;
const techRow = $input.first()?.json || {};
const techName = techRow.tech_name || (params.user_id === 32598 ? 'Eduardo Alaminos' : 'Igor Bonini');
const firstName = techRow.first_name || (params.user_id === 32598 ? 'Eduardo' : 'Igor');

return [{
  json: {
    ...params,
    tech_name: techName,
    first_name: firstName
  }
}];
"""
            }
        },
        {
            "id": "http_update_deal",
            "name": "Bitrix_Update_Deal_Takeover",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [660, 300],
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.update",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  id: $json.deal_id,\n  fields: $json.is_accept ? {\n    STAGE_ID: $json.target_stage,\n    ASSIGNED_BY_ID: $json.user_id,\n    UF_CRM_TI_RESPONSIBLE: $json.user_id\n  } : {\n    STAGE_ID: $json.target_stage\n  }\n}) }}",
                "options": {}
            }
        },
        {
            "id": "pg_lock_session",
            "name": "Update_Postgres_Session_Silence",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [900, 300],
            "onError": "continueRegularOutput",
            "parameters": {
                "operation": "executeQuery",
                "query": "UPDATE ticket_bot_sessions SET status = CASE WHEN '{{ $('Merge_Context').first().json.action }}' = 'accept' THEN 'HUMAN_TAKEOVER' ELSE 'IN_QUEUE' END, ai_state = 'AI_PAUSED', last_interaction_at = NOW() WHERE deal_id = {{ $('Merge_Context').first().json.deal_id }};",
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
            "id": "http_get_chat",
            "name": "Bitrix_Get_Deal_Chat",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1140, 300],
            "parameters": {
                "method": "GET",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.chat.get",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {"name": "ENTITY_TYPE", "value": "CRM"},
                        {"name": "ENTITY_ID", "value": "={{ 'DEAL|' + $('Merge_Context').first().json.deal_id }}"}
                    ]
                },
                "options": {}
            }
        },
        {
            "id": "code_prepare_chat_msg",
            "name": "Prepare_Chat_And_Timeline",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1380, 300],
            "parameters": {
                "jsCode": """
const ctx = $('Merge_Context').first().json;
const chatData = $input.first().json.result || {};
const chatId = chatData.ID;

const chatMsg = ctx.is_accept 
  ? `👨‍💻 [b]Atendimento Assumido[/b]\\nO analista de TI [b]${ctx.tech_name}[/b] assumiu o atendimento do chamado #${ctx.deal_id}. A partir de agora, o suporte é realizado diretamente com o técnico humano.`
  : `⏳ [b]Fila de Espera[/b]\\nO chamado #${ctx.deal_id} foi posicionado na fila de atendimento da equipe de TI e será atendido em breve.`;

const timelineComment = ctx.is_accept
  ? `👨‍💻 **[TI - ATENDIMENTO ASSUMIDO]**\\n\\nO técnico **${ctx.tech_name}** (ID ${ctx.user_id}) aceitou o chamado #${ctx.deal_id} via botão interativo.\\n\\n• **Nova Etapa:** Em atendimento (C160:PREPARATION)\\n• **Técnico Responsável:** ${ctx.tech_name}\\n• **Sophia AI:** Silenciada com sucesso.`
  : `⏳ **[TI - FILA DE ESPERA]**\\n\\nO chamado #${ctx.deal_id} foi mantido na fila de espera da TI (C160:UC_JIOBG8).`;

return [{
  json: {
    ...ctx,
    chat_id: chatId,
    chat_message: chatMsg,
    timeline_comment: timelineComment
  }
}];
"""
            }
        },
        {
            "id": "http_send_chat",
            "name": "Bitrix_Send_Chat_Notice",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1620, 200],
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  DIALOG_ID: 'chat' + $json.chat_id,\n  MESSAGE: $json.chat_message\n}) }}",
                "options": {}
            }
        },
        {
            "id": "http_timeline",
            "name": "Bitrix_Add_Timeline",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1620, 400],
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.timeline.comment.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  fields: {\n    ENTITY_ID: $json.deal_id,\n    ENTITY_TYPE: 'deal',\n    COMMENT: $json.timeline_comment\n  }\n}) }}",
                "options": {}
            }
        },
        {
            "id": "code_html",
            "name": "Generate_HTML_Page",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1860, 300],
            "parameters": {
                "jsCode": """
const ctx = $('Merge_Context').first().json;
const isAccept = ctx.is_accept;
const title = isAccept ? 'Chamado Assumido com Sucesso!' : 'Chamado Colocado na Fila';
const badgeColor = isAccept ? '#10b981' : '#f59e0b';
const icon = isAccept ? '✅' : '⏳';
const desc = isAccept 
  ? `Você assumiu o chamado <strong>#${ctx.deal_id}</strong> com sucesso! O card foi movido para <strong>Em atendimento</strong> e a Sophia AI foi silenciada para você conversar diretamente com o solicitante.`
  : `O chamado <strong>#${ctx.deal_id}</strong> foi mantido na <strong>Fila da TI</strong> aguardando disponibilidade técnica.`;

const dealUrl = `https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${ctx.deal_id}/`;

const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} - Central de TI Mundial</title>
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
    .icon {
      font-size: 54px;
      margin-bottom: 16px;
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
      background: ${badgeColor}22;
      color: ${badgeColor};
      border: 1px solid ${badgeColor}44;
      margin-bottom: 16px;
    }
    p {
      color: #94a3b8;
      font-size: 15px;
      line-height: 1.6;
      margin: 0 0 24px;
    }
    .btn {
      display: inline-block;
      width: 100%;
      box-sizing: border-box;
      padding: 12px 24px;
      background: #2563eb;
      color: white;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      transition: background 0.2s;
    }
    .btn:hover {
      background: #1d4ed8;
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
    <div class="icon">${icon}</div>
    <div class="badge">${isAccept ? 'ATENDIMENTO INICIADO' : 'EM ESPERA'}</div>
    <h1>${title}</h1>
    <p>${desc}</p>
    <a href="${dealUrl}" class="btn" target="_blank">Abrir Chamado no Bitrix24</a>
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
            "id": "resp_webhook",
            "name": "Respond_To_Webhook",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1,
            "position": [2100, 300],
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
    ],
    "connections": {
        "Webhook_Ticket_Action": {
            "main": [[{"node": "Parse_Action_Params", "type": "main", "index": 0}]]
        },
        "Parse_Action_Params": {
            "main": [[{"node": "Lookup_Technician_Name", "type": "main", "index": 0}]]
        },
        "Lookup_Technician_Name": {
            "main": [[{"node": "Merge_Context", "type": "main", "index": 0}]]
        },
        "Merge_Context": {
            "main": [
                [
                    {"node": "Bitrix_Update_Deal_Takeover", "type": "main", "index": 0},
                    {"node": "Update_Postgres_Session_Silence", "type": "main", "index": 0},
                    {"node": "Bitrix_Get_Deal_Chat", "type": "main", "index": 0}
                ]
            ]
        },
        "Bitrix_Get_Deal_Chat": {
            "main": [[{"node": "Prepare_Chat_And_Timeline", "type": "main", "index": 0}]]
        },
        "Prepare_Chat_And_Timeline": {
            "main": [
                [
                    {"node": "Bitrix_Send_Chat_Notice", "type": "main", "index": 0},
                    {"node": "Bitrix_Add_Timeline", "type": "main", "index": 0},
                    {"node": "Generate_HTML_Page", "type": "main", "index": 0}
                ]
            ]
        },
        "Generate_HTML_Page": {
            "main": [[{"node": "Respond_To_Webhook", "type": "main", "index": 0}]]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

print("1. Verificando se o workflow já existe no n8n...")
all_wfs = requests.get(f"{N8N_BASE}/workflows", headers=headers).json()
existing_id = None
for w in all_wfs.get('data', []):
    if w.get('name') == 'BITRIX_TI_TICKET_TAKEOVER_HANDLER':
        existing_id = w['id']
        break

if existing_id:
    print(f"Workflow já existe com ID: {existing_id}. Atualizando...")
    resp = requests.put(f"{N8N_BASE}/workflows/{existing_id}", headers=headers, json=workflow_data)
else:
    print("Criando novo workflow BITRIX_TI_TICKET_TAKEOVER_HANDLER...")
    resp = requests.post(f"{N8N_BASE}/workflows", headers=headers, json=workflow_data)

if resp.status_code in (200, 201):
    wf_res = resp.json()
    wf_id = wf_res.get('id')
    print(f"Workflow salvo com sucesso! ID: {wf_id}")
    
    # Ativa o workflow
    act_resp = requests.post(f"{N8N_BASE}/workflows/{wf_id}/activate", headers=headers)
    print(f"Status de ativação: {act_resp.status_code} - {act_resp.text}")
else:
    print(f"Erro ao salvar: {resp.status_code} - {resp.text}")
    sys.exit(1)
