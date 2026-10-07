# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

wf = requests.get(N8N_URL, headers=headers).json()

# 1. Update 15_Prepare_Final_Chat:
# O chat do ticket recebe SOMENTE a mensagem informativa SEM NENHUM BOTÃO.
# Os botões vão EXCLUSIVAMENTE para a propriedade approver_keyboard.
prepare_final_chat_code = """// Prepara payload para envio no chat final.
// REGRA DE SEGURANÇA: O chat do ticket NUNCA recebe botões de aprovação (evita que o próprio solicitante aprove sua compra).
// Os botões vão EXCLUSIVAMENTE para o chat privado do gestor/aprovador.
const b01Items = $('11_B01_Priority_And_Payload').all();
const updatePayloadItems = $('12_Prepare_Deal_Update_Payload').all();
const items = $input.all();

return items.map((item, idx) => {
  const b01 = b01Items[idx]?.json || item.json;
  const updateData = updatePayloadItems[idx]?.json || {};
  const isPurchase = Boolean(updateData.is_purchase || b01.is_purchase || updateData.target_stage_id === 'C160:UC_JIOBG8');
  const dealId = b01.deal_id;

  let finalMessage = '';

  // Teclado exclusivo para a diretoria/gestor no privado
  const approverKeyboard = [
    {
      TEXT: '✅ Autorizar Compra',
      LINK: `https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id=${dealId}&action=approve&user=32598`,
      BG_COLOR: '#29b24f',
      TEXT_COLOR: '#ffffff',
      DISPLAY: 'LINE'
    },
    {
      TEXT: '💬 Falar no Chamado',
      LINK: `https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${dealId}/`,
      BG_COLOR: '#007bff',
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

  if (b01.is_resolved_l1) {
    finalMessage = '🎉 Parabéns! Ficamos muito felizes que o teste resolveu o problema!\\n\\nSeu chamado foi registrado e finalizado como Ganho com sucesso.\\n\\nQualquer nova dúvida ou necessidade, estamos sempre à disposição por aqui!';
  } else if (isPurchase) {
    finalMessage = `📦 [b]SOLICITAÇÃO DE COMPRA DE TI[/b]\\n` +
      `Seu chamado foi classificado como Prioridade ${b01.priority_label} e encaminhado para a etapa [b]Aguardando autorização[/b].\\n\\n` +
      `A solicitação foi enviada para a Diretoria/Gestão para análise e aprovação. Assim que houver um retorno ou se precisarem de mais detalhes, você será notificado diretamente aqui!`;
  } else {
    finalMessage = `✅ Triagem concluída com sucesso!\\n\\nSeu chamado foi classificado como Prioridade ${b01.priority_label} e já está disponível para a equipe de TI.\\n\\nQualquer novo detalhe ou print pode ser enviado diretamente aqui neste chat!`;
  }

  return {
    json: {
      ...b01,
      is_purchase: isPurchase,
      target_stage_id: isPurchase ? 'C160:UC_JIOBG8' : b01.target_stage_id,
      final_message: finalMessage,
      approver_keyboard: approverKeyboard
    }
  };
});"""

# 2. Update 15_Send_Final_Confirmation_To_Chat:
# Garante que NUNCA envia KEYBOARD para o chat do ticket
send_final_chat_json_body = """={{ JSON.stringify({
  DIALOG_ID: $json.dialog_id,
  MESSAGE: $json.final_message
}) }}"""

# 3. Update 15_Filter_Purchase_For_Approver
filter_approver_code = """// Filtra apenas compras para envio dos botões no privado do aprovador
const items = $('15_Prepare_Final_Chat').all();
const purchases = [];

for (const item of items) {
  if (item.json.is_purchase && item.json.approver_keyboard) {
    purchases.push(item);
  }
}

return purchases;"""

# 4. Update 15_Send_Direct_Approval_To_Approver:
send_direct_json_body = """={{ JSON.stringify({
  DIALOG_ID: '32598',
  MESSAGE: '📦 [b]NOVA SOLICITAÇÃO DE COMPRA PENDENTE[/b]\\nChamado #' + $json.deal_id + ': ' + $json.formatted_title + '\\n\\nStatus: Aguardando autorização\\nPrioridade: ' + $json.priority_label + '\\n\\nVocê pode aprovar diretamente, abrir o chamado para falar com o solicitante ou negar a solicitação:',
  KEYBOARD: $json.approver_keyboard
}) }}"""

# 5. Remove or bypass 03_Send_Buttons_Deal_Chat from intake so intake doesn't send buttons to deal chat either
for n in wf.get('nodes', []):
    if n['name'] == '15_Prepare_Final_Chat':
        n['parameters']['functionCode'] = prepare_final_chat_code
        print("-> 15_Prepare_Final_Chat atualizado (sem botões para o chat do ticket)")
    elif n['name'] == '15_Send_Final_Confirmation_To_Chat':
        n['parameters']['jsonBody'] = send_final_chat_json_body
        print("-> 15_Send_Final_Confirmation_To_Chat garantido sem KEYBOARD")
    elif n['name'] == '15_Filter_Purchase_For_Approver':
        n['parameters']['functionCode'] = filter_approver_code
        print("-> 15_Filter_Purchase_For_Approver atualizado")
    elif n['name'] == '15_Send_Direct_Approval_To_Approver':
        n['parameters']['jsonBody'] = send_direct_json_body
        print("-> 15_Send_Direct_Approval_To_Approver configurado")
    elif n['name'] == '03_Send_Buttons_Deal_Chat':
        # Remove KEYBOARD from intake deal chat node too
        n['parameters']['jsonBody'] = """={{ JSON.stringify({
  DIALOG_ID: $json.dialog_id,
  MESSAGE: '📦 [b]SOLICITAÇÃO DE COMPRA DE TI[/b]\\nIdentifiquei a abertura de uma solicitação de compra neste chamado #' + $json.deal_id + '. O chamado foi encaminhado para avaliação da gestão.'
}) }}"""
        print("-> 03_Send_Buttons_Deal_Chat removido botões do chat do card no intake")

# Save canonical
canonical_path = r"C:\mundial-n8n-automations\workflows\canonical\BITRIX_TI_AI_TRIAGE_AGENT.json"
with open(canonical_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

# Deploy to n8n
deploy_payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}

resp = requests.put(N8N_URL, headers=headers, json=deploy_payload)
print("Deploy n8n status code:", resp.status_code)
if resp.status_code == 200:
    print("✅ Workflow BITRIX_TI_AI_TRIAGE_AGENT atualizado com sucesso! Botões agora vão EXCLUSIVAMENTE para o privado do aprovador.")
else:
    print("❌ Erro:", resp.text)
