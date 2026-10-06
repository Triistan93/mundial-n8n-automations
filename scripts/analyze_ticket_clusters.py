import json
import re
from collections import Counter

with open('C:/mundial-n8n-automations/scripts/deals_sample_c160.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

print(f"Total de tickets carregados: {len(deals)}")

# 1. Agrupamento por palavras-chave nos títulos
clusters = {
    'COMPUTADOR / HARDWARE': [],
    'IMPRESSORA / SCANNER': [],
    'REDE / INTERNET / WI-FI': [],
    'MICROWORK / ERP': [],
    'ACESSO / SENHA / WINDOWS / EMAIL': [],
    'TELEFONIA / RAMAL': [],
    'CFTV / CÂMERA': [],
    'BITRIX24': [],
    'ATPV / RENAVE / DETRAN': [],
    'COMPRA / INSTALAÇÃO / MOVIMENTAÇÃO': [],
    'OUTROS / GERAL': []
}

patterns = [
    ('IMPRESSORA / SCANNER', r'impressora|imprime|toner|papel|scanner|zebra|etiqueta|spooler'),
    ('REDE / INTERNET / WI-FI', r'internet|rede|wi-fi|wifi|conex[aã]o|cabo de rede|link|sem sinal'),
    ('MICROWORK / ERP', r'microwork|erp|m[oó]dulo|faturar|faturamento|caixa|ordem de servi[çc]o|dms'),
    ('ATPV / RENAVE / DETRAN', r'atpv|renave|detran|comunicac|comunica[çc][aã]o'),
    ('ACESSO / SENHA / WINDOWS / EMAIL', r'senha|bloquead|desbloque|acesso|login|outlook|e-mail|email|permiss[aã]o|usu[aá]rio'),
    ('TELEFONIA / RAMAL', r'ramal|telefone|telefonia|ligac|liga[çc][aã]o|mudo'),
    ('CFTV / CÂMERA', r'c[aâ]mera|cftv|dvr|grava[çc][aã]o|imagem'),
    ('BITRIX24', r'bitrix|chat bitrix|tarefa bitrix'),
    ('COMPRA / INSTALAÇÃO / MOVIMENTAÇÃO', r'compra|cota[çc][aã]o|instala[çc][aã]o|troca de m[aá]quina|mudan[çc]a|transfer[eê]ncia|formatar|formata[çc][aã]o'),
    ('COMPUTADOR / HARDWARE', r'computador|pc|notebook|n[aã]o liga|tela|monitor|mouse|teclado|travando|lento|fonte|hd|mem[oó]ria')
]

for d in deals:
    title = (d.get('TITLE') or '').lower()
    comments = (d.get('COMMENTS') or '').lower()
    full_text = f"{title} {comments}"
    
    matched = False
    for cat_name, rgx in patterns:
        if re.search(rgx, full_text):
            clusters[cat_name].append(d)
            matched = True
            break
            
    if not matched:
        clusters['OUTROS / GERAL'].append(d)

print("\n=== DISTRIBUICAO DOS TICKETS POR CLUSTER TECNICO ===")
for cat, items in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True):
    pct = (len(items) / len(deals)) * 100
    print(f"[*] {cat}: {len(items)} tickets ({pct:.1f}%)")

# Amostras de cada cluster
print("\n=== TOP EXEMPLOS DE CADA CATEGORIA ===")
for cat, items in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n--- {cat} ({len(items)} casos) ---")
    for d in items[:5]:
        did = d.get('ID')
        stg = d.get('_stage_name')
        t = d.get('TITLE')
        print(f"  #{did} [{stg}]: {t}")
