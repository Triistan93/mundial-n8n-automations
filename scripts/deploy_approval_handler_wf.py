# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

wf = {
    "name": "BITRIX_TI_PURCHASE_APPROVAL_HANDLER",
    "nodes": [
        {
            "id": "wh_action",
            "name": "Webhook_Purchase_Action",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [-300, 300],
            "parameters": {
                "httpMethod": "GET",
                "path": "purchase-action",
                "responseMode": "lastNode",
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
const userId = query.user || '32598';

if (!dealId) {
  throw new Error("Parâmetro 'deal_id' é obrigatório.");
}

const isApprove = action === 'approve';
const targetStage = isApprove ? 'C160:UC_AR9ORZ' : 'C160:UC_A18YO8';
const statusLabel = isApprove ? 'AUTORIZADO' : 'NEGADO';
const actionEmoji = isApprove ? '✅' : '❌';

return [{
  json: {
    deal_id: dealId,
    action: action,
    is_approve: isApprove,
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
            "id": "http_update_deal",
            "name": "Bitrix_Update_Deal_Stage",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [180, 300],
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.update",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  id: $json.deal_id,\n  fields: {\n    STAGE_ID: $json.target_stage\n  }\n}) }}"
            }
        },
        {
            "id": "http_add_timeline",
            "name": "Bitrix_Add_Timeline_Comment",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [420, 300],
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.timeline.comment.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  fields: {\n    ENTITY_ID: $('Parse_Action_Params').first().json.deal_id,\n    ENTITY_TYPE: 'deal',\n    COMMENT: ($('Parse_Action_Params').first().json.is_approve ? '[AUTORIZAÇÃO DE COMPRA] Solicitação de compra AUTORIZADA por Eduardo Alaminos.' : '[COMPRA NEGADA] Solicitação de compra NEGADA por Eduardo Alaminos.')\n  }\n}) }}"
            }
        },
        {
            "id": "http_notify_im",
            "name": "Bitrix_Notify_Eduardo_Chat",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [660, 300],
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  DIALOG_ID: '32598',\n  MESSAGE: $('Parse_Action_Params').first().json.action_emoji + ' [b]CHAMADO #' + $('Parse_Action_Params').first().json.deal_id + '[/b]\\nAção registrada com sucesso: [b]' + $('Parse_Action_Params').first().json.status_label + '[/b]!\\nO card foi movido para a etapa correspondente.'\n}) }}"
            }
        },
        {
            "id": "code_html_response",
            "name": "Generate_HTML_Response",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 300],
            "parameters": {
                "jsCode": """
const data = $('Parse_Action_Params').first().json;
const color = data.is_approve ? '#29b24f' : '#e84343';
const title = data.is_approve ? 'Compra Autorizada com Sucesso!' : 'Solicitação de Compra Negada';

const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>${title}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f4f7f6; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
    .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; max-width: 480px; width: 90%; }
    .badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; color: white; background: ${color}; margin-bottom: 20px; font-size: 14px; }
    h1 { color: #333; font-size: 24px; margin: 0 0 10px 0; }
    p { color: #666; font-size: 16px; line-height: 1.5; margin: 0 0 25px 0; }
    .btn { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; transition: background 0.2s; }
    .btn:hover { background: #0056b3; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">${data.action_emoji} ${data.status_label}</div>
    <h1>${title}</h1>
    <p>O chamado <strong>#${data.deal_id}</strong> foi atualizado e movido automaticamente para a etapa <strong>${data.status_label}</strong> na Central de TI do Bitrix24.</p>
    <a href="https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${data.deal_id}/" class="btn">Abrir Chamado no Bitrix24</a>
  </div>
</body>
</html>`;

$response = {
  body: html,
  headers: {
    'content-type': 'text/html; charset=utf-8'
  }
};

return [{ json: { success: true } }];
"""
            }
        }
    ],
    "connections": {
        "Webhook_Purchase_Action": {
            "main": [[{"node": "Parse_Action_Params", "type": "main", "index": 0}]]
        },
        "Parse_Action_Params": {
            "main": [[{"node": "Bitrix_Update_Deal_Stage", "type": "main", "index": 0}]]
        },
        "Bitrix_Update_Deal_Stage": {
            "main": [[{"node": "Bitrix_Add_Timeline_Comment", "type": "main", "index": 0}]]
        },
        "Bitrix_Add_Timeline_Comment": {
            "main": [[{"node": "Bitrix_Notify_Eduardo_Chat", "type": "main", "index": 0}]]
        },
        "Bitrix_Notify_Eduardo_Chat": {
            "main": [[{"node": "Generate_HTML_Response", "type": "main", "index": 0}]]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

print("Deployando workflow BITRIX_TI_PURCHASE_APPROVAL_HANDLER no n8n...")
resp = requests.post(N8N_URL, headers=headers, json=wf)
print("Status code:", resp.status_code)
if resp.status_code in [200, 201]:
    wf_id = resp.json().get("id")
    print("Workflow criado com sucesso! ID:", wf_id)
    act = requests.post(f"{N8N_URL}/{wf_id}/activate", headers=headers)
    print("Ativação:", act.status_code)
else:
    print("Erro:", resp.text)
