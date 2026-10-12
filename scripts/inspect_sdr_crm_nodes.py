# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}

targets = [
    '1. Preparar Dados Lead',
    '3. Buscar Processo no Funil',
    'Montar URL de Busca',
    'Preparar Payload de Criação (Fallback)',
    '4b. Criar Card de Candidato1 (Fallback)',
    '4a. Atualizar Card Existente1',
    '5b. Adicionar Log no Timeline (Novo Card)',
    '5a. Adicionar Nova Info no Timeline1',
    'Mover Card de Etapa',
    'Transferir Chat Pós-Venda',
    'Enviar MSG Final'
]

print("=== DETALHAMENTO DOS NÓS DE INTEGRAÇÃO COM BITRIX24 ===")
for t in targets:
    n = nodes.get(t)
    if not n:
        # Search partial match
        matching = [k for k in nodes.keys() if t.lower() in k.lower()]
        if matching:
            n = nodes.get(matching[0])
            t = matching[0]

    if n:
        print(f"\n==========================================")
        print(f"NÓ: {t} ({n.get('type')})")
        print(f"==========================================")
        params = n.get('parameters', {})
        print(json.dumps(params, indent=2, ensure_ascii=False)[:1500])
