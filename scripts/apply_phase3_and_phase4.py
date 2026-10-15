# -*- coding: utf-8 -*-
"""
Implementação das Fases 3 e 4 do Plano de Ação:
Fase 3: Refinamento de Regex de Temas com Borda de Palavra (\b) e Blindagem Estrita de Outage
Fase 4: Guardrail Cognitivo Anti-Redundância (Pré-Extração de Entidades e Anti-Repetição no Prompt)
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

# 1. Novo código de 01_Strict_Gate_Cat160_Pilot com Regex Contextual (\b)
new_gate_code = r"""// GATE FAIL-CLOSED ABSOLUTO:
// Verifica se o Deal pertence EXCLUSIVAMENTE à Categoria 160
// Piloto Aberto para TODOS os Colaboradores da Concessionária com Botão de Pânico Ativo
const items = $input.all();
const allowed = [];

// Flag de Liberação Geral: aberta para todos os colaboradores
const ALLOW_ALL_USERS = true;
const ALLOWED_REQUESTERS = [32598];

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

    // Detecção Rigorosa de Temas por Regex Contextual com Borda de Palavra (\b)
    let categoryTheme = 'GENERAL_IT';

    const rxRobo = /\b(rob[ôo]|card\s+rob[ôo]|entrada\s+honda|entrada\s+grupo|vigia|dms_vigia|faturamento\s+direto|solicita[çc][ãa]o\s+de\s+entrada|loop)\b/i;
    const rxDetran = /\b(atpv|atpv-?e|renave|detran|inten[çc][ãa]o\s+de\s+venda|9c2[a-hj-npr-z0-9]{14})\b/i;
    const rxNetwork = /\b(internet|rede\s+caiu|queda\s+de\s+link|roteador|vpn|fora\s+do\s+ar|offline|sem\s+sistema|tudo\s+vermelho|lentid[ãa]o\s+geral|sem\s+net|wi-?fi|link\s+caiu)\b/i;
    const rxTelefonia = /\b(telefone|ramal|liga[çc][ãa]o|liga[çc][õo]es|headset|fone|fale\s+f[áa]cil|n[ãa]o\s+toca|sem\s+tom)\b/i;
    const rxWhatsapp = /\b(whats?app|wpp|zap|conex[ãa]o\s+zap|n[úu]mero\s+corporativo|espelhamento)\b/i;
    const rxAccess = /\b(libera[çc][ãa]o\s+de\s+acesso|liberar\s+acesso|acesso\s+crm|liberar\s+crm|permiss[ãa]o|permissoes|criar\s+usu[áa]rio|novo\s+colaborador|novo\s+consultor|onboarding|admiss[ãa]o|reset\s+de\s+senha|esqueci\s+a\s+senha|trocar\s+senha)\b/i;
    const rxMicroWork = /\b(microwork|dms|banco\s+travou|nuvem\s+microwork|icms|ordem\s+de\s+servi[çc]o|o\.?s\.?\s*\d+|rotina\s*\d+)\b/i;

    if (rxRobo.test(fullText)) {
      categoryTheme = 'ROBO_RPA';
    } else if (rxDetran.test(fullText)) {
      categoryTheme = 'DETRAN_RENAVE';
    } else if (rxNetwork.test(fullText)) {
      categoryTheme = 'CONNECTIVITY_NETWORK';
    } else if (rxTelefonia.test(fullText)) {
      categoryTheme = 'TELEFONIA';
    } else if (rxWhatsapp.test(fullText)) {
      categoryTheme = 'WHATSAPP_FALEFACIL';
    } else if (rxAccess.test(fullText)) {
      categoryTheme = 'ACCESS_PERMISSIONS';
    } else if (rxMicroWork.test(fullText)) {
      categoryTheme = 'MICROWORK_DMS';
    }

    allowed.push({
      json: {
        deal_id: Number(deal.ID),
        title: title,
        description: description,
        requester_user_id: requesterId,
        requester_name: 'Colaborador',
        is_purchase: isPurchase,
        store_name: storeName,
        category_theme: categoryTheme
      }
    });
  }
}

