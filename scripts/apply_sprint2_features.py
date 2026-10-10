# -*- coding: utf-8 -*-
import json
import sys
import copy

sys.stdout.reconfigure(encoding='utf-8')

# Load current workflow
wf_path = 'workflows/BITRIX_TI_AI_TRIAGE_AGENT.json'
with open(wf_path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Save backup before Sprint 2
with open('workflows/backup_before_sprint2.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
print("Backup created: workflows/backup_before_sprint2.json")

nodes = wf.get('nodes', [])
connections = wf.get('connections', {})

# ----------------------------------------------------
# 1. Update 01_Strict_Gate_Cat160_Pilot
# ----------------------------------------------------
gate_node = next(n for n in nodes if n['name'] == '01_Strict_Gate_Cat160_Pilot')
gate_code = """// GATE FAIL-CLOSED ABSOLUTO:
// Verifica se o Deal pertence EXCLUSIVAMENTE à Categoria 160 e ao usuário 32598 (Eduardo Alaminos)
// Sprint 2: Adiciona mapeamento determinístico de Loja/Unidade e Detecção de Tema para Incident Clustering
const items = $input.all();
const allowed = [];
const ALLOWED_REQUESTERS = [32598]; // Piloto restrito Eduardo Alaminos

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

  const requesterId = ALLOWED_REQUESTERS.includes(createdBy) 
    ? createdBy 
    : (ALLOWED_REQUESTERS.includes(assignedBy) ? assignedBy : 0);

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
    const microKeywords = ['microwork', 'dms', 'banco travou', 'nuvem microwork'];
    const zapKeywords = ['whatsapp', 'fale facil', 'fale fácil', 'conexao zap', 'numero corporativo', 'número corporativo'];
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
        requester_name: 'Eduardo Alaminos',
        is_purchase: isPurchase,
        store_name: storeName,
        category_theme: categoryTheme
      }
    });
  }
}

return allowed;
"""
gate_node['parameters']['functionCode'] = gate_code

# ----------------------------------------------------
# 2. Add Cluster Outage Check Nodes (Feature 2)
# ----------------------------------------------------
outage_check_node = {
    "id": "node_check_store_outage",
    "name": "01_Check_Store_Outage_Cluster",
    "type": "n8n-nodes-base.postgres",
    "typeVersion": 1,
    "position": [600, 128],
    "parameters": {
        "operation": "executeQuery",
        "query": """WITH recent_events AS (
    SELECT COUNT(*) AS count_recent
    FROM store_outage_events
    WHERE store_name = '{{ $json.store_name }}'
      AND category_theme = '{{ $json.category_theme }}'
      AND created_at >= NOW() - INTERVAL '30 MINUTES'
),
inserted AS (
    INSERT INTO store_outage_events (store_name, category_theme, deal_id, created_at)
    VALUES ('{{ $json.store_name }}', '{{ $json.category_theme }}', {{ $json.deal_id }}, NOW())
    RETURNING id
)
SELECT recent_events.count_recent,
       '{{ $json.store_name }}' AS store_name,
       '{{ $json.category_theme }}' AS category_theme,
       {{ $json.deal_id }} AS deal_id,
       '{{ $json.title }}' AS title,
       '{{ $json.description }}' AS description,
       {{ $json.requester_user_id }} AS requester_user_id,
       '{{ $json.requester_name }}' AS requester_name,
       {{ $json.is_purchase ? 'TRUE' : 'FALSE' }} AS is_purchase
FROM recent_events;"""
    },
    "credentials": {
        "postgres": {
            "id": "J8q2YHlBbp4WxxV2",
            "name": "Postgres account"
        }
    }
}

outage_eval_node = {
    "id": "node_evaluate_store_outage",
    "name": "01_Evaluate_Store_Outage",
    "type": "n8n-nodes-base.function",
    "typeVersion": 1,
    "position": [720, 128],
    "parameters": {
        "functionCode": """// Avalia resultado do clustering de outage por loja
const items = $input.all();
return items.map(item => {
  const d = item.json;
  const countRecent = Number(d.count_recent || 0);
  const isOutage = countRecent >= 2; // 3º ou mais chamado na mesma janela de 30 min
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
    }
}

# Update 02_Reserve_Deal_Session_Atomic to store outage info
reserve_node = next(n for n in nodes if n['name'] == '02_Reserve_Deal_Session_Atomic')
reserve_node['parameters']['query'] = """INSERT INTO ticket_bot_sessions (
    deal_id, requester_user_id, requester_name, channel, private_dialog_id, 
    dialog_type, status, state, ai_state, redis_memory_key, collected_data_json, 
    created_at, last_interaction_at
) VALUES (
    {{ $json.deal_id }}, {{ $json.requester_user_id }}, '{{ $json.requester_name }}', 
    'BITRIX_CRM_CHAT', '', 'chat', 'CHAT_CREATING', 'INIT', 'AI_ACTIVE', 
    'bitrix:ti:deal:{{ $json.deal_id }}:memory', 
    '{"store_name": "{{ $json.store_name }}", "category_theme": "{{ $json.category_theme }}", "is_store_outage": {{ $json.is_store_outage ? 'true' : 'false' }}, "outage_count": {{ $json.outage_count || 1 }}}'::jsonb,
    NOW(), NOW()
) ON CONFLICT (deal_id) DO UPDATE SET 
    last_interaction_at = NOW(),
    collected_data_json = '{"store_name": "{{ $json.store_name }}", "category_theme": "{{ $json.category_theme }}", "is_store_outage": {{ $json.is_store_outage ? 'true' : 'false' }}, "outage_count": {{ $json.outage_count || 1 }}}'::jsonb
WHERE ticket_bot_sessions.internal_chat_id IS NULL AND ticket_bot_sessions.status != 'COMPLETED'
RETURNING id, deal_id, requester_user_id, requester_name, '{{ $json.title }}' AS deal_title, 
          {{ $json.is_purchase ? 'TRUE' : 'FALSE' }} AS is_purchase,
          {{ $json.is_store_outage ? 'TRUE' : 'FALSE' }} AS is_store_outage,
          '{{ $json.store_name }}' AS store_name,
          '{{ $json.category_theme }}' AS category_theme,
          {{ $json.outage_count || 1 }} AS outage_count;"""

# Update 03_Create_CRM_Card_Chat greeting to reflect Outage Alert
chat_add_node = next(n for n in nodes if n['name'] == '03_Create_CRM_Card_Chat')
chat_add_node['parameters']['jsonBody'] = """={{ (() => {
  const firstName = ($json.requester_name || 'amigo').trim().split(' ')[0];
  const title = String($json.deal_title || '').trim();
  const hasCustomTitle = title && !title.startsWith('Chamado #') && !title.startsWith('#');
  const isOutage = Boolean($json.is_store_outage);
  const storeName = $json.store_name || 'sua filial';
  const theme = $json.category_theme === 'CONNECTIVITY_NETWORK' ? 'conexão / internet' : ($json.category_theme || 'sistema');

  let greeting = '';
  if (isOutage) {
    greeting = 'Oi, ' + firstName + '! Tudo bem? Sou da equipe virtual de TI aqui da Mundial.\\n\\n🚨 **ALERTA DE FILIAL:** Identifiquei que outros colegas da filial **' + storeName + '** relataram esse mesmo problema de ' + theme + ' nos últimos minutos.\\n\\nA TI já abriu um incidente de **Prioridade Máxima (P1)** para restabelecer a loja toda! Você não precisa se preocupar em abrir novos chamados, nossa equipe técnica já está atuando para todos.';
  } else if (hasCustomTitle) {
    greeting = 'Oi, ' + firstName + '! Tudo bem? Sou da equipe virtual de TI aqui da Mundial.\\n\\nVi que você abriu este chamado sobre: \"' + title + '\".\\n\\nMe conta com calma o que está acontecendo por aí? Se quiser mandar uma foto da tela ou do equipamento, fica à vontade! Vamos tentar resolver juntos.';
  } else {
    greeting = 'Oi, ' + firstName + '! Tudo bem? Sou da equipe virtual de TI aqui da Mundial.\\n\\nMe conta com calma o que está acontecendo com o seu computador ou sistema? Pode mandar uma foto da tela ou do equipamento se preferir, e vamos tentar resolver juntos!';
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

# ----------------------------------------------------
# 3. Update 05_Filter_And_Classify_Messages for Vision (Feature 1)
# ----------------------------------------------------
filter_node = next(n for n in nodes if n['name'] == '05_Filter_And_Classify_Messages')
filter_code = """// Classificação e filtragem multi-item com suporte a Anti-Carona e Imagens (Sprint 2 Vision)
const sessions = $('04_Get_Active_Sessions_Postgres').all();
const items = $input.all();
const outputItems = [];

for (let i = 0; i < items.length; i++) {
  const session = sessions[i]?.json || {};
  const res = items[i].json.result || {};
  const messages = res.messages || [];
  const files = res.files || [];

  const lastProcessedId = Number(session.last_processed_message_id || 0);
  const requesterId = Number(session.requester_user_id);
  const BOT_ID = 61622;
  const isCompleted = session.status === 'COMPLETED';

  // Ordena cronologicamente crescente
  messages.sort((a, b) => Number(a.id) - Number(b.id));

  const newMessages = [];
  let humanTakeoverDetected = false;
  let lastMsgId = lastProcessedId;
  let attachedImage = null;

  for (const msg of messages) {
    const msgId = Number(msg.id);
    if (msgId <= lastProcessedId) continue;
    lastMsgId = Math.max(lastMsgId, msgId);

    const authorId = Number(msg.author_id);
    // Ignora mensagens do bot (61622) ou de sistema (0)
    if (authorId === BOT_ID || authorId === 0) continue;

    // Se autor não for o solicitante nem o bot
    if (authorId !== requesterId) {
      if (!isCompleted) {
        humanTakeoverDetected = true;
        break;
      }
      continue;
    }

    // Mensagem válida do solicitante
    const cleanText = String(msg.text || '').trim();
    if (cleanText) {
      newMessages.push(cleanText);
    }

    // Checagem de anexo de imagem na mensagem
    const fileIds = Array.isArray(msg.params?.FILE_ID) ? msg.params.FILE_ID : [];
    if (fileIds.length > 0 && Array.isArray(files)) {
      for (const fid of fileIds) {
        const found = files.find(f => Number(f.id) === Number(fid) && f.type === 'image');
        if (found) {
          attachedImage = {
            file_id: Number(found.id),
            name: found.name || 'print_anexo.png',
            extension: found.extension || 'png'
          };
          break;
        }
      }
    }
  }

  if (humanTakeoverDetected) {
    outputItems.push({
      json: {
        deal_id: session.deal_id,
        dialog_id: session.dialog_id,
        human_takeover: true,
        last_msg_id: lastMsgId
      }
    });
    continue;
  }

  // Se AI está pausada manualmente em ticket ativo, ignora
  if (!isCompleted && session.ai_state === 'AI_PAUSED') {
    continue;
  }

  // Se há imagem ou mensagens novas
  if (newMessages.length > 0 || attachedImage) {
    outputItems.push({
      json: {
        deal_id: session.deal_id,
        chat_id: session.internal_chat_id,
        dialog_id: session.dialog_id,
        requester_user_id: requesterId,
        requester_name: session.requester_name || 'colaborador',
        message_id: lastMsgId,
        message_text: newMessages.join('\\n'),
        redis_memory_key: `bitrix:ti:deal:${session.deal_id}:memory`,
        ai_state: session.ai_state,
        session_status: session.status || 'ACTIVE',
        session_state: session.state || 'INIT',
        collected_data_json: session.collected_data_json || {},
        has_image: Boolean(attachedImage),
        image_file_id: attachedImage ? attachedImage.file_id : null,
        image_name: attachedImage ? attachedImage.name : null,
        image_extension: attachedImage ? attachedImage.extension : null
      }
    });
  }
}

return outputItems;
"""
filter_node['parameters']['functionCode'] = filter_code

# ----------------------------------------------------
# 4. Add Vision Multimodal Sub-Flow Nodes (Feature 1)
# ----------------------------------------------------
if_has_image_node = {
    "id": "node_if_has_image",
    "name": "06_If_Has_Image_To_Process",
    "type": "n8n-nodes-base.if",
    "typeVersion": 1,
    "position": [620, 528],
    "parameters": {
        "conditions": {
            "boolean": [
                {
                    "value1": "={{ $json.has_image }}",
                    "value2": True
                }
            ]
        }
    }
}

vision_get_url_node = {
    "id": "node_vision_get_url",
    "name": "Vision_01_Get_Download_Url",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [760, 420],
    "parameters": {
        "method": "GET",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.v2.File.download",
        "sendQuery": True,
        "queryParameters": {
            "parameters": [
                {"name": "dialogId", "value": "={{ $json.dialog_id }}"},
                {"name": "fileId", "value": "={{ $json.image_file_id }}"}
            ]
        },
        "options": {}
    },
    "onError": "continueRegularOutput"
}

vision_download_image_node = {
    "id": "node_vision_download_image",
    "name": "Vision_02_Download_Image",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [900, 420],
    "parameters": {
        "method": "GET",
        "url": "={{ $json.result?.downloadUrl || '' }}",
        "options": {
            "response": {
                "response": {
                    "responseFormat": "file"
                }
            }
        }
    },
    "onError": "continueRegularOutput"
}

vision_prep_payload_node = {
    "id": "node_vision_prep_payload",
    "name": "Vision_03_Prepare_Vision_Payload",
    "type": "n8n-nodes-base.function",
    "typeVersion": 1,
    "position": [1040, 420],
    "parameters": {
        "functionCode": """// Prepara payload multimodal para o OpenAI Vision
const items = $input.all();
const sessionItems = $('06_If_Has_Image_To_Process').all();

return items.map((item, idx) => {
  const session = sessionItems[idx]?.json || {};
  const binaryData = item.binary?.data;
  
  if (!binaryData || !binaryData.data) {
    // Se download falhou, repassa sem imagem
    return {
      json: {
        ...session,
        vision_failed: true
      }
    };
  }

  const mimeType = binaryData.mimeType || 'image/png';
  const base64Str = binaryData.data;

  return {
    json: {
      ...session,
      openai_payload: {
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: "Você é um especialista em OCR e triagem visual de erros para Help Desk de TI da Rede Mundial Honda.\\nAnalise a imagem/print de erro anexado pelo colaborador.\\nExtraia com precisão:\\n1. Sistema/Aplicação (MicroWork Cloud, Portais Honda, RENAVE/Detran, WebPeças, Windows, Outlook, Navegador, Impressora).\\n2. Código do erro ou texto exato do alerta/caixa de diálogo (ex: 'Erro 104', 'Falha de comunicação', etc).\\n3. Chassi (17 dígitos), Chave de NFe (44 dígitos), OS ou Pedido se visíveis.\\n4. Breve diagnóstico em 1 linha.\\n\\nFormate rigorosamente assim:\\n[ANÁLISE DE PRINT ANEXADO]\\n- Sistema: <sistema>\\n- Mensagem/Erro na Tela: <mensagem>\\n- Dados Identificados: <dados>\\n- Diagnóstico Visual: <diagnostico>"
          },
          {
            role: "user",
            content: [
              { type: "text", text: "Analise o print anexado pelo colaborador no chat do chamado de TI:" },
              {
                type: "image_url",
                image_url: {
                  url: `data:${mimeType};base64,${base64Str}`
                }
              }
            ]
          }
        ],
        max_tokens: 300
      }
    }
  };
});"""
    }
}

vision_call_openai_node = {
    "id": "node_vision_call_openai",
    "name": "Vision_04_Call_OpenAI_Vision",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1180, 420],
    "parameters": {
        "method": "POST",
        "url": "https://api.openai.com/v1/chat/completions",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "openAiApi",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.openai_payload) }}",
        "options": {}
    },
    "credentials": {
        "openAiApi": {
            "id": "zJ462uvngfWgM0PB",
            "name": "OpenAi account 3"
        }
    },
    "onError": "continueRegularOutput"
}

vision_merge_context_node = {
    "id": "node_vision_merge_context",
    "name": "Vision_05_Merge_Vision_Context",
    "type": "n8n-nodes-base.function",
    "typeVersion": 1,
    "position": [1320, 420],
    "parameters": {
        "functionCode": """// Mescla a análise de visão computacional no contexto textual do usuário
const items = $input.all();
const sessionItems = $('Vision_03_Prepare_Vision_Payload').all();

return items.map((item, idx) => {
  const session = sessionItems[idx]?.json || {};
  const visionContent = item.json.choices?.[0]?.message?.content || '';

  let enrichedMessage = String(session.message_text || '').trim();
  if (visionContent) {
    enrichedMessage = (enrichedMessage ? enrichedMessage + '\\n\\n' : '') + visionContent;
  }

  return {
    json: {
      deal_id: session.deal_id,
      chat_id: session.chat_id,
      dialog_id: session.dialog_id,
      requester_user_id: session.requester_user_id,
      requester_name: session.requester_name,
      message_id: session.message_id,
      message_text: enrichedMessage,
      redis_memory_key: session.redis_memory_key,
      ai_state: session.ai_state,
      session_status: session.session_status,
      session_state: session.session_state,
      collected_data_json: session.collected_data_json
    }
  };
});"""
    }
}

# ----------------------------------------------------
# 5. Update 11_B01_Priority_And_Payload for Outage & Vision Context
# ----------------------------------------------------
b01_node = next(n for n in nodes if n['name'] == '11_B01_Priority_And_Payload')
b01_code = """// MOTOR DETERMINÍSTICO B01 DE PRIORIDADE & SUPORTE A AUTOATENDIMENTO L1
// Sprint 1: Detecção de Frustração e Cliente em Loja
// Sprint 2: Queda Geral por Loja (Incident Clustering P1)
const items = $input.all();
const results = [];

const IMPACT_MAP = {
  'ENTIRE_COMPANY': { id: 1180, label: 'Empresa Inteira (Todas as Lojas)' },
  'ENTIRE_STORE': { id: 1182, label: 'Loja Inteira' },
  'ENTIRE_DEPARTMENT': { id: 1184, label: 'Departamento Inteiro' },
  'MULTIPLE_USERS': { id: 1186, label: 'Múltiplos Usuários' },
  'SINGLE_USER': { id: 1188, label: 'Usuário Individual' },
  'NO_IMPACT': { id: 1190, label: 'Sem Impacto Operacional' }
};

const URGENCY_MAP = {
  'OPERATION_HALTED': { id: 1192, label: 'Operação Parada (Crítico)' },
  'SEVERELY_DEGRADED': { id: 1194, label: 'Severamente Degradada' },
  'WORKAROUND_AVAILABLE': { id: 1196, label: 'Contorno Disponível' },
  'PLANNED_REQUEST': { id: 1198, label: 'Solicitação Planejada' },
  'INQUIRY': { id: 1200, label: 'Dúvida / Informação' }
};

for (const item of items) {
  const data = item.json.structured_data || {};
  const facts = data.facts || {};
  const isResolvedL1 = Boolean(item.json.is_resolved_l1 || data.resolvido_l1 || data.action === 'RESOLVED_L1');

  // Recupera dados de sessão do Postgres (clustering de queda de loja)
  const sessionData = item.json.collected_data_json || {};
  const isStoreOutage = Boolean(sessionData.is_store_outage || data.is_store_outage);
  const storeName = sessionData.store_name || data.store_name || '';
  const outageCount = Number(sessionData.outage_count || data.outage_count || 1);

  // Detecção de Contexto Crítico / Cliente em Loja
  const contextoCritico = data.contexto_critico || {};
  const isClienteEmLoja = Boolean(contextoCritico.cliente_em_loja);
  const isFrustracaoAlta = Boolean(contextoCritico.frustracao_alta);
  const motivoCritico = String(contextoCritico.motivo || '').trim();

  let rawImpact = (facts.impacto?.value || data.impacto || 'SINGLE_USER').toUpperCase();
  let rawUrgency = (facts.urgencia?.value || data.urgencia || 'NORMAL').toUpperCase();

  // Força Urgência OPERATION_HALTED se tiver cliente em loja ou queda de loja
  if (isStoreOutage) {
    rawImpact = 'ENTIRE_STORE';
    rawUrgency = 'OPERATION_HALTED';
  } else if (isClienteEmLoja) {
    rawUrgency = 'OPERATION_HALTED';
  }

  const impactObj = IMPACT_MAP[rawImpact] || IMPACT_MAP['SINGLE_USER'];
  const urgencyObj = URGENCY_MAP[rawUrgency] || URGENCY_MAP['PLANNED_REQUEST'];

  let priorityId = 1206; // P3_MEDIUM Default
  let priorityCode = 'P3_MEDIUM';
  let priorityLabel = 'P3 - Médio';

  if (isStoreOutage) {
    priorityId = 1202;
    priorityCode = 'P1_CRITICAL';
    priorityLabel = 'P1 - Crítico (Queda Geral de Loja)';
  } else if (isResolvedL1) {
    priorityId = 1208;
    priorityCode = 'P4_LOW';
    priorityLabel = 'P4 - Resolvido L1';
  } else if (rawImpact === 'ENTIRE_COMPANY') {
    if (rawUrgency === 'OPERATION_HALTED' || rawUrgency === 'SEVERELY_DEGRADED') {
      priorityId = 1202; priorityCode = 'P1_CRITICAL'; priorityLabel = 'P1 - Crítico';
    } else if (rawUrgency === 'WORKAROUND_AVAILABLE') {
      priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto';
    } else if (rawUrgency === 'PLANNED_REQUEST') {
      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';
    } else {
      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';
    }
  } else if (rawImpact === 'ENTIRE_STORE') {
    if (rawUrgency === 'OPERATION_HALTED') {
      priorityId = 1202; priorityCode = 'P1_CRITICAL'; priorityLabel = 'P1 - Crítico';
    } else if (rawUrgency === 'SEVERELY_DEGRADED' || rawUrgency === 'WORKAROUND_AVAILABLE') {
      priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto';
    } else if (rawUrgency === 'PLANNED_REQUEST') {
      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';
    } else {
      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';
    }
  } else if (rawImpact === 'ENTIRE_DEPARTMENT') {
    if (rawUrgency === 'OPERATION_HALTED' || rawUrgency === 'SEVERELY_DEGRADED') {
      priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto';
    } else if (rawUrgency === 'WORKAROUND_AVAILABLE' || rawUrgency === 'PLANNED_REQUEST') {
      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';
    } else {
      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';
    }
  } else if (rawImpact === 'MULTIPLE_USERS') {
    if (rawUrgency === 'OPERATION_HALTED') {
      priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto';
    } else if (rawUrgency === 'SEVERELY_DEGRADED' || rawUrgency === 'WORKAROUND_AVAILABLE') {
      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';
    } else {
      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';
    }
  } else if (rawImpact === 'SINGLE_USER') {
    if (rawUrgency === 'OPERATION_HALTED' || rawUrgency === 'SEVERELY_DEGRADED') {
      if (isClienteEmLoja) {
        priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto (Cliente em Loja)';
      } else {
        priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';
      }
    } else {
      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';
    }
  } else {
    priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';
  }

  const shortSubject = data.assunto_curto || 'Atendimento de TI';
  const tema = data.tema || 'GERAL';
  const resumo = data.resumo_problema || 'Triagem realizada pelo assistente de IA.';
  const lowerContext = (tema + ' ' + shortSubject + ' ' + resumo).toLowerCase();
  const isPurchaseSemantic = (
    tema === 'COMPRA' ||
    lowerContext.includes('compra') ||
    lowerContext.includes('comprar') ||
    lowerContext.includes('memoria ram') ||
    lowerContext.includes('memória ram') ||
    lowerContext.includes('hardware') ||
    lowerContext.includes('aquisição') ||
    lowerContext.includes('aquisicao')
  );
  const isPurchase = Boolean(item.json.is_purchase || isPurchaseSemantic);

  // Formatação do Título com Selo Crítico
  let prefixoCritico = '';
  if (isStoreOutage) {
    prefixoCritico = `[🚨 QUEDA GERAL ${storeName.toUpperCase()}] `;
  } else if (isClienteEmLoja) {
    prefixoCritico = '[🚨 CLIENTE EM LOJA] ';
  } else if (isFrustracaoAlta) {
    prefixoCritico = '[⚠️ PRIORITÁRIO] ';
  }

  const formattedTitle = isResolvedL1 
    ? `[RESOLVIDO-L1] - ${shortSubject} (Eduardo Alaminos)` 
    : `${prefixoCritico}[TI-${tema}] - ${shortSubject} (Eduardo Alaminos)`;
  const targetStageId = isResolvedL1 ? 'C160:WON' : (isPurchase ? 'C160:UC_JIOBG8' : 'C160:NEW');

  results.push({
    json: {
      deal_id: item.json.deal_id,
      chat_id: item.json.chat_id,
      dialog_id: item.json.dialog_id,
      message_id: item.json.message_id,
      impact_id: impactObj.id,
      impact_label: impactObj.label,
      urgency_id: urgencyObj.id,
      urgency_label: urgencyObj.label,
      priority_id: priorityId,
      priority_code: priorityCode,
      priority_label: priorityLabel,
      target_stage_id: targetStageId,
      is_resolved_l1: isResolvedL1,
      is_purchase: isPurchase,
      is_store_outage: isStoreOutage,
      store_name: storeName,
      outage_count: outageCount,
      is_cliente_em_loja: isClienteEmLoja,
      is_frustracao_alta: isFrustracaoAlta,
      motivo_critico: motivoCritico,
      tema: tema,
      short_subject: shortSubject,
      formatted_title: formattedTitle,
      resumo: resumo,
      next_owner_id: 1148,
      wait_reason_id: 1162
    }
  });
}

return results;
"""
b01_node['parameters']['functionCode'] = b01_code

# ----------------------------------------------------
# 6. Update 14_Add_Timeline_Milestone_Comment
# ----------------------------------------------------
timeline_comment_node = next(n for n in nodes if n['name'] == '14_Add_Timeline_Milestone_Comment')
timeline_comment_node['parameters']['jsonBody'] = """={{ JSON.stringify({
  fields: {
    ENTITY_ID: $json.deal_id,
    ENTITY_TYPE: 'deal',
    COMMENT: ($json.is_store_outage ? ('🚨 **INCIDENTE CRÍTICO P1: POSSÍVEL QUEDA GERAL NA FILIAL (' + ($json.store_name || 'Loja') + ')!**\\n⚠️ **Cluster Detectado:** ' + ($json.outage_count || '2') + ' chamados abertos nos últimos 30 min sobre ' + ($json.tema || 'Conectividade/Sistema') + '.\\n⚡ *Prioridade elevada automaticamente pelo robô para P1 - Crítico (Loja Inteira).*\\n---------------------------------------------\\n') : '') + ($json.is_cliente_em_loja ? ('🚨 **ALERTA COMERCIAL: CLIENTE AGUARDANDO EM LOJA!**\\n⚠️ **Motivo:** ' + ($json.motivo_critico || 'Cliente em atendimento presencial/retirada') + '\\n⚡ *Prioridade elevada automaticamente pela IA para P2/P1 para agilizar o atendimento.*\\n---------------------------------------------\\n') : ($json.is_frustracao_alta ? ('⚠️ **ALERTA DE REINCIDÊNCIA / FRUSTRAÇÃO CRÍTICA DO COLABORADOR**\\nMotivo: ' + ($json.motivo_critico || 'Múltiplas falhas relatadas ou tempo excessivo de paralisação') + '\\n---------------------------------------------\\n') : '')) + ($json.is_resolved_l1 ? ('🎉 **Chamado Solucionado com Sucesso via Autoatendimento (L1)!**\\n---------------------------------------------\\n📌 **Tema:** ' + $json.tema + '\\n🚨 **Prioridade:** ' + $json.priority_label + '\\n\\n📝 **Resumo:**\\n' + $json.resumo + '\\n\\n✅ *O colaborador confirmou que o problema foi solucionado com os testes rápidos orientados pelo assistente. Chamado concluído como Ganho automaticamente.*') : ('🤖 **Triagem IA Concluída com Sucesso!**\\n---------------------------------------------\\n📌 **Tema:** ' + $json.tema + '\\n👥 **Impacto:** ' + $json.impact_label + '\\n⏱️ **Urgência:** ' + $json.urgency_label + '\\n🚨 **Prioridade B01:** ' + $json.priority_label + ' (' + $json.priority_code + ')\\n\\n📝 **Resumo:**\\n' + $json.resumo + '\\n\\n💬 *Histórico detalhado da conversa mantido no Chat do Card.*'))
  }
}) }}"""

# ----------------------------------------------------
# 7. Add New Nodes to Workflow and Rewire Connections
# ----------------------------------------------------
# Add nodes
new_nodes = [
    outage_check_node,
    outage_eval_node,
    if_has_image_node,
    vision_get_url_node,
    vision_download_image_node,
    vision_prep_payload_node,
    vision_call_openai_node,
    vision_merge_context_node
]

# Ensure no duplicate names
existing_names = {n['name'] for n in nodes}
for nn in new_nodes:
    if nn['name'] not in existing_names:
        nodes.append(nn)

# Rewire connections:
# Flow 1 (Outage Check):
# 01_If_Is_Duplicate [FALSE / branch 1] -> 01_Check_Store_Outage_Cluster -> 01_Evaluate_Store_Outage -> 02_Reserve_Deal_Session_Atomic
connections['01_If_Is_Duplicate']['main'][1] = [{'node': '01_Check_Store_Outage_Cluster', 'type': 'main', 'index': 0}]
connections['01_Check_Store_Outage_Cluster'] = {'main': [[{'node': '01_Evaluate_Store_Outage', 'type': 'main', 'index': 0}]]}
connections['01_Evaluate_Store_Outage'] = {'main': [[{'node': '02_Reserve_Deal_Session_Atomic', 'type': 'main', 'index': 0}]]}

# Flow 2 (Vision):
# 06_Route_Session_Status [FALSE / branch 1 (ACTIVE)] -> 06_If_Has_Image_To_Process
connections['06_Route_Session_Status']['main'][1] = [{'node': '06_If_Has_Image_To_Process', 'type': 'main', 'index': 0}]

# 06_If_Has_Image_To_Process:
# Branch 0 (TRUE): Vision_01_Get_Download_Url -> Vision_02_Download_Image -> Vision_03_Prepare_Vision_Payload -> Vision_04_Call_OpenAI_Vision -> Vision_05_Merge_Vision_Context -> 07_Prepare_AI_Deal_Input
# Branch 1 (FALSE): 07_Prepare_AI_Deal_Input
connections['06_If_Has_Image_To_Process'] = {
    'main': [
        [{'node': 'Vision_01_Get_Download_Url', 'type': 'main', 'index': 0}],
        [{'node': '07_Prepare_AI_Deal_Input', 'type': 'main', 'index': 0}]
    ]
}
connections['Vision_01_Get_Download_Url'] = {'main': [[{'node': 'Vision_02_Download_Image', 'type': 'main', 'index': 0}]]}
connections['Vision_02_Download_Image'] = {'main': [[{'node': 'Vision_03_Prepare_Vision_Payload', 'type': 'main', 'index': 0}]]}
connections['Vision_03_Prepare_Vision_Payload'] = {'main': [[{'node': 'Vision_04_Call_OpenAI_Vision', 'type': 'main', 'index': 0}]]}
connections['Vision_04_Call_OpenAI_Vision'] = {'main': [[{'node': 'Vision_05_Merge_Vision_Context', 'type': 'main', 'index': 0}]]}
connections['Vision_05_Merge_Vision_Context'] = {'main': [[{'node': '07_Prepare_AI_Deal_Input', 'type': 'main', 'index': 0}]]}

# Save updated workflow file
wf['nodes'] = nodes
wf['connections'] = connections

with open(wf_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print(f"Workflow updated successfully! Total nodes: {len(nodes)}")
