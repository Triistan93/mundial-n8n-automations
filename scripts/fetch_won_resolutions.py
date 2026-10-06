import requests
import json

WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'

with open('C:/mundial-n8n-automations/scripts/deals_sample_c160.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

won_deals = [d for d in deals if d.get('STAGE_ID') == 'C160:WON']
print(f"Total de tickets WON: {len(won_deals)}")

# Seleciona uma amostra representativa de 20 tickets WON com títulos variados
sample_won = won_deals[:25]

results = []
for d in sample_won:
    did = d.get('ID')
    title = d.get('TITLE')
    
    r_com = requests.get(f'{WEBHOOK}crm.timeline.comment.list', params={
        'filter[ENTITY_ID]': did,
        'filter[ENTITY_TYPE]': 'deal'
    }).json().get('result', [])
    
    comments = []
    for c in r_com:
        comm_text = (c.get('COMMENT') or '').strip()
        if comm_text:
            comments.append({
                'author_id': c.get('AUTHOR_ID'),
                'created': c.get('CREATED'),
                'comment': comm_text
            })
            
    results.append({
        'id': did,
        'title': title,
        'comments': comments
    })
    print(f"Deal #{did}: {title} ({len(comments)} comentários na timeline)")

with open('C:/mundial-n8n-automations/scripts/won_resolutions_sample.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nAmostra de resoluções salva em won_resolutions_sample.json!")
