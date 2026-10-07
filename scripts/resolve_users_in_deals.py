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

# Fetch ALL users with pagination
user_map = {}
start = 0
while True:
    res = call("user.get", {"start": start})
    users = res.get("result", [])
    for u in users:
        uid = str(u.get("ID"))
        name = f"{u.get('NAME', '')} {u.get('LAST_NAME', '')}".strip()
        pos = u.get("WORK_POSITION", "")
        dept = f" ({pos})" if pos else ""
        user_map[uid] = f"{name}{dept}"
    if "next" in res:
        start = res["next"]
    else:
        break

print(f"Total de usuários mapeados: {len(user_map)}")

# Load deals
with open(r"C:\mundial-n8n-automations\scripts\cotacao_autorizado_deals.json", "r", encoding="utf-8") as f:
    deals = json.load(f)

# Resolve user names in deals
for d in deals:
    d["created_name"] = user_map.get(str(d.get("created_name", "").replace("ID ", "")), d["created_name"])
    d["assigned_name"] = user_map.get(str(d.get("assigned_name", "").replace("ID ", "")), d["assigned_name"])
    for tc in d.get("timeline_comments", []):
        author_clean = tc["author"].replace("ID ", "")
        tc["author"] = user_map.get(author_clean, tc["author"])

# Save resolved deals
with open(r"C:\mundial-n8n-automations\scripts\cotacao_autorizado_deals_resolved.json", "w", encoding="utf-8") as f:
    json.dump(deals, f, ensure_ascii=False, indent=2)

print("Usuários resolvidos salvos com sucesso!")
