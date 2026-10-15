# -*- coding: utf-8 -*-
"""
Script de Correção:
1. Corrige o nó 02_Reserve_Deal_Session_Atomic (elimina 'column "Flavio" does not exist' usando single quotes)
2. Corrige o nó 01_Strict_Gate_Cat160_Pilot:
   - 2606: 'Hadner' (Gerente Mogi Mirim)
   - Remove o falso positivo de 'os ' em microKeywords (usava 'os ' que casava com o artigo 'os')
   - Adiciona categoryTheme ACCESS_PERMISSIONS para chamadas de liberação de acessos/crm/permissões
3. Atualiza 07_Prepare_AI_Deal_Input para explicitar o nome do Solicitante/Gestor no chat
4. Refina o System Prompt em 08_AI_Agent_Triage_Deal com diretriz para Permissões Bitrix24
5. Atualiza o banco de dados ticket_bot_sessions para o Deal 1411066 (requester_name = 'Hadner')
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

print("1. Buscando workflow atual do n8n...")
resp = requests.get(N8N_URL, headers=headers)
wf = resp.json()

# 1. Correção de 02_Reserve_Deal_Session_Atomic
reserve_query = """INSERT INTO ticket_bot_sessions (
    deal_id, requester_user_id, requester_name, channel, private_dialog_id, 
    dialog_type, status, state, ai_state, redis_memory_key, collected_data_json, 
    created_at, last_interaction_at
) VALUES (
    {{ $json.deal_id }}, {{ $json.requester_user_id }}, '{{ ($json.requester_name || "").replace(/'/g, "''") }}', 
    'BITRIX_CRM_CHAT', '', 'chat', 'CHAT_CREATING', 'INIT', 'AI_ACTIVE', 
    'bitrix:ti:deal:{{ $json.deal_id }}:memory', 
    json_build_object('store_name', '{{ ($json.store_name || "").replace(/'/g, "''") }}', 'category_theme', '{{ ($json.category_theme || "").replace(/'/g, "''") }}', 'is_store_outage', {{ $json.is_store_outage ? 'true' : 'false' }}, 'outage_count', {{ $json.outage_count || 1 }}, 'deal_title', '{{ ($json.title || "").replace(/'/g, "''") }}'),
    NOW(), NOW()
) ON CONFLICT (deal_id) DO UPDATE SET 
    last_interaction_at = NOW(),
    collected_data_json = json_build_object('store_name', '{{ ($json.store_name || "").replace(/'/g, "''") }}', 'category_theme', '{{ ($json.category_theme || "").replace(/'/g, "''") }}', 'is_store_outage', {{ $json.is_store_outage ? 'true' : 'false' }}, 'outage_count', {{ $json.outage_count || 1 }}, 'deal_title', '{{ ($json.title || "").replace(/'/g, "''") }}')
WHERE ticket_bot_sessions.internal_chat_id IS NULL AND ticket_bot_sessions.status != 'COMPLETED'
RETURNING id, deal_id, requester_user_id, requester_name, '{{ ($json.title || "").replace(/'/g, "''") }}' AS deal_title, 
          {{ $json.is_purchase ? 'TRUE' : 'FALSE' }} AS is_purchase,
          {{ $json.is_store_outage ? 'TRUE' : 'FALSE' }} AS is_store_outage,
          '{{ ($json.store_name || "").replace(/'/g, "''") }}' AS store_name,
          '{{ ($json.category_theme || "").replace(/'/g, "''") }}' AS category_theme,
          {{ $json.outage_count || 1 }} AS outage_count;"""

# 2. Correção do nó 01_Strict_Gate_Cat160_Pilot
new_gate_code = """// GATE FAIL-CLOSED ABSOLUTO:
// Verifica se o Deal pertence EXCLUSIVAMENTE à Categoria 160
// Piloto Aberto para TODOS os Colaboradores da Concessionária com Botão de Pânico Ativo
const items = $input.all();
const allowed = [];

// Flag de Liberação Geral: aberta para todos os colaboradores
const ALLOW_ALL_USERS = true;
const ALLOWED_REQUESTERS = [32598];

const USER_NAMES = {
  32598: 'Eduardo Alaminos',
  7: 'Élton Caetano',
  352678: 'Igor Bonini',
  12190: 'Nataelen Balduino',
  3926: 'Karina Volsi',
  4272: 'Paula Brenda',
  4880: 'Celeste',
  2602: 'Neia Souza',
  2638: 'Isabela Cassiano',
  3928: 'Vanisse Helena',
  2604: 'Lauane',
  2574: 'Anderson Viotto',
  2644: 'Silvana Pacagnella',
  18436: 'Camily Silva',
  20072: 'Brenda Flois',
  5854: 'Juliana Bressan',
  35026: 'Daniela Momesso',
  25282: 'Debora',
  342040: 'Gabrielle Romeu',
  344400: 'Mariana Reis',
  72620: 'Yara Souza',
  4736: 'Juliana Masson',
  2576: 'Tatiana Ambrozio',
  101920: 'Lucas Silva',
  108288: 'Andréia Messa',
  3640: 'Caroline Ruas',
  280486: 'Taina Sousa',
  5886: 'Leonardo Ribeiro',
  115138: 'Wagner Pereira',
  7370: 'Janaina',
  17744: 'Sérgio Campos',
  184294: 'Livia Eduarda',
  5330: 'João Paulo',
  2606: 'Hadner',
  469422: 'Flavio Queiroz',
  439968: 'Danielly'
};