return allowed;"""

# 2. Novo código de 07_Prepare_AI_Deal_Input com Pré-Extração de Entidades e Anti-Redundância
new_prepare_code = r"""// Prepara input isolado para o Agente LangChain por Deal com contexto do card, separação Gestor vs Beneficiário e Anti-Redundância
const items = $input.all();
return items.map(item => {
  const collected = item.json.collected_data_json || {};
  const title = String(collected.deal_title || '').trim();
  const userInput = String(item.json.message_text || '').trim();
  const requesterName = String(item.json.requester_name || 'Colaborador').trim();
  const requesterPosition = String(collected.requester_position || '').trim();

  // 1. Pré-Extração Determinística de Entidades Conhecidas no Card (Anti-Redundância)
  const fullSearchText = `${title} ${userInput}`;
  const extractedEntities = [];

  // Chassi de 17 dígitos
  const chassiMatch = fullSearchText.match(/\b(9C2[A-HJ-NPR-Z0-9]{14})\b/i);
  if (chassiMatch) {
    extractedEntities.push(`Chassi Identificado: "${chassiMatch[1].toUpperCase()}" -> (REGRA ESTRITA: PROIBIDO PERGUNTAR O CHASSI NOVAMENTE AO USUÁRIO)`);
  }

  // Link de Card Bitrix
  const cardLinkMatch = fullSearchText.match(/(https:\/\/b24-[a-z0-9]+\.bitrix24\.com\.br\/crm\/deal\/details\/\d+\/)/i);
  if (cardLinkMatch) {
    extractedEntities.push(`Link do Card no Bitrix: "${cardLinkMatch[1]}" -> (REGRA ESTRITA: PROIBIDO PEDIR O LINK DO CARD NOVAMENTE)`);
  }

  // Número de Nota Fiscal
  const nfMatch = fullSearchText.match(/\b(?:nf|nota|nfe)\s*[:#ºn]?\s*(\d{4,9})\b/i);
  if (nfMatch) {
    extractedEntities.push(`Número de Nota Fiscal: "${nfMatch[1]}"`);
  }

  // Ordem de Serviço (OS)
  const osMatch = fullSearchText.match(/\b(?:os|o\.s\.)\s*[:#ºn]?\s*(\d{4,8})\b/i);
  if (osMatch) {
    extractedEntities.push(`Número da OS: "${osMatch[1]}"`);
  }

  let factsBlock = '';
  if (extractedEntities.length > 0) {
    factsBlock = `[DADOS JÁ CONFIRMADOS E COMPROVADOS NO CARD (NÃO PERGUNTE NOVAMENTE AO USUÁRIO)]:\n` +
      extractedEntities.map(e => `• ${e}`).join('\n') + '\n\n';
  }

  // 2. Detecção de solicitação em nome de terceiro (Gestor abrindo para colaborador)
  let thirdPartyNote = '';
  const thirdPartyMatch = title.match(/(?:para|do|da|mecanico|mecânico|vendedor|estoquista|novo colaborador|novo consultor)\s+([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+)?)/i);
  
  if (thirdPartyMatch && thirdPartyMatch[1] && !thirdPartyMatch[1].toLowerCase().includes(requesterName.toLowerCase())) {
    const beneficiary = thirdPartyMatch[1].trim();
    thirdPartyNote = `[ATENÇÃO - CHAMADO ABERTO EM NOME DE OUTRA PESSOA]:\n` +
      `- O usuário conversando com você no chat é o(a) solicitante: ${requesterName}${requesterPosition ? ' (' + requesterPosition + ')' : ''}.\n` +
      `- O colaborador citado que precisa da liberação/suporte é: "${beneficiary}".\n` +
      `- DIRETIVA: Dirija-se sempre a ${requesterName} pelo nome dele(a). NUNCA o confunda com ${beneficiary}. Trate a demanda como uma solicitação feita por ${requesterName} em favor de ${beneficiary}.\n\n`;
  }

  let contextHeader = `[SOLICITANTE DO CARD / USUÁRIO NO CHAT]: ${requesterName}${requesterPosition ? ' (' + requesterPosition + ')' : ''}\n`;
  if (title && !title.startsWith('Chamado #') && !title.startsWith('#')) {
    contextHeader += `[TÍTULO DO CHAMADO]: "${title}"\n`;
  }
  
  const contextualInput = `${contextHeader}${factsBlock}${thirdPartyNote}[MENSAGEM DO COLABORADOR NO CHAT]:\n${userInput}`;

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

# 3. Atualizar System Prompt de 08_AI_Agent_Triage_Deal com Guardrail Anti-Redundância
anti_redundancy_rule = """
# REGRA DE OURO ANTI-REDUNDÂNCIA & EFICIÊNCIA CONVERSACIONAL (UX):
1. NUNCA pergunte ao usuário uma informação que já foi informada:
   - No título do chamado;
   - Na mensagem de abertura;
   - Na seção [DADOS JÁ CONFIRMADOS E COMPROVADOS NO CARD];
   - No print de erro analisado via OCR Vision.
2. Se o Chassi, Link do Card, NF ou Erro já foram informados, use-os diretamente no diagnóstico ou na conclusão da triagem.
3. Se faltarem dados essenciais, formule uma ÚNICA mensagem harmoniosa, gentil e completa. NUNCA dispare rajadas de mensagens ou perguntas repetidas em sequência.
"""

print("\n2. Aplicando alterações nos nós do workflow...")
for node in wf['nodes']:
    name = node['name']
    if name == '01_Strict_Gate_Cat160_Pilot':
        print(f"  [Fase 3] 01_Strict_Gate_Cat160_Pilot -> Regex contextual com bordas de palavra (\\b)")
        node['parameters']['jsCode'] = new_gate_code
    elif name == '07_Prepare_AI_Deal_Input':
        print(f"  [Fase 4] 07_Prepare_AI_Deal_Input -> Pré-extração de entidades determinísticas")
        node['parameters']['jsCode'] = new_prepare_code
    elif name == '08_AI_Agent_Triage_Deal':
        print(f"  [Fase 4] 08_AI_Agent_Triage_Deal -> Guardrail Anti-Redundância no System Prompt")
        prompt = node.get('parameters', {}).get('options', {}).get('systemMessage', '')
        if 'ANTI-REDUNDÂNCIA & EFICIÊNCIA CONVERSACIONAL' not in prompt:
            prompt = prompt + "\n" + anti_redundancy_rule
            node['parameters']['options']['systemMessage'] = prompt

print("\n3. Salvando workflow atualizado no n8n...")
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}
put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Workflow c0F2GUMFm2BI94UG salvo com sucesso no n8n com Fases 3 e 4 ativas!")
else:
    print(f"Erro ao salvar: {put_resp.status_code} - {put_resp.text}")
    sys.exit(1)
