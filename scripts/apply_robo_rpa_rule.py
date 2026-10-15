# -*- coding: utf-8 -*-
"""
Script de Implementação da Regra Operacional para Robôs RPA da Mundial Honda:
- Atualiza 08_AI_Agent_Triage_Deal com a Seção 13 (Robôs RPA);
- Atualiza 01_Strict_Gate_Cat160_Pilot para detectar ROBO_RPA;
- Atualiza 03_Create_CRM_Card_Chat com a abordagem de robôs (pedir link e conferência de dados);
- Ingesta KB-019 em kb_ti_conhecimento.
"""
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
INGEST_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-ingest'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# =====================================================================
# 1. ATUALIZAÇÃO DO WORKFLOW N8N
# =====================================================================
print("1. Obtendo workflow c0F2GUMFm2BI94UG do n8n...")
wf = requests.get(N8N_URL, headers=headers).json()

# 1.1. System Prompt com Seção 13
robo_rule = """
13. CHAMADOS ENVOLVENDO ROBÔS / AUTOMAÇÕES RPA (CARD ROBÔ, ENTRADA HONDA, ENTRADA GRUPO, VIGIA, FATURAMENTO):
   - Aplicável quando o colaborador cita 'robô', 'robo', 'card robo', 'card robô', 'entrada honda', 'entrada grupo', 'faturamento direto', 'dms_vigia', 'travado em processamento', 'solicitação de entrada em loop', 'robô parado'.
   - CONDUTA OBRIGATÓRIA DA SOPHIA AI (DIRETIVA ESTRITA DA TI):
     * NUNCA oriente o colaborador a fechar navegador, reiniciar computador ou limpar cache! Trata-se de um processo de backend em servidor de automação, não tem relação com o navegador do usuário.
     * O assistente deve APENAS:
       1. Pedir o LINK DO CARD do Bitrix24 onde o robô está atuando (se a pessoa ainda não informou);
       2. Perguntar se a pessoa já conferiu se todos os dados do card estão corretos (número da nota, chassi, fornecedor, valores);
       3. Imediatamente após a resposta da pessoa (ou se ela já informou esses dois dados), CONCLUA A TRIAGEM (action COMPLETE) com alta urgência e encaminhe para a equipe técnica de TI intervir no robô no servidor!"""

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

    // Detecção de Tema de Incidente com suporte a ROBÔS RPA e TELEFONIA
    let categoryTheme = 'GENERAL_IT';
    const roboKeywords = ['robo', 'robô', 'card robo', 'card robô', 'entrada honda', 'entrada grupo', 'faturamento direto', 'dms_vigia', 'processamento', 'solicitacao de entrada', 'solicitação de entrada'];
    const connKeywords = ['internet', 'rede', 'caiu', 'conexao', 'conexão', 'link', 'roteador', 'vpn', 'fora do ar', 'offline', 'sem sistema', 'tudo vermelho', 'lentidao geral', 'sem net', 'wi-fi', 'wifi'];
    const telKeywords = ['telefone', 'ramal', 'ligacao', 'ligação', 'headset', 'fone', 'não toca', 'nao toca', 'mudo', 'fale facil', 'fale fácil'];
    const microKeywords = ['microwork', 'dms', 'banco travou', 'nuvem microwork', 'icms', 'ordem de servico', 'os '];
    const zapKeywords = ['whatsapp', 'wpp', 'conexao zap', 'numero corporativo', 'número corporativo', 'espelhamento'];
    const detranKeywords = ['detran', 'renave', 'atpv', 'intencao de venda', 'intenção de venda'];

    if (roboKeywords.some(kw => fullText.includes(kw))) {
      categoryTheme = 'ROBO_RPA';
    } else if (connKeywords.some(kw => fullText.includes(kw))) {
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
  const categoryTheme = $json.category_theme || 'GENERAL_IT';

  const THEME_NAMES = {
    'CONNECTIVITY_NETWORK': 'internet / rede da loja',
    'TELEFONIA': 'telefonia e ramal',
    'WHATSAPP_FALEFACIL': 'WhatsApp corporativo',
    'MICROWORK_DMS': 'MicroWork Cloud',
    'DETRAN_RENAVE': 'emissão de ATPV / RENAVE',
    'ROBO_RPA': 'robô de automação / integração RPA',
    'GENERAL_IT': 'computador / sistema'
  };

  const hasDesc = desc && !desc.startsWith('Chamado #') && !desc.startsWith('#');
  const hasCustomTitle = title && !title.startsWith('Chamado #') && !title.startsWith('#') && title.toLowerCase() !== rawName.toLowerCase();

  const greetingPrefix = firstName 
    ? ('Oi, ' + firstName + '! Tudo bem? Sou da Sophia, assistente virtual de TI da Mundial.') 
    : 'Olá! Tudo bem? Sou da Sophia, assistente virtual de TI da Mundial.';

  let greeting = '';
  if (isOutage) {
    greeting = greetingPrefix + '\\n\\n🚨 **ALERTA DE FILIAL:** Identifiquei que outros colegas da filial **' + storeName + '** relataram esse mesmo problema de **' + (THEME_NAMES[categoryTheme] || 'conexão') + '** nos últimos minutos.\\n\\nA TI já abriu um incidente de **Prioridade Máxima (P1)** para restabelecer a loja toda! Você não precisa se preocupar em abrir novos chamados, nossa equipe técnica já está atuando para todos.';
  } else if (categoryTheme === 'ROBO_RPA') {
    greeting = greetingPrefix + '\\n\\nIdentifiquei que sua solicitação envolve um de nossos **robôs de automação** (' + (hasDesc ? desc : (hasCustomTitle ? title : 'processamento RPA')) + ').\\n\\n' +
      'Para que a equipe de TI possa analisar e destravar o robô com rapidez:\\n' +
      '1. Você pode me enviar o **link do card de negócio** no Bitrix24 onde o robô está atuando?\\n' +
      '2. Você já chegou a conferir se todos os dados e valores do card estão preenchidos corretamente?';
  } else if (hasDesc) {
    greeting = greetingPrefix + '\\n\\nVi que você abriu este chamado relatando: "' + desc + '".\\n\\n' +
      (categoryTheme === 'TELEFONIA'
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
    if n['name'] == '01_Strict_Gate_Cat160_Pilot':
        n['parameters']['jsCode'] = new_gate_code
        updated_nodes += 1
        print("-> 01_Strict_Gate_Cat160_Pilot atualizado com tema ROBO_RPA")
    elif n['name'] == '03_Create_CRM_Card_Chat':
        n['parameters']['jsonBody'] = new_chat_body
        updated_nodes += 1
        print("-> 03_Create_CRM_Card_Chat atualizado com fluxo dedicado para ROBO_RPA")
    elif n['name'] == '08_AI_Agent_Triage_Deal':
        sm = n['parameters']['options']['systemMessage']
        needle = "12. CHAMADOS ABERTOS APENAS COM NOME DE PESSOA:"
        if "13. CHAMADOS ENVOLVENDO ROBÔS" not in sm:
            end_sec12 = sm.find("# DETECTOR DE RISCO COMERCIAL")
            if end_sec12 > 0:
                sm = sm[:end_sec12] + robo_rule + "\n\n" + sm[end_sec12:]
                n['parameters']['options']['systemMessage'] = sm
                updated_nodes += 1
                print("-> 08_AI_Agent_Triage_Deal atualizado com Seção 13 (Robôs RPA)")

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
# 2. INGESTÃO DE KB-019 NO PGVECTOR
# =====================================================================
print("\n2. Ingerindo KB-019 (Robôs RPA) no pgvector...")
kb_019 = {
    "kb_id": "KB-019",
    "title": "Robôs de Automação RPA (Entrada Honda, Entrada Grupo, Vigia e Faturamento): Cards Travados e Escalonamento para TI",
    "systems": "Robôs RPA Mundial, Entrada Honda (C122), Entrada Grupo (C146), Faturamento Direto (C24), Vigia (C24), Bitrix24",
    "keywords": "robo, robô, card robo, card robô, entrada honda, entrada grupo, faturamento direto, vigia, processo travado, solicitação de entrada, loop de processamento, robô parado, link do card, dados corretos, danielly",
    "source": "KB-019-robos-rpa-cards-travados.md",
    "text": """# KB-019 - Robôs de Automação RPA (Entrada Honda, Entrada Grupo, Vigia e Faturamento): Cards Travados e Escalonamento para TI
Sistemas: Robôs RPA Mundial, Entrada Honda (C122), Entrada Grupo (C146), Faturamento Direto (C24), Vigia (C24), Bitrix24 CRM
Palavras-chave: robo, robô, card robo, card robô, entrada honda, entrada grupo, faturamento direto, vigia, processo travado, solicitação de entrada, loop de processamento, robô parado, link do card, dados corretos, danielly

## Quando usar
Colaborador relata: "card do robô travado em processamento", "robô de entrada honda não finaliza nota", "solicitação de entrada em loop", "robô parado", "card do robô com erro".

## DIRETIVA OBRIGATÓRIA DA TI (ESCOPO DA SOPHIA AI)
Os robôs são automações executadas em servidores dedicados de backend. Não há qualquer ação no navegador ou computador do colaborador que destrave um robô.
A Sophia AI NUNCA deve instruir o colaborador a fechar navegador, reiniciar máquina ou limpar cookies!

## Checklist Obrigatório de Triagem para a TI:
O assistente deve realizar EXCLUSIVAMENTE estas duas verificações:
1. **Link do Card de Negócio:** Solicitar o link do card no Bitrix24 onde o robô está em execução (ex: https://b24-88dbfb.bitrix24.com.br/crm/deal/details/XXXXX/);
2. **Conferência de Dados:** Confirmar se o colaborador já verificou se todos os dados do card estão preenchidos corretamente (número da nota, chassi, fornecedor, valores e anexos).

## Conclusão Imediata (Escalonamento L2):
Assim que o colaborador responder (ou se ele já forneceu o link e confirmou os dados):
- Conclua a triagem IMEDIATAMENTE (action COMPLETE) com alta urgência;
- Escale o chamado para a fila da equipe de TI intervir no robô no servidor corporativo."""
}

r_ingest = requests.post(INGEST_URL, json={"documents": [kb_019]})
print(f"Status da ingestão da KB-019: {r_ingest.status_code}")
