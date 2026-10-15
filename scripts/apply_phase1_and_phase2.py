# -*- coding: utf-8 -*-
"""
Implementação das Fases 1 e 2 do Plano de Ação:
Fase 1: Blindagem de Resiliência no n8n (onError: 'continueRegularOutput' em nós críticos)
Fase 2: Identidade Dinâmica via bitrix_users_cache no PostgreSQL e Detector Gestor vs Beneficiário
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

print("1. Obtendo workflow atual do n8n...")
resp = requests.get(N8N_URL, headers=headers)
wf = resp.json()

# Lista de nós críticos para receber onError = 'continueRegularOutput'
CRITICAL_RESILIENCE_NODES = [
    '02_Reserve_Deal_Session_Atomic',
    '01_Check_Store_Outage_Cluster',
    '01_Evaluate_Store_Outage',
    '04_Fetch_Chat_Messages_Bitrix',
    '03_Create_CRM_Card_Chat',
    '12_Update_Deal_CRM_Bitrix',
    '14_Add_Timeline_Milestone_Comment',
    '15_Send_Final_Confirmation_To_Chat',
    '16_Mark_Session_Completed_Postgres'
]

# Nova query de 02_Reserve_Deal_Session_Atomic com resolução dinâmica de usuários via bitrix_users_cache
new_reserve_query = """INSERT INTO ticket_bot_sessions (
    deal_id, requester_user_id, requester_name, channel, private_dialog_id, 
    dialog_type, status, state, ai_state, redis_memory_key, collected_data_json, 
    created_at, last_interaction_at
) VALUES (
    {{ $json.deal_id }}, {{ $json.requester_user_id }}, 
    COALESCE((SELECT SPLIT_PART(TRIM(name), ' ', 1) FROM bitrix_users_cache WHERE user_id = {{ $json.requester_user_id }}), '{{ ($json.requester_name || "").replace(/'/g, "''") }}'), 
    'BITRIX_CRM_CHAT', '', 'chat', 'CHAT_CREATING', 'INIT', 'AI_ACTIVE', 
    'bitrix:ti:deal:{{ $json.deal_id }}:memory', 
    json_build_object(
        'store_name', '{{ ($json.store_name || "").replace(/'/g, "''") }}', 
        'category_theme', '{{ ($json.category_theme || "").replace(/'/g, "''") }}', 
        'is_store_outage', {{ $json.is_store_outage ? 'true' : 'false' }}, 
        'outage_count', {{ $json.outage_count || 1 }}, 
        'deal_title', '{{ ($json.title || "").replace(/'/g, "''") }}',
        'requester_position', COALESCE((SELECT work_position FROM bitrix_users_cache WHERE user_id = {{ $json.requester_user_id }}), '')
    ),
    NOW(), NOW()
) ON CONFLICT (deal_id) DO UPDATE SET 
    last_interaction_at = NOW(),
    collected_data_json = json_build_object(
        'store_name', '{{ ($json.store_name || "").replace(/'/g, "''") }}', 
        'category_theme', '{{ ($json.category_theme || "").replace(/'/g, "''") }}', 
        'is_store_outage', {{ $json.is_store_outage ? 'true' : 'false' }}, 
        'outage_count', {{ $json.outage_count || 1 }}, 
        'deal_title', '{{ ($json.title || "").replace(/'/g, "''") }}',
        'requester_position', COALESCE((SELECT work_position FROM bitrix_users_cache WHERE user_id = {{ $json.requester_user_id }}), '')
    )
