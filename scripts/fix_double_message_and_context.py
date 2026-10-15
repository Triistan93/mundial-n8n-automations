# -*- coding: utf-8 -*-
"""
Script de Correção Imediata:
1. Corrige o bug de indexação em 10_Prepare_Cursor_Update que gerava mensagens duplicadas em loop;
2. Atualiza 04_Get_Active_Sessions_Postgres para retornar collected_data_json;
3. Atualiza 02_Reserve_Deal_Session_Atomic para persistir deal_title em collected_data_json;
4. Atualiza 07_Prepare_AI_Deal_Input para injetar [CONTEXTO DO CARD DO CHAMADO] com título do deal;
5. Refina a instrução no System Prompt para NUNCA pedir dados já presentes no título do card.
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

print("1. Obtendo workflow c0F2GUMFm2BI94UG do n8n...")
resp = requests.get(N8N_URL, headers=headers)
wf = resp.json()

# 1. Correção de 10_Prepare_Cursor_Update
new_prepare_cursor = """// Cursor SOMENTE após envio com sucesso no Bitrix
// Correção de indexação: consome branch FALSE (outputIndex 1) de 09_If_Triage_Complete
const askInputs = $('09_If_Triage_Complete').all(1);
const items = $input.all();
const results = [];

for (let i = 0; i < items.length; i++) {
  const bitrixRes = items[i].json;
  const itemIdx = items[i].pairedItem?.item ?? i;
  const askData = askInputs[itemIdx]?.json || askInputs[i]?.json || {};
  
  if (bitrixRes.result && askData.deal_id) {
    results.push({
      json: {
        deal_id: askData.deal_id,
        message_id: askData.message_id,
        sent_bitrix_msg_id: bitrixRes.result
      }
    });
  }
}

return results;"""

# 2. Correção de 04_Get_Active_Sessions_Postgres
new_get_active_sessions_query = """-- SELF-HEALING GENERICO POR ESTADO:
UPDATE ticket_bot_sessions 
SET status = 'ACTIVE' 
WHERE status = 'CHAT_CREATING' AND internal_chat_id IS NOT NULL;

-- Recupera sessoes ativas recentes com collected_data_json (ultimas 48h)
SELECT id, deal_id, requester_user_id, requester_name, internal_chat_id, dialog_id, last_processed_message_id, ai_state, redis_memory_key, status, state, collected_data_json 
FROM ticket_bot_sessions 
WHERE (
    (status = 'ACTIVE' AND last_interaction_at > NOW() - INTERVAL '48 hours') 
    OR 
    (status = 'COMPLETED' AND last_interaction_at > NOW() - INTERVAL '24 hours')
  ) 
  AND internal_chat_id IS NOT NULL;"""

# 3. Correção de 02_Reserve_Deal_Session_Atomic
new_reserve_query = """INSERT INTO ticket_bot_sessions (
    deal_id, requester_user_id, requester_name, channel, private_dialog_id, 
    dialog_type, status, state, ai_state, redis_memory_key, collected_data_json, 
    created_at, last_interaction_at
) VALUES (
    {{ $json.deal_id }}, {{ $json.requester_user_id }}, '{{ $json.requester_name }}', 
    'BITRIX_CRM_CHAT', '', 'chat', 'CHAT_CREATING', 'INIT', 'AI_ACTIVE', 
    'bitrix:ti:deal:{{ $json.deal_id }}:memory', 
    json_build_object('store_name', '{{ $json.store_name }}', 'category_theme', '{{ $json.category_theme }}', 'is_store_outage', {{ $json.is_store_outage ? 'true' : 'false' }}, 'outage_count', {{ $json.outage_count || 1 }}, 'deal_title', {{ JSON.stringify($json.title) }}),
    NOW(), NOW()
) ON CONFLICT (deal_id) DO UPDATE SET 
    last_interaction_at = NOW(),
    collected_data_json = json_build_object('store_name', '{{ $json.store_name }}', 'category_theme', '{{ $json.category_theme }}', 'is_store_outage', {{ $json.is_store_outage ? 'true' : 'false' }}, 'outage_count', {{ $json.outage_count || 1 }}, 'deal_title', {{ JSON.stringify($json.title) }})
