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

# 1. Update 01_Strict_Gate_Cat160_Pilot to detect purchase
gate_code = """// GATE FAIL-CLOSED ABSOLUTO:
// Verifica se o Deal pertence EXCLUSIVAMENTE à Categoria 160 e ao usuário 32598 (Eduardo)
const items = $input.all();
const allowed = [];
const ALLOWED_REQUESTERS = [32598]; // Piloto restrito Eduardo Alaminos

for (const item of items) {
  const deal = item.json.result || item.json;
  const categoryId = String(deal.CATEGORY_ID || '');
  const stageId = String(deal.STAGE_ID || '');
  const createdBy = Number(deal.CREATED_BY_ID || 0);
  const title = deal.TITLE || `Chamado #${deal.ID}`;
  const ufCategory = String(deal.UF_CRM_1763388156 || '');

  if (categoryId === '160' && (stageId === 'C160:NEW' || stageId === 'C160:UC_JIOBG8') && ALLOWED_REQUESTERS.includes(createdBy)) {
    const isPurchase = ufCategory === '876' || title.toLowerCase().includes('compra');
    allowed.push({
      json: {
        deal_id: Number(deal.ID),
        title: title,
        requester_user_id: createdBy,
        requester_name: 'Eduardo Alaminos',
        is_purchase: isPurchase
      }
    });
  }
}

return allowed;"""

# 2. Update 02_Reserve_Deal_Session_Atomic to pass is_purchase
reserve_query = "INSERT INTO ticket_bot_sessions (deal_id, requester_user_id, requester_name, channel, private_dialog_id, dialog_type, status, state, ai_state, redis_memory_key, created_at, last_interaction_at) VALUES ({{ $json.deal_id }}, {{ $json.requester_user_id }}, '{{ $json.requester_name }}', 'BITRIX_CRM_CHAT', '', 'chat', 'CHAT_CREATING', 'INIT', 'AI_ACTIVE', 'bitrix:ti:deal:{{ $json.deal_id }}:memory', NOW(), NOW()) ON CONFLICT (deal_id) DO UPDATE SET last_interaction_at = NOW() WHERE ticket_bot_sessions.internal_chat_id IS NULL AND ticket_bot_sessions.status != 'COMPLETED' RETURNING id, deal_id, requester_user_id, requester_name, '{{ $json.title }}' AS deal_title, {{ $json.is_purchase ? 'TRUE' : 'FALSE' }} AS is_purchase;"

# 3. Update 03_Prepare_Activation to pass is_purchase and deal_title
prepare_activation_code = """// Preserva deal context via all(), associando item a item
const reserveItems = $('02_Reserve_Deal_Session_Atomic').all();
const items = $input.all();
return items.map((item, idx) => {
  const chatId = Number(item.json.result || 0);
  const r = reserveItems[idx]?.json || {};
  return {
    json: {
      deal_id: r.deal_id,
      deal_title: r.deal_title || `Chamado #${r.deal_id}`,
      is_purchase: Boolean(r.is_purchase),
      chat_id: chatId,
      dialog_id: `chat${chatId}`
    }
  };
});"""

for n in wf["nodes"]:
    if n.get("name") == "01_Strict_Gate_Cat160_Pilot":
        n["parameters"]["functionCode"] = gate_code
    elif n.get("name") == "02_Reserve_Deal_Session_Atomic":
        n["parameters"]["query"] = reserve_query
    elif n.get("name") == "03_Prepare_Activation":
        n["parameters"]["functionCode"] = prepare_activation_code

# 4. Check if purchase filter and buttons node already exist
node_names = [n.get("name") for n in wf["nodes"]]

