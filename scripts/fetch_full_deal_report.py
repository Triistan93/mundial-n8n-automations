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

# 1. Fetch user mapping
print("Buscando lista de usuários do Bitrix...")
users_raw = call("user.get", {}).get("result", [])
user_map = {}
for u in users_raw:
    uid = str(u.get("ID"))
    full_name = f"{u.get('NAME', '')} {u.get('LAST_NAME', '')}".strip()
    dept = u.get("WORK_POSITION", "")
    user_map[uid] = f"{full_name} ({dept})" if dept else full_name

# Target stages
target_stages = {
    "C160:UC_YUL75I": "Em Cotação",
    "C160:UC_AR9ORZ": "Autorizado",
    "C160:UC_JIOBG8": "Aguardando autorização"
}

all_deals_data = []

for stage_id, stage_name in target_stages.items():
    res = call("crm.deal.list", {
        "filter": {
            "CATEGORY_ID": 160,
            "STAGE_ID": stage_id
        },
        "select": ["*", "UF_*"]
    })
    deals = res.get("result", [])
    print(f"\nEtapa '{stage_name}' ({stage_id}): {len(deals)} chamados encontrados.")

    for d in deals:
        did = d.get("ID")
        title = d.get("TITLE")
        assigned_id = str(d.get("ASSIGNED_BY_ID", ""))
        created_id = str(d.get("CREATED_BY_ID", ""))
        date_create = d.get("DATE_CREATE")
        date_modify = d.get("DATE_MODIFY")
        
        assigned_name = user_map.get(assigned_id, f"ID {assigned_id}")
        created_name = user_map.get(created_id, f"ID {created_id}")
        
        # Custom fields
        desc_raw = d.get("UF_CRM_1729774515200")
        desc = "\n".join(desc_raw) if isinstance(desc_raw, list) else str(desc_raw or "")
        comments = d.get("COMMENTS", "")
        store = d.get("UF_CRM_1689593052602", "")
        category = d.get("UF_CRM_1763388156", "")
        subcategory = d.get("UF_CRM_1763388469429", "")
        
        # 1. Timeline comments
        tl = call("crm.timeline.comment.list", {
            "filter": {"ENTITY_TYPE": "deal", "ENTITY_ID": did}
        }).get("result", [])
        tl_list = []
        for t in tl:
            author_id = str(t.get("AUTHOR_ID", ""))
            author_name = user_map.get(author_id, f"ID {author_id}")
            tl_list.append({
                "author": author_name,
                "created": t.get("CREATED"),
                "text": t.get("COMMENT", "").strip()
            })
            
        # 2. Tasks and task comments
        tasks = call("tasks.task.list", {"filter": {"UF_CRM_TASK": f"D_{did}"}}).get("result", {}).get("tasks", [])
        task_list = []
        for tsk in tasks:
            tid = tsk.get("id")
            resp_name = tsk.get("responsible", {}).get("name", "")
            tcomments = call("task.commentitem.getlist", [tid]).get("result", [])
            tc_list = []
            for tc in tcomments:
                tc_list.append({
                    "author": tc.get("AUTHOR_NAME"),
                    "text": tc.get("POST_MESSAGE", "").strip()
                })
            task_list.append({
                "id": tid,
                "title": tsk.get("title"),
                "status": tsk.get("status"),
                "responsible": resp_name,
                "comments": tc_list
            })
            
        # 3. IM Chat check
        chat_info = call("im.chat.get", {"ENTITY_TYPE": "CRM", "ENTITY_ID": f"DEAL|{did}"}).get("result")
        chat_msgs = []
        if chat_info:
            cid = chat_info.get("ID")
            m_res = call("im.dialog.messages.get", {"DIALOG_ID": f"chat{cid}"})
            if "result" in m_res and m_res["result"]:
                for msg in m_res["result"].get("messages", []):
                    auth_id = str(msg.get("author_id", ""))
                    auth_name = user_map.get(auth_id, f"ID {auth_id}")
                    chat_msgs.append({
                        "author": auth_name,
                        "text": msg.get("text", "").strip()
                    })

        all_deals_data.append({
            "deal_id": did,
            "stage_id": stage_id,
            "stage_name": stage_name,
            "title": title,
            "created_name": created_name,
            "assigned_name": assigned_name,
            "date_create": date_create,
            "date_modify": date_modify,
            "description": desc,
            "comments": comments,
            "timeline_comments": tl_list,
            "tasks": task_list,
            "chat_messages": chat_msgs
        })

print(f"\nTotal consolidado de chamados coletados: {len(all_deals_data)}")

# Save to scratch for analysis
out_p = r"C:\mundial-n8n-automations\scripts\cotacao_autorizado_deals.json"
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(all_deals_data, f, ensure_ascii=False, indent=2)
print(f"Salvo relatório consolidado em {out_p}")