WHERE ticket_bot_sessions.internal_chat_id IS NULL AND ticket_bot_sessions.status != 'COMPLETED'
RETURNING id, deal_id, requester_user_id, requester_name, '{{ $json.title }}' AS deal_title, 
          {{ $json.is_purchase ? 'TRUE' : 'FALSE' }} AS is_purchase,
          {{ $json.is_store_outage ? 'TRUE' : 'FALSE' }} AS is_store_outage,
          '{{ $json.store_name }}' AS store_name,
          '{{ $json.category_theme }}' AS category_theme,
          {{ $json.outage_count || 1 }} AS outage_count;"""

# 4. Correção de 07_Prepare_AI_Deal_Input
new_prepare_ai_input = """// Prepara input isolado para o Agente LangChain por Deal com contexto do card
const items = $input.all();
return items.map(item => {
  const collected = item.json.collected_data_json || {};
  const title = String(collected.deal_title || '').trim();
  const userInput = String(item.json.message_text || '').trim();

  let contextualInput = userInput;
  // Se o chamado possui título específico e relevante, injeta no contexto
  if (title && !title.startsWith('Chamado #') && !title.startsWith('#') && !userInput.includes(title)) {
    contextualInput = `[CONTEXTO DO CARD DO CHAMADO #${item.json.deal_id}]: Título informado: "${title}"\\n\\n[MENSAGEM DO COLABORADOR NO CHAT]:\\n${userInput}`;
  }

  return {
    json: {
      deal_id: item.json.deal_id,
      chat_id: item.json.chat_id,
      dialog_id: item.json.dialog_id,
      requester_user_id: item.json.requester_user_id,
      requester_name: item.json.requester_name || 'Colaborador',
      message_id: item.json.message_id,
      full_user_input: contextualInput,
      redis_memory_key: item.json.redis_memory_key,
      ai_state: item.json.ai_state
    }
  };
});"""

# 5. Atualização de nós no workflow
updated_count = 0
for n in wf.get('nodes', []):
    if n['name'] == '10_Prepare_Cursor_Update':
        n['parameters']['jsCode'] = new_prepare_cursor
        updated_count += 1
        print("-> 10_Prepare_Cursor_Update corrigido (index mismatch resolvido)")
    elif n['name'] == '04_Get_Active_Sessions_Postgres':
        n['parameters']['query'] = new_get_active_sessions_query
        updated_count += 1
        print("-> 04_Get_Active_Sessions_Postgres atualizado (seleciona collected_data_json)")
    elif n['name'] == '02_Reserve_Deal_Session_Atomic':
        n['parameters']['query'] = new_reserve_query
        updated_count += 1
        print("-> 02_Reserve_Deal_Session_Atomic atualizado (persiste deal_title)")
    elif n['name'] == '07_Prepare_AI_Deal_Input':
        n['parameters']['jsCode'] = new_prepare_ai_input
        updated_count += 1
        print("-> 07_Prepare_AI_Deal_Input atualizado (injeta título do card no contexto)")
    elif n['name'] == '08_AI_Agent_Triage_Deal':
        sm = n['parameters']['options']['systemMessage']
        title_rule = """
# CONTEXTO INICIAL DO CARD DO CHAMADO:
- Quando a mensagem contiver "[CONTEXTO DO CARD DO CHAMADO #...]: Título informado: ...":
  * LEIA COM MÁXIMA ATENÇÃO O TÍTULO DO CARD. Se o colaborador já informou o Chassi (iniciado por 9C2...), número da OS, número do pedido ou o problema no título do chamado, CONSIDERE ESSE DADO COMO JÁ FORNECIDO!
  * NUNCA pergunte novamente dados que já constam no título do chamado!
  * Demonstre que você já leu o título (ex: "Vi que você abriu este chamado para gerar o ATPV do chassi 9C2JB0100VR452123...")."""
        if "[CONTEXTO DO CARD DO CHAMADO #" not in sm:
            n['parameters']['options']['systemMessage'] = sm + "\n" + title_rule
            updated_count += 1
            print("-> 08_AI_Agent_Triage_Deal System Prompt atualizado com regra de leitura do título do card")

print("2. Enviando workflow atualizado para a API do n8n...")
payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print(f"Sucesso absoluto! Workflow atualizado ({updated_count} nós refinados)!")
else:
    print(f"Erro ao salvar: {put_resp.status_code} - {put_resp.text}")
    sys.exit(1)
