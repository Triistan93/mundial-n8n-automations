# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.get?id=1396550'
ctx = ssl.create_default_context()
req = urllib.request.Request(url)
with urllib.request.urlopen(req, context=ctx) as resp:
    data = json.loads(resp.read().decode('utf-8'))

res = data.get('result', {})
print("Deal 1396550:")
print("TITLE:", res.get("TITLE"))
print("COMMENTS:", repr(res.get("COMMENTS")))
print("UF_CRM_1729774515200:", repr(res.get("UF_CRM_1729774515200")))
