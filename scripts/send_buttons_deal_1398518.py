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

# 1. Fetch deal chat ID
deal_id = 1398518
im_chat = call("im.chat.get", {"ENTITY_TYPE": "CRM", "ENTITY_ID": f"DEAL|{deal_id}"})
chat_id = im_chat.get("result", {}).get("ID")
print(f"Deal #{deal_id} Chat ID:", chat_id)

# 2. Print recent messages from deal chat
if chat_id:
    msgs = call("im.dialog.messages.get", {"DIALOG_ID": f"chat{chat_id}"})
    messages = msgs.get("result", {}).get("messages", [])
    print(f"\n--- Mensagens no chat851272 ({len(messages)}) ---")
    for m in reversed(messages):
        print(f"[{m.get('author_id')}]: {m.get('text')}\n")

# 3. Payload with interactive keyboard for approval
deal_title = "[TI-COMPUTADOR] - Computador com lentidão por uso alto de memória RAM (Eduardo Alaminos)"
approve_url = f"https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id={deal_id}&action=approve&user=32598"
reject_url = f"https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action?deal_id={deal_id}&action=reject&user=32598"

keyboard = [
    {
        "TEXT": "✅ Autorizar Compra",
        "LINK": approve_url,
        "BG_COLOR": "#29b24f",
        "TEXT_COLOR": "#ffffff",
        "DISPLAY": "LINE"
    },
    {
        "TEXT": "❌ Negar",
        "LINK": reject_url,
        "BG_COLOR": "#e84343",
        "TEXT_COLOR": "#ffffff",
        "DISPLAY": "LINE"
    }
]

# Send to Deal Chat
if chat_id:
    deal_chat_payload = {
        "DIALOG_ID": f"chat{chat_id}",
        "MESSAGE": f"📦 [b]SOLICITAÇÃO DE COMPRA DE TI[/b]\n"
                   f"Chamado #{deal_id}: {deal_title}\n"
                   f"A triagem identificou necessidade de aquisição de item de hardware.\n\n"
                   f"👉 [b]Aprovação da Gestão:[/b] Por favor, utilize os botões interativos abaixo para definir o direcionamento:",
        "KEYBOARD": keyboard
    }
    res1 = call("im.message.add", deal_chat_payload)
    print("Envio para Deal Chat:", res1)

# Send to Eduardo Alaminos Direct Chat (User 32598)
direct_payload = {
    "DIALOG_ID": "32598",
    "MESSAGE": f"📦 [b]NOVA SOLICITAÇÃO DE COMPRA PENDENTE[/b]\n"
               f"Chamado #{deal_id}: {deal_title}\n\n"
               f"Status: Aguardando autorização\n"
               f"Clique no botão abaixo para autorizar ou negar:",
    "KEYBOARD": keyboard
}
res2 = call("im.message.add", direct_payload)
print("Envio para Chat Direto (Eduardo 32598):", res2)
