# -*- coding: utf-8 -*-
import json
import sys
import requests

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
WORKFLOW_ID = '5pFwAtQWvsuhyxO0'
N8N_URL = f'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/{WORKFLOW_ID}'

homolog_file = 'c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_HOMOLOG.json'
with open(homolog_file, 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf['nodes']}

print("=================================================================")
print("    APLICANDO SPRINT 1 NO SDR HOMOLOGAÇÃO (5pFwAtQWvsuhyxO0)     ")
print("=================================================================\n")

# 1. ATUALIZAÇÃO DO PROMPT DA IA (AI Agent)
agent = nodes.get('AI Agent')
if agent:
    prompt = agent['parameters']['options']['systemMessage']
    
    # Adicionar instrução de temperatura no JSON de saída
    target_text = '"status_triagem": "Defina ESTRITAMENTE o roteamento: \'transferencia_vendas\' (Trilha 1), \'transferencia_posvendas\' (Trilha 2), \'transferencia_adm\' (Trilha 3) ou \'transferencia_outros\' (Trilha 4 e 5)",'
    replacement_text = '''"status_triagem": "Defina ESTRITAMENTE o roteamento: 'transferencia_vendas' (Trilha 1), 'transferencia_posvendas' (Trilha 2), 'transferencia_adm' (Trilha 3) ou 'transferencia_outros' (Trilha 4 e 5)",
  "temperatura_lead": "Classifique ESTRITAMENTE entre: 'QUENTE' (alta intencao de compra em ate 7 dias, tem entrada/moto de troca definida ou quer fechar negocio), 'MORNO' (pesquisando modelos, em duvida entre consorcio/financiamento ou comparando precos sem pressa) ou 'FRIO' (apenas especulando, sem condicoes financeiras imediatas ou desqualificado)",
  "justificativa_temperatura": "Frase curta explicando a razao da temperatura atribuida",
  "proxima_acao_recomendada": "Recomendacao tatica objetiva para o vendedor fechar a venda (ex: 'Ligar hoje apresentando simulacao da Bros 160 com entrada de R$ 4.000 e agendar test-ride')",'''
    
    if target_text in prompt:
        agent['parameters']['options']['systemMessage'] = prompt.replace(target_text, replacement_text)
        print("1. Prompt do AI Agent atualizado com regras de Temperatura & Próxima Ação!")
    else:
        print("AVISO: target_text não encontrado no prompt do AI Agent.")

# 2. ATUALIZAÇÃO DO NÓ Formatar Output do Agente
fmt_node = nodes.get('Formatar Output do Agente')
if fmt_node:
    code = fmt_node['parameters']['jsCode']
    # Garante que os novos campos estejam acessíveis
    old_status = 'const statusTriagem =\n    extractedData?.status_triagem ||\n    "andamento";'
    new_status = '''const statusTriagem =
    extractedData?.status_triagem ||
    "andamento";
const temperaturaLead = extractedData?.temperatura_lead || "MORNO";
const justificativaTemp = extractedData?.justificativa_temperatura || "";
const proximaAcao = extractedData?.proxima_acao_recomendada || "";'''
    
    if old_status in code:
        code = code.replace(old_status, new_status)
        # Substitui no retorno de itens
        old_ret_empty = 'status_triagem: statusTriagem'
        new_ret_empty = '''status_triagem: statusTriagem,
                temperatura_lead: temperaturaLead,
                justificativa_temperatura: justificativaTemp,
                proxima_acao_recomendada: proximaAcao'''
        code = code.replace(old_ret_empty, new_ret_empty)
        fmt_node['parameters']['jsCode'] = code
        print("2. Nó 'Formatar Output do Agente' atualizado com suporte aos campos de Feeling!")

# 3. ATUALIZAÇÃO DO NÓ 1. Preparar Dados Lead
prep_lead = nodes.get('1. Preparar Dados Lead')
if prep_lead:
    code = prep_lead['parameters']['jsCode']
    # Adicionar leitura de temperatura e destinatário 32598
    old_slice = 'const statusTriagem = $json.status_triagem || data.status_triagem || "andamento";'
    new_slice = '''const statusTriagem = $json.status_triagem || data.status_triagem || "andamento";
const temperatura = data.temperatura_lead || $json.temperatura_lead || "MORNO";
const justificativaTemp = data.justificativa_temperatura || $json.justificativa_temperatura || "";
const proximaAcao = data.proxima_acao_recomendada || $json.proxima_acao_recomendada || "";

const badgeTemperatura = {
    "QUENTE": "🔥 LEAD QUENTE (Alta Intenção de Compra)",
    "MORNO": "🟡 LEAD MORNO (Em Comparação/Pesquisa)",
    "FRIO": "❄️ LEAD FRIO (Curioso/Sem Urgência)"
}[String(temperatura).toUpperCase()] || "🟡 LEAD MORNO";

const RESPONSAVEL_HOMOLOGACAO_ID = 32598; // Eduardo Alaminos (Bitrix ID Oficial)'''
    
    if old_slice in code:
        code = code.replace(old_slice, new_slice)
        old_return = 'StatusTriagem: statusTriagem,'
        new_return = '''StatusTriagem: statusTriagem,
            Temperatura: String(temperatura).toUpperCase(),
            BadgeTemperatura: badgeTemperatura,
            JustificativaTemperatura: justificativaTemp,
            ProximaAcaoRecomendada: proximaAcao,
            ResponsavelHomologacaoId: RESPONSAVEL_HOMOLOGACAO_ID,'''
        code = code.replace(old_return, new_return)
        prep_lead['parameters']['jsCode'] = code
        print("3. Nó '1. Preparar Dados Lead' atualizado com Badge de Temperatura e Atribuição #32598!")

