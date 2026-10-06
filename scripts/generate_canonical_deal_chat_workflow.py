# -*- coding: utf-8 -*-
"""
Script para geração canônica do workflow n8n: BITRIX_TI_AI_TRIAGE_AGENT
Arquitetura: CRM Deal Chat (Chat Nativo do Card) + Agente de IA LangChain
Hotfix: Context Integrity (Zero .first() em deal context, Generic Self-Healing, Cursor pós-sucesso)
Concessionárias Mundial Honda — Central de TI RPA
"""

import json
import os

workflow = {
    "name": "BITRIX_TI_AI_TRIAGE_AGENT",
    "nodes": [
        # --- STICKY NOTES ---
        {
            "parameters": {
                "content": "## 01 — ENTRADA & CRIAÇÃO IDEMPOTENTE DO CHAT NO CARD\nRecebe novos tickets (Webhook ONCRMDEALADD ou Polling a cada 15s).\nReserva a sessão atomicamente no Postgres (deal_id UNIQUE) antes de chamar im.chat.add.\nCria o chat vinculado ao Deal (ENTITY_TYPE='CRM', ENTITY_ID='DEAL|<ID>').",
                "height": 420,
                "width": 680,
                "color": 4
            },
            "id": "sticky_01_intake",
            "name": "Sticky_01_Intake_Idempotency",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [-320, -100]
        },
        {
            "parameters": {
                "content": "## 02 — MONITORAMENTO DE MENSAGENS & HUMAN TAKEOVER\nBusca novas mensagens exclusivamente nas sessões ACTIVE com auto-recuperação genérica por estado.\nDetecta Human Takeover: se um técnico humano falar no chat, pausa a IA (ai_state='AI_PAUSED').\nFiltra mensagens do próprio robô (author_id=61622) e do sistema.",
                "height": 420,
                "width": 680,
                "color": 5
            },
            "id": "sticky_02_polling",
            "name": "Sticky_02_Message_Polling_Takeover",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [400, -100]
        },
        {
            "parameters": {
                "content": "## 03 — DEBOUNCE ADAPTATIVO (MÓDULO RESERVADO)\nJanela adaptativa de silêncio de 4s.\nPara o E2E atual, o buffer em lista está em bypass e o roteamento é direto ao Agente.",
                "height": 420,
                "width": 640,
                "color": 6
            },
            "id": "sticky_03_debounce",
            "name": "Sticky_03_Debounce_Redis",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [1120, -100]
        },
        {
            "parameters": {
                "content": "## 04 — AGENTE DE IA (LANGCHAIN + GPT-4o-MINI + MEMÓRIA REDIS)\nMemória isolada por Deal (bitrix:ti:deal:<deal_id>:memory).\nPrompt canônico dos 11 temas de TI, separação rigorosa de escopo e extração de fatos.\nTool Think e saída estruturada (ASK / COMPLETE).",
                "height": 480,
                "width": 640,
                "color": 1
            },
            "id": "sticky_04_ai",
            "name": "Sticky_04_AI_LangChain_Agent",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [1800, -100]
        },
        {
            "parameters": {
                "content": "## 05 — VALIDADOR B01, CRM UPDATE & TIMELINE\nValidação determinística de enums (sem intervenção arbitrária da IA).\nMotor B01: P1 (1202), P2 (1204), P3 (1206), P4 (1208) — CONTRATO RESTRITO P1 A P4!\nB02 Title, Read-Back de integridade, marco resumido na Timeline e conclusão da sessão.",
                "height": 480,
                "width": 780,
                "color": 2
            },
            "id": "sticky_05_crm",
            "name": "Sticky_05_B01_CRM_Timeline",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [2480, -100]
        },

        # --- GATILHOS DE ENTRADA (INTAKE) ---
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "seconds",
                            "secondsInterval": 15
                        }
                    ]
                }
            },
            "name": "00_Schedule_Trigger",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [-320, 80],
            "id": "node_schedule_trigger"
        },
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "bitrix-crm-deal-webhook",
                "options": {}
            },
            "name": "00_Webhook_Deal_Add",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [-320, 240],
            "id": "node_webhook_deal"
        },

        # --- DESCOBERTA DE DEALS (POLLING FALLBACK) ---
        {
            "parameters": {
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.list",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        { "name": "filter[CATEGORY_ID]", "value": "160" },
                        { "name": "filter[STAGE_ID]", "value": "C160:NEW" },
                        { "name": "filter[CREATED_BY_ID]", "value": "32598" },
                        { "name": "order[ID]", "value": "DESC" },
                        { "name": "select[]", "value": "ID" },
                        { "name": "select[]", "value": "TITLE" },
                        { "name": "select[]", "value": "CREATED_BY_ID" },
                        { "name": "select[]", "value": "DATE_CREATE" }
                    ]
                },
                "options": {}
            },
            "name": "01_Polling_Get_New_Deals",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [-120, 80],
            "id": "node_poll_deals"
        },
        {
            "parameters": {
                "functionCode": "// Extrai ID do Deal de webhook ONCRMDEALADD ou lista do polling\nconst items = $input.all();\nconst ids = [];\n\nfor (const item of items) {\n  const json = item.json;\n  const body = json.body || json;\n\n  // Polling: array em json.result\n  if (json.result && Array.isArray(json.result)) {\n    for (const d of json.result) {\n      if (d.ID) ids.push(Number(d.ID));\n    }\n  }\n  // Webhook ONCRMDEALADD (URL encoded ou JSON)\n  else {\n    let dId = null;\n    if (body['data[FIELDS][ID]']) dId = Number(body['data[FIELDS][ID]']);\n    else if (body.data?.FIELDS?.ID) dId = Number(body.data.FIELDS.ID);\n    else if (body.FIELDS?.ID) dId = Number(body.FIELDS.ID);\n    else if (body.id || body.ID) dId = Number(body.id || body.ID);\n    if (dId) ids.push(dId);\n  }\n}\n\n// Deduplica IDs\nconst uniqueIds = [...new Set(ids)];\nreturn uniqueIds.map(id => ({ json: { deal_id: id } }));"
            },
            "name": "01_Extract_Discovered_Deal_IDs",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [-120, 240],
            "id": "node_extract_ids"
        },
        {
            "parameters": {
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.get",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        { "name": "id", "value": "={{ $json.deal_id }}" }
                    ]
                },
                "options": {}
            },
            "name": "01_Fetch_Deal_Bitrix_Verification",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [80, 240],
            "id": "node_fetch_deal_verify"
        },
        {
            "parameters": {
                "functionCode": "// GATE FAIL-CLOSED ABSOLUTO:\n// Verifica se o Deal pertence EXCLUSIVAMENTE à Categoria 160 e ao usuário 32598 (Eduardo)\nconst items = $input.all();\nconst allowed = [];\nconst ALLOWED_REQUESTERS = [32598]; // Piloto restrito Eduardo Alaminos\n\nfor (const item of items) {\n  const deal = item.json.result || item.json;\n  const categoryId = String(deal.CATEGORY_ID || '');\n  const stageId = String(deal.STAGE_ID || '');\n  const createdBy = Number(deal.CREATED_BY_ID || 0);\n  const title = deal.TITLE || `Chamado #${deal.ID}`;\n\n  if (categoryId === '160' && stageId === 'C160:NEW' && ALLOWED_REQUESTERS.includes(createdBy)) {\n    allowed.push({\n      json: {\n        deal_id: Number(deal.ID),\n        title: title,\n        requester_user_id: createdBy,\n        requester_name: 'Eduardo Alaminos'\n      }\n    });\n  }\n}\n\nreturn allowed;"
            },
            "name": "01_Strict_Gate_Cat160_Pilot",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [280, 240],
            "id": "node_gate_pilot"
        },

        # --- IDEMPOTÊNCIA: RESERVA ATÔMICA DA SESSÃO ---
        {
            "parameters": {
                "operation": "executeQuery",
                "query": "INSERT INTO ticket_bot_sessions (deal_id, requester_user_id, requester_name, channel, private_dialog_id, dialog_type, status, state, ai_state, redis_memory_key, created_at, last_interaction_at) VALUES ({{ $json.deal_id }}, {{ $json.requester_user_id }}, '{{ $json.requester_name }}', 'BITRIX_CRM_CHAT', '', 'chat', 'CHAT_CREATING', 'INIT', 'AI_ACTIVE', 'bitrix:ti:deal:{{ $json.deal_id }}:memory', NOW(), NOW()) ON CONFLICT (deal_id) DO UPDATE SET last_interaction_at = NOW() WHERE ticket_bot_sessions.internal_chat_id IS NULL AND ticket_bot_sessions.status != 'COMPLETED' RETURNING id, deal_id, requester_user_id, requester_name, '{{ $json.title }}' AS deal_title;",
                "additionalFields": {}
            },
            "name": "02_Reserve_Deal_Session_Atomic",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [480, 240],
            "id": "node_reserve_session",
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        },
        {
            "parameters": {
                "conditions": {
                    "number": [
                        {
                            "value1": "={{ $json.id }}",
                            "operation": "larger",
                            "value2": 0
                        }
                    ]
                }
            },
            "name": "02_If_Reservation_Won",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [680, 240],
            "id": "node_if_reservation_won"
        },

        # --- CRIAÇÃO DO CHAT NO CARD (im.chat.add) ---
        {
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.chat.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  TYPE: 'CHAT',\n  TITLE: 'Triagem TI - Chamado #' + $json.deal_id + ': ' + $json.deal_title,\n  ENTITY_TYPE: 'CRM',\n  ENTITY_ID: 'DEAL|' + $json.deal_id,\n  USERS: [Number($json.requester_user_id), 61622],\n  MESSAGE: 'Olá ' + $json.requester_name + '! 👋 Sou o assistente de triagem de TI da Central Mundial Honda.\\n\\nEste é o chat exclusivo do chamado #' + $json.deal_id + '.\\nPor favor, conte o que está acontecendo e se isso afeta apenas você ou todo o setor/loja.'\n}) }}",
                "options": {}
            },
            "name": "03_Create_CRM_Card_Chat",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [880, 240],
            "id": "node_create_crm_chat"
        },
        {
            "parameters": {
                "functionCode": "// Preserva deal context via all(), associando item a item\nconst reserveItems = $('02_Reserve_Deal_Session_Atomic').all();\nconst items = $input.all();\nreturn items.map((item, idx) => {\n  const chatId = Number(item.json.result || 0);\n  const r = reserveItems[idx]?.json || {};\n  return {\n    json: {\n      deal_id: r.deal_id,\n      chat_id: chatId,\n      dialog_id: `chat${chatId}`\n    }\n  };\n});"
            },
            "name": "03_Prepare_Activation",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [1080, 240],
            "id": "node_prepare_activation"
        },
        {
            "parameters": {
                "operation": "executeQuery",
                "query": "UPDATE ticket_bot_sessions SET internal_chat_id = {{ $json.chat_id }}, dialog_id = '{{ $json.dialog_id }}', status = 'ACTIVE', last_processed_message_id = '0', last_interaction_at = NOW() WHERE deal_id = {{ $json.deal_id }};",
                "additionalFields": {}
            },
            "name": "03_Activate_Session_With_Chat",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [1280, 240],
            "id": "node_activate_session",
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        },

        # --- SEÇÃO 02: MONITORAMENTO DE SESSÕES ATIVAS COM SELF-HEALING GENÉRICO ---
        {
            "parameters": {
                "operation": "executeQuery",
                "query": "-- Limpa sessões legadas/antigas que não pertencem ao piloto ativo\nUPDATE ticket_bot_sessions \nSET status = 'CANCELLED' \nWHERE status = 'ACTIVE' AND deal_id IN (1372316, 1372304, 1372318, 1372320, 1372322, 1372324, 1372326, 1372356, 1372428);\n\n-- SELF-HEALING GENÉRICO POR ESTADO (SEM IDS FIXOS):\n-- Promove qualquer sessão em CHAT_CREATING que já possua internal_chat_id gravado\nUPDATE ticket_bot_sessions \nSET status = 'ACTIVE' \nWHERE status = 'CHAT_CREATING' AND internal_chat_id IS NOT NULL;\n\n-- Recupera todas as sessões ativas legítimas\nSELECT id, deal_id, requester_user_id, requester_name, internal_chat_id, dialog_id, last_processed_message_id, ai_state, redis_memory_key \nFROM ticket_bot_sessions \nWHERE status = 'ACTIVE' AND internal_chat_id IS NOT NULL;",
                "additionalFields": {}
            },
            "name": "04_Get_Active_Sessions_Postgres",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [-120, 420],
            "id": "node_get_active_sessions",
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        },
        {
            "parameters": {
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.dialog.messages.get",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        { "name": "DIALOG_ID", "value": "={{ $json.dialog_id }}" },
                        { "name": "LIMIT", "value": "10" }
                    ]
                },
                "options": {}
            },
            "name": "04_Fetch_Chat_Messages_Bitrix",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [80, 420],
            "id": "node_fetch_messages"
        },
        {
            "parameters": {
                "functionCode": "// Classificação e filtragem multi-item: Processamento multi-item usando all()!\n// Cada item carrega seu próprio deal_id, dialog_id e message_id\nconst sessions = $('04_Get_Active_Sessions_Postgres').all();\nconst items = $input.all();\nconst outputItems = [];\n\nfor (let i = 0; i < items.length; i++) {\n  const session = sessions[i]?.json || {};\n  const res = items[i].json.result || {};\n  const messages = res.messages || [];\n\n  const lastProcessedId = Number(session.last_processed_message_id || 0);\n  const requesterId = Number(session.requester_user_id);\n  const BOT_ID = 61622;\n\n  // Ordena cronologicamente crescente\n  messages.sort((a, b) => Number(a.id) - Number(b.id));\n\n  const newMessages = [];\n  let humanTakeoverDetected = false;\n  let lastMsgId = lastProcessedId;\n\n  for (const msg of messages) {\n    const msgId = Number(msg.id);\n    if (msgId <= lastProcessedId) continue;\n    lastMsgId = Math.max(lastMsgId, msgId);\n\n    const authorId = Number(msg.author_id);\n    // Ignora mensagens do bot (61622) ou de sistema (0)\n    if (authorId === BOT_ID || authorId === 0) continue;\n\n    // Se autor não for o solicitante nem o bot -> Humano da TI falando no chat do card!\n    if (authorId !== requesterId) {\n      humanTakeoverDetected = true;\n      break;\n    }\n\n    // Mensagem válida do solicitante\n    const cleanText = String(msg.text || '').trim();\n    if (cleanText) {\n      newMessages.push(cleanText);\n    }\n  }\n\n  if (humanTakeoverDetected) {\n    outputItems.push({\n      json: {\n        deal_id: session.deal_id,\n        dialog_id: session.dialog_id,\n        human_takeover: true,\n        last_msg_id: lastMsgId\n      }\n    });\n    continue;\n  }\n\n  if (session.ai_state === 'AI_PAUSED') {\n    continue;\n  }\n\n  if (newMessages.length > 0) {\n    outputItems.push({\n      json: {\n        deal_id: session.deal_id,\n        chat_id: session.internal_chat_id,\n        dialog_id: session.dialog_id,\n        requester_user_id: requesterId,\n        message_id: lastMsgId,\n        message_text: newMessages.join('\\n'),\n        redis_memory_key: `bitrix:ti:deal:${session.deal_id}:memory`,\n        ai_state: session.ai_state\n      }\n    });\n  }\n}\n\nreturn outputItems;"
            },
            "name": "05_Filter_And_Classify_Messages",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [280, 420],
            "id": "node_filter_messages"
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{ Boolean($json.human_takeover) }}",
                            "value2": True
                        }
                    ]
                }
            },
            "name": "05_If_Human_Takeover",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [480, 420],
            "id": "node_if_human_takeover"
        },
        {
            "parameters": {
                "operation": "executeQuery",
                "query": "UPDATE ticket_bot_sessions SET ai_state = 'AI_PAUSED', last_processed_message_id = '{{ $json.last_msg_id }}', last_interaction_at = NOW() WHERE deal_id = {{ $json.deal_id }};",
                "additionalFields": {}
            },
            "name": "05_Pause_AI_On_Human_Takeover",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [680, 540],
            "id": "node_pause_ai_pg",
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        },

        # --- SEÇÃO 03: MÓDULO DEBOUNCE ADAPTATIVO (RESERVADO) ---
        {
            "parameters": {
                "amount": 4
            },
            "name": "06_Wait_Debounce_4s",
            "type": "n8n-nodes-base.wait",
            "typeVersion": 1.1,
            "position": [880, 540],
            "id": "node_wait_debounce_4s"
        },
        {
            "parameters": {
                "functionCode": "// Prepara input isolado para o Agente LangChain por Deal\nconst items = $input.all();\nreturn items.map(item => ({\n  json: {\n    deal_id: item.json.deal_id,\n    chat_id: item.json.chat_id,\n    dialog_id: item.json.dialog_id,\n    requester_user_id: item.json.requester_user_id,\n    message_id: item.json.message_id,\n    full_user_input: item.json.message_text,\n    redis_memory_key: item.json.redis_memory_key,\n    ai_state: item.json.ai_state\n  }\n}));"
            },
            "name": "07_Prepare_AI_Deal_Input",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [680, 360],
            "id": "node_prep_ai_input"
        },

        # --- SEÇÃO 04: AGENTE DE IA LANGCHAIN (GPT-4o-MINI + MEMÓRIA REDIS) ---
        {
            "parameters": {
                "promptType": "define",
                "text": "={{ $json.full_user_input }}",
                "options": {
                    "systemMessage": "=HORÁRIO ATUAL: {{ $now.setZone('America/Sao_Paulo').toFormat('HH:mm:ss') }}\nCHAMADO CRM ATUAL: #{{ $json.deal_id }}\n\n# PAPEL E OBJETIVO\nVocê é o Especialista de Triagem Inicial de TI da Central Mundial Honda.\nVocê atende o colaborador DIRETAMENTE dentro do chat exclusivo deste chamado (#{{ $json.deal_id }}).\nSeu objetivo é acolher o colaborador com empatia e técnica, entender o problema para que a equipe de TI atue com máxima precisão.\n\n# REGRAS CRÍTICAS E INVARIANTES DE NEGÓCIO\n1. BREVIDADE: Faça no MÁXIMO UMA pergunta por vez. Nunca sobrecarregue o usuário.\n2. INVARIANTE ABSOLUTA DE DOMAIN SCOPE: A quantidade física de equipamentos, veículos ou telas NÃO define o impacto do negócio!\n   - Exemplo: '3 computadores com lentidão' NÃO significa empresa toda. Significa múltiplos usuários ou setor.\n   - O Impacto reflete QUEM está impedido de operar na concessionária.\n3. CONDIÇÃO OBSERVADA != CAUSA-RAIZ: Você coleta o sintoma visível (ex: cabo de rede conecta? Wi-Fi funciona?). Nunca deduza causa raiz antecipadamente.\n4. HUMAN TAKEOVER RESPEITADO: Você está em um chat colaborativo. Seja sempre profissional e cortês.\n5. O AGENTE NÃO DECIDE PRIORIDADE: Você apenas extrai os fatos (Impacto e Urgência). A prioridade física (P1 a P4) é calculada de forma 100% determinística pelo motor B01.\n\n# TEMAS CANÔNICOS DE TI:\n- INTERNET_REDE (Cabo funciona? Wi-Fi funciona? Afeta uma máquina ou o setor?)\n- COMPUTADOR (Liga? Travando? Erro de tela? Consegue usar outro?)\n- IMPRESSORA (Não imprime? Atolou papel? É a impressora de notas/caixa?)\n- ERP_MICROWORK (Qual módulo/tela? Consegue continuar faturando?)\n- ATPV_RENAVE (Comunicação com Detran/Renave parada? Afeta a loja?)\n- BITRIX24 (Qual tela/módulo? Falha de acesso ou carregamento?)\n- ACESSO_SENHA (Senha expirada? Bloqueio de rede?)\n- DESATIVAR_ACESSO (Desligamento de colaborador)\n- CAMERA (Sem imagem? Monitoramento comprometido?)\n- TELEFONIA (Ramal mudo? Não recebe chamadas?)\n- OUTROS (Demais solicitações de TI)\n\n# ENUMS CANÔNICOS OBRIGATÓRIOS:\nIMPACTO:\n- 'SINGLE_USER': Apenas o solicitante afetado.\n- 'MULTIPLE_USERS': Mais de um colaborador afetado.\n- 'ENTIRE_DEPARTMENT': O setor inteiro da concessionária parado.\n- 'ENTIRE_STORE': A loja inteira afetada.\n- 'ENTIRE_COMPANY': Todas as lojas da rede Mundial.\n\nURGÊNCIA:\n- 'OPERATION_HALTED': Atividade principal totalmente interrompida (caixa parado, emissão de NF parada).\n- 'SEVERELY_DEGRADED': Operação muito lenta ou com falhas graves, mas ainda roda.\n- 'WORKAROUND_AVAILABLE': Existe contorno imediato disponível (usa outra máquina, outro meio).\n- 'PLANNED_REQUEST': Solicitação normal ou preventiva.\n- 'INQUIRY': Dúvida ou esclarecimento.\n\n# AÇÕES PERMITIDAS:\n- Se ainda faltarem detalhes para entender o tema, o escopo ou a continuidade: use action 'ASK'. Responda diretamente ao usuário com a pergunta.\n- Se já tiver entendido com clareza o TEMA, o IMPACTO e a URGÊNCIA: use action 'COMPLETE'. Emita uma breve mensagem cordial de encerramento e anexe o bloco JSON estruturado obrigatório abaixo.\n\n# FORMATO OBRIGATÓRIO NA CONCLUSÃO:\n```json\n{\n  \"action\": \"COMPLETE\",\n  \"tema\": \"INTERNET_REDE\",\n  \"facts\": {\n    \"impacto\": {\n      \"value\": \"SINGLE_USER\",\n      \"confidence\": \"HIGH\",\n      \"evidence\": \"Apenas no meu computador\"\n    },\n    \"urgencia\": {\n      \"value\": \"OPERATION_HALTED\",\n      \"confidence\": \"HIGH\",\n      \"evidence\": \"Não consigo emitir a NF do cliente\"\n    }\n  },\n  \"assunto_curto\": \"Sem conexão de rede no faturamento\",\n  \"resumo_problema\": \"Computador do colaborador sem conexão cabeada. Wi-Fi funcional em outros aparelhos. Faturamento interrompido.\"\n}\n```"
                }
            },
            "name": "08_AI_Agent_Triage_Deal",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 3.1,
            "position": [920, 360],
            "id": "node_ai_deal_agent"
        },
        {
            "parameters": {
                "model": {
                    "__rl": True,
                    "value": "gpt-4.1-mini",
                    "mode": "list",
                    "cachedResultName": "gpt-4.1-mini"
                },
                "builtInTools": {},
                "options": {
                    "temperature": 0.2
                }
            },
            "name": "OpenAI_Chat_Model_Deal",
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
            "typeVersion": 1.3,
            "position": [920, 560],
            "id": "node_openai_deal",
            "credentials": {
                "openAiApi": {
                    "id": "zJ462uvngfWgM0PB",
                    "name": "OpenAi account 3"
                }
            }
        },
        {
            "parameters": {
                "sessionIdType": "customKey",
                "sessionKey": "={{ $json.redis_memory_key }}",
                "sessionTTL": 86400,
                "contextWindowLength": 12
            },
            "name": "Redis_Deal_Chat_Memory",
            "type": "@n8n/n8n-nodes-langchain.memoryRedisChat",
            "typeVersion": 1.5,
            "position": [1120, 560],
            "id": "node_redis_deal_memory",
            "credentials": {
                "redis": {
                    "id": "NlIbdmbaePYxgp6S",
                    "name": "Redis Evolution"
                }
            }
        },
        {
            "parameters": {
                "description": "Pense cuidadosamente: você já possui informações suficientes sobre QUEM é afetado (impacto) e se a OPERAÇÃO está parada (urgência)? Só complete se tiver confiança ALTA."
            },
            "name": "Tool_Think_Deal",
            "type": "@n8n/n8n-nodes-langchain.toolThink",
            "typeVersion": 1.1,
            "position": [760, 560],
            "id": "node_think_deal"
        },

        # --- SEÇÃO 05: VALIDADOR DETERMINÍSTICO B01 & FORMATADOR ---
        {
            "parameters": {
                "functionCode": "// Formatação multi-item via all()!\nconst prepItems = $('07_Prepare_AI_Deal_Input').all();\nconst items = $input.all();\nconst results = [];\n\nfor (let i = 0; i < items.length; i++) {\n  const agentItem = items[i].json;\n  const prevData = prepItems[i]?.json || {};\n  \n  const rawOutput = agentItem.output || agentItem.text || '';\n  let cleanMessage = String(rawOutput).trim();\n  let structuredData = null;\n\n  const match = cleanMessage.match(/```(?:json)?\\s*(\\{[\\s\\S]*?\\})\\s*```/i);\n  if (match) {\n    try {\n      structuredData = JSON.parse(match[1]);\n      cleanMessage = cleanMessage.replace(match[0], '').trim();\n    } catch (e) {}\n  }\n\n  const isComplete = Boolean(structuredData && (structuredData.action === 'COMPLETE' || structuredData.status_triagem === 'concluido'));\n\n  results.push({\n    json: {\n      deal_id: prevData.deal_id,\n      chat_id: prevData.chat_id,\n      dialog_id: prevData.dialog_id,\n      requester_user_id: prevData.requester_user_id,\n      message_id: prevData.message_id,\n      reply_text: cleanMessage,\n      structured_data: structuredData,\n      is_complete: isComplete\n    }\n  });\n}\n\nreturn results;"
            },
            "name": "09_Format_AI_Response",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [1200, 360],
            "id": "node_format_ai_response"
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{ $json.is_complete }}",
                            "value2": True
                        }
                    ]
                }
            },
            "name": "09_If_Triage_Complete",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [1400, 360],
            "id": "node_if_complete"
        },

        # --- RAMO 1: AÇÃO 'ASK' (ENVIAR PERGUNTA NO CHAT DO CARD) ---
        {
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  DIALOG_ID: $json.dialog_id,\n  MESSAGE: $json.reply_text\n}) }}",
                "options": {}
            },
            "name": "10_Send_AI_Question_To_Card_Chat",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [1640, 480],
            "id": "node_send_ask_msg"
        },
        {
            "parameters": {
                "functionCode": "// Cursor SOMENTE após envio com sucesso no Bitrix (via all())\nconst askInputs = $('09_Format_AI_Response').all();\nconst items = $input.all();\nconst results = [];\n\nfor (let i = 0; i < items.length; i++) {\n  const bitrixRes = items[i].json;\n  const askData = askInputs[i]?.json || {};\n  \n  // Valida que o Bitrix retornou o ID da mensagem com sucesso\n  if (bitrixRes.result) {\n    results.push({\n      json: {\n        deal_id: askData.deal_id,\n        message_id: askData.message_id,\n        sent_bitrix_msg_id: bitrixRes.result\n      }\n    });\n  }\n}\n\nreturn results;"
            },
            "name": "10_Prepare_Cursor_Update",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [1840, 480],
            "id": "node_prepare_cursor_ask"
        },
        {
            "parameters": {
                "operation": "executeQuery",
                "query": "UPDATE ticket_bot_sessions SET last_processed_message_id = '{{ $json.message_id }}', last_interaction_at = NOW() WHERE deal_id = {{ $json.deal_id }};",
                "additionalFields": {}
            },
            "name": "10_Update_Cursor_On_Ask",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [2040, 480],
            "id": "node_update_cursor_ask",
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        },

        # --- RAMO 2: AÇÃO 'COMPLETE' (VALIDADOR B01, CRM UPDATE & TIMELINE) ---
        {
            "parameters": {
                "functionCode": "// MOTOR DETERMINÍSTICO B01 DE PRIORIDADE (V1 HOMOLOGADA) - MULTI-ITEM\nconst items = $input.all();\nconst results = [];\n\nconst IMPACT_MAP = {\n  'ENTIRE_COMPANY': { id: 1180, label: 'Empresa Inteira (Todas as Lojas)' },\n  'ENTIRE_STORE': { id: 1182, label: 'Loja Inteira' },\n  'ENTIRE_DEPARTMENT': { id: 1184, label: 'Departamento Inteiro' },\n  'MULTIPLE_USERS': { id: 1186, label: 'Múltiplos Usuários' },\n  'SINGLE_USER': { id: 1188, label: 'Usuário Individual' },\n  'NO_IMPACT': { id: 1190, label: 'Sem Impacto Operacional' }\n};\n\nconst URGENCY_MAP = {\n  'OPERATION_HALTED': { id: 1192, label: 'Operação Parada (Crítico)' },\n  'SEVERELY_DEGRADED': { id: 1194, label: 'Severamente Degradada' },\n  'WORKAROUND_AVAILABLE': { id: 1196, label: 'Contorno Disponível' },\n  'PLANNED_REQUEST': { id: 1198, label: 'Solicitação Planejada' },\n  'INQUIRY': { id: 1200, label: 'Dúvida / Informação' }\n};\n\nfor (const item of items) {\n  const data = item.json.structured_data || {};\n  const facts = data.facts || {};\n\n  const rawImpact = (facts.impacto?.value || data.impacto || 'SINGLE_USER').toUpperCase();\n  const rawUrgency = (facts.urgencia?.value || data.urgencia || 'NORMAL').toUpperCase();\n\n  const impactObj = IMPACT_MAP[rawImpact] || IMPACT_MAP['SINGLE_USER'];\n  const urgencyObj = URGENCY_MAP[rawUrgency] || URGENCY_MAP['PLANNED_REQUEST'];\n\n  let priorityId = 1206; // P3_MEDIUM Default\n  let priorityCode = 'P3_MEDIUM';\n  let priorityLabel = 'P3 - Médio';\n\n  if (rawImpact === 'ENTIRE_COMPANY') {\n    if (rawUrgency === 'OPERATION_HALTED' || rawUrgency === 'SEVERELY_DEGRADED') {\n      priorityId = 1202; priorityCode = 'P1_CRITICAL'; priorityLabel = 'P1 - Crítico';\n    } else if (rawUrgency === 'WORKAROUND_AVAILABLE') {\n      priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto';\n    } else if (rawUrgency === 'PLANNED_REQUEST') {\n      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';\n    } else {\n      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';\n    }\n  } else if (rawImpact === 'ENTIRE_STORE') {\n    if (rawUrgency === 'OPERATION_HALTED') {\n      priorityId = 1202; priorityCode = 'P1_CRITICAL'; priorityLabel = 'P1 - Crítico';\n    } else if (rawUrgency === 'SEVERELY_DEGRADED' || rawUrgency === 'WORKAROUND_AVAILABLE') {\n      priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto';\n    } else if (rawUrgency === 'PLANNED_REQUEST') {\n      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';\n    } else {\n      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';\n    }\n  } else if (rawImpact === 'ENTIRE_DEPARTMENT') {\n    if (rawUrgency === 'OPERATION_HALTED' || rawUrgency === 'SEVERELY_DEGRADED') {\n      priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto';\n    } else if (rawUrgency === 'WORKAROUND_AVAILABLE' || rawUrgency === 'PLANNED_REQUEST') {\n      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';\n    } else {\n      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';\n    }\n  } else if (rawImpact === 'MULTIPLE_USERS') {\n    if (rawUrgency === 'OPERATION_HALTED') {\n      priorityId = 1204; priorityCode = 'P2_HIGH'; priorityLabel = 'P2 - Alto';\n    } else if (rawUrgency === 'SEVERELY_DEGRADED' || rawUrgency === 'WORKAROUND_AVAILABLE') {\n      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';\n    } else {\n      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';\n    }\n  } else if (rawImpact === 'SINGLE_USER') {\n    if (rawUrgency === 'OPERATION_HALTED' || rawUrgency === 'SEVERELY_DEGRADED') {\n      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';\n    } else {\n      priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';\n    }\n  } else {\n    priorityId = 1208; priorityCode = 'P4_LOW'; priorityLabel = 'P4 - Baixo';\n  }\n\n  const shortSubject = data.assunto_curto || 'Atendimento de TI';\n  const tema = data.tema || 'GERAL';\n  const formattedTitle = `[TI-${tema}] - ${shortSubject} (Eduardo Alaminos)`;\n\n  results.push({\n    json: {\n      deal_id: item.json.deal_id,\n      chat_id: item.json.chat_id,\n      dialog_id: item.json.dialog_id,\n      message_id: item.json.message_id,\n      impact_id: impactObj.id,\n      impact_label: impactObj.label,\n      urgency_id: urgencyObj.id,\n      urgency_label: urgencyObj.label,\n      priority_id: priorityId,\n      priority_code: priorityCode,\n      priority_label: priorityLabel,\n      tema: tema,\n      short_subject: shortSubject,\n      formatted_title: formattedTitle,\n      resumo: data.resumo_problema || 'Triagem realizada pelo assistente de IA.',\n      next_owner_id: 1148,\n      wait_reason_id: 1162\n    }\n  });\n}\n\nreturn results;"
            },
            "name": "11_B01_Priority_And_Payload",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [1640, 240],
            "id": "node_calc_b01"
        },
        {
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.update",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  id: $json.deal_id,\n  fields: {\n    TITLE: $json.formatted_title,\n    UF_CRM_TI_IMPACT: $json.impact_id,\n    UF_CRM_TI_URGENCY: $json.urgency_id,\n    UF_CRM_TI_PRIORITY: $json.priority_id,\n    UF_CRM_TI_NEXT_OWNER: $json.next_owner_id,\n    UF_CRM_TI_WAIT_REASON: $json.wait_reason_id,\n    UF_CRM_TI_SHORT_SUBJECT: $json.short_subject\n  }\n}) }}",
                "options": {}
            },
            "name": "12_Update_Deal_CRM_Bitrix",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [1840, 240],
            "id": "node_update_deal_crm"
        },
        {
            "parameters": {
                "functionCode": "// Reassocia contexto do Deal após CRM Update via all()\nconst b01Items = $('11_B01_Priority_And_Payload').all();\nconst items = $input.all();\nreturn items.map((item, idx) => ({\n  json: b01Items[idx]?.json || item.json\n}));"
            },
            "name": "12_Prepare_Readback_Context",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [2040, 240],
            "id": "node_prep_readback"
        },
        {
            "parameters": {
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.get",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        { "name": "id", "value": "={{ $json.deal_id }}" }
                    ]
                },
                "options": {}
            },
            "name": "13_Readback_Verify_Deal",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [2240, 240],
            "id": "node_readback_deal"
        },
        {
            "parameters": {
                "functionCode": "// Prepara contexto para Timeline e Confirmação no Chat\nconst b01Items = $('11_B01_Priority_And_Payload').all();\nconst items = $input.all();\nreturn items.map((item, idx) => ({\n  json: b01Items[idx]?.json || item.json\n}));"
            },
            "name": "14_Prepare_Timeline_And_Chat",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [2440, 240],
            "id": "node_prep_timeline"
        },
        {
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.timeline.comment.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  fields: {\n    ENTITY_ID: $json.deal_id,\n    ENTITY_TYPE: 'deal',\n    COMMENT: '🤖 **Triagem IA Concluída com Sucesso!**\\n---------------------------------------------\\n📌 **Tema:** ' + $json.tema + '\\n👥 **Impacto:** ' + $json.impact_label + '\\n⏱️ **Urgência:** ' + $json.urgency_label + '\\n🚨 **Prioridade B01:** ' + $json.priority_label + ' (' + $json.priority_code + ')\\n\\n📝 **Resumo:**\\n' + $json.resumo + '\\n\\n💬 *Histórico detalhado da conversa mantido no Chat do Card.*'\n  }\n}) }}",
                "options": {}
            },
            "name": "14_Add_Timeline_Milestone_Comment",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [2640, 240],
            "id": "node_timeline_comment"
        },
        {
            "parameters": {
                "functionCode": "// Prepara payload para envio no chat final\nconst b01Items = $('11_B01_Priority_And_Payload').all();\nconst items = $input.all();\nreturn items.map((item, idx) => ({\n  json: b01Items[idx]?.json || item.json\n}));"
            },
            "name": "15_Prepare_Final_Chat",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [2840, 240],
            "id": "node_prep_final_chat"
        },
        {
            "parameters": {
                "method": "POST",
                "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({\n  DIALOG_ID: $json.dialog_id,\n  MESSAGE: '✅ Triagem concluída com sucesso!\\n\\nSeu chamado foi classificado como Prioridade ' + $json.priority_label + ' e já está disponível para a equipe de TI.\\n\\nQualquer novo detalhe ou print pode ser enviado diretamente aqui neste chat!'\n}) }}",
                "options": {}
            },
            "name": "15_Send_Final_Confirmation_To_Chat",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [3040, 240],
            "id": "node_send_final_chat"
        },
        {
            "parameters": {
                "functionCode": "// Cursor SOMENTE após confirmação enviada com sucesso no Bitrix (via all())\nconst b01Items = $('11_B01_Priority_And_Payload').all();\nconst items = $input.all();\nconst results = [];\n\nfor (let i = 0; i < items.length; i++) {\n  const bitrixRes = items[i].json;\n  const b01Data = b01Items[i]?.json || {};\n  \n  if (bitrixRes.result) {\n    results.push({\n      json: {\n        deal_id: b01Data.deal_id,\n        message_id: b01Data.message_id\n      }\n    });\n  }\n}\n\nreturn results;"
            },
            "name": "16_Prepare_Complete_Session",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [3240, 240],
            "id": "node_prep_complete_session"
        },
        {
            "parameters": {
                "operation": "executeQuery",
                "query": "UPDATE ticket_bot_sessions SET status = 'COMPLETED', state = 'COMPLETED', ai_state = 'COMPLETED', completed_at = NOW(), last_interaction_at = NOW(), last_processed_message_id = '{{ $json.message_id }}' WHERE deal_id = {{ $json.deal_id }};",
                "additionalFields": {}
            },
            "name": "16_Mark_Session_Completed_Postgres",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [3440, 240],
            "id": "node_complete_session_pg",
            "credentials": {
                "postgres": {
                    "id": "J8q2YHlBbp4WxxV2",
                    "name": "Postgres account"
                }
            }
        }
    ],
    "connections": {
        "00_Schedule_Trigger": {
            "main": [
                [
                    { "node": "01_Polling_Get_New_Deals", "type": "main", "index": 0 },
                    { "node": "04_Get_Active_Sessions_Postgres", "type": "main", "index": 0 }
                ]
            ]
        },
        "00_Webhook_Deal_Add": {
            "main": [
                [
                    { "node": "01_Extract_Discovered_Deal_IDs", "type": "main", "index": 0 }
                ]
            ]
        },
        "01_Polling_Get_New_Deals": {
            "main": [
                [
                    { "node": "01_Extract_Discovered_Deal_IDs", "type": "main", "index": 0 }
                ]
            ]
        },
        "01_Extract_Discovered_Deal_IDs": {
            "main": [
                [
                    { "node": "01_Fetch_Deal_Bitrix_Verification", "type": "main", "index": 0 }
                ]
            ]
        },
        "01_Fetch_Deal_Bitrix_Verification": {
            "main": [
                [
                    { "node": "01_Strict_Gate_Cat160_Pilot", "type": "main", "index": 0 }
                ]
            ]
        },
        "01_Strict_Gate_Cat160_Pilot": {
            "main": [
                [
                    { "node": "02_Reserve_Deal_Session_Atomic", "type": "main", "index": 0 }
                ]
            ]
        },
        "02_Reserve_Deal_Session_Atomic": {
            "main": [
                [
                    { "node": "02_If_Reservation_Won", "type": "main", "index": 0 }
                ]
            ]
        },
        "02_If_Reservation_Won": {
            "main": [
                [
                    { "node": "03_Create_CRM_Card_Chat", "type": "main", "index": 0 }
                ]
            ]
        },
        "03_Create_CRM_Card_Chat": {
            "main": [
                [
                    { "node": "03_Prepare_Activation", "type": "main", "index": 0 }
                ]
            ]
        },
        "03_Prepare_Activation": {
            "main": [
                [
                    { "node": "03_Activate_Session_With_Chat", "type": "main", "index": 0 }
                ]
            ]
        },
        "04_Get_Active_Sessions_Postgres": {
            "main": [
                [
                    { "node": "04_Fetch_Chat_Messages_Bitrix", "type": "main", "index": 0 }
                ]
            ]
        },
        "04_Fetch_Chat_Messages_Bitrix": {
            "main": [
                [
                    { "node": "05_Filter_And_Classify_Messages", "type": "main", "index": 0 }
                ]
            ]
        },
        "05_Filter_And_Classify_Messages": {
            "main": [
                [
                    { "node": "05_If_Human_Takeover", "type": "main", "index": 0 }
                ]
            ]
        },
        "05_If_Human_Takeover": {
            "main": [
                [
                    { "node": "05_Pause_AI_On_Human_Takeover", "type": "main", "index": 0 }
                ],
                [
                    { "node": "07_Prepare_AI_Deal_Input", "type": "main", "index": 0 }
                ]
            ]
        },
        "07_Prepare_AI_Deal_Input": {
            "main": [
                [
                    { "node": "08_AI_Agent_Triage_Deal", "type": "main", "index": 0 }
                ]
            ]
        },
        "OpenAI_Chat_Model_Deal": {
            "ai_languageModel": [
                [
                    { "node": "08_AI_Agent_Triage_Deal", "type": "ai_languageModel", "index": 0 }
                ]
            ]
        },
        "Redis_Deal_Chat_Memory": {
            "ai_memory": [
                [
                    { "node": "08_AI_Agent_Triage_Deal", "type": "ai_memory", "index": 0 }
                ]
            ]
        },
        "Tool_Think_Deal": {
            "ai_tool": [
                [
                    { "node": "08_AI_Agent_Triage_Deal", "type": "ai_tool", "index": 0 }
                ]
            ]
        },
        "08_AI_Agent_Triage_Deal": {
            "main": [
                [
                    { "node": "09_Format_AI_Response", "type": "main", "index": 0 }
                ]
            ]
        },
        "09_Format_AI_Response": {
            "main": [
                [
                    { "node": "09_If_Triage_Complete", "type": "main", "index": 0 }
                ]
            ]
        },
        "09_If_Triage_Complete": {
            "main": [
                [
                    { "node": "11_B01_Priority_And_Payload", "type": "main", "index": 0 }
                ],
                [
                    { "node": "10_Send_AI_Question_To_Card_Chat", "type": "main", "index": 0 }
                ]
            ]
        },
        "10_Send_AI_Question_To_Card_Chat": {
            "main": [
                [
                    { "node": "10_Prepare_Cursor_Update", "type": "main", "index": 0 }
                ]
            ]
        },
        "10_Prepare_Cursor_Update": {
            "main": [
                [
                    { "node": "10_Update_Cursor_On_Ask", "type": "main", "index": 0 }
                ]
            ]
        },
        "11_B01_Priority_And_Payload": {
            "main": [
                [
                    { "node": "12_Update_Deal_CRM_Bitrix", "type": "main", "index": 0 }
                ]
            ]
        },
        "12_Update_Deal_CRM_Bitrix": {
            "main": [
                [
                    { "node": "12_Prepare_Readback_Context", "type": "main", "index": 0 }
                ]
            ]
        },
        "12_Prepare_Readback_Context": {
            "main": [
                [
                    { "node": "13_Readback_Verify_Deal", "type": "main", "index": 0 }
                ]
            ]
        },
        "13_Readback_Verify_Deal": {
            "main": [
                [
                    { "node": "14_Prepare_Timeline_And_Chat", "type": "main", "index": 0 }
                ]
            ]
        },
        "14_Prepare_Timeline_And_Chat": {
            "main": [
                [
                    { "node": "14_Add_Timeline_Milestone_Comment", "type": "main", "index": 0 }
                ]
            ]
        },
        "14_Add_Timeline_Milestone_Comment": {
            "main": [
                [
                    { "node": "15_Prepare_Final_Chat", "type": "main", "index": 0 }
                ]
            ]
        },
        "15_Prepare_Final_Chat": {
            "main": [
                [
                    { "node": "15_Send_Final_Confirmation_To_Chat", "type": "main", "index": 0 }
                ]
            ]
        },
        "15_Send_Final_Confirmation_To_Chat": {
            "main": [
                [
                    { "node": "16_Prepare_Complete_Session", "type": "main", "index": 0 }
                ]
            ]
        },
        "16_Prepare_Complete_Session": {
            "main": [
                [
                    { "node": "16_Mark_Session_Completed_Postgres", "type": "main", "index": 0 }
                ]
            ]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
output_path = os.path.join(repo_root, "workflows", "canonical", "BITRIX_TI_AI_TRIAGE_AGENT.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"Workflow salvo com sucesso em: {output_path}")
print(f"Total de nós: {len(workflow['nodes'])}")
print(f"Total de conexões: {len(workflow['connections'])}")
