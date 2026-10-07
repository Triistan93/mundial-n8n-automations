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

# Check tasks linked to deal
for did in [1389566, 1388298, 1377818]:
    print(f"\n--- TAREFAS VINCULADAS AO DEAL #{did} ---")
    tasks = call("tasks.task.list", {"filter": {"UF_CRM_TASK": f"D_{did}"}}).get("result", {}).get("tasks", [])
    print(f"Tasks: {len(tasks)}")
    for t in tasks:
        tid = t.get("id")
        print(f"  Task {tid}: {t.get('title')} | Status: {t.get('status')} | Responsible: {t.get('responsible', {}).get('name')}")
        # Fetch task comments
        tcomments = call("task.commentitem.getlist", [tid]).get("result", [])
        print(f"    Task comments count: {len(tcomments)}")
        for tc in tcomments:
            print(f"      [{tc.get('AUTHOR_NAME')}]: {tc.get('POST_MESSAGE')}")
