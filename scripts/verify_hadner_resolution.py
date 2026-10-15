import requests
import json

B24_WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm'
sql_url = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'

deal = requests.get(f'{B24_WEBHOOK}/crm.deal.get', params={'id': 1411066}).json().get('result', {})
print("DEAL STAGE:", deal.get("STAGE_ID"))
print("DEAL TITLE:", deal.get("TITLE"))

q = 'SELECT id, deal_id, requester_name, status, state, ai_state, completed_at FROM ticket_bot_sessions WHERE deal_id = 1411066;'
r = requests.post(sql_url, json={'query': q}).json()
print("DB Session:", json.dumps(r, indent=2))

comments = requests.get(f'{B24_WEBHOOK}/crm.timeline.comment.list', params={'filter': {'ENTITY_ID': 1411066, 'ENTITY_TYPE': 'deal'}}).json()
print("TIMELINE COMMENTS COUNT:", len(comments.get('result', [])))
if comments.get('result'):
    print("LATEST COMMENT:\n", comments.get('result')[0].get('COMMENT'))
