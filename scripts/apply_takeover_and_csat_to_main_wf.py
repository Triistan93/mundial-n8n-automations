# -*- coding: utf-8 -*-
"""
Aplica no Workflow Principal BITRIX_TI_AI_TRIAGE_AGENT (c0F2GUMFm2BI94UG):
1. Botões Nativos 'Aceitar Chamado' e 'Colocar na Fila' no fim da triagem e alertas da TI.
2. Correção do bug de intromissão em 05_Filter_And_Classify_Messages (silêncio total após intervenção humana).
3. Trava de HUMAN_TAKEOVER no Postgres.
4. Ramo automático de CSAT quando o card for encerrado (C160:WON).
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

print("1. Obtendo workflow atual do n8n...")
wf = requests.get(N8N_URL, headers=headers).json()

# ------------------------------------------------------------------------------
# 1. 04_Get_Active_Sessions_Postgres: Inclui HUMAN_TAKEOVER e IN_QUEUE
# ------------------------------------------------------------------------------
new_sql_active_sessions = """-- SELF-HEALING GENERICO POR ESTADO:
UPDATE ticket_bot_sessions 
SET status = 'ACTIVE' 
WHERE status = 'CHAT_CREATING' AND internal_chat_id IS NOT NULL;

-- Recupera sessoes ativas, takeover, fila e concluidas recentes (ultimas 48h)
SELECT id, deal_id, requester_user_id, requester_name, internal_chat_id, dialog_id, last_processed_message_id, ai_state, redis_memory_key, status, state, collected_data_json 
FROM ticket_bot_sessions 
WHERE (
    (status IN ('ACTIVE', 'HUMAN_TAKEOVER', 'IN_QUEUE') AND last_interaction_at > NOW() - INTERVAL '48 hours') 
    OR 
    (status = 'COMPLETED' AND last_interaction_at > NOW() - INTERVAL '24 hours')
  ) 
  AND internal_chat_id IS NOT NULL;"""

# ------------------------------------------------------------------------------
# 2. 05_Filter_And_Classify_Messages: Trava Rígida de Human Takeover e Silêncio
# ------------------------------------------------------------------------------
new_filter_code = """// Classificação e filtragem multi-item com suporte a Anti-Carona, Imagens, Human Takeover Rigoroso e Silêncio
const sessions = $('04_Get_Active_Sessions_Postgres').all();
const items = $input.all();
const outputItems = [];

