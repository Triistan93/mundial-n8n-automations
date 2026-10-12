# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}
conns = wf.get('connections', {})

print("=================================================================")
print("          FLUXO COMPLETO: SDR MUNDIAL MOTOS (UNIFICADO)         ")
print("=================================================================\n")

# 1. Webhook e Entrada
print("--- 1. ENTRADA & WEBHOOK ---")
webhook = nodes.get('Webhook')
if webhook:
    print("Webhook parameters:", json.dumps(webhook.get('parameters', {}), indent=2, ensure_ascii=False))

# Trace a partir do Webhook
def trace_path(start, depth=0, visited=None):
    if visited is None: visited = set()
    if start in visited or depth > 8: return
    visited.add(start)
    if start in conns:
        for btype, blist in conns[start].items():
            for tg in blist:
                for t in tg:
                    tname = t.get('node')
                    print(f"{'  ' * depth}└─[{btype}] {tname} ({nodes.get(tname, {}).get('type')})")
                    trace_path(tname, depth + 1, visited)

print("\nCadeia inicial a partir do Webhook:")
trace_path('Webhook')

# 2. Nós HTTP (Bitrix24, Evolution, etc.)
print("\n--- 2. NÓS HTTP REQUEST (CRM BITRIX E EVOLUTION) ---")
http_nodes = [n for n in wf.get('nodes', []) if n.get('type') == 'n8n-nodes-base.httpRequest']
for h in http_nodes:
    params = h.get('parameters', {})
    url = params.get('url', '')
    method = params.get('method', 'GET')
    print(f"• {h['name']} [{method}]: {url}")

# 3. Formatação de Output & Roteador
print("\n--- 3. SAÍDA DA IA & ROTEAMENTO ---")
for r_name in ['Formatar Output', 'Roteador', 'Roteador1', 'Switch', 'Condicional de Saída']:
    for n in wf.get('nodes', []):
        if r_name.lower() in n['name'].lower():
            print(f"• Nó: {n['name']} ({n['type']})")
            print("  Params:", json.dumps(n.get('parameters', {}), indent=2, ensure_ascii=False)[:300])

# 4. Prompt do AI Agent (Regras de negócio, qualificação, etapas)
print("\n--- 4. SYSTEM PROMPT DO SDR ---")
agent = nodes.get('AI Agent')
if agent:
    prompt = agent.get('parameters', {}).get('options', {}).get('systemMessage', '')
    print(f"Tamanho total: {len(prompt)} caracteres\n")
    # Mostrar tópicos / seções do prompt
    for line in prompt.split('\n'):
        if line.startswith('#') or line.startswith('REGRA') or line.startswith('PASSO') or line.startswith('ETAPA') or line.startswith('FILIAIS') or line.startswith('MODELOS'):
            print(f"  {line}")

# 5. Análise de URLs do Bitrix24 e Webhook URL
print("\n--- 5. WEBHOOKS BITRIX24 IDENTIFICADOS ---")
bitrix_urls = set()
for h in http_nodes:
    url = h.get('parameters', {}).get('url', '')
    if 'bitrix' in url.lower():
        # mask token partially
        parts = url.split('/rest/')
        if len(parts) > 1:
            bitrix_urls.add(parts[0] + '/rest/' + parts[1].split('/')[0] + '/...')
        else:
            bitrix_urls.add(url)
for bu in bitrix_urls:
    print(f"  • {bu}")
