# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK = "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/"
ctx = ssl.create_default_context()

def call(method, payload=None):
    url = f"{WEBHOOK}{method}"
    data = json.dumps(payload).encode('utf-8') if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode('utf-8')}

print("=== 1. VERIFICAÇÃO DE CATEGORIAS (UF_CRM_1763388156 / ID 1676) ===")
cat_uf = call("crm.deal.userfield.get", {"id": 1676}).get("result", {})
cat_list = cat_uf.get("LIST", [])
print(f"Total de categorias ativas: {len(cat_list)}")
for c in cat_list:
    print(f"  [{c.get('ID')}] (Sort: {c.get('SORT')}) {c.get('VALUE')}")

print("\n=== 2. VERIFICAÇÃO DE SUBCATEGORIAS (UF_CRM_1763388469429 / ID 1678) ===")
sub_uf = call("crm.deal.userfield.get", {"id": 1678}).get("result", {})
sub_list = sub_uf.get("LIST", [])
print(f"Total de subcategorias ativas: {len(sub_list)}")
for s in sub_list:
    print(f"  [{s.get('ID')}] (Sort: {s.get('SORT')}) {s.get('VALUE')}")

print("\n=== 3. VERIFICAÇÃO DA CONFIGURAÇÃO DO CARD (PIPELINE 160) ===")
card_conf = call("crm.deal.details.configuration.get", {
    "scope": "C",
    "extras": {"dealCategoryId": 160}
}).get("result", [])

for sec in card_conf:
    print(f"\n--- Seção: {sec.get('title')} ({sec.get('name')}) ---")
    for el in sec.get("elements", []):
        print(f"  - Campo: {el.get('name')}")
