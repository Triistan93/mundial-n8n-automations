# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

B24 = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm'
deal_id = 1411594

im = requests.get(f'{B24}/im.chat.get', params={'ENTITY_TYPE': 'CRM', 'ENTITY_ID': f'DEAL|{deal_id}'}).json()
chat_id = im.get('result', {}).get('ID')
print(f"Deal #{deal_id} Chat ID: {chat_id}")

if chat_id:
    msgs = requests.get(f'{B24}/im.dialog.messages.get', params={'DIALOG_ID': f'chat{chat_id}'}).json()
    messages = msgs.get('result', {}).get('messages', [])
    print(f"\nTotal de mensagens no chat: {len(messages)}")
    for m in reversed(messages):
        author = m.get('author_id')
        text = m.get('text')
        date = m.get('date')
        print(f"[{date}] [User {author}]: {text}\n")
