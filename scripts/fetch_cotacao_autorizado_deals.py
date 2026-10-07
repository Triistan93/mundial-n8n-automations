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

# Check deals in target stages
target_stages = ["C160:UC_YUL75I", "C160:UC_AR9ORZ", "C160:UC_JIOBG8"]

for st in target_stages:
    res = call("crm.deal.list", {
        "filter": {
            "CATEGORY_ID": 160,
            "STAGE_ID": st
        },
        "select": ["*", "UF_*"]
    })
    deals = res.get("result", [])
    print(f"Etapa {st}: {len(deals)} chamados encontrados")
    for d in deals:
        print(f"  ID: {d.get('ID')} | TITLE: {d.get('TITLE')} | ASSIGNED_BY_ID: {d.get('ASSIGNED_BY_ID')} | DATE_CREATE: {d.get('DATE_CREATE')}")