for (let i = 0; i < items.length; i++) {
  const session = sessions[i]?.json || {};
  const res = items[i].json.result || {};
  const messages = res.messages || [];
  const rawFiles = res.files || [];
  const filesList = Array.isArray(rawFiles) ? rawFiles : Object.values(rawFiles || {});

  const lastProcessedId = Number(session.last_processed_message_id || 0);
  const requesterId = Number(session.requester_user_id);
  const BOT_ID = 61622;
  const isCompleted = session.status === 'COMPLETED';
  const isTakeover = session.status === 'HUMAN_TAKEOVER' || session.status === 'IN_QUEUE' || session.ai_state === 'AI_PAUSED';

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

    // Se o autor for QUALQUER pessoa que não seja o solicitante (ex: Igor, Eduardo, outro analista de TI):
    // REGRA DE OURO: Sempre dispara Human Takeover! NUNCA ignora, mesmo se a sessão era COMPLETED!
    if (authorId !== requesterId) {
      humanTakeoverDetected = true;
      break;
    }

    // Mensagem válida do solicitante
    const cleanText = String(msg.text || '').trim();
    if (cleanText) {
      newMessages.push(cleanText);
    }

    // Checagem de anexo de imagem na mensagem
    let fileIds = [];
    if (Array.isArray(msg.params?.FILE_ID)) {
      fileIds = msg.params.FILE_ID;
    } else if (msg.params?.FILE_ID) {
      fileIds = [msg.params.FILE_ID];
    }

    if (fileIds.length > 0 && filesList.length > 0) {
      for (const fid of fileIds) {
        const found = filesList.find(f => 
          Number(f.id) === Number(fid) && 
          (f.type === 'image' || ['png', 'jpg', 'jpeg', 'webp', 'bmp'].includes(String(f.extension || '').toLowerCase()))
        );
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

  // Se detectou intervenção humana de um técnico na conversa
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

  // SILÊNCIO TOTAL: Se o chamado já está sob controle humano (HUMAN_TAKEOVER ou AI_PAUSED),
  // a Sophia NUNCA se intromete, mesmo que o solicitante mande novas mensagens!
  if (isTakeover) {
    continue;
  }

  // Se há imagem ou mensagens novas
  if (newMessages.length > 0 || attachedImage) {
    const fallbackText = attachedImage ? 'O colaborador enviou um print/imagem de erro em anexo.' : '';
    outputItems.push({
      json: {
        deal_id: session.deal_id,
        chat_id: session.internal_chat_id,
        dialog_id: session.dialog_id,
        requester_user_id: requesterId,
        requester_name: session.requester_name || 'Colaborador',
        message_id: lastMsgId,
        message_text: newMessages.join('\\n') || fallbackText,
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

return outputItems;"""

# ------------------------------------------------------------------------------
# 3. 05_Pause_AI_On_Human_Takeover: Marca HUMAN_TAKEOVER no Postgres
# ------------------------------------------------------------------------------
new_pause_sql = "UPDATE ticket_bot_sessions SET status = 'HUMAN_TAKEOVER', ai_state = 'AI_PAUSED', last_processed_message_id = '{{ $json.last_msg_id }}', last_interaction_at = NOW() WHERE deal_id = {{ $json.deal_id }};"

# ------------------------------------------------------------------------------
# 4. 15_Prepare_Final_Chat: Adiciona Botões 'Aceitar Chamado' e 'Colocar na Fila'
# ------------------------------------------------------------------------------
new_prepare_final_chat = """// Prepara payload para envio no chat final com botões interativos de Aceite / Fila
const b01Items = $('11_B01_Priority_And_Payload').all();
const updatePayloadItems = $('12_Prepare_Deal_Update_Payload').all();
const items = $input.all();

return items.map((item, idx) => {
  const b01 = b01Items[idx]?.json || item.json;
  const updateData = updatePayloadItems[idx]?.json || {};
  const isPurchase = Boolean(updateData.is_purchase || b01.is_purchase || updateData.target_stage_id === 'C160:UC_JIOBG8');
  const isClienteEmLoja = Boolean(b01.is_cliente_em_loja);
  const isResolvedL1 = Boolean(b01.is_resolved_l1);
  const dealId = b01.deal_id;
  const firstName = (b01.formatted_title || '').includes('(')
    ? (b01.formatted_title.split('(')[1].split(')')[0].split(' ')[0] || 'amigo')
    : 'amigo';

  let finalMessage = '';
  let keyboard = [];

  const defaultButtons = [
    {
      "TEXT": "🙋‍♂️ Aceitar Chamado",
      "LINK": `https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-ticket-action?deal_id=${dealId}&action=accept`,
      "BG_COLOR": "#29b24f",
      "TEXT_COLOR": "#ffffff",
      "DISPLAY": "LINE"
    },
    {
      "TEXT": "⏳ Colocar na Fila",
      "LINK": `https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-ticket-action?deal_id=${dealId}&action=queue`,
      "BG_COLOR": "#f59e0b",
      "TEXT_COLOR": "#ffffff",
      "DISPLAY": "LINE"
    }
  ];

  if (isPurchase) {
    finalMessage = `Prontinho, ${firstName}! Encaminhei a sua solicitação de compra para a aprovação da liderança e diretoria. Assim que tivermos o retorno, a equipe de TI dará o andamento imediato na compra e configuração para você!`;
  } else if (isResolvedL1) {
    finalMessage = `Fico muito feliz que conseguimos resolver o seu chamado #${dealId} por aqui, ${firstName}! 🎉\\n\\n⭐ **Pesquisa Rápida:** Como você avalia o suporte recebido hoje?\\nResponda com uma nota de 1 a 5:\\n⭐ 1 (Péssimo) | ⭐⭐ 2 (Ruim) | ⭐⭐⭐ 3 (Regular) | ⭐⭐⭐⭐ 4 (Bom) | ⭐⭐⭐⭐⭐ 5 (Excelente)`;
  } else if (isClienteEmLoja) {
    finalMessage = `Pode deixar, ${firstName}! Como você está com cliente aguardando na loja, já sinalizei o seu chamado #${dealId} com prioridade comercial máxima (🚨 CLIENTE EM LOJA) para a equipe técnica agilizar o seu atendimento imediatamente!`;
    keyboard = defaultButtons;
  } else {
    finalMessage = `Perfeito, ${firstName}! Todas as informações do chamado #${dealId} já foram organizadas e direcionadas para a fila da equipe de TI. O técnico responsável já vai assumir o seu atendimento!`;
    keyboard = defaultButtons;
  }

  return {
    json: {
      deal_id: dealId,
      dialog_id: b01.dialog_id,
      final_message: finalMessage,
      keyboard: keyboard
    }
  };
});"""

# ------------------------------------------------------------------------------
# 5. 15_Filter_Tickets_Ready_For_IT: Adiciona Botões por Destinatário (Eduardo / Igor)
# ------------------------------------------------------------------------------
new_filter_tickets_it = """// Filtra chamados que concluíram triagem e estão prontos para atendimento humano pela TI
const b01Items = $('11_B01_Priority_And_Payload').all();
const updatePayloadItems = $('12_Prepare_Deal_Update_Payload').all();
const notifications = [];

// Técnicos que recebem o alerta de fila da TI:
// 32598: Eduardo Alaminos (Gestor TI)
// 352678: Igor Bonini (Suporte TI)
const IT_TEAM_RECIPIENTS = [32598, 352678];

for (let i = 0; i < b01Items.length; i++) {
  const b01 = b01Items[i]?.json || {};
  const updateData = updatePayloadItems[i]?.json || {};

  const isPurchase = Boolean(updateData.is_purchase || b01.is_purchase || updateData.target_stage_id === 'C160:UC_JIOBG8');
  const isResolvedL1 = Boolean(b01.is_resolved_l1);

  // Notifica a equipe quando o chamado NÃO foi resolvido por L1 e NÃO é compra pendente de diretoria
  if (!isResolvedL1 && !isPurchase) {
    const dealId = b01.deal_id;
    const formattedTitle = b01.formatted_title || `Chamado #${dealId}`;
    const requesterName = b01.requester_name || 'Colaborador';
    const storeName = b01.store_name || 'Geral';
    const priorityLabel = b01.priority_label || 'Média';
    const shortSubject = b01.short_subject || b01.resumo || 'Sem resumo disponível';
    const isClienteEmLoja = Boolean(b01.is_cliente_em_loja);
    const dealUrl = `https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${dealId}/`;

    let alertHeader = '🔔 [b]CHAMADO TRIADO PELA IA - PRONTO PARA ATENDIMENTO[/b]';
    if (isClienteEmLoja) {
      alertHeader = '🚨 [b]URGENTE: CLIENTE EM LOJA - CHAMADO PRONTO PARA ATENDIMENTO[/b]';
    }

    const msgText = `${alertHeader}\\n` +
      `🎫 [b]Chamado #${dealId}:[/b] ${formattedTitle}\\n` +
      `👤 [b]Solicitante:[/b] ${requesterName}\\n` +
      `🏢 [b]Loja/Filial:[/b] ${storeName}\\n` +
      `⚡ [b]Prioridade:[/b] ${priorityLabel}\\n` +
      `📝 [b]Resumo:[/b] ${shortSubject}\\n` +
      (isClienteEmLoja ? `🚨 [b]Atenção:[/b] Colaborador com cliente presencial aguardando!\\n` : '') +
      `\\n👉 [URL=${dealUrl}]Abrir Chamado no Bitrix[/URL]`;

    for (const recipientId of IT_TEAM_RECIPIENTS) {
      const keyboard = [
        {
          "TEXT": "🙋‍♂️ Aceitar Chamado",
          "LINK": `https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-ticket-action?deal_id=${dealId}&action=accept&user_id=${recipientId}`,
          "BG_COLOR": "#29b24f",
          "TEXT_COLOR": "#ffffff",
          "DISPLAY": "LINE"
        },
        {
          "TEXT": "⏳ Colocar na Fila",
          "LINK": `https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-ticket-action?deal_id=${dealId}&action=queue&user_id=${recipientId}`,
          "BG_COLOR": "#f59e0b",
          "TEXT_COLOR": "#ffffff",
          "DISPLAY": "LINE"
        }
      ];

      notifications.push({
        json: {
          deal_id: dealId,
          recipient_id: String(recipientId),
          notification_message: msgText,
          keyboard: keyboard
        }
      });
    }
  }
}

return notifications;"""

print("2. Aplicando atualizações nos nós do workflow...")
for node in wf['nodes']:
    name = node['name']
    if name == '04_Get_Active_Sessions_Postgres':
        print(f"  Atualizando {name} -> Consulta com HUMAN_TAKEOVER e IN_QUEUE")
        node['parameters']['query'] = new_sql_active_sessions
    elif name == '05_Filter_And_Classify_Messages':
        print(f"  Atualizando {name} -> Trava de Silêncio e Human Takeover Passivo")
        node['parameters']['jsCode'] = new_filter_code
    elif name == '05_Pause_AI_On_Human_Takeover':
        print(f"  Atualizando {name} -> Grava HUMAN_TAKEOVER no banco")
        node['parameters']['query'] = new_pause_sql
    elif name == '15_Prepare_Final_Chat':
        print(f"  Atualizando {name} -> Botões 'Aceitar Chamado' e 'Colocar na Fila'")
        node['parameters']['jsCode'] = new_prepare_final_chat
    elif name == '15_Send_Final_Confirmation_To_Chat':
        print(f"  Atualizando {name} -> Envio de KEYBOARD no chat")
        node['parameters']['jsonBody'] = "={{ JSON.stringify({\n  DIALOG_ID: $json.dialog_id,\n  MESSAGE: $json.final_message,\n  KEYBOARD: ($json.keyboard && $json.keyboard.length > 0) ? $json.keyboard : undefined\n}) }}"
    elif name == '15_Filter_Tickets_Ready_For_IT':
        print(f"  Atualizando {name} -> Botões de Ação na notificação dos técnicos")
        node['parameters']['jsCode'] = new_filter_tickets_it
    elif name == '15_Notify_IT_Team_Ready':
        print(f"  Atualizando {name} -> Envio de KEYBOARD na notificação push")
        node['parameters']['jsonBody'] = "={{ JSON.stringify({\n  DIALOG_ID: $json.recipient_id,\n  MESSAGE: $json.notification_message,\n  KEYBOARD: ($json.keyboard && $json.keyboard.length > 0) ? $json.keyboard : undefined\n}) }}"

# ------------------------------------------------------------------------------
# 6. Branch de CSAT no Encerramento de Chamados (C160:WON)
# ------------------------------------------------------------------------------
# Verifica se os nós de CSAT no WON já existem
existing_node_names = [n['name'] for n in wf['nodes']]

if 'CSAT_Poll_Won_Deals' not in existing_node_names:
    print("  Adicionando ramo CSAT_Poll_Won_Deals para envio automático no encerramento...")
    csat_branch_nodes = [
        {
            "id": "node_csat_poll_won",
            "name": "CSAT_Poll_Won_Deals",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [368, 600],
            "onError": "continueRegularOutput",
            "parameters": {
                "method": "GET",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.list",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {"name": "filter[CATEGORY_ID]", "value": "160"},
                        {"name": "filter[STAGE_ID]", "value": "C160:WON"},
                        {"name": "order[DATE_MODIFY]", "value": "DESC"},
                        {"name": "select[]", "value": "ID"},
                        {"name": "select[]", "value": "TITLE"},
                        {"name": "select[]", "value": "ASSIGNED_BY_ID"},
                        {"name": "select[]", "value": "DATE_MODIFY"}
                    ]
                },
                "options": {}
            }
        },
        {
            "id": "node_csat_filter_unsent",
            "name": "CSAT_Filter_Unsent_Deals",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [600, 600],
            "parameters": {
                "jsCode": """
// Filtra chamados em C160:WON que ainda não receberam a pesquisa CSAT
const items = $input.all();
const deals = items[0]?.json?.result || items.map(i => i.json);
const output = [];

for (const deal of deals) {
  const dealId = Number(deal.ID);
  if (!dealId) continue;

  output.push({
    json: {
      deal_id: dealId,
      deal_title: deal.TITLE || `Chamado #${dealId}`,
      assigned_by_id: Number(deal.ASSIGNED_BY_ID || 0)
    }
  });
}

return output.slice(0, 5); // Limita a 5 por ciclo para não sobrecarregar
"""
            }
        },
        {
            "id": "node_csat_lookup_session",
            "name": "CSAT_Lookup_Session_Postgres",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [840, 600],
            "onError": "continueRegularOutput",
            "parameters": {
                "operation": "executeQuery",
                "query": "SELECT id, deal_id, requester_name, internal_chat_id, dialog_id, collected_data_json FROM ticket_bot_sessions WHERE deal_id = {{ $json.deal_id }} AND internal_chat_id IS NOT NULL AND (collected_data_json->>'csat_sent') IS NULL;",
                "additionalFields": {}
            },
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        },
        {
            "id": "node_csat_prepare_message",
            "name": "CSAT_Prepare_Survey_Payload",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1080, 600],
            "parameters": {
                "jsCode": """
const rows = $input.all();
const readyList = [];

for (const row of rows) {
  const session = row.json;
  const dealId = session.deal_id;
  if (!dealId || !session.dialog_id) continue;

  const requesterName = session.requester_name || 'Colaborador';
  const firstName = requesterName.split(' ')[0] || 'amigo';

  const surveyMessage = `🎉 Olá, ${firstName}! O seu chamado #${dealId} foi finalizado com sucesso pela equipe de TI.\\n\\n⭐ **Pesquisa de Satisfação:** Como você avalia o suporte recebido hoje?\\n👉 Clique em uma das opções abaixo para registrar sua nota em 1 clique:`;

  const keyboard = [
    {
      "TEXT": "⭐⭐⭐⭐⭐ Excelente",
      "LINK": `https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-csat-vote?deal_id=${dealId}&rating=5`,
      "BG_COLOR": "#10b981",
      "TEXT_COLOR": "#ffffff",
      "DISPLAY": "LINE"
    },
    {
      "TEXT": "⭐⭐⭐⭐ Bom",
      "LINK": `https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-csat-vote?deal_id=${dealId}&rating=4`,
      "BG_COLOR": "#3b82f6",
      "TEXT_COLOR": "#ffffff",
      "DISPLAY": "LINE"
    },
    {
      "TEXT": "⭐⭐⭐ Regular",
      "LINK": `https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-csat-vote?deal_id=${dealId}&rating=3`,
      "BG_COLOR": "#f59e0b",
      "TEXT_COLOR": "#ffffff",
      "DISPLAY": "LINE"
    },
    {
      "TEXT": "⭐ Precisa Melhorar",
      "LINK": `https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-csat-vote?deal_id=${dealId}&rating=1`,
      "BG_COLOR": "#ef4444",
      "TEXT_COLOR": "#ffffff",
      "DISPLAY": "LINE"
    }
  ];

  readyList.push({
    json: {
      deal_id: dealId,
      dialog_id: session.dialog_id,
      survey_message: surveyMessage,
      keyboard: keyboard
    }
  });
}

return readyList;
"""
            }
        },
        {
            "id": "node_csat_send_chat",
            "name": "CSAT_Send_Survey_To_Chat",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1320, 600],
            "onError": "continueRegularOutput",
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  DIALOG_ID: $json.dialog_id,\n  MESSAGE: $json.survey_message,\n  KEYBOARD: $json.keyboard\n}) }}",
                "options": {}
            }
        },
        {
            "id": "node_csat_mark_postgres",
            "name": "CSAT_Mark_Sent_Postgres",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [1560, 600],
            "onError": "continueRegularOutput",
            "parameters": {
                "operation": "executeQuery",
                "query": "UPDATE ticket_bot_sessions SET collected_data_json = COALESCE(collected_data_json, '{}'::jsonb) || '{\"csat_sent\": true}'::jsonb, last_interaction_at = NOW() WHERE deal_id = {{ $json.deal_id }};",
                "additionalFields": {}
            },
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        }
    ]
    wf['nodes'].extend(csat_branch_nodes)

    # Conecta no 00_Schedule_Trigger
    schedule_connections = wf['connections'].get('00_Schedule_Trigger', {}).get('main', [[]])
    if len(schedule_connections) > 0:
        schedule_connections[0].append({"node": "CSAT_Poll_Won_Deals", "type": "main", "index": 0})
    else:
        wf['connections']['00_Schedule_Trigger'] = {"main": [[{"node": "CSAT_Poll_Won_Deals", "type": "main", "index": 0}]]}

    wf['connections']['CSAT_Poll_Won_Deals'] = {"main": [[{"node": "CSAT_Filter_Unsent_Deals", "type": "main", "index": 0}]]}
    wf['connections']['CSAT_Filter_Unsent_Deals'] = {"main": [[{"node": "CSAT_Lookup_Session_Postgres", "type": "main", "index": 0}]]}
    wf['connections']['CSAT_Lookup_Session_Postgres'] = {"main": [[{"node": "CSAT_Prepare_Survey_Payload", "type": "main", "index": 0}]]}
    wf['connections']['CSAT_Prepare_Survey_Payload'] = {"main": [[{"node": "CSAT_Send_Survey_To_Chat", "type": "main", "index": 0}]]}
    wf['connections']['CSAT_Send_Survey_To_Chat'] = {"main": [[{"node": "CSAT_Mark_Sent_Postgres", "type": "main", "index": 0}]]}

print("\n3. Salvando workflow atualizado no n8n...")
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}

put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Workflow c0F2GUMFm2BI94UG salvo com sucesso no n8n com Human Takeover e CSAT no WON!")
    # Exporta backup local
    open(r'c:\mundial-n8n-automations\workflows\BITRIX_TI_AI_TRIAGE_AGENT.json', 'w', encoding='utf-8').write(
        json.dumps(put_resp.json(), indent=2, ensure_ascii=False)
    )
    print("Backup local exportado para workflows/BITRIX_TI_AI_TRIAGE_AGENT.json!")
else:
    print(f"Erro ao salvar: {put_resp.status_code} - {put_resp.text}")
    sys.exit(1)
