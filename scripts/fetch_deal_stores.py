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

# Get Loja enum field options
loja_uf = call("crm.deal.userfield.get", {"id": 213}).get("result", {}) # UF_CRM_1689593052602
loja_map = {}
for item in loja_uf.get("LIST", []):
    loja_map[str(item.get("ID"))] = item.get("VALUE")

target_ids = [1389566, 1377818, 1388298, 1362214, 1374358, 1328192, 1317680, 1303940]

for did in target_ids:
    d = call("crm.deal.get", {"id": did}).get("result", {})
    loja_id = str(d.get("UF_CRM_1689593052602", ""))
    loja_nome = loja_map.get(loja_id, f"ID {loja_id}")
    print(f"Deal {did}: Loja='{loja_nome}', Solicitante='{d.get('CREATED_BY_ID')}'")