# 4. ATUALIZAÇÃO DO NÓ Preparar Payload de Criação (Fallback)
create_payload = nodes.get('Preparar Payload de Criação (Fallback)')
if create_payload:
    code = create_payload['parameters']['jsCode']
    
    # Injetar campos de temperatura no HTML da Timeline
    old_comment = '<b>🏍️ Novo atendimento qualificado pelo SDR IA - Mundial Motos</b><br><br>'
    new_comment = '''<b>🏍️ Novo atendimento qualificado pelo SDR IA - Mundial Motos</b><br><br>
<b>Classificação / Feeling:</b> ${dadosLead.BadgeTemperatura || "🟡 LEAD MORNO"}<br>
${dadosLead.JustificativaTemperatura ? "<b>Motivo do Score:</b> " + dadosLead.JustificativaTemperatura + "<br>" : ""}
${dadosLead.ProximaAcaoRecomendada ? "<b>🎯 Próxima Ação Recomendada:</b> <u>" + dadosLead.ProximaAcaoRecomendada + "</u><br>" : ""}
<br>'''
    if old_comment in code:
        code = code.replace(old_comment, new_comment)
    
    # Injetar ASSIGNED_BY_ID: 32598 no fields do deal
    old_fields = 'COMMENTS: comentarioTexto\n};'
    new_fields = '''COMMENTS: comentarioTexto,
    ASSIGNED_BY_ID: 32598 // Atribuição oficial ao Eduardo Alaminos (Homologação)
};'''
    if old_fields in code:
        code = code.replace(old_fields, new_fields)
    
    # Injetar Próxima Ação no Resumo do CRM
    old_resumo_push = 'resumoLinhas.push(`Resumo: ${resumo || "Não informado"}`);'
    new_resumo_push = '''if (dadosLead.BadgeTemperatura) resumoLinhas.push(`Classificação: ${dadosLead.BadgeTemperatura}`);
if (dadosLead.ProximaAcaoRecomendada) resumoLinhas.push(`Próxima Ação Recomendada: ${dadosLead.ProximaAcaoRecomendada}`);
resumoLinhas.push(`Resumo: ${resumo || "Não informado"}`);'''
    if old_resumo_push in code:
        code = code.replace(old_resumo_push, new_resumo_push)

    create_payload['parameters']['jsCode'] = code
    print("4. Nó 'Preparar Payload de Criação (Fallback)' atualizado com ASSIGNED_BY_ID #32598 e Card Briefing!")

# 5. ATUALIZAÇÃO DO NÓ Preparar Payload de Atualização1
update_payload = nodes.get('Preparar Payload de Atualização1')
if update_payload:
    code = update_payload['parameters']['jsCode']
    
    # Injetar campos de temperatura no HTML da Timeline
    old_comment_u = '<b>🏍️ Nova interação qualificada pelo SDR IA - Mundial Motos</b><br><br>'
    new_comment_u = '''<b>🏍️ Nova interação qualificada pelo SDR IA - Mundial Motos</b><br><br>
<b>Classificação / Feeling:</b> ${dadosLead.BadgeTemperatura || "🟡 LEAD MORNO"}<br>
${dadosLead.JustificativaTemperatura ? "<b>Motivo do Score:</b> " + dadosLead.JustificativaTemperatura + "<br>" : ""}
${dadosLead.ProximaAcaoRecomendada ? "<b>🎯 Próxima Ação Recomendada:</b> <u>" + dadosLead.ProximaAcaoRecomendada + "</u><br>" : ""}
<br>'''
    if old_comment_u in code:
        code = code.replace(old_comment_u, new_comment_u)
    
    # Injetar ASSIGNED_BY_ID: 32598 no fields do deal
    old_fields_u = 'SOURCE_DESCRIPTION: "WhatsApp - SDR IA Mundial Motos"\n};'
    new_fields_u = '''SOURCE_DESCRIPTION: "WhatsApp - SDR IA Mundial Motos (Homologação)",
    ASSIGNED_BY_ID: 32598 // Atribuição oficial ao Eduardo Alaminos (Homologação)
};'''
    if old_fields_u in code:
        code = code.replace(old_fields_u, new_fields_u)

    # Injetar Próxima Ação no Resumo do CRM
    if old_resumo_push in code:
        code = code.replace(old_resumo_push, new_resumo_push)

    update_payload['parameters']['jsCode'] = code
    print("5. Nó 'Preparar Payload de Atualização1' atualizado com ASSIGNED_BY_ID #32598 e Card Briefing!")

# Salvar workflow localmente
with open(homolog_file, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

# Deploy to n8n API
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}

headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}
r = requests.put(N8N_URL, json=payload, headers=headers)

if r.status_code == 200:
    print(f"\nDEPLOY SPRINT 1 REALIZADO COM SUCESSO! Workflow ID: {WORKFLOW_ID} | Status: HTTP {r.status_code}")
    r_act = requests.post(f"{N8N_URL}/activate", headers=headers)
    print(f"Workflow Ativo: HTTP {r_act.status_code}")
else:
    print(f"\nERRO NO DEPLOY: {r.status_code} - {r.text}")
    sys.exit(1)
