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

# Test sending a message with KEYBOARD to Eduardo (32598)
payload = {
    "DIALOG_ID": "32598",
    "MESSAGE": "[b]🤖 TESTE DE AUTOMAÇÃO DE APROVAÇÃO[/b]\nEste é um teste dos botões interativos de aprovação de compras da TI.",
    "KEYBOARD": [
        {
            "TEXT": "✅ Autorizar Compra",
            "LINK": "https://sophia-n8nsophia.timft8.easypanel.host/webhook/test-approve?action=approve",
            "BG_COLOR": "#29b24f",
            "TEXT_COLOR": "#ffffff",
            "DISPLAY": "LINE"
        },
        {
            "TEXT": "❌ Negar",
            "LINK": "https://sophia-n8nsophia.timft8.easypanel.host/webhook/test-approve?action=reject",
            "BG_COLOR": "#e84343",
            "TEXT_COLOR": "#ffffff",
            "DISPLAY": "LINE"
        }
    ]
}

res = call("im.message.add", payload)
print("Resposta do envio com KEYBOARD:", res)
