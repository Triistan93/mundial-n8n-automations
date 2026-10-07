# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# 1. Fetch current workflow from n8n
r = requests.get(N8N_URL, headers=headers)
if r.status_code != 200:
    print("Erro ao buscar workflow:", r.status_code, r.text)
    sys.exit(1)

wf = r.json()
print("Workflow carregado. Total de nós:", len(wf.get("nodes", [])))

# 2. Update 11_B01_Priority_And_Payload
b01_code = """// MOTOR DETERMINÍSTICO B01 DE PRIORIDADE & SUPORTE A AUTOATENDIMENTO L1
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

  const rawImpact = (facts.impacto?.value || data.impacto || 'SINGLE_USER').toUpperCase();
  const rawUrgency = (facts.urgencia?.value || data.urgencia || 'NORMAL').toUpperCase();

  const impactObj = IMPACT_MAP[rawImpact] || IMPACT_MAP['SINGLE_USER'];
  const urgencyObj = URGENCY_MAP[rawUrgency] || URGENCY_MAP['PLANNED_REQUEST'];

  let priorityId = 1206; // P3_MEDIUM Default
  let priorityCode = 'P3_MEDIUM';
  let priorityLabel = 'P3 - Médio';

  if (isResolvedL1) {
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
      priorityId = 1206; priorityCode = 'P3_MEDIUM'; priorityLabel = 'P3 - Médio';
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

  const formattedTitle = isResolvedL1 ? `[RESOLVIDO-L1] - ${shortSubject} (Eduardo Alaminos)` : `[TI-${tema}] - ${shortSubject} (Eduardo Alaminos)`;
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
      tema: tema,
      short_subject: shortSubject,
      formatted_title: formattedTitle,
      resumo: resumo,
      next_owner_id: 1148,
      wait_reason_id: 1162
    }
  });
}

return results;"""

# 3. Update 12_Prepare_Deal_Update_Payload
prepare_deal_update_code = """// Combina dados do B01 com a descrição existente do Deal via all()
const b01Items = $('11_B01_Priority_And_Payload').all();
const items = $input.all();
const results = [];

for (let i = 0; i < items.length; i++) {
  const b01 = b01Items[i]?.json || {};
  const deal = items[i].json.result || items[i].json || {};

  // Detecção de compra enriquecida com campos do Bitrix
  const ufCategory = String(deal.UF_CRM_1763388156 || '');
  const dealTitle = String(deal.TITLE || '').toLowerCase();
  let dealDesc = '';
  if (Array.isArray(deal.UF_CRM_1729774515200)) {
    dealDesc = deal.UF_CRM_1729774515200.join(' ').toLowerCase();
  } else if (deal.UF_CRM_1729774515200) {
    dealDesc = String(deal.UF_CRM_1729774515200).toLowerCase();
  }

  const isPurchaseDeal = (
    ufCategory === '876' ||
    dealTitle.includes('compra') ||
    dealTitle.includes('comprar') ||
    dealDesc.includes('compra') ||
    dealDesc.includes('comprar') ||
    dealDesc.includes('memoria ram') ||
    dealDesc.includes('memória ram')
  );

  const finalIsPurchase = Boolean(b01.is_purchase || isPurchaseDeal);
  const finalTargetStage = b01.is_resolved_l1 ? 'C160:WON' : (finalIsPurchase ? 'C160:UC_JIOBG8' : b01.target_stage_id);

  // Resumo do robô formatado (sem emojis de 4-bytes para evitar incompatibilidade no MySQL do Bitrix)
  const milestoneSummary = b01.is_resolved_l1
    ? `[AUTOATENDIMENTO L1 RESOLVIDO]\\n---------------------------------------------\\nTema: ${b01.tema}\\nPrioridade: ${b01.priority_label}\\n\\nResumo:\\n${b01.resumo}\\n\\n(Chamado concluído automaticamente como Ganho)`
    : `[TRIAGEM IA CONCLUÍDA]\\n---------------------------------------------\\nTema: ${b01.tema}\\nImpacto: ${b01.impact_label}\\nUrgência: ${b01.urgency_label}\\nPrioridade B01: ${b01.priority_label} (${b01.priority_code})\\nEtapa: ${finalIsPurchase ? 'Aguardando autorização (Compra)' : 'Novo Chamado'}\\n\\nResumo:\\n${b01.resumo}\\n\\n(Histórico detalhado da conversa mantido no Chat do Card)`;

  // Recupera descrição existente no campo UF_CRM_1729774515200 (Descrição)
  let existingDescList = deal.UF_CRM_1729774515200;
  let existingDescArray = [];
  if (Array.isArray(existingDescList)) {
    existingDescArray = existingDescList.map(x => String(x || '').trim()).filter(Boolean);
  } else if (existingDescList) {
    existingDescArray = [String(existingDescList).trim()];
  }

  // Preserva a descrição do usuário e adiciona o resumo do robô como complemento
  const finalDescArray = [...existingDescArray, milestoneSummary];

  // Recupera campo COMMENTS (Observação)
  const existingComments = String(deal.COMMENTS || '').trim();
  const finalComments = existingComments
    ? `${existingComments}\\n\\n---------------------------------------------\\n${milestoneSummary}`
    : milestoneSummary;

  results.push({
    json: {
      ...b01,
      is_purchase: finalIsPurchase,
      target_stage_id: finalTargetStage,
      final_desc_array: finalDescArray,
      final_comments: finalComments
    }
  });
}

return results;"""

