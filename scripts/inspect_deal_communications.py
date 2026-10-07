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

test_deal_id = 1389566

print(f"=== TESTANDO COMUNICAÇÃO DO DEAL #{test_deal_id} ===")

# 1. crm.deal.get
deal = call("crm.deal.get", {"id": test_deal_id}).get("result", {})
print("Deal title:", deal.get("TITLE"))
print("Descricao UF_CRM_1729774515200:", deal.get("UF_CRM_1729774515200"))
print("Comments:", deal.get("COMMENTS"))
print("Assigned:", deal.get("ASSIGNED_BY_ID"), "Created:", deal.get("CREATED_BY_ID"))

# 2. Timeline comments
tl = call("crm.timeline.comment.list", {
    "filter": {
        "ENTITY_TYPE": "deal",
        "ENTITY_ID": test_deal_id
    }
})
print("Timeline comments:", len(tl.get("result", [])))
for c in tl.get("result", []):
    print("  TL:", c.get("CREATED"), c.get("AUTHOR_ID"), c.get("COMMENT")[:100])

# 3. IM Chat get for ENTITY_TYPE=CRM, ENTITY_ID=DEAL|1389566
im_chat = call("im.chat.get", {
    "ENTITY_TYPE": "CRM",
    "ENTITY_ID": f"DEAL|{test_deal_id}"
})
print("IM Chat:", im_chat)
if "result" in im_chat and im_chat["result"]:
    chat_id = im_chat["result"].get("ID")
    print("Chat ID:", chat_id)
    # Fetch messages
    msgs = call("im.dialog.messages.get", {"DIALOG_ID": f"chat{chat_id}"})
    print("Messages count:", len(msgs.get("result", {}).get("messages", [])))
    for m in msgs.get("result", {}).get("messages", []):
        print(f"  [{m.get('author_id')}]: {m.get('text')}")