WHERE ticket_bot_sessions.internal_chat_id IS NULL AND ticket_bot_sessions.status != 'COMPLETED'
RETURNING id, deal_id, requester_user_id, 
          COALESCE((SELECT SPLIT_PART(TRIM(name), ' ', 1) FROM bitrix_users_cache WHERE user_id = {{ $json.requester_user_id }}), '{{ ($json.requester_name || "").replace(/'/g, "''") }}') AS requester_name, 
          '{{ ($json.title || "").replace(/'/g, "''") }}' AS deal_title, 
          {{ $json.is_purchase ? 'TRUE' : 'FALSE' }} AS is_purchase,
          {{ $json.is_store_outage ? 'TRUE' : 'FALSE' }} AS is_store_outage,
          '{{ ($json.store_name || "").replace(/'/g, "''") }}' AS store_name,
          '{{ ($json.category_theme || "").replace(/'/g, "''") }}' AS category_theme,
          {{ $json.outage_count || 1 }} AS outage_count,
          COALESCE((SELECT work_position FROM bitrix_users_cache WHERE user_id = {{ $json.requester_user_id }}), '') AS requester_position;"""

# Novo código de 07_Prepare_AI_Deal_Input com Detector Gestor vs Beneficiário
new_prepare_code = """// Prepara input isolado para o Agente LangChain por Deal com contexto do card e separação Gestor vs Beneficiário
const items = $input.all();
return items.map(item => {
  const collected = item.json.collected_data_json || {};
  const title = String(collected.deal_title || '').trim();
  const userInput = String(item.json.message_text || '').trim();
  const requesterName = String(item.json.requester_name || 'Colaborador').trim();
  const requesterPosition = String(collected.requester_position || '').trim();

  // Detecção de solicitação em nome de terceiro (Gestor abrindo para colaborador)
  let thirdPartyNote = '';
  const thirdPartyMatch = title.match(/(?:para|do|da|mecanico|mecânico|vendedor|estoquista|novo colaborador|novo consultor)\s+([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+)?)/i);
  
  if (thirdPartyMatch && thirdPartyMatch[1] && !thirdPartyMatch[1].toLowerCase().includes(requesterName.toLowerCase())) {
    const beneficiary = thirdPartyMatch[1].trim();
    thirdPartyNote = `[ATENÇÃO - CHAMADO ABERTO EM NOME DE OUTRA PESSOA]:\\n` +
      `- O usuário conversando com você no chat é o(a) solicitante: ${requesterName}${requesterPosition ? ' (' + requesterPosition + ')' : ''}.\\n` +
      `- O colaborador citado que precisa da liberação/suporte é: "${beneficiary}".\\n` +
      `- DIRETIVA: Dirija-se sempre a ${requesterName} pelo nome dele(a). NUNCA o confunda com ${beneficiary}. Trate a demanda como uma solicitação feita por ${requesterName} em favor de ${beneficiary}.\\n\\n`;
  }

  let contextHeader = `[SOLICITANTE DO CARD / USUÁRIO NO CHAT]: ${requesterName}${requesterPosition ? ' (' + requesterPosition + ')' : ''}\\n`;
  if (title && !title.startsWith('Chamado #') && !title.startsWith('#')) {
    contextHeader += `[TÍTULO DO CHAMADO]: "${title}"\\n`;
  }
  
  const contextualInput = `${contextHeader}${thirdPartyNote}[MENSAGEM DO COLABORADOR NO CHAT]:\\n${userInput}`;

  return {
    json: {
      deal_id: item.json.deal_id,
      chat_id: item.json.chat_id,
      dialog_id: item.json.dialog_id,
      requester_user_id: item.json.requester_user_id,
      requester_name: requesterName,
      requester_position: requesterPosition,
      message_id: item.json.message_id,
      full_user_input: contextualInput,
      redis_memory_key: item.json.redis_memory_key,
      ai_state: item.json.ai_state,
      collected_data_json: collected
    }
  };
});"""

# Atualizar nós no workflow
print("\n2. Aplicando blindagem de resiliência e identidade dinâmica nos nós...")
for node in wf['nodes']:
    name = node['name']
    
    # 1. Configurar onError: 'continueRegularOutput'
    if name in CRITICAL_RESILIENCE_NODES:
        node['onError'] = 'continueRegularOutput'
        print(f"  [Resiliência] {name} -> onError = 'continueRegularOutput'")
        
    # 2. Atualizar nó 02_Reserve_Deal_Session_Atomic
    if name == '02_Reserve_Deal_Session_Atomic':
        print(f"  [Identidade Dinâmica] 02_Reserve_Deal_Session_Atomic -> query com bitrix_users_cache")
        node['parameters']['query'] = new_reserve_query
        
    # 3. Atualizar nó 07_Prepare_AI_Deal_Input
    if name == '07_Prepare_AI_Deal_Input':
        print(f"  [Identidade Dinâmica] 07_Prepare_AI_Deal_Input -> Detector Gestor vs Beneficiário")
        node['parameters']['jsCode'] = new_prepare_code

print("\n3. Salvando workflow atualizado no n8n...")
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}
put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Workflow c0F2GUMFm2BI94UG salvo com sucesso no n8n com Fases 1 e 2 ativas!")
else:
    print(f"Erro ao salvar: {put_resp.status_code} - {put_resp.text}")
    sys.exit(1)
