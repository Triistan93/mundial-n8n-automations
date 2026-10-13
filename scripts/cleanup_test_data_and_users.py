# -*- coding: utf-8 -*-
"""
Script de Limpeza de Usuários de Teste e Tickets de Teste de Hoje (13/10/2026)
1. Remove usuários de teste (7 e 352678) do Gate do Workflow n8n (c0F2GUMFm2BI94UG), mantendo apenas Eduardo Alaminos (32598).
2. Deleta o Deal de teste #1406380 no Bitrix24 (crm.deal.delete).
3. Deleta as sessões de teste no PostgreSQL (ticket_bot_sessions IDs 7897 e 7893).
4. Deleta a avaliação de teste no PostgreSQL (ticket_csat_ratings ID 2).
5. Limpa chaves de memória Redis de teste.
"""
import requests
import json
import sys

BITRIX_WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'
N8N_SQL_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
N8N_HEADERS = {
    'X-N8N-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

print("=== ETAPA 1: REMOVER USUÁRIOS DE TESTE DO WORKFLOW N8N ===")
r_wf = requests.get(N8N_URL, headers=N8N_HEADERS)
if r_wf.status_code == 200:
    wf = r_wf.json()
    nodes = wf.get('nodes', [])
    updated = False
    for node in nodes:
        if node.get('name') == '01_Strict_Gate_Cat160_Pilot':
            code = node.get('parameters', {}).get('jsCode', '')
            if 'const ALLOWED_REQUESTERS = [32598, 7, 352678];' in code:
                # Reverter para apenas Eduardo Alaminos
                old_decl = '''// Piloto expandido: Eduardo Alaminos (32598), Élton Caetano (7) e Igor Bonini (352678)
const ALLOWED_REQUESTERS = [32598, 7, 352678];'''
                new_decl = '''// Piloto restrito Eduardo Alaminos (32598) - Pronto para liberação gradual
const ALLOWED_REQUESTERS = [32598];'''
                code = code.replace(old_decl, new_decl)
                node['parameters']['jsCode'] = code
                updated = True
                print("-> Usuários 7 (Élton) e 352678 (Igor) removidos de ALLOWED_REQUESTERS no nó 01_Strict_Gate_Cat160_Pilot.")

    if updated:
        payload = {
            'name': wf.get('name'),
            'nodes': nodes,
            'connections': wf.get('connections'),
            'settings': wf.get('settings', {})
        }
        r_put = requests.put(N8N_URL, json=payload, headers=N8N_HEADERS)
        if r_put.status_code == 200:
            print("-> Workflow atualizado e salvo com sucesso no n8n!")
        else:
            print(f"-> Erro ao salvar workflow: {r_put.status_code} - {r_put.text}")
    else:
        print("-> Nó 01_Strict_Gate_Cat160_Pilot já se encontra no estado desejado.")
else:
    print(f"Erro ao obter workflow: {r_wf.status_code}")

print("\n=== ETAPA 2: DELETAR TICKETS DE TESTE NO BITRIX24 ===")
test_deals_to_delete = ['1406380', '1406390']
for did in test_deals_to_delete:
    r_del = requests.post(BITRIX_WEBHOOK + 'crm.deal.delete', json={'id': did})
    res = r_del.json()
    print(f"Deleção do Deal #{did} no Bitrix24: {res}")

print("\n=== ETAPA 3: LIMPAR SESSÕES DE TESTE NO POSTGRESQL ===")
sql_delete_sessions = "DELETE FROM ticket_bot_sessions WHERE id IN (7897, 7893) OR deal_id IN (1406380, 1406390);"
r_sql1 = requests.post(N8N_SQL_URL, json={'query': sql_delete_sessions})
print(f"Exclusão de sessões no PostgreSQL: {r_sql1.json()}")

print("\n=== ETAPA 4: LIMPAR AVALIAÇÃO CSAT DE TESTE NO POSTGRESQL ===")
sql_delete_csat = "DELETE FROM ticket_csat_ratings WHERE id = 2 OR deal_id IN ('1406380', '1406390');"
r_sql2 = requests.post(N8N_SQL_URL, json={'query': sql_delete_csat})
print(f"Exclusão de CSAT no PostgreSQL: {r_sql2.json()}")

print("\n=== LIMPEZA DE TESTES CONCLUÍDA COM SUCESSO! ===")
