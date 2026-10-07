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

for did in [1389566, 1388298, 1377818, 1257544]:
    print(f"\n=================== DEAL #{did} ===================")
    d = call("crm.deal.get", {"id": did}).get("result", {})
    print(f"TITLE: {d.get('TITLE')}")
    print(f"STAGE: {d.get('STAGE_ID')}")
    print(f"DESC: {d.get('UF_CRM_1729774515200')}")
    print(f"ASSIGNED: {d.get('ASSIGNED_BY_ID')} | CREATED: {d.get('CREATED_BY_ID')}")
    
    # Check im.chat.get
    c = call("im.chat.get", {"ENTITY_TYPE": "CRM", "ENTITY_ID": f"DEAL|{did}"}).get("result")
    print(f"IM CHAT: {c}")
    if c:
        cid = c.get("ID")
        # Test im.dialog.messages.get with DIALOG_ID=chat<cid>
        m1 = call("im.dialog.messages.get", {"DIALOG_ID": f"chat{cid}"}).get("result", {})
        print(f"  Messages (DIALOG_ID=chat{cid}): {len(m1.get('messages', []))}")
        for msg in m1.get("messages", []):
            print(f"    Author {msg.get('author_id')}: {msg.get('text')}")
            
    # Check timeline comments
    tl = call("crm.timeline.comment.list", {"filter": {"ENTITY_TYPE": "deal", "ENTITY_ID": did}}).get("result", [])
    print(f"Timeline comments: {len(tl)}")
    for t in tl:
        print(f"  Author {t.get('AUTHOR_ID')}: {t.get('COMMENT')}")

    # Check activities
    acts = call("crm.activity.list", {"filter": {"BINDINGS": [{"OWNER_TYPE_ID": 2, "OWNER_ID": did}]}}).get("result", [])
    print(f"Activities: {len(acts)}")
    for a in acts:
        print(f"  Act {a.get('TYPE_ID')}: {a.get('SUBJECT')} | Description: {a.get('DESCRIPTION')[:100] if a.get('DESCRIPTION') else ''}")
