# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url_db = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
r_db = requests.post(url_db, json={'query': "SELECT deal_id, dialog_id, internal_chat_id FROM ticket_bot_sessions WHERE dialog_id IS NOT NULL ORDER BY id DESC LIMIT 50;"})
data = r_db.json()
sessions = data.get('rows', [])

webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'

print(f"Checking {len(sessions)} sessions...")
found = False
for s in sessions:
    did = s.get('dialog_id')
    if not did:
        continue
    r = requests.get(webhook + 'im.dialog.messages.get', params={'DIALOG_ID': did, 'LIMIT': 50})
    res = r.json().get('result', {})
    files = res.get('files')
    if files:
        print(f"FOUND FILES in {did} (Deal {s.get('deal_id')}):")
        print(json.dumps(files, indent=2))
        found = True
        break

if not found:
    print("No files found in recent chats.")
