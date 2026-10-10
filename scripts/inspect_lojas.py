# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'
r = requests.get(webhook + 'crm.deal.userfield.get', params={'id': 213})
uf = r.json().get('result', {})
print('Field Name:', uf.get('FIELD_NAME'))
for item in uf.get('LIST', []):
    print(f"ID: {item.get('ID')} | Name: {item.get('VALUE')}")