# 4. Update 15_Prepare_Final_Chat
prepare_final_chat_code = """// Prepara payload para envio no chat final com suporte a botões de compra
const b01Items = $('11_B01_Priority_And_Payload').all();
const updatePayloadItems = $('12_Prepare_Deal_Update_Payload').all();
const items = $input.all();

return items.map((item, idx) => {
  const b01 = b01Items[idx]?.json || item.json;
  const updateData = updatePayloadItems[idx]?.json || {};
  const isPurchase = Boolean(updateData.is_purchase || b01.is_purchase || updateData.target_stage_id === 'C160:UC_JIOBG8');
  const dealId = b01.deal_id;

  let finalMessage = '';
  let keyboard = null;

  if (b01.is_resolved_l1) {
    finalMessage = '🎉 Parabéns! Ficamos muito felizes que o teste resolveu o problema!\\n\\nSeu chamado foi registrado e finalizado como Ganho com sucesso.\\n\\nQualquer nova dúvida ou necessidade, estamos sempre à disposição por aqui!';
  } else if (isPurchase) {
    finalMessage = `📦 [b]SOLICITAÇÃO DE COMPRA DE TI[/b]\\n` +
      `Seu chamado foi classificado como Prioridade ${b01.priority_label} e encaminhado para [b]Aguardando autorização[/b].\\n\\n` +
      `👉 [b]Aprovação da Gestão:[/b] Por favor, utilize os botões interativos abaixo para autorizar ou negar a solicitação:`;

    keyboard = [
      {
        TEXT: '✅ Autorizar Compra',
        LINK: `https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id=${dealId}&action=approve&user=32598`,
        BG_COLOR: '#29b24f',
        TEXT_COLOR: '#ffffff',
        DISPLAY: 'LINE'
      },
      {
        TEXT: '❌ Negar',
        LINK: `https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id=${dealId}&action=reject&user=32598`,
        BG_COLOR: '#e84343',
        TEXT_COLOR: '#ffffff',
        DISPLAY: 'LINE'
      }
    ];
  } else {
    finalMessage = `✅ Triagem concluída com sucesso!\\n\\nSeu chamado foi classificado como Prioridade ${b01.priority_label} e já está disponível para a equipe de TI.\\n\\nQualquer novo detalhe ou print pode ser enviado diretamente aqui neste chat!`;
  }

  return {
    json: {
      ...b01,
      is_purchase: isPurchase,
      target_stage_id: isPurchase ? 'C160:UC_JIOBG8' : b01.target_stage_id,
      final_message: finalMessage,
      keyboard: keyboard
    }
  };
});"""

# 5. Update 15_Send_Final_Confirmation_To_Chat
send_final_chat_json_body = """={{ JSON.stringify(Object.assign({
  DIALOG_ID: $json.dialog_id,
  MESSAGE: $json.final_message
}, ($json.keyboard && $json.keyboard.length > 0) ? { KEYBOARD: $json.keyboard } : {})) }}"""

