import requests
import json

WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'

with open('C:/mundial-n8n-automations/scripts/won_resolutions_sample.json', 'r', encoding='utf-8') as f:
    sample = json.load(f)

for s in sample[:10]:
    did = s['id']
    title = s['title']
    
    # 1. Checa chat nativo
    r_chat = requests.get(f'{WEBHOOK}im.chat.get', params={'ENTITY_TYPE': 'CRM', 'ENTITY_ID': f'DEAL|{did}'}).json()
    cid = r_chat.get('result', {}).get('id')
    
    chat_msgs = []
    if cid:
        r_msg = requests.get(f'{WEBHOOK}im.dialog.messages.get', params={'DIALOG_ID': f'chat{cid}', 'LIMIT': 10}).json()
        raw_msgs = r_msg.get('result', {}).get('messages', [])
        for m in reversed(raw_msgs):
            chat_msgs.append(f"[{m.get('author_id')}]: {m.get('text')}")
            
    # 2. Checa tarefas vinculadas
    r_task = requests.get(f'{WEBHOOK}tasks.task.list', params={'filter[UF_CRM_TASK][]': f'D_{did}'}).json()
    tasks = r_task.get('result', {}).get('tasks', [])
    
    print(f"\n========================================================")
    print(f"DEAL #{did} - {title}")
    if cid:
        print(f"Chat ID: {cid} ({len(chat_msgs)} mensagens):")
        for m in chat_msgs[:5]:
            print(f"  {m[:120]}")
    else:
        print("Chat: Nenhum chat CRM criado")
        
    if tasks:
        print(f"Tarefas ({len(tasks)}):")
        for t in tasks:
            print(f"  Task #{t.get('id')}: {t.get('title')} (Status {t.get('status')})")
