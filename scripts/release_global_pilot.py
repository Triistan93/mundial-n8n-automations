# -*- coding: utf-8 -*-
"""
Script de Liberação Geral do Atendimento de Tickets (Sophia AI - Categoria 160)
Abre o gatekeeper 01_Strict_Gate_Cat160_Pilot para TODOS os colaboradores
e refina a saudação calorosa em 03_Create_CRM_Card_Chat.
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

# Novo código do nó 01_Strict_Gate_Cat160_Pilot
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
  2606: 'Ailton'
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
    if (!storeName) storeName = 'Mogi Guaçu'; // Default filial piloto

    // Detecção de Tema de Incidente
    let categoryTheme = 'GENERAL_IT';
    const connKeywords = ['internet', 'rede', 'caiu', 'conexao', 'conexão', 'link', 'roteador', 'vpn', 'fora do ar', 'offline', 'sem sistema', 'tudo vermelho', 'lentidao geral', 'sem net'];
    const microKeywords = ['microwork', 'dms', 'banco travou', 'nuvem microwork', 'icms', 'ordem de servico', 'os '];
    const zapKeywords = ['whatsapp', 'fale facil', 'fale fácil', 'conexao zap', 'numero corporativo', 'número corporativo', 'espelhamento'];
    const detranKeywords = ['detran', 'renave', 'atpv', 'intencao de venda', 'intenção de venda'];

    if (connKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'CONNECTIVITY_NETWORK';
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

# Novo body do nó 03_Create_CRM_Card_Chat
new_chat_body = """={{ (() => {
  const rawName = String($json.requester_name || '').trim();
  const firstName = (rawName && rawName !== 'Colaborador' && rawName !== 'amigo') ? rawName.split(' ')[0] : '';
  const title = String($json.deal_title || '').trim();
  const hasCustomTitle = title && !title.startsWith('Chamado #') && !title.startsWith('#');
  const isOutage = Boolean($json.is_store_outage);
  const storeName = $json.store_name || 'sua filial';
  const theme = $json.category_theme === 'CONNECTIVITY_NETWORK' ? 'conexão / internet' : ($json.category_theme || 'sistema');

  const greetingPrefix = firstName ? ('Oi, ' + firstName + '! Tudo bem? Sou da Sophia, assistente virtual de TI da Mundial.') : 'Olá! Tudo bem? Sou da Sophia, assistente virtual de TI da Mundial.';

  let greeting = '';
  if (isOutage) {
    greeting = greetingPrefix + '\\n\\n🚨 **ALERTA DE FILIAL:** Identifiquei que outros colegas da filial **' + storeName + '** relataram esse mesmo problema de ' + theme + ' nos últimos minutos.\\n\\nA TI já abriu um incidente de **Prioridade Máxima (P1)** para restabelecer a loja toda! Você não precisa se preocupar em abrir novos chamados, nossa equipe técnica já está atuando para todos.';
  } else if (hasCustomTitle) {
    greeting = greetingPrefix + '\\n\\nVi que você abriu este chamado sobre: "' + title + '".\\n\\nMe conta com calma o que está acontecendo por aí? Se quiser mandar uma foto da tela ou do equipamento, fica à vontade! Vamos tentar resolver juntos.';
  } else {
    greeting = greetingPrefix + '\\n\\nMe conta com calma o que está acontecendo com o seu computador ou sistema? Pode mandar uma foto da tela ou do equipamento se preferir, e vamos tentar resolver juntos!';
  }

  return JSON.stringify({
    TYPE: 'CHAT',
    TITLE: 'Triagem TI - Chamado #' + $json.deal_id + (isOutage ? ' [🚨 QUEDA GERAL ' + storeName + ']' : (hasCustomTitle ? ': ' + title : '')),
    ENTITY_TYPE: 'CRM',
    ENTITY_ID: 'DEAL|' + $json.deal_id,
    USERS: [Number($json.requester_user_id), 61622],
    MESSAGE: greeting
  });
})() }}"""

updated_nodes = 0
for n in wf.get('nodes', []):
    if n['name'] == '01_Strict_Gate_Cat160_Pilot':
        n['parameters']['jsCode'] = new_gate_code
        updated_nodes += 1
        print("-> Nó 01_Strict_Gate_Cat160_Pilot configurado para ALLOW_ALL_USERS = true")
    elif n['name'] == '03_Create_CRM_Card_Chat':
        n['parameters']['jsonBody'] = new_chat_body
        updated_nodes += 1
        print("-> Nó 03_Create_CRM_Card_Chat configurado com saudação enriquecida")

if updated_nodes != 2:
    print(f"Erro: apenas {updated_nodes}/2 nós foram encontrados!")
    sys.exit(1)

print("2. Enviando workflow atualizado para a API do n8n...")
payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Sucesso! Workflow c0F2GUMFm2BI94UG atualizado com liberação geral!")
else:
    print(f"Erro ao salvar: {put_resp.status_code} - {put_resp.text}")
    sys.exit(1)
