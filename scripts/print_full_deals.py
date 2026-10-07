# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\mundial-n8n-automations\scripts\cotacao_autorizado_deals_resolved.json", "r", encoding="utf-8") as f:
    deals = json.load(f)

print(f"TOTAL DE CHAMADOS: {len(deals)}\n")

for i, d in enumerate(deals):
    print("="*80)
    print(f"ITEM {i+1} | ID #{d['deal_id']} | ETAPA: {d['stage_name']} ({d['stage_id']})")
    print(f"Título: {d['title']}")
    print(f"Solicitante: {d['created_name']}")
    print(f"Responsável/Atendente: {d['assigned_name']}")
    print(f"Data Abertura: {d['date_create']} | Última Modificação: {d['date_modify']}")
    print(f"Descrição do Pedido:\n{d['description'].strip()}")
    if d.get('comments'):
        print(f"Observação do Card:\n{d['comments'].strip()}")
    if d.get('timeline_comments'):
        print("Comentários da Linha do Tempo / Chat:")
        for tc in d['timeline_comments']:
            print(f"  - [{tc['created']}] {tc['author']}: {tc['text']}")
    if d.get('tasks'):
        for tsk in d['tasks']:
            print(f"Tarefa Vinculada #{tsk['id']} ({tsk['title']}) - Resp: {tsk['responsible']}")
            for c in tsk.get('comments', []):
                print(f"    [Comentário Tarefa] {c['author']}: {c['text']}")