const STORE_MAP = {
  '45': 'Araras',
  '47': 'Itapira',
  '49': 'Leme',
  '51': 'Mogi Guaçu',
  '53': 'Mogi Mirim',
  '55': 'Santa Bárbara',
  '57': 'Campinas',
  '59': 'Hortolândia',
  '61': 'Sumaré',
  '105': 'Nova Odessa',
  '180': 'Pinhal',
  '182': 'Conchal',
  '536': 'Santo Antonio de Posse',
  '534': 'Outros'
};

for (const item of items) {
  const deal = item.json.result || item.json;
  const categoryId = String(deal.CATEGORY_ID || '');
  const stageId = String(deal.STAGE_ID || '');
  const createdBy = Number(deal.CREATED_BY_ID || 0);
  const assignedBy = Number(deal.ASSIGNED_BY_ID || 0);
  const title = deal.TITLE || `Chamado #${deal.ID}`;
  const ufCategory = String(deal.UF_CRM_1763388156 || '');

  let requesterId = 0;
  if (ALLOW_ALL_USERS) {
    requesterId = createdBy || assignedBy;
  } else {
    requesterId = ALLOWED_REQUESTERS.includes(createdBy) 
      ? createdBy 
      : (ALLOWED_REQUESTERS.includes(assignedBy) ? assignedBy : 0);
  }

  // Validação estrita: apenas Categoria 160 e fases iniciais (NEW ou Aguardando autorização)
  if (categoryId === '160' && (stageId === 'C160:NEW' || stageId === 'C160:UC_JIOBG8') && requesterId > 0) {
    const isPurchase = ufCategory === '876' || title.toLowerCase().includes('compra');
    const rawDesc = deal.UF_CRM_1729774515200;
    const description = (Array.isArray(rawDesc) ? rawDesc.join(' ') : String(rawDesc || '')).trim();

    // Mapeamento de Loja/Unidade
    const rawStoreId = String(deal.UF_CRM_1689593052602 || '');
    let storeName = STORE_MAP[rawStoreId] || '';
    
    // Fallback: busca menção de loja no título ou descrição
    const fullText = (title + ' ' + description).toLowerCase();
    if (!storeName) {
      for (const [id, name] of Object.entries(STORE_MAP)) {
        if (name !== 'Outros' && fullText.includes(name.toLowerCase())) {
          storeName = name;
          break;
        }
      }
    }
    if (!storeName) storeName = 'Mogi Guaçu';

    // Detecção de Tema de Incidente com suporte a ROBÔS RPA, TELEFONIA, ACESSOS e demais temas
    let categoryTheme = 'GENERAL_IT';
    const roboKeywords = ['robo', 'robô', 'card robo', 'card robô', 'entrada honda', 'entrada grupo', 'faturamento direto', 'dms_vigia', 'processamento', 'solicitacao de entrada', 'solicitação de entrada'];
    const connKeywords = ['internet', 'rede', 'caiu', 'conexao', 'conexão', 'link', 'roteador', 'vpn', 'fora do ar', 'offline', 'sem sistema', 'tudo vermelho', 'lentidao geral', 'sem net', 'wi-fi', 'wifi'];
    const telKeywords = ['telefone', 'ramal', 'ligacao', 'ligação', 'headset', 'fone', 'não toca', 'nao toca', 'mudo', 'fale facil', 'fale fácil'];
    const accessKeywords = ['acesso', 'permissao', 'permissão', 'liberar crm', 'acesso crm', 'criar usuario', 'novo colaborador', 'onboarding', 'novo consultor', 'admissao', 'admissão', 'liberacao de acesso', 'liberação de acesso', 'reset de senha', 'troca de senha'];
    const microKeywords = ['microwork', 'dms', 'banco travou', 'nuvem microwork', 'icms', 'ordem de servico', 'ordem de serviço', 'o.s.'];
    const zapKeywords = ['whatsapp', 'wpp', 'conexao zap', 'numero corporativo', 'número corporativo', 'espelhamento'];
    const detranKeywords = ['detran', 'renave', 'atpv', 'intencao de venda', 'intenção de venda'];

    if (roboKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'ROBO_RPA';
    } else if (connKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'CONNECTIVITY_NETWORK';
    } else if (telKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'TELEFONIA';
    } else if (accessKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'ACCESS_PERMISSIONS';
    } else if (microKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'MICROWORK_DMS';
    } else if (zapKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'WHATSAPP_FALEFACIL';
    } else if (detranKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'DETRAN_RENAVE';
    }

    allowed.push({
      json: {
        deal_id: Number(deal.ID),
        title: title,
        description: description,
        requester_user_id: requesterId,
        requester_name: USER_NAMES[requesterId] || 'Colaborador',
        is_purchase: isPurchase,
        store_name: storeName,
        category_theme: categoryTheme
      }
    });
  }
}

