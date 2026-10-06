import requests
import json

WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'

for tid in [21194, 21200, 21196]:
    r = requests.get(f'{WEBHOOK}tasks.task.get', params={'taskId': tid}).json()
    task = r.get('result', {}).get('task', {})
    print(f"\n=============================================")
    print(f"TASK #{tid}: {task.get('title')}")
    print(f"Created: {task.get('createdDate')} | Closed: {task.get('closedDate')}")
    print(f"Description:\n{task.get('description')}")
    
    # Comentários da tarefa
    r_c = requests.get(f'{WEBHOOK}task.commentitem.getlist', params={'TASKID': tid}).json()
    comms = r_c.get('result', [])
    print(f"Comentários ({len(comms)}):")
    for c in comms:
        print(f"  [{c.get('POST_DATE')}] {c.get('POST_MESSAGE')}")
