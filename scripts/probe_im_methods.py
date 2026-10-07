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

# Test different IM methods for chat 842710
cid = 842710
print("im.chat.get:", call("im.chat.get", {"CHAT_ID": cid}))
print("im.chat.user.list:", call("im.chat.user.list", {"CHAT_ID": cid}))
print("im.dialog.messages.get (CHAT_ID):", call("im.dialog.messages.get", {"CHAT_ID": cid}))
print("im.dialog.messages.get (DIALOG_ID=chat...):", call("im.dialog.messages.get", {"DIALOG_ID": f"chat{cid}"}))

# Also check im.disk.file.list or im.message.search
print("im.message.search:", call("im.message.search", {"CHAT_ID": cid}))
