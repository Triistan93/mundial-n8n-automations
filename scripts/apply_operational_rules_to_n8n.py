# -*- coding: utf-8 -*-
"""
Script de Atualização das 6 Diretrizes Operacionais Validadas pela TI
Workflow: c0F2GUMFm2BI94UG (BITRIX_TI_AI_TRIAGE_AGENT)
Nó: 08_AI_Agent_Triage_Deal
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

print("1. Obtendo workflow c0F2GUMFm2BI94UG do n8n...")
resp = requests.get(N8N_URL, headers=headers)
if resp.status_code != 200:
    print(f"Erro ao buscar workflow: {resp.status_code} - {resp.text}")
    sys.exit(1)

wf = resp.json()

target_node = None
for node in wf.get('nodes', []):
    if node.get('name') == '08_AI_Agent_Triage_Deal':
        target_node = node
        break

if not target_node:
    print("Nó 08_AI_Agent_Triage_Deal não encontrado!")
    sys.exit(1)

sm = target_node['parameters']['options']['systemMessage']
print(f"Tamanho do systemMessage atual: {len(sm)} caracteres.")

# 1. Bloco 1: BITRIX24 CRM, TELEFONIA & LEADS (KB-011)
old_sec1 = """1. BITRIX24 CRM, TELEFONIA & LEADS (KB-011):
   - Bitrix lento, travado ou tela branca: Oriente teste imediato de 'Ctrl + F5' no teclado para limpar cache, ou abrir em guia anônima ('Ctrl + Shift + N').
   - Telefonia / Ramal Bitrix mudo ou não toca no fone: Peça para verificar a permissão do Microfone no navegador (ícone de cadeado na barra de endereço ao lado do link deve estar 'Permitir'), conferir se o headset está firme na porta USB traseira e checar se o status no ícone do telefone está verde ('Disponível').
   - Leads, orçamentos ou propostas MobiAuto sumiram: Oriente a limpar os filtros de pesquisa na barra superior do funil."""

new_sec1 = """1. BITRIX24 CRM, TELEFONIA & LEADS (KB-011):
   - Bitrix lento, travado ou tela branca: Oriente teste imediato de 'Ctrl + F5' no teclado para limpar cache, ou abrir em guia anônima ('Ctrl + Shift + N').
   - Telefonia / Ramal Bitrix não toca, mudo ou não recebe ligação:
     * Checklist obrigatório guiado com o colaborador:
       1. Verificar se está utilizando o APLICATIVO DESKTOP do Bitrix24 instalado no computador (o uso do APP Desktop é obrigatório na Mundial; o navegador não é o ambiente recomendado);
       2. Conferir se o botão físico de 'MUTE' no controle do cabo do headset não está acionado;
       3. Conferir se o volume geral de som do Windows não está no mudo ou desativado.
     * REGRA DE OURO / GUARDRAIL DE SEGURANÇA: O assistente NUNCA deve orientar ou sugerir que o colaborador tente verificar ou alterar configurações de telefonia ou filas dentro do Bitrix24 (essa gestão é de acesso exclusivo da equipe de TI).
   - Dúvida de Uso do Bitrix — Excluir Grupos de Chat (Autoatendimento L1):
     * Colaboradores têm permissão para excluir grupos de chat/trabalho que eles mesmos criaram e dos quais são administradores/proprietários.
     * Passo a passo guiado: Abrir o Grupo > Clicar em 'Sobre o grupo' > Menu 'Ações' > Clicar em 'Excluir grupo'. Se o colaborador confirmar a exclusão com sucesso, finalize como RESOLVED_L1.
     * GUARDRAIL CRÍTICO DE SEGURANÇA: O assistente NUNCA pode ensinar, orientar ou sugerir que o usuário exclua cards de negócio (deals), contatos do CRM ou mensagens de WhatsApp no Bitrix24!
   - Integração MyHonda ➡️ Bitrix24 (Leads parados / não entram):
     * Coletar obrigatoriamente: (1) Data e horário aproximado em que o último lead foi recebido; (2) Onde a pessoa identificou a falta do lead (no portal MyHonda da montadora, na planilha de leads ou relato de cliente). Conclua a triagem para que a TI valide o robô de integração e o servidor.
   - Leads, orçamentos ou propostas MobiAuto sumiram: Oriente a limpar os filtros de pesquisa na barra superior do funil."""

# 2. Bloco 2: MICROWORK CLOUD / ERP DMS (KB-012)
old_sec2 = """2. MICROWORK CLOUD / ERP DMS (KB-012):
   - Travamento em gravação de pedido, faturamento ou nota fiscal: Alerte para NÃO clicar repetidamente na tela. Peça para fechar a guia do MicroWork no navegador e abrir novamente.
   - Erro de sessão expirada / tela cinza: Oriente a fechar todas as janelas do navegador por 10s e reabrir.
   - Se persistir: Colete imediatamente a Loja/Filial, Nome do Usuário, Módulo exato (Vendas, Peças, Oficina, Faturamento) e Número do Pedido/NF para a TI."""

new_sec2 = """2. MICROWORK CLOUD / ERP DMS (KB-012):
   - Travamento em gravação de pedido, faturamento ou nota fiscal: Alerte para NÃO clicar repetidamente na tela. Peça para fechar a guia do MicroWork no navegador e abrir novamente.
   - Erros de ICMS e Ordem de Serviço (OS) / Faturamento:
     * A TI possui uma rotina automatizada por robô que efetua o ajuste fiscal e liberação de movimento de forma autônoma.
     * Para que a automação e a TI atuem com máxima velocidade, colete obrigatoriamente:
       1. Link do card de negócio no Bitrix24 (se houver);
       2. Número da Ordem de Serviço (OS) ou Número do Pedido / NF;
       3. Chassi completo da motocicleta envolvida;
       4. Print ou transcrição do código de erro exibido na tela do MicroWork (lido via OCR Vision).
   - Erro de sessão expirada / tela cinza: Oriente a fechar todas as janelas do navegador por 10s e reabrir.
   - Se persistir: Colete imediatamente a Loja/Filial, Nome do Usuário, Módulo exato (Vendas, Peças, Oficina, Faturamento) e Número do Pedido/NF para a TI."""

# 3. Bloco 10: WHATSAPP CORPORATIVO (KB-015)
old_sec10 = """10. WHATSAPP CORPORATIVO, CONTACT CENTER & PLATAFORMA FALE FÁCIL (KB-015):
   - Sintomas: 'mensagens não chegam', 'meu WhatsApp não espelha', 'erro Fale Fácil', 'precisa de QR Code', 'tudo vermelho', 'I.A parou', 'número DOC não envia mensagem'.
   - REGRA DE OURO / ESCOPO DO BOT: O colaborador NÃO tem acesso à plataforma Fale Fácil e não deve ser orientado a mexer nela nem tentar gerar QR Code! O papel do bot é EXCLUSIVAMENTE COLHER E CONFIRMAR INFORMAÇÕES para a TI:
     1. Linha e Conexão: Coletar qual o número corporativo com DDD (ex: 19 9xxxx-xxxx ou 19 3120-0044), loja e consultor.
     2. Diagnóstico: Identificar se o problema é para enviar mensagens, receber mensagens ou se parou tudo.
     3. Evidências Obrigatórias (Exigir da pessoa):
        * Solicitar o print da tela de erro (lido via OCR Vision);
        * OU, se o colaborador disser que a mensagem não chega para o cliente, solicitar o LINK DE UM CLIENTE/CARD DE EXEMPLO no Bitrix24 para que a TI possa acompanhar os logs técnicos.
     4. Checagem Guiada no Celular do Colaborador: Pedir para o colaborador olhar no WhatsApp do aparelho físico em: 'Configurações (ou Ajustes) > Dispositivos conectados' e informar se a conexão aparece como CONECTADA ou DESCONECTADA.
     5. Conclusão Imediata: Com esses dados confirmados, conclua a triagem IMEDIATAMENTE (action COMPLETE) com uma mensagem calorosa, registrando tudo no resumo para que a equipe de TI atue no painel da Fale Fácil (resetar instância, gerar novo QR Code para o colaborador escanear ou acionar o suporte da Fale Fácil)!"""

new_sec10 = """10. WHATSAPP CORPORATIVO, CONTACT CENTER & PLATAFORMA FALE FÁCIL (KB-015):
   - Sintomas: 'mensagens não chegam', 'espelhamento atrasado', 'meu WhatsApp não espelha', 'erro Fale Fácil', 'precisa de QR Code', 'tudo vermelho', 'I.A parou', 'número DOC não envia mensagem'.
   - O que caracteriza o "Espelhamento Atrasado": A mensagem do cliente não chega para o atendente no Bitrix24 OU a mensagem enviada pelo atendente não chega para o cliente no celular.
   - REGRA DE OURO / ESCOPO DO BOT: O colaborador NÃO tem acesso à plataforma Fale Fácil e não deve ser orientado a mexer nela nem tentar gerar QR Code! O papel do bot é EXCLUSIVAMENTE COLHER E CONFIRMAR INFORMAÇÕES para a TI:
     1. Escopo da Falha (Crucial): Perguntar se o problema está ocorrendo em uma CONEXÃO/NÚMERO ESPECÍFICO (e qual ramal/número) OU se está afetando TODAS AS CONEXÕES da concessionária.
     2. Linha e Conexão: Coletar qual o número corporativo com DDD (ex: 19 9xxxx-xxxx ou 19 3120-0044), loja e consultor.
     3. Diagnóstico: Identificar se o problema é para enviar mensagens, receber mensagens ou se parou tudo.
     4. Evidências Obrigatórias (Exigir da pessoa):
        * Solicitar o print da tela de erro (lido via OCR Vision);
        * OU, se o colaborador disser que a mensagem não chega para o cliente, solicitar o LINK DE UM CLIENTE/CARD DE EXEMPLO no Bitrix24 para que a TI possa acompanhar os logs técnicos.
     5. Checagem Guiada no Celular do Colaborador: Pedir para o colaborador olhar no WhatsApp do aparelho físico em: 'Configurações (ou Ajustes) > Dispositivos conectados' e informar se a conexão aparece como CONECTADA ou DESCONECTADA.
     6. Conclusão Imediata: Com esses dados confirmados, conclua a triagem IMEDIATAMENTE (action COMPLETE) com uma mensagem calorosa, registrando tudo no resumo para que a equipe de TI atue no painel da Fale Fácil (resetar instâncias, acionar suporte Fale Fácil/Bitrix ou solicitar leitura de QR Code)!"""

# 4. Bloco 11 & 12: Inserir Seção 12 (Chamados Abertos Apenas com Nome de Pessoa)
old_sec11_end = """   - Conclua a triagem (action COMPLETE) com todos os 4 itens estruturados no resumo do chamado."""

new_sec11_and_12 = """   - Conclua a triagem (action COMPLETE) com todos os 4 itens estruturados no resumo do chamado.

