# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/crm.deal.fields'
ctx = ssl.create_default_context()
req = urllib.request.Request(url)
with urllib.request.urlopen(req, context=ctx) as resp:
    fields = json.loads(resp.read().decode('utf-8'))['result']

for f in ['UF_CRM_1735304929', 'UF_CRM_1689597532', 'UF_CRM_TI_IMPACT', 'UF_CRM_TI_URGENCY', 'UF_CRM_TI_SHORT_SUBJECT', 'UF_CRM_TI_PRIORITY', 'UF_CRM_TI_NEXT_OWNER', 'UF_CRM_TI_WAIT_REASON']:
    field_info = fields.get(f, {})
    lbl = field_info.get('formLabel') or field_info.get('listLabel') or field_info.get('title')
    print(f"{f}: label='{lbl}', type='{field_info.get('type')}'")
