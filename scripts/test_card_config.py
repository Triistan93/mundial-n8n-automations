# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
url = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.details.configuration.get?scope=C&extras[dealCategoryId]=160'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, context=ctx) as resp:
    data = json.loads(resp.read().decode('utf-8'))

res = data.get('result', [])
print("CARD CONFIGURATION FOR CATEGORY 160 (Central de TI):")
print(json.dumps(res, indent=2, ensure_ascii=False))
