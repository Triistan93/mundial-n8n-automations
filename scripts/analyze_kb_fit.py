# -*- coding: utf-8 -*-
import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\mundial-n8n-automations\scripts\deals_sample_c160.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

with open(r'C:\mundial-n8n-automations\scripts\parsed_tasks_database.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

print(f"Total Deals: {len(deals)}")
print(f"Total Tasks: {len(tasks)}")

# Amostra de títulos que não foram categorizados antes
print("\n--- AMOSTRA DE DEALS DIVERSOS (TÍTULOS REAIS) ---")
for d in deals[20:50]:
    print(f"Deal {d.get('ID')}: {d.get('TITLE')}")

# Analisar categorias das tasks
print("\n--- CATEGORIAS DAS TASKS ---")
task_cats = Counter(t.get('categoria', 'SEM_CAT') for t in tasks)
for c, cnt in task_cats.most_common():
    print(f"{cnt:3d}x {c}")