if "03_Filter_Purchase_Only" not in node_names:
    filter_purchase_node = {
        "parameters": {
            "functionCode": """// Filtra apenas solicitações de compra para envio dos botões
const items = $('03_Prepare_Activation').all();
const purchases = [];

for (const item of items) {
  if (item.json.is_purchase) {
    purchases.push(item);
  }
}

return purchases;"""
        },
        "id": "node_filter_purchase",
        "name": "03_Filter_Purchase_Only",
        "type": "n8n-nodes-base.function",
        "typeVersion": 1,
        "position": [400, 20]
    }

    send_deal_chat_buttons = {
        "parameters": {
            "method": "POST",
            "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": """={{ JSON.stringify({
  DIALOG_ID: $json.dialog_id,
  MESSAGE: '📦 [b]SOLICITAÇÃO DE COMPRA DE TI[/b]\\nOlá ' + $json.deal_title + '!\\nIdentifiquei a abertura de uma solicitação de compra neste chamado #' + $json.deal_id + '.\\n\\nPor favor, utilize os botões abaixo para definir a autorização:',
  KEYBOARD: [
    {
      TEXT: '✅ Autorizar Compra',
      LINK: 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id=' + $json.deal_id + '&action=approve&user=32598',
      BG_COLOR: '#29b24f',
      TEXT_COLOR: '#ffffff',
      DISPLAY: 'LINE'
    },
    {
      TEXT: '❌ Negar',
      LINK: 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id=' + $json.deal_id + '&action=reject&user=32598',
      BG_COLOR: '#e84343',
      TEXT_COLOR: '#ffffff',
      DISPLAY: 'LINE'
    }
  ]
}) }}"""
        },
        "id": "node_send_deal_chat_buttons",
        "name": "03_Send_Buttons_Deal_Chat",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [620, 20]
    }

    send_direct_chat_buttons = {
        "parameters": {
            "method": "POST",
            "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": """={{ JSON.stringify({
  DIALOG_ID: '32598',
  MESSAGE: '📦 [b]NOVA SOLICITAÇÃO DE COMPRA PENDENTE[/b]\\nChamado #' + $json.deal_id + ': ' + $json.deal_title + '\\n\\nClique no botão abaixo para autorizar ou negar:',
  KEYBOARD: [
    {
      TEXT: '✅ Autorizar Compra',
      LINK: 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id=' + $json.deal_id + '&action=approve&user=32598',
      BG_COLOR: '#29b24f',
      TEXT_COLOR: '#ffffff',
      DISPLAY: 'LINE'
    },
    {
      TEXT: '❌ Negar',
      LINK: 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id=' + $json.deal_id + '&action=reject&user=32598',
      BG_COLOR: '#e84343',
      TEXT_COLOR: '#ffffff',
      DISPLAY: 'LINE'
    }
  ]
}) }}"""
        },
        "id": "node_send_direct_chat_buttons",
        "name": "03_Send_Buttons_Direct_Chat",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [840, 20]
    }

    move_stage_aguardando = {
        "parameters": {
            "method": "POST",
            "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.update",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": """={{ JSON.stringify({
  id: $json.deal_id,
  fields: {
    STAGE_ID: 'C160:UC_JIOBG8'
  }
}) }}"""
        },
        "id": "node_move_stage_aguardando",
        "name": "03_Move_To_Aguardando_Autorizacao",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [1060, 20]
    }

    wf["nodes"].extend([
        filter_purchase_node,
        send_deal_chat_buttons,
        send_direct_chat_buttons,
        move_stage_aguardando
    ])

    # Connect from 03_Activate_Session_With_Chat to 03_Filter_Purchase_Only
    if "03_Activate_Session_With_Chat" not in wf["connections"]:
        wf["connections"]["03_Activate_Session_With_Chat"] = {"main": [[]]}
    wf["connections"]["03_Activate_Session_With_Chat"]["main"] = [
        [{"node": "03_Filter_Purchase_Only", "type": "main", "index": 0}]
    ]

    wf["connections"]["03_Filter_Purchase_Only"] = {
        "main": [[{"node": "03_Send_Buttons_Deal_Chat", "type": "main", "index": 0}]]
    }
    wf["connections"]["03_Send_Buttons_Deal_Chat"] = {
        "main": [[{"node": "03_Send_Buttons_Direct_Chat", "type": "main", "index": 0}]]
    }
    wf["connections"]["03_Send_Buttons_Direct_Chat"] = {
        "main": [[{"node": "03_Move_To_Aguardando_Autorizacao", "type": "main", "index": 0}]]
    }

# Save local canonical
with open(canonical_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print("Salvo arquivo canônico com o fluxo de aprovação de compras.")

# Deploy to n8n
deploy_payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

resp = requests.put(N8N_URL, headers=headers, json=deploy_payload)
print("Status do deploy no n8n:", resp.status_code)
if resp.status_code == 200:
    print("Workflow principal atualizado com o fluxo de botões de compra!")
else:
    print("Erro no deploy:", resp.text)
