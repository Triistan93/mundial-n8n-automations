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

new_sections = [
    {
        "name": "main",
        "title": "Dados do Chamado (Solicitante)",
        "type": "section",
        "elements": [
            {"name": "TITLE", "optionFlags": "1"},
            {"name": "UF_CRM_1689593052602", "optionFlags": "1"},
            {"name": "UF_CRM_1763388156", "optionFlags": "0"},
            {"name": "UF_CRM_1763388469429", "optionFlags": "0"},
            {"name": "UF_CRM_1729774515200", "optionFlags": "0"},
            {"name": "UF_CRM_TI_IMPACT", "optionFlags": "0"},
            {"name": "UF_CRM_TI_URGENCY", "optionFlags": "0"},
            {"name": "UF_CRM_1735304929", "optionFlags": "1"},
            {"name": "ASSIGNED_BY_ID", "optionFlags": "1"},
            {"name": "OBSERVER", "optionFlags": "1"}
        ]
    },
    {
        "name": "ti_management",
        "title": "Triagem & Gestão Técnica (TI)",
        "type": "section",
        "elements": [
            {"name": "UF_CRM_TI_RESPONSIBLE", "optionFlags": "0"},
            {"name": "UF_CRM_TI_PRIORITY", "optionFlags": "0"},
            {"name": "UF_CRM_TI_SHORT_SUBJECT", "optionFlags": "0"},
            {"name": "UF_CRM_TI_NEXT_OWNER", "optionFlags": "0"},
            {"name": "UF_CRM_TI_WAIT_REASON", "optionFlags": "0"},
            {"name": "COMMENTS", "optionFlags": "1"},
            {"name": "UF_CRM_1689597532", "optionFlags": "1"}
        ]
    }
]

payload = {
    "scope": "C",
    "data": new_sections,
    "extras": {
        "dealCategoryId": 160
    }
}

res = call("crm.deal.details.configuration.set", payload)
print("Configuração do Card atualizada:", res)
