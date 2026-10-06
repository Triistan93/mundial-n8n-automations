import requests
import json
import re
from collections import Counter

WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'

print("=== COLETANDO TAREFAS VINCULADAS AOS TICKETS DE TI ===")

# Busca as últimas 200 tarefas com título 'Ticket'
tasks = []
start = 0
while start < 200:
    r = requests.post(f'{WEBHOOK}tasks.task.list', json={
        'filter': {'TITLE': 'Ticket'},
        'select': ['ID', 'TITLE', 'DESCRIPTION', 'STATUS', 'CREATED_DATE', 'CLOSED_DATE', 'RESPONSIBLE_ID'],
        'order': {'CREATED_DATE': 'DESC'},
        'start': start
    }).json()
    batch = r.get('result', {}).get('tasks', [])
    if not batch:
        break
    tasks.extend(batch)
    if 'next' not in r:
        break
    start = r['next']

print(f"Total de tarefas coletadas: {len(tasks)}")

parsed_tickets = []
cat_counter = Counter()
subcat_counter = Counter()

for t in tasks:
    desc = t.get('description', '')
    tid = t.get('id')
    status = t.get('status') # 5 = fechada, 2/3 = aberta
    
    # Extrai Categoria, Subcategoria e Descrição via regex
    m_cat = re.search(r'Categoria:\s*(.+)', desc)
    m_sub = re.search(r'Subcategoria:\s*(.+)', desc)
    m_desc = re.search(r'Descri[çc][aã]o:\s*([\s\S]+)', desc)
    
    categoria = m_cat.group(1).strip() if m_cat else 'N/A'
    subcategoria = m_sub.group(1).strip() if m_sub else 'N/A'
    detalhe = m_desc.group(1).strip() if m_desc else desc.strip()
    
    cat_counter[categoria] += 1
    subcat_counter[f"{categoria} > {subcategoria}"] += 1
    
    parsed_tickets.append({
        'task_id': tid,
        'status': status,
        'created': t.get('createdDate'),
        'closed': t.get('closedDate'),
        'categoria': categoria,
        'subcategoria': subcategoria,
        'descricao': detalhe
    })

with open('C:/mundial-n8n-automations/scripts/parsed_tasks_database.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_tickets, f, ensure_ascii=False, indent=2)

print("\n=== TOP CATEGORIAS DOS TICKETS REAIS ===")
for c, count in cat_counter.most_common(20):
    pct = (count / len(parsed_tickets)) * 100
    print(f"  {c}: {count} ({pct:.1f}%)")

print("\n=== TOP 25 SUBCATEGORIAS / MOTIVOS MAIS FREQUENTES ===")
for sc, count in subcat_counter.most_common(25):
    print(f"  {sc}: {count}")
