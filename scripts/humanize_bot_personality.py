# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

wf = requests.get(N8N_URL, headers=headers).json()

# 1. Update 03_Create_CRM_Card_Chat com saudação humanizada, calorosa e natural
new_initial_greeting_json = """={{ (() => {
  const firstName = ($json.requester_name || 'amigo').trim().split(' ')[0];
  const title = String($json.deal_title || '').trim();
  const hasCustomTitle = title && !title.startsWith('Chamado #') && !title.startsWith('#');

  let greeting = '';
  if (hasCustomTitle) {
    greeting = 'Oi, ' + firstName + '! Tudo bem? Sou da equipe virtual de TI aqui da Mundial.\\n\\nVi que você abriu este chamado sobre: "' + title + '".\\n\\nMe conta com calma o que está acontecendo por aí? Se quiser mandar uma foto da tela ou do equipamento, fica à vontade! Vamos tentar resolver juntos.';
  } else {
    greeting = 'Oi, ' + firstName + '! Tudo bem? Sou da equipe virtual de TI aqui da Mundial.\\n\\nMe conta com calma o que está acontecendo com o seu computador ou sistema? Pode mandar uma foto da tela ou do equipamento se preferir, e vamos tentar resolver juntos!';
  }

  return JSON.stringify({
    TYPE: 'CHAT',
    TITLE: 'Triagem TI - Chamado #' + $json.deal_id + (hasCustomTitle ? ': ' + title : ''),
    ENTITY_TYPE: 'CRM',
    ENTITY_ID: 'DEAL|' + $json.deal_id,
    USERS: [Number($json.requester_user_id), 61622],
    MESSAGE: greeting
  });
})() }}"""

for n in wf.get('nodes', []):
    if n['name'] == '03_Create_CRM_Card_Chat':
        n['parameters']['jsonBody'] = new_initial_greeting_json
        print("-> 03_Create_CRM_Card_Chat atualizado com mensagem inicial humana e natural")

# 2. Update 08_AI_Agent_Triage_Deal System Prompt
# Vamos enriquecer o PAPEL, OBJETIVO e as REGRAS CRÍTICAS DE CONVERSAÇÃO com a filosofia:
# - Tom natural e descontraído de colega prestativo (anti-engessamento).
# - Modo DIY (Do It Yourself) com extremo cuidado para público leigo (cores de cabos, botões, posições físicas, zero 'tecniquês').
# - Acolhimento se o usuário não souber ou tiver receio de mexer.

new_conversational_guidelines = """
# PAPEL E PERSONALIDADE (ANTI-ENGESSAMENTO & EMPATIA MÁXIMA):
Você é o parceiro virtual da equipe de TI da Mundial Honda.
Converse de forma NATURAL, CALOROSA e AMIGÁVEL, exatamente como um colega de trabalho atencioso que está sentado do lado do colaborador pronto para ajudar.
- NUNCA fale de forma robótica, engessada ou corporativa ("Prezado usuário", "Registramos a sua solicitação sob o protocolo...", "Favor informar se afeta seu posto ou departamento").
- Use cumprimentos e expressões cotidianas naturais: "Oi!", "Opa, tudo bem?", "Tranquilo!", "Entendi perfeitamente!", "Fica tranquilo que vamos ver isso!".
- Demonstre empatia real com a dor do usuário: "Poxa, imagino como isso atrapalha seu trabalho hoje", "Vamos tentar resolver rapidinho!".

# DIRETRIZ DO MODO "DO IT YOURSELF" (AUTOATENDIMENTO COM CUIDADO PARA USUÁRIOS LEIGOS):
IMPORTANTE: A maioria dos colaboradores de concessionária (vendas, oficina, peças, faturamento, caixa) possui BAIXA FAMILIARIDADE com informática ("não sabem nem ligar o computador direito").
Portanto, sua missão no autoatendimento L1 deve seguir RIGOROSAMENTE estas regras:

1. PROIBIÇÃO TOTAL DE JARGÕES TÉCNICOS:
   - NUNCA use termos como: driver, spooler, DHCP, DNS, gateway, boot, resolução, conector RJ45, porta COM, cache do DNS, gerenciador de dispositivos, terminal.
   - SEMPRE descreva visualmente pelo que a pessoa vê na frente dela:
     * O cabo de rede: "aquele cabo azul ou cinza com a pontinha transparente que vai atrás do computador".
     * O computador (CPU): "a caixinha do computador que fica embaixo ou em cima da mesa".
     * O monitor: "a tela do computador".
     * Botão de ligar: "aquele botãozinho redondo na parte de baixo da tela com o símbolo de ligar".
     * Permissão do microfone: "o cadeadinho que fica lá em cima, no cantinho esquerdo do link da página".

2. UMA COISA DE CADA VEZ (PASSO A PASSO GUIADO):
   - NUNCA passe duas ou três instruções ao mesmo tempo. Oriente apenas UM teste simples por mensagem.
   - Exemplo: "Vamos fazer um teste bem rapidinho? Dá uma olhadinha atrás da tela pra ver se aquele cabo preto de energia está bem encaixadinho."

3. ACOLHIMENTO SE O USUÁRIO NÃO SOUBER OU TIVER MEDO DE MEXER:
   - Se o colaborador disser "não sei onde fica", "não entendo nada de computador", "tenho medo de estragar", ou se demonstrar insegurança:
   - NUNCA insista, nunca tente ensinar à força nem faça perguntas difíceis!
   - Acolha IMEDIATAMENTE com carinho e tranquilidade:
     "Fica tranquilo! Não precisa se preocupar em mexer nisso se não tiver certeza. Já vou deixar tudo anotadinho aqui pro técnico do TI vir resolver pra você, tá bom?"
   - E conclua a triagem IMEDIATAMENTE (action COMPLETE) para o técnico assumir!

4. SOLICITAÇÕES DE COMPRA OU TROCA DE EQUIPAMENTOS (MEMÓRIA, MONITOR, MOUSE, ETC.):
   - Entenda a necessidade com simpatia.
   - Faça a checagem obrigatória da Diretoria/Zélia de forma leve e descontraída:
     "Entendido! E só pra eu já deixar tudo mastigado pra diretoria aprovar rapidinho: você ou sua liderança chegaram a ver se tem algum sobrando na loja ou reserva pra você usar enquanto isso?"
   - Registre a resposta clara no resumo e conclua para aprovação!
"""

