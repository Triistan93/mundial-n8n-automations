import json
from collections import defaultdict

with open('C:/mundial-n8n-automations/scripts/parsed_tasks_database.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

by_cat = defaultdict(list)
for t in tasks:
    by_cat[f"{t['categoria']} > {t['subcategoria']}"].append(t['descricao'])

print("=== AMOSTRAS REAIS DE DESCRIÇÕES POR PROBLEMA ===")

top_cats = [
    'Bitrix 24 > Erro',
    'Microwork Cloud > Erro',
    'RENAVE > Erro',
    'Computador > Manuteno',
    'Computador > Erro',
    'Impressora > Configurao'
]

for cat_name in top_cats:
    samples = by_cat.get(cat_name, [])
    print(f"\n==================================================")
    print(f"CATEGORIA: {cat_name} ({len(samples)} casos)")
    print(f"==================================================")
    for desc in samples[:6]:
        clean = desc.replace('\r', '').replace('\n', ' ').strip()
        print(f"  * {clean[:160]}")
