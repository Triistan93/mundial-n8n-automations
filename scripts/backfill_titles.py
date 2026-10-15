# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

sql_url = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
r = requests.post(sql_url, json={'query': "SELECT deal_id FROM ticket_bot_sessions WHERE status = 'ACTIVE';"})
deals = r.json().get('rows', [])
print(f"Sessões ativas para preencher título: {len(deals)}")

for d in deals:
    did = d['deal_id']
    b24_url = f"https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.get?id={did}"
    try:
        r_b24 = requests.get(b24_url).json()
        title = r_b24.get('result', {}).get('TITLE', '')
        if title:
            safe_title = title.replace("'", "''").replace('"', '\\"')
            upd_sql = f"UPDATE ticket_bot_sessions SET collected_data_json = COALESCE(collected_data_json, '{{}}'::jsonb) || '{{\"deal_title\": \"{safe_title}\"}}'::jsonb WHERE deal_id = {did};"
            requests.post(sql_url, json={'query': upd_sql})
            print(f"  Atualizado #{did}: {title}")
    except Exception as e:
        print(f"  Erro no deal #{did}: {e}")
