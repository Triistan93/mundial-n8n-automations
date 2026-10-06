# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
url_get = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.details.configuration.get?scope=C&extras[dealCategoryId]=160'
req_get = urllib.request.Request(url_get)
with urllib.request.urlopen(req_get, context=ctx) as resp:
    curr_conf = json.loads(resp.read().decode('utf-8'))['result']

print("Current config sections count:", len(curr_conf))
print("Current sections titles:", [s.get('title') for s in curr_conf])
