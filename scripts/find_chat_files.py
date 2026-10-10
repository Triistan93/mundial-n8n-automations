# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'

# Let's search deals from C160 that have files or comments
r = requests.get(webhook + 'crm.deal.list', params={
    'filter[CATEGORY_ID]': 160,
    'select[]': ['ID', 'TITLE', 'STAGE_ID'],
    'order[ID]': 'DESC',
    'start': 0
})

deals = r.json().get('result', [])
print(f"Total deals found: {len(deals)}")

found_files = []
for d in deals[:15]:
    did = d['ID']
    # Check if there is an IM chat for this deal
    # Usually dialog_id is chat... but let's check im.chat.get by ENTITY_ID
    # Or let's check im.dialog.messages.get for known chats
    pass
