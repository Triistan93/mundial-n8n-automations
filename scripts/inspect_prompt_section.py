# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_HOMOLOG.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}
agent = nodes.get('AI Agent')
prompt = agent.get('parameters', {}).get('options', {}).get('systemMessage', '')

# Find where the JSON output format is described
marker = "# FORMATO DE SAÍDA OBRIGATÓRIO"
idx = prompt.find(marker)
if idx != -1:
    print("Seção de Formato de Saída encontrada!")
    print(prompt[idx:idx+1500])
else:
    print("Marker não encontrado, procurando json...")
    for line in prompt.split('\n'):
        if 'status_triagem' in line:
            print(line)