for n in wf["nodes"]:
    if n.get("name") == "11_B01_Priority_And_Payload":
        n["parameters"]["functionCode"] = b01_code
        print("-> Atualizado 11_B01_Priority_And_Payload")
    elif n.get("name") == "12_Prepare_Deal_Update_Payload":
        n["parameters"]["functionCode"] = prepare_deal_update_code
        print("-> Atualizado 12_Prepare_Deal_Update_Payload")
    elif n.get("name") == "15_Prepare_Final_Chat":
        n["parameters"]["functionCode"] = prepare_final_chat_code
        print("-> Atualizado 15_Prepare_Final_Chat")
    elif n.get("name") == "15_Send_Final_Confirmation_To_Chat":
        n["parameters"]["jsonBody"] = send_final_chat_json_body
        print("-> Atualizado 15_Send_Final_Confirmation_To_Chat")

# 6. Check and add 15_Filter_Purchase_For_Approver and 15_Send_Direct_Approval_To_Approver
existing_node_names = [n.get("name") for n in wf["nodes"]]

if "15_Filter_Purchase_For_Approver" not in existing_node_names:
    filter_node = {
        "parameters": {
            "functionCode": """// Filtra apenas compras com botões para notificação direta ao gestor
const items = $('15_Prepare_Final_Chat').all();
const purchases = [];

for (const item of items) {
  if (item.json.is_purchase && item.json.keyboard) {
    purchases.push(item);
  }
}

return purchases;"""
        },
        "id": "node_filter_purchase_approver",
        "name": "15_Filter_Purchase_For_Approver",
        "type": "n8n-nodes-base.function",
        "typeVersion": 1,
        "position": [2460, 420]
    }

    send_direct_node = {
        "parameters": {
            "method": "POST",
            "url": "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.message.add",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": """={{ JSON.stringify({
  DIALOG_ID: '32598',
  MESSAGE: '📦 [b]NOVA SOLICITAÇÃO DE COMPRA PENDENTE[/b]\\nChamado #' + $json.deal_id + ': ' + $json.formatted_title + '\\n\\nStatus: Aguardando autorização\\nPrioridade: ' + $json.priority_label + '\\n\\nClique no botão abaixo para autorizar ou negar:',
  KEYBOARD: $json.keyboard
}) }}"""
        },
        "id": "node_send_direct_approver",
        "name": "15_Send_Direct_Approval_To_Approver",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2680, 420]
    }

    wf["nodes"].extend([filter_node, send_direct_node])
    print("-> Adicionados nós 15_Filter_Purchase_For_Approver e 15_Send_Direct_Approval_To_Approver")

    # Connect from 15_Send_Final_Confirmation_To_Chat to 15_Filter_Purchase_For_Approver
    conn_list = wf["connections"].setdefault("15_Send_Final_Confirmation_To_Chat", {}).setdefault("main", [[]])
    if len(conn_list[0]) > 0:
        conn_list[0].append({"node": "15_Filter_Purchase_For_Approver", "type": "main", "index": 0})
    else:
        conn_list[0] = [{"node": "16_Prepare_Complete_Session", "type": "main", "index": 0}, {"node": "15_Filter_Purchase_For_Approver", "type": "main", "index": 0}]

    wf["connections"]["15_Filter_Purchase_For_Approver"] = {
        "main": [[{"node": "15_Send_Direct_Approval_To_Approver", "type": "main", "index": 0}]]
    }
    print("-> Conexões criadas para notificação direta ao gestor")

# 7. Save backup and canonical file
canonical_path = r"C:\mundial-n8n-automations\workflows\canonical\BITRIX_TI_AI_TRIAGE_AGENT.json"
with open(canonical_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print("-> Salvo arquivo canônico atualizado")

# 8. Deploy to n8n
deploy_payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

resp = requests.put(N8N_URL, headers=headers, json=deploy_payload)
print("Deploy n8n status code:", resp.status_code)
if resp.status_code == 200:
    print("✅ Workflow BITRIX_TI_AI_TRIAGE_AGENT atualizado com sucesso no n8n!")
else:
    print("❌ Erro no deploy:", resp.text)
