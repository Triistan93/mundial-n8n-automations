# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\mundial-n8n-automations\scripts\cotacao_autorizado_deals.json", "r", encoding="utf-8") as f:
    deals = json.load(f)

for d in deals:
    print("="*80)
    print(f"ID #{d['deal_id']} | Etapa: {d['stage_name']} ({d['stage_id']})")
    print(f"Título: {d['title']}")
    print(f"Criado por: {d['created_name']} | Atendido/Responsável: {d['assigned_name']}")
    print(f"Abertura: {d['date_create']} | Modificado: {d['date_modify']}")
    print(f"Descrição: {d['description']}")
    if d.get('comments'):
        print(f"Observação: {d['comments']}")
    if d.get('timeline_comments'):
        print("Comentários da Linha do Tempo:")
        for tc in d['timeline_comments']:
            print(f"  [{tc['created']}] {tc['author']}: {tc['text']}")
    if d.get('chat_messages'):
        print("Mensagens do Chat:")
        for m in d['chat_messages']:
            print(f"  {m['author']}: {m['text']}")
    if d.get('tasks'):
        for tsk in d['tasks']:
            print(f"Tarefa #{tsk['id']} ({tsk['title']}) - Resp: {tsk['responsible']}")
            for c in tsk.get('comments', []):
                print(f"  Comment Tarefa: [{c['author']}] {c['text']}")
