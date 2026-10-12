# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

b24_url = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.dealcategory.stage.list.json?id=18"
r = requests.get(b24_url)
print("=== ETAPAS DA CATEGORIA 18 (Vendas Outras mídias) ===")
for st in r.json().get('result', []):
    print(f"  • ID: {st.get('STATUS_ID')} | Nome: {st.get('NAME')}")
