import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'
for uid in [4278, 32598]:
    url = f'{webhook}user.get.json?ID={uid}'
    req = urllib.request.urlopen(url)
    res = json.loads(req.read().decode('utf-8'))
    users = res.get('result', [])
    if users:
        u = users[0]
        name = f"{u.get('NAME')} {u.get('LAST_NAME')}"
        pos = u.get('WORK_POSITION')
        email = u.get('EMAIL')
        print(f"User ID: {uid} | Name: {name} | Cargo: {pos} | Email: {email}")
    else:
        print(f"User ID: {uid} not found")
