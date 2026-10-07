# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

wf = requests.get(N8N_URL, headers=headers).json()

# 1. Update 08_AI_Agent_Triage_Deal systemMessage
zelia_rule = """
   - Solicitação de Compra ou Troca de Hardware / Peças (Memória RAM, Notebook, Teclado, Mouse, Monitor, etc.):
     * DIRETIVA OBRIGATÓRIA DA DIRETORIA/CONTROLADORIA (ZÉLIA SILVA): Antes de concluir qualquer chamado que envolva compra ou aquisição de peças/equipamentos, você DEVE OBRIGATORIAMENTE perguntar se o colaborador já verificou no setor/loja ou com a liderança se há peças/equipamentos disponíveis para reaproveitamento ou substituição temporária.
     * Exemplo de pergunta: "Você chegou a verificar no seu setor ou com a sua liderança se há algum equipamento ou peça reserva disponível para reaproveitamento ou substituição?"
     * Registre expressamente no `resumo_problema` se há ou não equipamento para reaproveitamento no setor e o patrimônio da máquina, pois a Diretoria precisa dessas informações para autorizar a compra sem atrasos."""

for n in wf.get('nodes', []):
    if n['name'] == '08_AI_Agent_Triage_Deal':
        sm = n.get('parameters', {}).get('options', {}).get('systemMessage', '')
        # Insert after 'COMPUTADOR, MONITOR & HARDWARE' section
        needle = "- Antivírus / alerta na tela travando: Oriente a fechar no 'X'. Se impedir o trabalho, solicite o código AnyDesk para acesso remoto da TI."
        if needle in sm and "ZÉLIA SILVA" not in sm:
            n['parameters']['options']['systemMessage'] = sm.replace(needle, needle + "\n" + zelia_rule)
            print("-> Regra da Controladoria/Zélia injetada no systemMessage do AI Agent")
        elif "ZÉLIA SILVA" in sm:
            print("-> Regra da Zélia já presente no systemMessage")

# 2. Update 15_Prepare_Final_Chat to include 3 buttons: [ ✅ Autorizar Compra ] | [ 💬 Falar no Chamado ] | [ ❌ Negar ]
prepare_final_chat_code = """// Prepara payload para envio no chat final com suporte a 3 botões de compra
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
      `👉 [b]Aprovação da Gestão:[/b] Utilize os botões interativos abaixo para autorizar, falar diretamente no chamado com o solicitante ou negar a solicitação:`;

    keyboard = [
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

for n in wf.get('nodes', []):
    if n['name'] == '15_Prepare_Final_Chat':
        n['parameters']['functionCode'] = prepare_final_chat_code
        print("-> Atualizado 15_Prepare_Final_Chat com os 3 botões")

# 3. Update 15_Send_Direct_Approval_To_Approver message
for n in wf.get('nodes', []):
    if n['name'] == '15_Send_Direct_Approval_To_Approver':
        n['parameters']['jsonBody'] = """={{ JSON.stringify({
  DIALOG_ID: '32598',
  MESSAGE: '📦 [b]NOVA SOLICITAÇÃO DE COMPRA PENDENTE[/b]\\nChamado #' + $json.deal_id + ': ' + $json.formatted_title + '\\n\\nStatus: Aguardando autorização\\nPrioridade: ' + $json.priority_label + '\\n\\nVocê pode aprovar diretamente, abrir o chamado para falar com o solicitante ou negar a solicitação:',
  KEYBOARD: $json.keyboard
}) }}"""
        print("-> Atualizado 15_Send_Direct_Approval_To_Approver")

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
    print("✅ Workflow BITRIX_TI_AI_TRIAGE_AGENT atualizado com sucesso!")
    # Update local canonical
    canonical_path = r"C:\mundial-n8n-automations\workflows\canonical\BITRIX_TI_AI_TRIAGE_AGENT.json"
    with open(canonical_path, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
else:
    print("❌ Erro:", resp.text)
