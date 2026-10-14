# -*- coding: utf-8 -*-
"""
Script de Atualização da Base de Conhecimento e Prompt Cognitivo da Sophia AI
com base nas 4 diretrizes oficiais validadas pelo gestor de TI:
1. ATPV-e / RENAVE: Verificação de Venda Final vs Transferência entre Lojas + Chassi + Print do Erro + Link da rotina MicroWork.
2. Reset de Senhas: L1 Autoatendimento para Bitrix, Cloud e Fandi via "Esqueci minha senha" no e-mail; L2 manual para IHS e Rede.
3. WhatsApp / Fale Fácil: Número corporativo + Print do erro OU Link de cliente/card de exemplo no Bitrix24.
4. Onboarding / Liberação de Acessos: Checklist com Função, Telefonia e Fila, WhatsApp Loja vs Individual, e Equipamentos no setor.
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
N8N_HEADERS = {
    'X-N8N-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

print("1. Baixando workflow c0F2GUMFm2BI94UG...")
r = requests.get(N8N_URL, headers=N8N_HEADERS)
if r.status_code != 200:
    print(f"Erro ao buscar workflow: {r.status_code} - {r.text}")
    sys.exit(1)

wf = r.json()
nodes = wf.get('nodes', [])

updated = False

NEW_RENAVE_SECTION = '''3. RENAVE & ATPV-E / TRANSFERÊNCIAS (KB-013):
   - VERIFICAÇÃO L1 OBRIGATÓRIA (CRUCIAL):
     * Pergunte/identifique se a solicitação é uma VENDA PARA CLIENTE FINAL ou uma TRANSFERÊNCIA ENTRE LOJAS INTERNAS.
     * Se for TRANSFERÊNCIA ENTRE LOJAS INTERNAS: Explique com gentileza que a TI não emite ATPV para transferências entre concessionárias da rede Mundial. Oriente a procurar o setor responsável por transferências de estoque.
     * Se for VENDA PARA CLIENTE FINAL (Exige emissão de ATPV pela TI):
       1. Coletar o Chassi completo de 17 dígitos (obrigatoriamente iniciado por 9C2...);
       2. Solicitar o print ou mensagem do erro exibido na tela do sistema ao tentar gerar a intenção.
       3. Registrar no resumo para o técnico o atalho direto da rotina no MicroWork:
          "Rotina: Renave - MicroWork CLOUD DMS (https://microworkcloud.com.br/cloud/#/veiculo/estoque/renave) -> Filtrar por Chassi -> Período: PERÍODO -> Desmarcar NOVO -> Selecionar Filial -> Busca".
   - TRATAMENTO DE IMPASSE: Se o colaborador informar apenas o Chassi e declarar que não sabe gerar o pedido ou pedir expressamente que a TI gere a intenção, aceite o Chassi, peça o print e conclua (COMPLETE).'''

NEW_SENHAS_SECTION = '''8. ACESSOS, SENHAS & CONTAS (KB-005):
   - Regra de segurança: NUNCA solicite nem aceite senhas no chat. O assistente nunca emite senhas em texto.
   - FLUXO DE AUTOATENDIMENTO L1 (RESOLUÇÃO DIRETA PELO USUÁRIO):
     * Bitrix24, MicroWork Cloud e Plataforma Fandi possuem a opção "Esqueci minha senha" na tela inicial de login, que dispara o e-mail de redefinição diretamente para o e-mail corporativo do colaborador.
     * Antes de abrir chamado para a TI, oriente: "Antes de acionarmos a equipe de suporte, você pode utilizar a opção 'Esqueci minha senha' na tela de login do [Bitrix/Cloud/Fandi]. O link de redefinição é enviado imediatamente para o seu e-mail corporativo. Você já chegou a testar essa opção?"
     * Se o colaborador relatar que não tem acesso ao e-mail corporativo ou que a conta está bloqueada por excesso de tentativas, conclua a triagem e encaminhe para a TI.
   - SISTEMAS COM RESET MANUAL OBRIGATÓRIO PELA TI (L2):
     * IHS Motocicleta (Portal Honda), Windows / Rede Corporativa, VPN: Dependem de reset manual pelo suporte técnico. Colete o login/e-mail e a filial.'''

NEW_WHATSAPP_SECTION = '''10. WHATSAPP CORPORATIVO, CONTACT CENTER & PLATAFORMA FALE FÁCIL (KB-015):
   - Sintomas: 'mensagens não chegam', 'meu WhatsApp não espelha', 'erro Fale Fácil', 'precisa de QR Code', 'tudo vermelho', 'I.A parou', 'número DOC não envia mensagem'.
   - REGRA DE OURO / ESCOPO DO BOT: O colaborador NÃO tem acesso à plataforma Fale Fácil e não deve ser orientado a mexer nela nem tentar gerar QR Code! O papel do bot é EXCLUSIVAMENTE COLHER E CONFIRMAR INFORMAÇÕES para a TI:
     1. Linha e Conexão: Coletar qual o número corporativo com DDD (ex: 19 9xxxx-xxxx ou 19 3120-0044), loja e consultor.
     2. Diagnóstico: Identificar se o problema é para enviar mensagens, receber mensagens ou se parou tudo.
     3. Evidências Obrigatórias (Exigir da pessoa):
        * Solicitar o print da tela de erro (lido via OCR Vision);
        * OU, se o colaborador disser que a mensagem não chega para o cliente, solicitar o LINK DE UM CLIENTE/CARD DE EXEMPLO no Bitrix24 para que a TI possa acompanhar os logs técnicos.
     4. Checagem Guiada no Celular do Colaborador: Pedir para o colaborador olhar no WhatsApp do aparelho físico em: 'Configurações (ou Ajustes) > Dispositivos conectados' e informar se a conexão aparece como CONECTADA ou DESCONECTADA.
     5. Conclusão Imediata: Com esses dados confirmados, conclua a triagem IMEDIATAMENTE (action COMPLETE) com uma mensagem calorosa, registrando tudo no resumo para que a equipe de TI atue no painel da Fale Fácil (resetar instância, gerar novo QR Code para o colaborador escanear ou acionar o suporte da Fale Fácil)!'''

NEW_ONBOARDING_SECTION = '''11. ONBOARDING & LIBERAÇÃO DE ACESSOS PARA NOVOS COLABORADORES (KB-016):
   - Aplicável quando gerentes de loja (Celeste, Silvana, Anderson, Andréia) ou supervisoras (Paula Brenda, Karina Volsi) solicitam criação ou liberação de acessos para novo consultor/colaborador.
   - CHECKLIST OBRIGATÓRIO QUE O BOT DEVE EXTRAIR DO GESTOR:
     1. Função / Cargo: Qual a função exata do novo colaborador na loja?
     2. Telefonia & Fila: Quer que ative a telefonia corporativa (ramal / Fale Fácil)? Se sim, qual a FILA DE ATENDIMENTO onde ele deve ser inserido?
     3. WhatsApp: O colaborador utilizará o WhatsApp oficial da loja ou terá canal individual?
     4. Equipamentos (Hardware): Já foi solicitada a máquina/notebook, monitor e headset, ou o setor já possui os equipamentos disponíveis?
   - Conclua a triagem (action COMPLETE) com todos os 4 itens estruturados no resumo do chamado.'''

for node in nodes:
    if node.get('name') == '08_AI_Agent_Triage_Deal':
        sp = node.get('parameters', {}).get('options', {}).get('systemMessage', '')
        
        # 1. Substituir RENAVE
        old_renave_start = "3. RENAVE & ATPV-E / TRANSFERÊNCIAS (KB-013):"
        old_renave_end = "4. COMPUTADOR, MONITOR & HARDWARE (KB-004, KB-007):"
        if old_renave_start in sp and old_renave_end in sp:
            idx1 = sp.find(old_renave_start)
            idx2 = sp.find(old_renave_end)
            sp = sp[:idx1] + NEW_RENAVE_SECTION + "\n\n" + sp[idx2:]
            print("-> Seção RENAVE & ATPV atualizada no System Prompt.")

        # 2. Substituir SENHAS
        old_senhas_start = "8. ACESSOS, SENHAS & CONTAS (KB-005):"
        old_senhas_end = "9. E-MAIL CORPORATIVO & OUTLOOK (KB-008):"
        if old_senhas_start in sp and old_senhas_end in sp:
            idx1 = sp.find(old_senhas_start)
            idx2 = sp.find(old_senhas_end)
            sp = sp[:idx1] + NEW_SENHAS_SECTION + "\n\n" + sp[idx2:]
            print("-> Seção SENHAS & AUTOATENDIMENTO atualizada no System Prompt.")

        # 3. Substituir WHATSAPP
        old_wpp_start = "10. WHATSAPP CORPORATIVO, CONTACT CENTER & PLATAFORMA FALE FÁCIL (KB-015):"
        old_wpp_end = "# DETECTOR DE RISCO COMERCIAL & SENTIMENTO CRÍTICO:"
        if old_wpp_start in sp and old_wpp_end in sp:
            idx1 = sp.find(old_wpp_start)
            idx2 = sp.find(old_wpp_end)
            sp = sp[:idx1] + NEW_WHATSAPP_SECTION + "\n\n" + NEW_ONBOARDING_SECTION + "\n\n" + sp[idx2:]
            print("-> Seção WHATSAPP & ONBOARDING atualizada no System Prompt.")

        node['parameters']['options']['systemMessage'] = sp
        updated = True

if updated:
    payload = {
        'name': wf.get('name'),
        'nodes': nodes,
        'connections': wf.get('connections'),
        'settings': wf.get('settings', {})
    }
    r_put = requests.put(N8N_URL, json=payload, headers=N8N_HEADERS)
    if r_put.status_code == 200:
        print("\n[SUCESSO] Workflow c0F2GUMFm2BI94UG atualizado com a Base de Conhecimento refinada!")
    else:
        print(f"\n[ERRO] Falha ao atualizar workflow: {r_put.status_code} - {r_put.text}")
else:
    print("\nNenhuma alteração foi necessária ou nós não encontrados.")
