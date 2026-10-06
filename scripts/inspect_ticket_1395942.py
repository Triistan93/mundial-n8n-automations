import requests
import json

WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'
did = 1395942

deal = requests.get(f'{WEBHOOK}crm.deal.get', params={'id': did}).json().get('result', {})
print('=== DEAL 1395942 ===')
print('TITLE:', deal.get('TITLE'))
print('STAGE_ID:', deal.get('STAGE_ID'))
print('COMMENTS:', deal.get('COMMENTS'))
print('UF_CRM_TI_IMPACT:', deal.get('UF_CRM_TI_IMPACT'))
print('UF_CRM_TI_URGENCY:', deal.get('UF_CRM_TI_URGENCY'))
print('UF_CRM_TI_PRIORITY:', deal.get('UF_CRM_TI_PRIORITY'))

r_chat = requests.get(f'{WEBHOOK}im.chat.get', params={'ENTITY_TYPE': 'CRM', 'ENTITY_ID': f'DEAL|{did}'}).json()
cid = r_chat.get('result', {}).get('id')
print('CHAT ID:', cid)

if cid:
    msgs = requests.get(f'{WEBHOOK}im.dialog.messages.get', params={'DIALOG_ID': f'chat{cid}', 'LIMIT': 20}).json()
    print('=== CHAT MESSAGES ===')
    for m in reversed(msgs.get('result', {}).get('messages', [])):
        print(f"[{m.get('author_id')}]: {m.get('text')}")
