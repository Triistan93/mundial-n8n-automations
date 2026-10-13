# -*- coding: utf-8 -*-
"""
Script para migrar nós function para code e liberar o Piloto do Bot de Tickets (Categoria 160)
para os novos usuários de teste:
- ID 7: Élton Caetano (bi@mundialhonda.com.br)
- ID 352678: Igor Bonini (auxiliarti@mundialhonda.com.br)
Além de manter o gestor Eduardo Alaminos (ID 32598).
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

converted_count = 0

for node in nodes:
    # 1. Converter nós depreciados 'n8n-nodes-base.function' para 'n8n-nodes-base.code'
    if node.get('type') == 'n8n-nodes-base.function':
        code = node.get('parameters', {}).get('functionCode') or node.get('parameters', {}).get('jsCode', '')
        node['type'] = 'n8n-nodes-base.code'
        node['typeVersion'] = 2
        node['parameters'] = {
            'jsCode': code
        }
        converted_count += 1

    # 2. Aplicar as alterações dos novos usuários do piloto
    name = node.get('name')
    if name == '01_Strict_Gate_Cat160_Pilot':
        code = node['parameters']['jsCode']
        new_decl = '''// Piloto expandido: Eduardo Alaminos (32598), Élton Caetano (7) e Igor Bonini (352678)
const ALLOWED_REQUESTERS = [32598, 7, 352678];

const USER_NAMES = {
  32598: 'Eduardo Alaminos',
  7: 'Élton Caetano',
  352678: 'Igor Bonini'
};'''
        if 'const ALLOWED_REQUESTERS = [32598];' in code:
            code = code.replace('const ALLOWED_REQUESTERS = [32598]; // Piloto restrito Eduardo Alaminos', new_decl)
            code = code.replace('const ALLOWED_REQUESTERS = [32598];', new_decl)
        code = code.replace("requester_name: 'Eduardo Alaminos',", "requester_name: USER_NAMES[requesterId] || 'Colaborador',")
        node['parameters']['jsCode'] = code
        print("-> Regra atualizada em 01_Strict_Gate_Cat160_Pilot")

    elif name == '07_Prepare_AI_Deal_Input':
        code = node['parameters']['jsCode']
        if 'requester_name' not in code:
            code = code.replace(
                "requester_user_id: item.json.requester_user_id,",
                "requester_user_id: item.json.requester_user_id,\n    requester_name: item.json.requester_name || 'Colaborador',"
            )
            node['parameters']['jsCode'] = code
            print("-> Regra atualizada em 07_Prepare_AI_Deal_Input")

    elif name == '09_Format_AI_Response':
        code = node['parameters']['jsCode']
        if 'requester_name' not in code:
            code = code.replace(
                "requester_user_id: prevData.requester_user_id,",
                "requester_user_id: prevData.requester_user_id,\n      requester_name: prevData.requester_name || 'Colaborador',"
            )
            node['parameters']['jsCode'] = code
            print("-> Regra atualizada em 09_Format_AI_Response")

    elif name == '11_B01_Priority_And_Payload':
        code = node['parameters']['jsCode']
        if '(Eduardo Alaminos)' in code:
            code = code.replace('(Eduardo Alaminos)', '(${item.json.requester_name || "Colaborador"})')
            node['parameters']['jsCode'] = code
            print("-> Regra atualizada em 11_B01_Priority_And_Payload")

    elif name == 'PostRes_02_Prepare_Prompt':
        code = node['parameters']['jsCode']
        if "prev.requester_name || 'colaborador'" in code:
            code = code.replace(
                "requester_name: prev.requester_name || 'colaborador',",
                "requester_name: prev.requester_name || ({32598: 'Eduardo Alaminos', 7: 'Élton Caetano', 352678: 'Igor Bonini'}[Number(deal.CREATED_BY_ID)] || 'Colaborador'),"
            )
            node['parameters']['jsCode'] = code
            print("-> Regra atualizada em PostRes_02_Prepare_Prompt")

print(f"\nTotal de nós function migrados para code: {converted_count}")

# 2. Salvar arquivos locais
print("\n2. Salvando cópias locais...")
with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
with open('workflows/canonical/BITRIX_TI_AI_TRIAGE_AGENT.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
print("Arquivos salvos em workflows/ e workflows/canonical/.")

# 3. Deploy via API do n8n (PUT)
print("\n3. Enviando workflow atualizado para o n8n...")
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

# 4. Ciclo de Deactivate / Activate para reload limpo dos agendamentos
print("\n4. Reiniciando workflow (Deactivate -> Activate)...")
requests.post(f"{N8N_URL}/deactivate", headers=HEADERS)
act_res = requests.post(f"{N8N_URL}/activate", headers=HEADERS)
if act_res.status_code == 200:
    print("Workflow reativado com sucesso! Schedulers e Webhooks recarregados.")
else:
    print(f"Erro ao reativar: {act_res.status_code} - {act_res.text}")

print("\nDeploy do piloto com Élton Caetano (7) e Igor Bonini (352678) concluído com sucesso!")
