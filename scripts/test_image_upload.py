# -*- coding: utf-8 -*-
import requests
import json
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'
dialog_id = 'chat855770'

# 1x1 transparent PNG
png_bytes = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')
b64_content = base64.b64encode(png_bytes).decode('utf-8')

payload = {
    'dialogId': dialog_id,
    'fields': {
        'name': 'teste_print.png',
        'content': b64_content,
        'message': 'Teste de upload de imagem para validacao de Vision'
    }
}

r = requests.post(webhook + 'im.v2.File.upload', json=payload)
print('Upload status:', r.status_code, r.text)

# Now fetch messages
r2 = requests.get(webhook + 'im.dialog.messages.get', params={'DIALOG_ID': dialog_id, 'LIMIT': 5})
print('Fetch messages status:', r2.status_code)
res = r2.json().get('result', {})
print('Files:', json.dumps(res.get('files'), indent=2))
for m in res.get('messages', [])[:3]:
    print('Message:', m.get('id'), m.get('text'), 'params:', m.get('params'))
