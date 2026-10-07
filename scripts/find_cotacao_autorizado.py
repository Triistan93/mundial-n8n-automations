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

# 1. List stages of category 160
stages = call("crm.dealcategory.stage.list", {"id": 160}).get("result", [])
print("ETAPAS DO FUNIL 160 (Central de TI):")
target_stages = []
for s in stages:
    sid = s.get('STATUS_ID')
    sname = s.get('NAME')
    print(f"  {sid} -> '{sname}'")
    sname_lower = sname.lower()
    if "cota" in sname_lower or "autoriz" in sname_lower or "compra" in sname_lower or "aprova" in sname_lower:
        target_stages.append(s)

print("\nETAPAS ALVO IDENTIFICADAS:")
for ts in target_stages:
    print(f"  {ts.get('STATUS_ID')} -> '{ts.get('NAME')}'")
