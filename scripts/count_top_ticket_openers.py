# -*- coding: utf-8 -*-
import requests
import json
from collections import Counter
from datetime import datetime

BITRIX_WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'

print("Buscando todos os negócios da Categoria 160 (Central de TI)...")

all_deals = []
start = 0

while True:
    r = requests.post(BITRIX_WEBHOOK + 'crm.deal.list', json={
        'filter': {'CATEGORY_ID': 160},
        'select': [
            'ID', 'TITLE', 'STAGE_ID', 'DATE_CREATE', 'CREATED_BY_ID', 
            'ASSIGNED_BY_ID', 'UF_CRM_1689593052602'
        ],
        'order': {'ID': 'DESC'},
        'start': start
    })
    
    data = r.json()
    res = data.get('result', [])
    if not res:
        break
    all_deals.extend(res)
    print(f"Carregados {len(all_deals)} negócios...")
    
    if 'next' in data:
        start = data['next']
    else:
        break

print(f"\nTotal absoluto de chamados encontrados na Categoria 160: {len(all_deals)}")

# 1. Contagem por CREATED_BY_ID
user_counts = Counter(str(d.get('CREATED_BY_ID', 'Desconhecido')) for d in all_deals)
top_user_ids = [uid for uid, _ in user_counts.most_common(40)]

# 2. Buscar detalhes dos usuários no Bitrix24
user_info = {}
print("Buscando detalhes dos usuários no Bitrix24...")
for i in range(0, len(top_user_ids), 50):
    chunk = top_user_ids[i:i+50]
    r_u = requests.post(BITRIX_WEBHOOK + 'user.get', json={
        'FILTER': {'ID': chunk}
    })
    for u in r_u.json().get('result', []):
        uid = str(u.get('ID'))
        name = f"{u.get('NAME', '')} {u.get('LAST_NAME', '')}".strip()
        email = u.get('EMAIL', '')
        work_pos = u.get('WORK_POSITION', '')
        user_info[uid] = {
            'name': name,
            'email': email,
            'position': work_pos
        }

print("\n=== RANKING DE USUÁRIOS QUE MAIS ABREM TICKETS ===")
ranking = []
for uid, count in user_counts.most_common(30):
    u = user_info.get(uid, {'name': f'Usuário #{uid}', 'email': '', 'position': ''})
    ranking.append({
        'user_id': uid,
        'name': u['name'],
        'position': u['position'],
        'email': u['email'],
        'total_tickets': count
    })
    print(f"{len(ranking):2d}. [{count:3d} tickets] {u['name']} (ID: {uid}) - Cargo: {u['position']} ({u['email']})")

# Salvar em JSON para análises e relatórios
with open('C:/mundial-n8n-automations/scripts/ranking_solicitantes_ti.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_deals_analyzed': len(all_deals),
        'generated_at': datetime.now().isoformat(),
        'ranking': ranking
    }, f, ensure_ascii=False, indent=2)

print("\nRelatório gerado com sucesso!")
