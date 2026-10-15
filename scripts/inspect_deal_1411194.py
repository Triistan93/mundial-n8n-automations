# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Pega dados do Deal no Bitrix24
b24_deal_url = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.get?id=1411194'
deal_res = requests.get(b24_deal_url).json().get('result', {})
print('=== DEAL 1411194 BITRIX ===')
print('Title:', deal_res.get('TITLE'))
print('Stage:', deal_res.get('STAGE_ID'))
print('Created By:', deal_res.get('CREATED_BY_ID'))
print('Assigned By:', deal_res.get('ASSIGNED_BY_ID'))
print('Date Create:', deal_res.get('DATE_CREATE'))
print('UF_CRM_1729774515200 (Desc):', deal_res.get('UF_CRM_1729774515200'))
print('UF_CRM_1763388156 (Cat):', deal_res.get('UF_CRM_1763388156'))
print('UF_CRM_1689593052602 (Loja):', deal_res.get('UF_CRM_1689593052602'))

# 2. Pega sessão no banco
sql_url = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
r_sess = requests.post(sql_url, json={'query': 'SELECT * FROM ticket_bot_sessions WHERE deal_id = 1411194;'})
sess = r_sess.json().get('rows', [])
print('=== SESSAO NO POSTGRES ===')
print(json.dumps(sess, indent=2, ensure_ascii=False))

# 3. Pega mensagens do chat
if sess:
    dialog_id = sess[0].get('dialog_id')
    im_url = f'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/im.dialog.messages.get?DIALOG_ID={dialog_id}&LIMIT=20'
    msgs = requests.get(im_url).json().get('result', {}).get('messages', [])
    print(f'=== MENSAGENS CHAT ({dialog_id}) ===')
    for m in reversed(msgs):
        print(f"[{m.get('date')}] Autor {m.get('author_id')}: {m.get('text')}\n---")
