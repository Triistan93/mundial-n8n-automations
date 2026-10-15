# -*- coding: utf-8 -*-
"""
Teste da Lógica de CSAT no Encerramento de Chamados (C160:WON)
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

B24 = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm'
SQL_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'

# 1. Busca os últimos 10 deals encerrados na C160
r = requests.get(f'{B24}/crm.deal.list', params={
    'filter[CATEGORY_ID]': 160,
    'filter[STAGE_ID]': 'C160:WON',
    'order[DATE_MODIFY]': 'DESC',
    'select[]': ['ID', 'TITLE', 'STAGE_ID', 'ASSIGNED_BY_ID', 'DATE_MODIFY']
}).json()
won_deals = r.get('result', [])
print(f"Total de chamados finalizados recentes (C160:WON): {len(won_deals)}")

for deal in won_deals[:5]:
    deal_id = int(deal['ID'])
    title = deal.get('TITLE', '')
    
    # Checa se existe sessão e se CSAT já foi enviado
    q = f"""
    SELECT id, internal_chat_id, dialog_id, requester_name, collected_data_json
    FROM ticket_bot_sessions 
    WHERE deal_id = {deal_id};
    """
    res = requests.post(SQL_URL, json={'query': q}).json()
    rows = res.get('rows', [])
    if rows:
        session = rows[0]
        collected = session.get('collected_data_json') or {}
        csat_sent = collected.get('csat_sent', False)
        print(f"Deal #{deal_id}: \"{title[:40]}...\" | Sessão ID: {session['id']} | CSAT Já Enviado: {csat_sent}")
    else:
        print(f"Deal #{deal_id}: Sem registro em ticket_bot_sessions")
