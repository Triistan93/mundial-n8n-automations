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

field_payload = {
    "fields": {
        "FIELD_NAME": "UF_CRM_TI_RESPONSIBLE",
        "USER_TYPE_ID": "employee",
        "XML_ID": "uf_crm_ti_responsible",
        "MULTIPLE": "N",
        "MANDATORY": "N",
        "SHOW_FILTER": "E",
        "SHOW_IN_LIST": "Y",
        "EDIT_IN_LIST": "Y",
        "EDIT_FORM_LABEL": {
            "br": "Responsável TI",
            "en": "Responsável TI"
        },
        "LIST_COLUMN_LABEL": {
            "br": "Responsável TI",
            "en": "Responsável TI"
        },
        "LIST_FILTER_LABEL": {
            "br": "Responsável TI",
            "en": "Responsável TI"
        }
    }
}

print("Criando campo UF_CRM_TI_RESPONSIBLE (Responsável TI)...")
res = call("crm.deal.userfield.add", field_payload)
print("Resultado:", res)