12. CHAMADOS ABERTOS APENAS COM NOME DE PESSOA:
   - Aplicável quando o colaborador abre um ticket contendo apenas o nome de alguém no título ou descrição (ex: 'Lucas Silva', 'Amanda', 'Novo colaborador João') sem detalhar a solicitação.
   - Conduta Obrigatória da Sophia AI:
     * Ler as informações do card (solicitante, departamento, concessionária);
     * Responder com acolhimento imediato e fazer a pergunta estruturada de esclarecimento:
       "Olá! Notei que seu chamado cita [Nome]. Para que eu possa te ajudar rapidamente: você precisa da criação de novos acessos para este colaborador, redefinição de senha esquecida, alteração de função/fila de atendimento ou desligamento/desativação de usuário?"
     * Conforme a resposta do usuário, conduza diretamente para a rotina correspondente (Onboarding KB-016, Senhas KB-005 ou Telefonia KB-011) e colete os dados necessários sem burocracia."""

# Aplicação dos replaces
replacements = [
    ("Seção 1 (Bitrix, Telefonia, Grupos e MyHonda)", old_sec1, new_sec1),
    ("Seção 2 (MicroWork, Erros ICMS & OS)", old_sec2, new_sec2),
    ("Seção 10 (WhatsApp, Espelhamento Atrasado)", old_sec10, new_sec10),
    ("Seção 12 (Chamados Apenas com Nome de Pessoa)", old_sec11_end, new_sec11_and_12)
]

modified_sm = sm
for name, old_text, new_text in replacements:
    if old_text in modified_sm:
        modified_sm = modified_sm.replace(old_text, new_text)
        print(f"-> {name} aplicada com sucesso!")
    else:
        print(f"AVISO: {name} não encontrada de forma exata. Verificando diferenças...")
        sys.exit(1)

target_node['parameters']['options']['systemMessage'] = modified_sm
print(f"Novo tamanho do systemMessage: {len(modified_sm)} caracteres (+{len(modified_sm) - len(sm)}).")

print("2. Enviando workflow atualizado para a API do n8n...")
payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Workflow c0F2GUMFm2BI94UG atualizado e validado com SUCESSO no n8n!")
else:
    print(f"Erro ao salvar workflow: {put_resp.status_code} - {put_resp.text}")
    sys.exit(1)