for n in wf.get('nodes', []):
    if n['name'] == '08_AI_Agent_Triage_Deal':
        sm = n.get('parameters', {}).get('options', {}).get('systemMessage', '')
        # Replace section from '# PAPEL E OBJETIVO' up to '# BASE DE CONHECIMENTO'
        p_start = sm.find('# PAPEL E OBJETIVO')
        p_end = sm.find('# BASE DE CONHECIMENTO & PLAYBOOK OPERACIONAL')
        if p_start != -1 and p_end != -1:
            # Keep previous rules like domain scope and enums prohibition
            rules_start = sm.find('# REGRAS CRÍTICAS DE CONVERSAÇÃO')
            sm_updated = sm[:p_start] + new_conversational_guidelines.strip() + "\n\n" + sm[rules_start:]
            n['parameters']['options']['systemMessage'] = sm_updated
            print("-> 08_AI_Agent_Triage_Deal prompt atualizado com tom humano e modo DIY leigo")
        else:
            print("Aviso: Marcadores do prompt não encontrados exatamente, injetando no topo")
            n['parameters']['options']['systemMessage'] = new_conversational_guidelines + "\n" + sm

# 3. Update 15_Prepare_Final_Chat com mensagens de encerramento amigáveis e acolhedoras
prepare_final_chat_code = """// Prepara payload para envio no chat final.
// Mensagens de encerramento amigáveis, sem termos burocráticos.
const b01Items = $('11_B01_Priority_And_Payload').all();
const updatePayloadItems = $('12_Prepare_Deal_Update_Payload').all();
const items = $input.all();

return items.map((item, idx) => {
  const b01 = b01Items[idx]?.json || item.json;
  const updateData = updatePayloadItems[idx]?.json || {};
  const isPurchase = Boolean(updateData.is_purchase || b01.is_purchase || updateData.target_stage_id === 'C160:UC_JIOBG8');
  const dealId = b01.deal_id;
  const firstName = (b01.formatted_title || '').includes('(')
    ? (b01.formatted_title.split('(')[1].split(')')[0].split(' ')[0] || 'amigo')
    : 'amigo';

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
    finalMessage = `🎉 Que ótimo que deu certo, ${firstName}! Fico muito feliz que conseguimos resolver por aqui rapidinho!\\n\\nO seu chamado já foi concluído com sucesso. Se precisar de mais alguma coisa, estamos sempre por aqui à disposição!`;
  } else if (isPurchase) {
    finalMessage = `Tudo certinho, ${firstName}! Já organizei todas as informações e enviei a solicitação para a avaliação da Diretoria/Gestão.\\n\\nAssim que houver um retorno ou se precisarem de mais detalhes, aviso você por aqui mesmo!`;
  } else {
    finalMessage = `Tudo certo, ${firstName}! Já anotei todos os detalhes aqui e passei para o técnico da nossa equipe de TI dar andamento no seu atendimento.\\n\\nSe você lembrar de mais algum detalhe ou quiser mandar fotos, pode enviar aqui no chat a qualquer momento!`;
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

for n in wf.get('nodes', []):
    if n['name'] == '15_Prepare_Final_Chat':
        n['parameters']['functionCode'] = prepare_final_chat_code
        print("-> 15_Prepare_Final_Chat atualizado com encerramento caloroso e acolhedor")

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
    print("✅ Workflow BITRIX_TI_AI_TRIAGE_AGENT atualizado com sucesso! Bot agora é 100% natural, acolhedor e paciente com usuários leigos.")
else:
    print("❌ Erro:", resp.text)
