# -*- coding: utf-8 -*-
"""
Script de Correção Imediata do Alerta Falso de Outage e Remediação do Chamado 1411194 (Flavio):
1. Restringe store outage EXCLUSIVAMENTE para CONNECTIVITY_NETWORK (elimina falso alarme em GENERAL_IT);
2. Adiciona keywords de TELEFONIA em 01_Strict_Gate_Cat160_Pilot;
3. Refina 03_Create_CRM_Card_Chat para ler descrição (UF_CRM_1729774515200) e título do card, sem termos em inglês;
4. Envia mensagem de retratação e pergunta correta no chat do Flavio (#1411194);
5. Notifica o Gestor de TI (Eduardo Alaminos 32598) sobre o chamado do Flavio.
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# =====================================================================
# PARTE 1: ATUALIZAÇÃO DO WORKFLOW NO N8N
# =====================================================================
print("1. Obtendo workflow c0F2GUMFm2BI94UG do n8n...")
wf = requests.get(N8N_URL, headers=headers).json()

# 1.1. Novo código de 01_Evaluate_Store_Outage
new_evaluate_store_outage = """// Avalia resultado do clustering de outage por loja
const items = $input.all();
return items.map(item => {
  const d = item.json;
  const countRecent = Number(d.count_recent || 0);

  // REGRA DE OURO: Outage é EXCLUSIVO para queda geral de INTERNET/REDE da loja!
  // Jamais disparar para GENERAL_IT, TELEFONIA, MICROWORK, etc.
  const isNetworkTheme = d.category_theme === 'CONNECTIVITY_NETWORK';
  const isOutage = isNetworkTheme && countRecent >= 2;
  const outageCount = countRecent + 1;

  return {
    json: {
      deal_id: d.deal_id,
      title: d.title,
      description: d.description,
      requester_user_id: d.requester_user_id,
      requester_name: d.requester_name,
      is_purchase: d.is_purchase,
      store_name: d.store_name,
      category_theme: d.category_theme,
      is_store_outage: isOutage,
      outage_count: outageCount
    }
  };
});"""

# 1.2. Novo código de 01_Strict_Gate_Cat160_Pilot
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
  2606: 'Ailton',
  469422: 'Flavio Queiroz'
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

    // Detecção de Tema de Incidente com suporte completo a TELEFONIA
    let categoryTheme = 'GENERAL_IT';
    const connKeywords = ['internet', 'rede', 'caiu', 'conexao', 'conexão', 'link', 'roteador', 'vpn', 'fora do ar', 'offline', 'sem sistema', 'tudo vermelho', 'lentidao geral', 'sem net', 'wi-fi', 'wifi'];
    const telKeywords = ['telefone', 'ramal', 'ligacao', 'ligação', 'headset', 'fone', 'não toca', 'nao toca', 'mudo', 'fale facil', 'fale fácil'];
    const microKeywords = ['microwork', 'dms', 'banco travou', 'nuvem microwork', 'icms', 'ordem de servico', 'os '];
    const zapKeywords = ['whatsapp', 'wpp', 'conexao zap', 'numero corporativo', 'número corporativo', 'espelhamento'];
    const detranKeywords = ['detran', 'renave', 'atpv', 'intencao de venda', 'intenção de venda'];

    if (connKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'CONNECTIVITY_NETWORK';
    } else if (telKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'TELEFONIA';
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

# 1.3. Novo body de 03_Create_CRM_Card_Chat
new_chat_body = """={{ (() => {
  const rawName = String($json.requester_name || '').trim();
  const firstName = (rawName && rawName !== 'Colaborador' && rawName !== 'amigo') ? rawName.split(' ')[0] : '';
  const title = String($json.deal_title || '').trim();
  const desc = String($json.description || '').trim();
  const isOutage = Boolean($json.is_store_outage);
  const storeName = $json.store_name || 'sua filial';

  const THEME_NAMES = {
    'CONNECTIVITY_NETWORK': 'internet / rede da loja',
    'TELEFONIA': 'telefonia e ramal',
    'WHATSAPP_FALEFACIL': 'WhatsApp corporativo',
    'MICROWORK_DMS': 'MicroWork Cloud',
    'DETRAN_RENAVE': 'emissão de ATPV / RENAVE',
    'GENERAL_IT': 'computador / sistema'
  };

  const hasDesc = desc && !desc.startsWith('Chamado #') && !desc.startsWith('#');
  const hasCustomTitle = title && !title.startsWith('Chamado #') && !title.startsWith('#') && title.toLowerCase() !== rawName.toLowerCase();

  const greetingPrefix = firstName 
    ? ('Oi, ' + firstName + '! Tudo bem? Sou da Sophia, assistente virtual de TI da Mundial.') 
    : 'Olá! Tudo bem? Sou da Sophia, assistente virtual de TI da Mundial.';

  let greeting = '';
  if (isOutage) {
    greeting = greetingPrefix + '\\n\\n🚨 **ALERTA DE FILIAL:** Identifiquei que outros colegas da filial **' + storeName + '** relataram esse mesmo problema de **' + (THEME_NAMES[$json.category_theme] || 'conexão') + '** nos últimos minutos.\\n\\nA TI já abriu um incidente de **Prioridade Máxima (P1)** para restabelecer a loja toda! Você não precisa se preocupar em abrir novos chamados, nossa equipe técnica já está atuando para todos.';
  } else if (hasDesc) {
    greeting = greetingPrefix + '\\n\\nVi que você abriu este chamado relatando: "' + desc + '".\\n\\n' +
      ($json.category_theme === 'TELEFONIA'
        ? 'Você está utilizando o **Aplicativo Desktop do Bitrix24** instalado no computador ou está acessando pelo navegador? E no cabo do fone/headset, o botão de mudo não está acionado?'
        : 'Pode me contar se isso começou agora e se você chegou a fazer algum teste? Se tiver uma foto ou print da tela, pode enviar aqui direto!');
  } else if (hasCustomTitle) {
    greeting = greetingPrefix + '\\n\\nVi que você abriu este chamado sobre: "' + title + '".\\n\\nMe conta com calma o que está acontecendo por aí? Se quiser mandar uma foto da tela ou do equipamento, fica à vontade! Vamos tentar resolver juntos.';
  } else {
    greeting = greetingPrefix + '\\n\\nMe conta com calma o que está acontecendo com o seu computador ou sistema? Pode mandar uma foto da tela ou do equipamento se preferir, e vamos tentar resolver juntos!';
  }

  return JSON.stringify({
    TYPE: 'CHAT',
    TITLE: 'Triagem TI - Chamado #' + $json.deal_id + (isOutage ? ' [🚨 QUEDA GERAL ' + storeName + ']' : (hasDesc ? ': ' + desc : (hasCustomTitle ? ': ' + title : ''))),
    ENTITY_TYPE: 'CRM',
    ENTITY_ID: 'DEAL|' + $json.deal_id,
    USERS: [Number($json.requester_user_id), 61622],
    MESSAGE: greeting
  });
})() }}"""

updated_nodes = 0
for n in wf.get('nodes', []):
    if n['name'] == '01_Evaluate_Store_Outage':
        n['parameters']['jsCode'] = new_evaluate_store_outage
        updated_nodes += 1
        print("-> 01_Evaluate_Store_Outage corrigido (outage restrito a CONNECTIVITY_NETWORK)")
    elif n['name'] == '01_Strict_Gate_Cat160_Pilot':
        n['parameters']['jsCode'] = new_gate_code
        updated_nodes += 1
        print("-> 01_Strict_Gate_Cat160_Pilot atualizado com tema TELEFONIA e nomes")
    elif n['name'] == '03_Create_CRM_Card_Chat':
        n['parameters']['jsonBody'] = new_chat_body
        updated_nodes += 1
        print("-> 03_Create_CRM_Card_Chat atualizado com leitura de descrição e sem jargões")

print("Enviando workflow atualizado para o n8n...")
payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}
put_resp = requests.put(N8N_URL, headers=headers, json=payload)
print(f"Status do update no n8n: {put_resp.status_code}")

# =====================================================================
# PARTE 2: REMEDIAÇÃO IMEDIATA DO CHAMADO 1411194 (FLAVIO)
# =====================================================================
print("\n2. Remediando chamado #1411194 no Bitrix24...")

# 2.1. Envia mensagem corrigida no chat com o Flavio (chat862836)
flavio_msg = (
    "Oi, Flavio! Tudo bem? Sou da Sophia, da Central de TI.\n\n"
    "Peço desculpas pela mensagem automática anterior de alerta geral! Já identifiquei que seu chamado é sobre o seu **telefone que não está tocando no Bitrix**.\n\n"
    "Para resolvermos rápido:\n"
    "1. Você está utilizando o **Aplicativo Desktop do Bitrix24** instalado no computador ou está acessando pelo navegador web?\n"
    "2. No cabo do seu headset/fone, o botão físico de mudo não está ativado (luz vermelha acesa no controle do fio)?"
)

send_url = "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add"
r_flavio = requests.post(send_url, json={
    'DIALOG_ID': 'chat862836',
    'MESSAGE': flavio_msg
})
print(f"Mensagem enviada no chat do Flavio: {r_flavio.json().get('result')}")

# 2.2. Atualiza a sessão no PostgreSQL para remover o falso outage
sql_url = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
upd_sess = """UPDATE ticket_bot_sessions 
SET collected_data_json = '{"store_name": "Mogi Mirim", "category_theme": "TELEFONIA", "is_store_outage": false, "deal_title": "Flavio", "deal_description": "telefone nao esta tocando no meu bitrix"}'::jsonb,
    ai_state = 'AI_ACTIVE',
    status = 'ACTIVE'
WHERE deal_id = 1411194;"""
requests.post(sql_url, json={'query': upd_sess})
print("Sessão do chamado #1411194 corrigida no PostgreSQL!")

# 2.3. Notifica o Gestor de TI (Eduardo Alaminos 32598) sobre o chamado do Flavio
it_msg = (
    "📞 **NOVO CHAMADO DE TELEFONIA EM ANDAMENTO (SOPHIA AI)**\n"
    "--------------------------------------------------\n"
    "📌 **Chamado:** #1411194 - Flavio Queiroz (Mogi Mirim)\n"
    "📝 **Problema:** Telefone não está tocando no Bitrix\n"
    "🔗 **Card:** https://b24-88dbfb.bitrix24.com.br/crm/deal/details/1411194/\n"
    "💬 **Chat:** https://b24-88dbfb.bitrix24.com.br/online/?IM_DIALOG=chat862836\n"
    "Status: Triagem guiada de headset/app em andamento."
)
r_it = requests.post(send_url, json={
    'DIALOG_ID': '32598',
    'MESSAGE': it_msg
})
print(f"Notificação enviada ao Gestor de TI (32598): {r_it.json().get('result')}")