return allowed;"""

# 3. Correção de 07_Prepare_AI_Deal_Input
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
      ai_state: item.json.ai_state
    }
  };
});"""

# Atualizar nós no JSON do workflow
for node in wf['nodes']:
    if node['name'] == '02_Reserve_Deal_Session_Atomic':
        print("Atualizando 02_Reserve_Deal_Session_Atomic...")
        node['parameters']['query'] = reserve_query
    elif node['name'] == '01_Strict_Gate_Cat160_Pilot':
        print("Atualizando 01_Strict_Gate_Cat160_Pilot...")
        node['parameters']['jsCode'] = new_gate_code
    elif node['name'] == '07_Prepare_AI_Deal_Input':
        print("Atualizando 07_Prepare_AI_Deal_Input...")
        node['parameters']['jsCode'] = new_prepare_code
    elif node['name'] == '08_AI_Agent_Triage_Deal':
        print("Atualizando System Prompt de 08_AI_Agent_Triage_Deal...")
        prompt = node.get('parameters', {}).get('options', {}).get('systemMessage', '')
        
        # Adicionar regra de liberação de permissão / CRM Bitrix24
        rule_crm = """
14. LIBERAÇÃO DE PERMISSÃO / MÓDULO NO BITRIX24 (CRM, FOLGAS, TICKETS):
   - Aplicável quando o solicitante ou gestor (ex: Hadner) pede liberação de acesso/módulo do Bitrix24 para um colaborador (ex: liberar CRM para mecânico acessar cards de folgas e tickets) ou relata que o menu CRM não aparece.
   - DIRETIVA ESTRITA:
     * O solicitante falando no chat é o gestor responsável pelo card (ex: Hadner). Dirija-se sempre a ele pelo nome correto e trate o acesso como sendo para o colaborador indicado no chamado.
     * NUNCA faça perguntas irrelevantes de telefonia, chip de WhatsApp ou compras de hardware para pedidos de permissão de sistema para colaboradores existentes!
     * Se o usuário confirmar que testou no computador/celular e a opção continua sem aparecer (ou se já relatou que não aparece em nenhum dispositivo):
       - Reconheça que se trata de configuração de perfil/permissão de acesso ao CRM no Bitrix24 que a TI precisa aplicar.
       - CONCLUA A TRIAGEM IMEDIATAMENTE (action COMPLETE) com mensagem calorosa dirigida ao gestor.
       - Estruture no resumo do chamado:
         * Gestor Solicitante: [Nome do Gestor]
         * Colaborador Beneficiário: [Nome do Colaborador, ex: Mecânico Ailton]
         * Sistema e Módulo: Bitrix24 - Permissão de Acesso ao CRM (visualização de folgas e tickets)
         * Filial: [Loja]
         * Status do Teste: Não aparece a opção de CRM no app nem no computador (requer liberação de permissão no perfil de usuário)
         * Ação da TI: Conceder permissão de CRM no perfil do usuário no Bitrix24.
"""
        if '14. LIBERAÇÃO DE PERMISSÃO / MÓDULO NO BITRIX24' not in prompt:
            prompt = prompt + "\n" + rule_crm
            node['parameters']['options']['systemMessage'] = prompt

print("2. Enviando workflow atualizado para o n8n...")
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}
put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Workflow c0F2GUMFm2BI94UG atualizado com sucesso no n8n!")
else:
    print(f"Erro ao atualizar workflow: {put_resp.status_code} - {put_resp.text}")
    sys.exit(1)

# 4. Atualizar o registro da sessão no PostgreSQL para o Deal 1411066
print("3. Atualizando sessão no banco de dados para Deal 1411066 (Hadner)...")
sql_url = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
update_sql = """UPDATE ticket_bot_sessions 
SET requester_name = 'Hadner',
    collected_data_json = jsonb_set(collected_data_json, '{category_theme}', '"ACCESS_PERMISSIONS"')
WHERE deal_id = 1411066;"""
db_res = requests.post(sql_url, json={'query': update_sql}).json()
print("Resultado da atualização no banco:", db_res)

print("\nTodas as correções aplicadas com sucesso!")
