# -*- coding: utf-8 -*-
"""
Ajuste de blindagem total contra SQL Syntax Error em 01_Check_Store_Outage_Cluster
e 01_Evaluate_Store_Outage.
Elimina interpolação de title e description em SQL, preservando 100% dos dados via gateItems.
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

print("1. Obtendo workflow...")
resp = requests.get(N8N_URL, headers=headers)
wf = resp.json()

# 1. Nova query limpa e segura de 01_Check_Store_Outage_Cluster
new_outage_query = """WITH recent_events AS (
    SELECT COUNT(*) AS count_recent
    FROM store_outage_events
    WHERE store_name = '{{ ($json.store_name || "").replace(/'/g, "''") }}'
      AND category_theme = '{{ ($json.category_theme || "").replace(/'/g, "''") }}'
      AND created_at >= NOW() - INTERVAL '30 MINUTES'
),
inserted AS (
    INSERT INTO store_outage_events (store_name, category_theme, deal_id, created_at)
    VALUES ('{{ ($json.store_name || "").replace(/'/g, "''") }}', '{{ ($json.category_theme || "").replace(/'/g, "''") }}', {{ $json.deal_id }}, NOW())
    RETURNING id
)
SELECT recent_events.count_recent
FROM recent_events;"""

# 2. Novo código de 01_Evaluate_Store_Outage com merge seguro
new_evaluate_code = """// Avalia resultado do clustering de outage por loja combinando com os itens originais do gate
const gateItems = $('01_If_Is_Duplicate').all(1);
const items = $input.all();

return items.map((item, i) => {
  const orig = gateItems[i]?.json || {};
  const countRecent = Number(item.json.count_recent || 0);

  // REGRA DE OURO: Outage é EXCLUSIVO para queda geral de INTERNET/REDE da loja!
  // Jamais disparar para GENERAL_IT, TELEFONIA, MICROWORK, etc.
  const isNetworkTheme = orig.category_theme === 'CONNECTIVITY_NETWORK';
  const isOutage = isNetworkTheme && countRecent >= 2;
  const outageCount = countRecent + 1;

  return {
    json: {
      ...orig,
      is_store_outage: isOutage,
      outage_count: outageCount
    }
  };
});"""

for node in wf['nodes']:
    if node['name'] == '01_Check_Store_Outage_Cluster':
        print("Blindando nó 01_Check_Store_Outage_Cluster...")
        node['parameters']['query'] = new_outage_query
    elif node['name'] == '01_Evaluate_Store_Outage':
        print("Atualizando nó 01_Evaluate_Store_Outage...")
        node['parameters']['jsCode'] = new_evaluate_code

print("2. Salvando workflow no n8n...")
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}
put_resp = requests.put(N8N_URL, headers=headers, json=payload)
if put_resp.status_code == 200:
    print("Clustering de Outage blindado com sucesso!")
else:
    print(f"Erro ao salvar: {put_resp.status_code} - {put_resp.text}")
