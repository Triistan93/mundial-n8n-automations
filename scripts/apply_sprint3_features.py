# -*- coding: utf-8 -*-
import json
import sys
import copy

sys.stdout.reconfigure(encoding='utf-8')

wf_path = 'workflows/BITRIX_TI_AI_TRIAGE_AGENT.json'
with open(wf_path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Save backup before Sprint 3
with open('workflows/backup_before_sprint3.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
print("Backup created: workflows/backup_before_sprint3.json")

nodes = wf.get('nodes', [])
connections = wf.get('connections', {})

# ----------------------------------------------------
# 1. Update 15_Prepare_Final_Chat for CSAT Invitation
# ----------------------------------------------------
prep_final = next(n for n in nodes if n['name'] == '15_Prepare_Final_Chat')
prep_final['parameters']['functionCode'] = """// Prepara payload para envio no chat final com convite para avaliação CSAT
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

  if (isPurchase) {
    finalMessage = `Prontinho, ${firstName}! Encaminhei a sua solicitação de compra para a aprovação da liderança e diretoria. Assim que tivermos o retorno, a equipe de TI dará o andamento imediato na compra e configuração para você!`;
  } else if (isResolvedL1) {
    finalMessage = `Fico muito feliz que conseguimos resolver o seu chamado #${dealId} por aqui, ${firstName}! 🎉\\n\\n⭐ **Pesquisa Rápida:** Como você avalia o suporte recebido hoje?\\nResponda com uma nota de 1 a 5:\\n⭐ 1 (Péssimo) | ⭐⭐ 2 (Ruim) | ⭐⭐⭐ 3 (Regular) | ⭐⭐⭐⭐ 4 (Bom) | ⭐⭐⭐⭐⭐ 5 (Excelente)`;
  } else if (isClienteEmLoja) {
    finalMessage = `Pode deixar, ${firstName}! Como você está com cliente aguardando na loja, já sinalizei o seu chamado #${dealId} com prioridade comercial máxima (🚨 CLIENTE EM LOJA) para a equipe técnica agilizar o seu atendimento imediatamente!`;
  } else {
    finalMessage = `Perfeito, ${firstName}! Todas as informações do chamado #${dealId} já foram organizadas e direcionadas para a fila da equipe de TI. O técnico responsável já vai assumir o seu atendimento!`;
  }

  return {
    json: {
      deal_id: dealId,
      dialog_id: b01.dialog_id,
      final_message: finalMessage
    }
  };
});
"""

# ----------------------------------------------------
# 2. Update PostRes Nodes for CSAT Feedback (Feature 5)
# ----------------------------------------------------
postres_prep = next(n for n in nodes if n['name'] == 'PostRes_02_Prepare_Prompt')
postres_prep['parameters']['functionCode'] = """const deal = $input.first().json.result || {};
const prev = $('06_Route_Session_Status').first().json || {};

const ufDesc = deal.UF_CRM_1729774515200;
let summary = deal.UF_CRM_TI_SHORT_SUBJECT || '';
if (Array.isArray(ufDesc)) {
  summary = ufDesc.join('\\n');
} else if (typeof ufDesc === 'string') {
  summary = ufDesc;
}

return [{
  json: {
    deal_id: Number(deal.ID),
    dialog_id: prev.dialog_id,
    chat_id: prev.chat_id,
    message_id: prev.message_id,
    requester_user_id: prev.requester_user_id || Number(deal.CREATED_BY_ID) || 32598,
    requester_name: prev.requester_name || 'colaborador',
    deal_title: deal.TITLE || `Chamado #${deal.ID}`,
    deal_summary: summary || deal.TITLE || 'Chamado de TI',
    user_message: prev.message_text
  }
}];
"""

postres_classify = next(n for n in nodes if n['name'] == 'PostRes_03_Classify_Intent')
postres_classify['parameters']['text'] = """=Você é o classificador de pós-atendimento da Central de TI da Mundial Honda.
Um chamado de suporte foi CONCLUÍDO com sucesso.
- Solicitante: {{ $json.requester_name }}
- Título do chamado: {{ $json.deal_title }}
- Problema/Resumo original resolvido: {{ $json.deal_summary }}

O colaborador agora enviou uma nova mensagem no chat deste chamado concluído:
\"{{ $json.user_message }}\"

Classifique a intenção em exatamente UMA das 4 categorias:
1. CSAT_FEEDBACK: O colaborador enviou uma nota ou avaliação sobre o atendimento (\"5\", \"nota 4\", \"⭐⭐⭐⭐⭐\", \"atendimento ótimo\", \"péssimo suporte\", \"10/10\", \"gostei muito\", \"nota 1\").
2. THANKS: O colaborador está apenas agradecendo, confirmando ou sendo cortês (\"valeu\", \"obrigado\", \"show\", \"beleza\", \"tudo certo\").
3. REOPEN: O MESMO problema original não foi resolvido ou voltou a acontecer (\"caiu de novo\", \"voltou a parar\", \"continua sem sinal\", \"não deu certo\", \"o cabo soltou\").
4. CARONA: O colaborador está relatando ou pedindo ajuda para um problema NOVO, diferente do tema original do chamado (\"aproveitando, o celular tá travando\", \"a impressora parou\", \"preciso de um mouse\").

Retorne OBRIGATORIAMENTE um JSON puro (sem markdown, sem tags, sem explicações extras) no formato exato:
{
  \"intent\": \"CSAT_FEEDBACK\" | \"THANKS\" | \"REOPEN\" | \"CARONA\",
  \"csat_rating\": 1 a 5 (número inteiro se for CSAT_FEEDBACK, se não for null),
  \"csat_comment\": \"texto do feedback do colaborador ou vazio\",
  \"reason\": \"breve justificativa\",
  \"reply_message\": \"mensagem carinhosa e natural para o usuário\"
}

Diretrizes para reply_message:
- Fale de forma amigável e empática, chamando pelo primeiro nome.
- Se CSAT_FEEDBACK: agradeça pela avaliação dizendo que o feedback ajuda o time de TI a melhorar a cada dia.
- Se THANKS: agradeça com carinho e deseje bom trabalho.
- Se REOPEN: lamente que o problema voltou e avise que reabriu o chamado para a equipe técnica de TI acompanhar com prioridade.
- Se CARONA: explique educadamente que como o chamado sobre o problema original já foi concluído, para esse novo assunto ele deve abrir um NOVO chamado no Bitrix24, garantindo prioridade e organização. Use emojis amigáveis."""

postres_parse = next(n for n in nodes if n['name'] == 'PostRes_04_Parse_Classification')
postres_parse['parameters']['functionCode'] = """const prev = $('PostRes_02_Prepare_Prompt').first().json || {};
const llmText = $input.first().json.text || '';
let parsed = {
  intent: 'CARONA',
  reply_message: `Oi, ${prev.requester_name}! Como este chamado já foi concluído, peço que você abra um novo chamado no Bitrix24 para esse novo assunto. Assim a equipe de TI atende com a prioridade correta! 🙌`
};

const match = llmText.match(/\\{[\\s\\S]*\\}/);
if (match) {
  try {
    parsed = JSON.parse(match[0]);
  } catch (e) {}
}

const intent = parsed.intent || 'CARONA';
const reply_message = parsed.reply_message || '';
const user_msg = String(prev.user_message || '').trim();

// Verificação determinística adicional de CSAT (ex: usuário digitou só "5" ou "10")
let csatRating = parsed.csat_rating ? Number(parsed.csat_rating) : null;
if (!csatRating) {
  if (/^[1-5]$/.test(user_msg)) {
    csatRating = parseInt(user_msg, 10);
  } else if (/^10$/.test(user_msg) || user_msg.includes('10/10')) {
    csatRating = 5;
  } else if (user_msg.includes('⭐') || user_msg.includes('estrela')) {
    const starCount = (user_msg.match(/⭐/g) || []).length;
    csatRating = starCount >= 1 ? Math.min(starCount, 5) : 5;
  }
}
if (csatRating) {
  csatRating = Math.max(1, Math.min(5, csatRating));
}
const isCsat = intent === 'CSAT_FEEDBACK' || csatRating !== null;
const csatComment = parsed.csat_comment || user_msg;

let timeline_comment = '';
if (intent === 'REOPEN') {
  timeline_comment = `🔄 **Chamado Reaberto pelo Solicitante**\\n\\nO colaborador informou que o problema persiste:\\n> \"${user_msg}\"\\n\\n*Retornado para \"Em atendimento\" (C160:PREPARATION) para atuação da equipe técnica.*`;
} else if (intent === 'CARONA') {
  timeline_comment = `🛑 **Tentativa de Chamado Carona Bloqueada**\\n\\nO colaborador tentou relatar um novo assunto neste chamado concluído:\\n> \"${user_msg}\"\\n\\n*O robô orientou educadamente a abertura de um novo chamado no Bitrix24.*`;
}

return [{
  json: {
    deal_id: prev.deal_id,
    dialog_id: prev.dialog_id,
    chat_id: prev.chat_id,
    message_id: prev.message_id,
    requester_user_id: prev.requester_user_id,
    requester_name: prev.requester_name,
    deal_title: prev.deal_title,
    user_message: user_msg,
    intent: isCsat ? 'CSAT_FEEDBACK' : intent,
    is_csat: isCsat,
    csat_rating: csatRating || 5,
    csat_comment: csatComment,
    reason: parsed.reason || '',
    reply_message: reply_message,
    timeline_comment: timeline_comment
  }
}];
"""

# ----------------------------------------------------
# 3. Add CSAT Route Nodes
# ----------------------------------------------------
if_csat_node = {
    "id": "node_postres_if_csat",
    "name": "PostRes_07_If_CSAT",
    "type": "n8n-nodes-base.if",
    "typeVersion": 1,
    "position": [950, 950],
    "parameters": {
        "conditions": {
            "boolean": [
                {
                    "value1": "={{ $json.is_csat }}",
                    "value2": True
                }
            ]
        }
    }
}

csat_insert_pg_node = {
    "id": "node_postres_csat_insert_pg",
    "name": "PostRes_CSAT_Insert_Postgres",
    "type": "n8n-nodes-base.postgres",
    "typeVersion": 1,
    "position": [1150, 880],
    "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO ticket_csat_ratings (deal_id, requester_user_id, rating, feedback_text, created_at) VALUES ({{ $json.deal_id }}, {{ $json.requester_user_id }}, {{ $json.csat_rating }}, '{{ $json.csat_comment.replace(/'/g, \"''\") }}', NOW()) RETURNING id;"
    },
    "credentials": {
        "postgres": {
            "id": "J8q2YHlBbp4WxxV2",
            "name": "Postgres account"
        }
    }
}

csat_timeline_crm_node = {
    "id": "node_postres_csat_timeline",
    "name": "PostRes_CSAT_Timeline_CRM",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 3,
    "position": [1300, 880],
    "parameters": {
        "method": "POST",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.timeline.comment.add",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ fields: { ENTITY_ID: $('PostRes_04_Parse_Classification').first().json.deal_id, ENTITY_TYPE: 'deal', COMMENT: '⭐ **AVALIAÇÃO DE ATENDIMENTO (CSAT) REGISTRADA!**\\n\\n📌 **Nota:** ' + $('PostRes_04_Parse_Classification').first().json.csat_rating + '/5 Estrelas\\n💬 **Feedback:** ' + ($('PostRes_04_Parse_Classification').first().json.csat_comment || 'Sem comentário adicional.') + '\\n\\n✅ *Registrado na base oficial de satisfação de TI.*' } }) }}",
        "options": {}
    }
}

csat_send_chat_node = {
    "id": "node_postres_csat_chat",
    "name": "PostRes_CSAT_Send_Chat",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 3,
    "position": [1450, 880],
    "parameters": {
        "method": "POST",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ DIALOG_ID: $('PostRes_04_Parse_Classification').first().json.dialog_id, MESSAGE: 'Muito obrigado pela sua avaliação! ⭐ Sua nota (' + $('PostRes_04_Parse_Classification').first().json.csat_rating + '/5) foi registrada com sucesso e ajuda muito o nosso time de TI a melhorar a cada dia. Conte sempre com a gente! 🙌' }) }}",
        "options": {}
    }
}

