import os
import requests
import json
from collections import Counter
from datetime import datetime

WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/'

print("=== INICIANDO VARREDURA DE TICKETS NA CATEGORIA 160 (SUPORTE TI) ===")

# 1. Obter estágios da Categoria 160
r_stages = requests.get(f'{WEBHOOK}crm.dealcategory.stage.list', params={'id': 160}).json()
stages = r_stages.get('result', [])
stage_map = {s.get('STATUS_ID'): s.get('NAME') for s in stages}
print(f"Estágios cadastrados na Categoria 160: {stage_map}")

# 2. Obter campos customizados (Userfields) para identificar categorias e subcategorias
r_fields = requests.get(f'{WEBHOOK}crm.deal.userfield.list', params={'filter': {'ENTITY_ID': 'CRM_DEAL'}}).json()
uf_list = r_fields.get('result', [])
uf_map = {u.get('FIELD_NAME'): u.get('EDIT_FORM_LABEL', {}).get('br') or u.get('LIST_COLUMN_LABEL', {}).get('br') or u.get('FIELD_NAME') for u in uf_list}

# 3. Buscar amostras de tickets abertos (NEW, PREPARATION, PREPAYMENT_INVOI) e encerrados (WON, LOSE)
stages_to_analyze = {
    'ABERTOS': ['C160:NEW', 'C160:PREPARATION', 'C160:PREPAYMENT_INVOI'],
    'ENCERRADOS': ['C160:WON', 'C160:LOSE']
}

all_deals = []

for group_name, s_list in stages_to_analyze.items():
    for sid in s_list:
        s_name = stage_map.get(sid, sid)
        print(f"Consultando estágio {sid} ({s_name})...")
        start = 0
        batch_count = 0
        while start < 300: # Amostra de até 300 por estágio para estatística sólida
            r = requests.post(f'{WEBHOOK}crm.deal.list', json={
                'filter': {'CATEGORY_ID': 160, 'STAGE_ID': sid},
                'select': ['ID', 'TITLE', 'STAGE_ID', 'DATE_CREATE', 'DATE_MODIFY', 'ASSIGNED_BY_ID', 'CREATED_BY_ID', 'COMMENTS', 'UF_*'],
                'order': {'DATE_CREATE': 'DESC'},
                'start': start
            }).json()
            items = r.get('result', [])
            if not items:
                break
            for item in items:
                item['_group'] = group_name
                item['_stage_name'] = s_name
                all_deals.append(item)
            batch_count += len(items)
            if 'next' not in r:
                break
            start = r['next']
        print(f"  -> Coletados {batch_count} deals em {sid}")

print(f"\nTotal geral de tickets coletados para análise: {len(all_deals)}")

# Salva dataset bruto para inspeção rápida
with open('C:/mundial-n8n-automations/scripts/deals_sample_c160.json', 'w', encoding='utf-8') as f:
    json.dump(all_deals, f, ensure_ascii=False, indent=2)

print("Dataset salvo em C:/mundial-n8n-automations/scripts/deals_sample_c160.json")
