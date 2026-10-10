# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'
r = requests.get(webhook + 'im.dialog.messages.get', params={'DIALOG_ID': 'chat855770', 'LIMIT': 20})
print("Status:", r.status_code)
res = r.json()
print("Top-level keys in result:", list(res.get('result', {}).keys()))

messages = res.get('result', {}).get('messages', [])
print(f"Messages count: {len(messages)}")
for m in messages:
    print(f"ID: {m.get('id')}, Author: {m.get('author_id')}, Text: {repr(m.get('text'))[:60]}, Params: {m.get('params')}")

files = res.get('result', {}).get('files', {})
print(f"Files in result: {files}")