csat_update_pg_node = {
    "id": "node_postres_csat_update_pg",
    "name": "PostRes_CSAT_Update_Postgres",
    "type": "n8n-nodes-base.postgres",
    "typeVersion": 1,
    "position": [1600, 880],
    "parameters": {
        "operation": "executeQuery",
        "query": "UPDATE ticket_bot_sessions SET last_processed_message_id = '{{ $('PostRes_04_Parse_Classification').first().json.message_id }}', last_interaction_at = NOW(), collected_data_json = COALESCE(collected_data_json, '{}'::jsonb) || '{\"csat_answered\": true, \"csat_rating\": {{ $('PostRes_04_Parse_Classification').first().json.csat_rating }}}'::jsonb WHERE deal_id = {{ $('PostRes_04_Parse_Classification').first().json.deal_id }};"
    },
    "credentials": {
        "postgres": {
            "id": "J8q2YHlBbp4WxxV2",
            "name": "Postgres account"
        }
    }
}

# ----------------------------------------------------
# 4. Add Tool_Diagnostico_TI to Agent (Feature 6)
# ----------------------------------------------------
tool_diag_node = {
    "id": "node_tool_diagnostico_ti",
    "name": "Tool_Diagnostico_TI",
    "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
    "typeVersion": 1.1,
    "position": [950, 720],
    "parameters": {
        "toolDescription": "FERRAMENTA DE AUTO-REMEDIAÇÃO E DIAGNÓSTICO ATIVO EM TEMPO REAL DA MUNDIAL HONDA. Use SEMPRE que o colaborador relatar problemas de rede/conectividade em filial ('rede'), travamento no MicroWork Cloud ('microwork'), erros de Chassi, Detran ou RENAVE/ATPV ('chassi_renave'), ou status de importação de Notas Fiscais pelos robôs da montadora ('robos_rpa'). Esta ferramenta consulta o status real dos servidores em tempo real.",
        "method": "POST",
        "url": "https://sophia-n8nsophia.timft8.easypanel.host/webhook/ti-diagnostic-tools",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={ \"tipo\": \"{{ $fromAI('tipo', 'Tipo de teste a executar: rede, microwork, chassi_renave ou robos_rpa', 'string') }}\", \"parametro\": \"{{ $fromAI('parametro', 'Loja, chassi, numero da nota ou detalhe do erro a ser testado', 'string') }}\" }"
    }
}

# Update 08_AI_Agent_Triage_Deal System Prompt
agent_node = next(n for n in nodes if n['name'] == '08_AI_Agent_Triage_Deal')
agent_prompt = agent_node['parameters']['options']['systemMessage']
if "Tool_Diagnostico_TI" not in agent_prompt:
    new_tools_header = """
# FERRAMENTAS DISPONÍVEIS:
1. Tool_Think_Deal: Use para estruturar seu raciocínio lógico antes de emitir a resposta final.
2. KB_TI_PGVector_Tool: BASE VETORIAL DE CONHECIMENTO OFICIAL DA CONCESSIONÁRIA MUNDIAL HONDA.
   - Use SEMPRE esta ferramenta para buscar procedimentos oficiais de atendimento ao receber qualquer problema relatado (MicroWork, RENAVE, Bitrix, Portais Honda, FANDI, Impressora, Rede, Computador, E-mail, Senhas).
3. Tool_Diagnostico_TI: FERRAMENTA DE AUTO-REMEDIAÇÃO E DIAGNÓSTICO ATIVO EM TEMPO REAL.
   - Use SEMPRE que o colaborador relatar problemas de lentidão/queda de rede em filial ('rede'), travamentos de tela no MicroWork Cloud ('microwork'), erros de Chassi/ATPV/Detran ('chassi_renave') ou status dos robôs de entrada de NF ('robos_rpa').
   - Execute o diagnóstico, avalie o resultado retornado e explique amigavelmente ao colaborador o que foi identificado!
"""
    # Replace the existing header
    import re
    agent_prompt = re.sub(r'# FERRAMENTAS DISPONÍVEIS:[\s\S]*?(?==HORÁRIO ATUAL:)', new_tools_header + "\n", agent_prompt)
    agent_node['parameters']['options']['systemMessage'] = agent_prompt

# ----------------------------------------------------
# 5. Integrate Nodes and Rewire Connections
# ----------------------------------------------------
sprint3_nodes = [
    if_csat_node,
    csat_insert_pg_node,
    csat_timeline_crm_node,
    csat_send_chat_node,
    csat_update_pg_node,
    tool_diag_node
]

existing_names = {n['name'] for n in nodes}
for sn in sprint3_nodes:
    if sn['name'] not in existing_names:
        nodes.append(sn)

# Wire PostRes_06_If_Carona FALSE (Branch 1) -> PostRes_07_If_CSAT
connections['PostRes_06_If_Carona']['main'][1] = [{'node': 'PostRes_07_If_CSAT', 'type': 'main', 'index': 0}]

# Wire PostRes_07_If_CSAT:
# Branch 0 (TRUE): CSAT Chain -> PostRes_CSAT_Insert_Postgres -> PostRes_CSAT_Timeline_CRM -> PostRes_CSAT_Send_Chat -> PostRes_CSAT_Update_Postgres
# Branch 1 (FALSE): Thanks Chain -> PostRes_Thanks_Send_Chat, PostRes_Thanks_Update_Postgres
connections['PostRes_07_If_CSAT'] = {
    'main': [
        [{'node': 'PostRes_CSAT_Insert_Postgres', 'type': 'main', 'index': 0}],
        [
            {'node': 'PostRes_Thanks_Send_Chat', 'type': 'main', 'index': 0},
            {'node': 'PostRes_Thanks_Update_Postgres', 'type': 'main', 'index': 0}
        ]
    ]
}
connections['PostRes_CSAT_Insert_Postgres'] = {'main': [[{'node': 'PostRes_CSAT_Timeline_CRM', 'type': 'main', 'index': 0}]]}
connections['PostRes_CSAT_Timeline_CRM'] = {'main': [[{'node': 'PostRes_CSAT_Send_Chat', 'type': 'main', 'index': 0}]]}
connections['PostRes_CSAT_Send_Chat'] = {'main': [[{'node': 'PostRes_CSAT_Update_Postgres', 'type': 'main', 'index': 0}]]}

# Wire Tool_Diagnostico_TI to Agent ai_tool
connections['Tool_Diagnostico_TI'] = {
    'ai_tool': [
        [
            {
                'node': '08_AI_Agent_Triage_Deal',
                'type': 'ai_tool',
                'index': 0
            }
        ]
    ]
}

wf['nodes'] = nodes
wf['connections'] = connections

with open(wf_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print(f"Workflow updated with Sprint 3 features! Total nodes: {len(nodes)}")
