# -*- coding: utf-8 -*-
"""
Script de Deploy para:
1. Correção definitiva do pipeline OCR / Multimodal Vision (Buffer extraction via helpers.getBinaryDataBuffer no n8n filesystem-v2)
2. Fallback de texto quando usuário envia apenas print de erro
3. Reconhecimento de [ANÁLISE DE PRINT ANEXADO] no System Prompt do Agente de IA
4. Implementação de notificação automática para a Equipe de TI (Eduardo 32598 e Igor 352678) quando chamado for triado e estiver pronto para atendimento técnico
"""

import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
HEADERS = {
    'X-N8N-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

print("1. Baixando workflow atual da API do n8n...")
r = requests.get(N8N_URL, headers=HEADERS)
if r.status_code != 200:
    print(f"Erro ao buscar workflow: {r.status_code} - {r.text}")
    sys.exit(1)

wf = r.json()
nodes = wf.get('nodes', [])
conns = wf.get('connections', {})

# 1. Atualizar nó 05_Filter_And_Classify_Messages
node_05 = next((n for n in nodes if n['name'] == '05_Filter_And_Classify_Messages'), None)
if node_05:
    node_05['parameters']['jsCode'] = """// Classificação e filtragem multi-item com suporte a Anti-Carona e Imagens (Sprint 2 Vision)
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

    // Checagem de anexo de imagem na mensagem (suporta array ou ID único)
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
    print("-> 05_Filter_And_Classify_Messages atualizado com sucesso.")

# 2. Atualizar Vision_03_Prepare_Vision_Payload
node_v03 = next((n for n in nodes if n['name'] == 'Vision_03_Prepare_Vision_Payload'), None)
if node_v03:
    node_v03['parameters']['jsCode'] = """// Prepara payload multimodal para o OpenAI Vision extraindo buffer binário real (suporte a n8n filesystem-v2)
const items = $input.all();
const sessionItems = $('06_If_Has_Image_To_Process').all();
const results = [];

for (let idx = 0; idx < items.length; idx++) {
  const item = items[idx];
  const session = sessionItems[idx]?.json || {};
  
  let base64Str = '';
  try {
    const buffer = await this.helpers.getBinaryDataBuffer(idx, 'data');
    if (buffer && buffer.length > 0) {
      base64Str = buffer.toString('base64');
    }
  } catch (e) {
    base64Str = '';
  }

  if (!base64Str) {
    // Se download ou conversão falhou, repassa sem imagem
    results.push({
      json: {
        ...session,
        vision_failed: true
      }
    });
    continue;
  }

  let mimeType = 'image/png';
  const ext = String(session.image_extension || '').toLowerCase();
  if (ext === 'jpg' || ext === 'jpeg') {
    mimeType = 'image/jpeg';
  } else if (ext === 'webp') {
    mimeType = 'image/webp';
  }

  results.push({
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
  });
}

return results;"""
    print("-> Vision_03_Prepare_Vision_Payload atualizado com sucesso.")

# 3. Atualizar Vision_05_Merge_Vision_Context
node_v05 = next((n for n in nodes if n['name'] == 'Vision_05_Merge_Vision_Context'), None)
if node_v05:
    node_v05['parameters']['jsCode'] = """// Mescla a análise de visão computacional no contexto textual do usuário
const items = $input.all();
const sessionItems = $('Vision_03_Prepare_Vision_Payload').all();

return items.map((item, idx) => {
  const session = sessionItems[idx]?.json || {};
  const visionContent = item.json.choices?.[0]?.message?.content || '';

  let userText = String(session.message_text || '').trim();
  // Se o texto original era apenas o fallback genérico, substitui pela análise de visão
  if (userText === 'O colaborador enviou um print/imagem de erro em anexo.') {
    userText = '';
  }

  let enrichedMessage = '';
  if (userText && visionContent) {
    enrichedMessage = `${userText}\\n\\n${visionContent}`;
  } else if (visionContent) {
    enrichedMessage = visionContent;
  } else {
    enrichedMessage = userText || 'O colaborador enviou uma imagem em anexo, porém não foi possível extrair texto visual.';
  }

  return {
    json: {
      deal_id: session.deal_id,
      chat_id: session.chat_id,
      dialog_id: session.dialog_id,
      requester_user_id: session.requester_user_id,
      requester_name: session.requester_name || 'Colaborador',
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
    print("-> Vision_05_Merge_Vision_Context atualizado com sucesso.")

# 4. Atualizar System Prompt do Agente 08_AI_Agent_Triage_Deal
node_08 = next((n for n in nodes if n['name'] == '08_AI_Agent_Triage_Deal'), None)
if node_08:
    prompt_text = node_08['parameters']['text']
    vision_directive = """
# LEITURA E INTERPRETAÇÃO DE PRINTS/IMAGENS ANEXADAS:
- Quando a mensagem do usuário ou o contexto contiver "[ANÁLISE DE PRINT ANEXADO]", considere todas as informações visuais extraídas (Sistema identificado, Mensagem/Erro na Tela, Código de Erro, Chassi, Chave de NFe, Alertas) como FATOS REAIS E COMPROVADOS.
- Acolha o colaborador demonstrando que você visualizou o print anexado (ex: "Vi pelo seu print que apareceu a mensagem '(12.1) Usuário Bloqueado' no IHS Motocicleta...").
- NÃO pergunte ao usuário o que já está visível e comprovado no print! Use os dados visuais diretamente para diagnosticar, orientar o teste L1 ou concluir a triagem técnica.
"""
    if '# LEITURA E INTERPRETAÇÃO DE PRINTS/IMAGENS ANEXADAS:' not in prompt_text:
        # Inserir antes de # DINÂMICA DE AUTOATENDIMENTO
        if '# DINÂMICA DE AUTOATENDIMENTO' in prompt_text:
            prompt_text = prompt_text.replace('# DINÂMICA DE AUTOATENDIMENTO', vision_directive + '\n# DINÂMICA DE AUTOATENDIMENTO')
        else:
            prompt_text = prompt_text + '\n' + vision_directive
        node_08['parameters']['text'] = prompt_text
        print("-> 08_AI_Agent_Triage_Deal System Prompt enriquecido com suporte a OCR de prints.")

# 5. Adicionar nós de notificação para a Equipe de TI
existing_node_names = [n['name'] for n in nodes]

if '15_Filter_Tickets_Ready_For_IT' not in existing_node_names:
    node_filter_it = {
        "id": "node_filter_tickets_ready_it",
        "name": "15_Filter_Tickets_Ready_For_IT",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [
            1880,
            2240
        ],
        "parameters": {
            "jsCode": """// Filtra chamados que concluíram triagem e estão prontos para atendimento humano pela TI
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
      notifications.push({
        json: {
          deal_id: dealId,
          recipient_id: String(recipientId),
          notification_message: msgText
        }
      });
    }
  }
}

return notifications;"""
        }
    }
    nodes.append(node_filter_it)
    print("-> Nó 15_Filter_Tickets_Ready_For_IT adicionado.")

if '15_Notify_IT_Team_Ready' not in existing_node_names:
    node_notify_it = {
        "id": "node_notify_it_team_ready",
        "name": "15_Notify_IT_Team_Ready",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "onError": "continueRegularOutput",
        "position": [
            2128,
            2240
        ],
        "parameters": {
            "method": "POST",
            "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({\n  DIALOG_ID: $json.recipient_id,\n  MESSAGE: $json.notification_message\n}) }}",
            "options": {}
        }
    }
    nodes.append(node_notify_it)
    print("-> Nó 15_Notify_IT_Team_Ready adicionado.")

# Conectar 15_Send_Final_Confirmation_To_Chat -> 15_Filter_Tickets_Ready_For_IT -> 15_Notify_IT_Team_Ready
if '15_Send_Final_Confirmation_To_Chat' in conns:
    final_chat_targets = conns['15_Send_Final_Confirmation_To_Chat'].get('main', [[]])[0]
    if not any(t.get('node') == '15_Filter_Tickets_Ready_For_IT' for t in final_chat_targets):
        final_chat_targets.append({
            'node': '15_Filter_Tickets_Ready_For_IT',
            'type': 'main',
            'index': 0
        })
        print("-> Conexão 15_Send_Final_Confirmation_To_Chat -> 15_Filter_Tickets_Ready_For_IT configurada.")

if '15_Filter_Tickets_Ready_For_IT' not in conns:
    conns['15_Filter_Tickets_Ready_For_IT'] = {
        'main': [
            [
                {
                    'node': '15_Notify_IT_Team_Ready',
                    'type': 'main',
                    'index': 0
                }
            ]
        ]
    }
    print("-> Conexão 15_Filter_Tickets_Ready_For_IT -> 15_Notify_IT_Team_Ready configurada.")

# Salvar cópias locais
print("\nSalvando cópias locais dos workflows...")
with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
with open('workflows/canonical/BITRIX_TI_AI_TRIAGE_AGENT.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
with open('workflows/current_c0F2GUMFm2BI94UG.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
print("Arquivos salvos localmente com sucesso.")

# Deploy via PUT para a API do n8n
print("\nEnviando workflow atualizado para o n8n...")
payload = {
    "name": wf.get("name"),
    "nodes": wf.get("nodes"),
    "connections": wf.get("connections"),
    "settings": wf.get("settings", {})
}

put_res = requests.put(N8N_URL, json=payload, headers=HEADERS)
if put_res.status_code == 200:
    print("PUT realizado com sucesso! Workflow atualizado no n8n.")
else:
    print(f"Erro no PUT: {put_res.status_code} - {put_res.text}")
    sys.exit(1)

# Ciclo de reload (deactivate -> activate)
print("\nRecarregando workflow (Deactivate -> Activate)...")
requests.post(f"{N8N_URL}/deactivate", headers=HEADERS)
act_res = requests.post(f"{N8N_URL}/activate", headers=HEADERS)
if act_res.status_code == 200:
    print("Workflow reativado com sucesso! Schedulers e Webhooks recarregados.")
else:
    print(f"Erro ao reativar: {act_res.status_code} - {act_res.text}")

print("\nDeploy de OCR Vision e Notificação da Equipe de TI concluído com sucesso!")
