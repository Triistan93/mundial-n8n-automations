# -*- coding: utf-8 -*-
"""
Ajuste de propagação de requester_name e store_name ao longo da esteira
para que notificações da equipe de TI (Eduardo e Igor) sempre exibam o nome real
do solicitante (ex: Hadner) e a loja correta (ex: Mogi Mirim).
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

print("1. Obtendo workflow...")
resp = requests.get(N8N_URL, headers=headers)
wf = resp.json()

# 1. 07_Prepare_AI_Deal_Input
new_prepare_code = """// Prepara input isolado para o Agente LangChain por Deal com contexto do card
const items = $input.all();
return items.map(item => {
  const collected = item.json.collected_data_json || {};
  const title = String(collected.deal_title || '').trim();
  const userInput = String(item.json.message_text || '').trim();
  const requesterName = String(item.json.requester_name || 'Colaborador').trim();

  let contextHeader = `[SOLICITANTE DO CARD / USUÁRIO NO CHAT]: ${requesterName} (Dirija-se sempre a ele(a) por este nome)\\n`;
  if (title && !title.startsWith('Chamado #') && !title.startsWith('#')) {
    contextHeader += `[TÍTULO DO CHAMADO]: "${title}"\\n`;
  }
  
  const contextualInput = `${contextHeader}\\n[MENSAGEM DO COLABORADOR NO CHAT]:\\n${userInput}`;

  return {
    json: {
      deal_id: item.json.deal_id,
      chat_id: item.json.chat_id,
      dialog_id: item.json.dialog_id,
      requester_user_id: item.json.requester_user_id,
      requester_name: requesterName,
      message_id: item.json.message_id,
      full_user_input: contextualInput,
      redis_memory_key: item.json.redis_memory_key,
      ai_state: item.json.ai_state,
      collected_data_json: collected
    }
  };
});"""

# 2. 09_Format_AI_Response
new_format_code = """// Formatação multi-item via all() com suporte a Autoatendimento L1!
const prepItems = $('07_Prepare_AI_Deal_Input').all();
const items = $input.all();
const results = [];

for (let i = 0; i < items.length; i++) {
  const agentItem = items[i].json;
  const prevData = prepItems[i]?.json || {};
  
  const rawOutput = agentItem.output || agentItem.text || '';
  let cleanMessage = String(rawOutput).trim();
  let structuredData = null;

  const match = cleanMessage.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/i);
  if (match) {
    try {
      structuredData = JSON.parse(match[1]);
      cleanMessage = cleanMessage.replace(match[0], '').trim();
    } catch (e) {}
  }

  const isResolvedL1 = Boolean(structuredData && (structuredData.action === 'RESOLVED_L1' || structuredData.resolvido_l1 === true || structuredData.testes_l1?.resultado === 'SUCESSO'));
  const isComplete = Boolean(structuredData && (structuredData.action === 'COMPLETE' || isResolvedL1 || structuredData.status_triagem === 'concluido'));

  results.push({
    json: {
      deal_id: prevData.deal_id,
      chat_id: prevData.chat_id,
      dialog_id: prevData.dialog_id,
      requester_user_id: prevData.requester_user_id,
      requester_name: prevData.requester_name || 'Colaborador',
      message_id: prevData.message_id,
      reply_text: cleanMessage,
      structured_data: structuredData,
      is_complete: isComplete,
      is_resolved_l1: isResolvedL1,
      collected_data_json: prevData.collected_data_json || {}
    }
  });
}

return results;"""

# 3. 11_B01_Priority_And_Payload
for node in wf['nodes']:
    if node['name'] == '07_Prepare_AI_Deal_Input':
        print("Atualizando 07_Prepare_AI_Deal_Input...")
        node['parameters']['jsCode'] = new_prepare_code
    elif node['name'] == '09_Format_AI_Response':
        print("Atualizando 09_Format_AI_Response...")
        node['parameters']['jsCode'] = new_format_code
    elif node['name'] == '11_B01_Priority_And_Payload':
        print("Atualizando 11_B01_Priority_And_Payload...")
        code = node['parameters']['jsCode']
        # Garantir que requester_name e store_name sejam repassados no json final
        if 'requester_name: item.json.requester_name' not in code:
            code = code.replace(
                "resumo: resumo,",
                "resumo: resumo,\n      requester_name: item.json.requester_name || 'Colaborador',\n      store_name: storeName || (item.json.collected_data_json?.store_name) || 'Geral',"
            )
            node['parameters']['jsCode'] = code

print("2. Salvando workflow no n8n...")
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}
put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Propagação de nomes e lojas atualizada com sucesso no n8n!")
else:
    print(f"Erro ao salvar: {put_resp.status_code} - {put_resp.text}")
