# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/JARVIS_KyGWXLxc08bemhEk.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
connections = wf.get('connections', {})

nodes_by_name = {n['name']: n for n in nodes}

print("=================================================================")
print("             RELATÓRIO DE AUDITORIA COMPLETA - JARVIS            ")
print("=================================================================\n")

# 1. AI Agent analysis
agents = [n for n in nodes if 'agent' in n.get('type', '').lower()]
print(f"--- 1. AGENTES DE IA ({len(agents)}) ---")
for ag in agents:
    print(f"Nome: {ag['name']}")
    params = ag.get('parameters', {})
    text = params.get('text', '')
    prompt = params.get('options', {}).get('systemMessage', '')
    print(f"Input Text Expression: {text}")
    print(f"System Prompt Length: {len(prompt)} caracteres")
    if prompt:
        print(f"Primeiras 300 letras do Prompt:\n{prompt[:300]}...\n")

# 2. Connections to AI Agent
print("--- 2. CONEXÕES LIGADAS AO AGENTE ---")
# Check incoming connections to AI Agent
for src, branch_dict in connections.items():
    for branch_type, targets in branch_dict.items():
        for tg in targets:
            for t in tg:
                if t.get('node') == ag['name']:
                    print(f"  [Entrada Principal] {src} ({branch_type}) -> {ag['name']}")

# Check langchain sub-node connections (ai_languageModel, ai_memory, ai_tool, etc.)
# In n8n langchain, agent connections can be from tools to agent or agent to tools depending on connection format:
for src, branch_dict in connections.items():
    for branch_type, targets in branch_dict.items():
        if 'ai_' in branch_type:
            for tg in targets:
                for t in tg:
                    print(f"  [LangChain Sub-Node] {src} --({branch_type})--> {t.get('node')}")

# Also check if agent connects to tools or tools connect to agent
print("\n--- 3. CONEXÕES SAINDO DO AGENTE ---")
if ag['name'] in connections:
    for branch_type, targets in connections[ag['name']].items():
        for tg in targets:
            for t in tg:
                print(f"  {ag['name']} --({branch_type})--> {t.get('node')}")

# 4. Check Webhook & Entrada
print("\n--- 4. PIPELINE DE ENTRADA (WEBHOOK -> AGENTE) ---")
webhook_node = nodes_by_name.get('Webhook')
if webhook_node:
    print(f"Webhook path: {webhook_node.get('parameters', {}).get('path')}")
    print(f"Webhook method: {webhook_node.get('parameters', {}).get('httpMethod')}")

# Trace path from Webhook forward
visited = []
def trace(curr, depth=0):
    if curr in visited or depth > 10:
        return
    visited.append(curr)
    if curr in connections:
        for b_name, b_list in connections[curr].items():
            for tg in b_list:
                for t in tg:
                    target_name = t.get('node')
                    print(f"{'  ' * depth} -> [{b_name}] {target_name} ({nodes_by_name.get(target_name, {}).get('type')})")
                    trace(target_name, depth + 1)

print("Caminho a partir do Webhook:")
trace('Webhook')

# 5. Check Output nodes (Sending back to WhatsApp)
print("\n--- 5. NÓS DE ENVIO / HTTP REQUEST ---")
http_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest']
for h in http_nodes:
    url = h.get('parameters', {}).get('url', '')
    method = h.get('parameters', {}).get('method', 'GET')
    print(f"  Nome: {h['name']} | Método: {method} | URL: {url}")

# 6. Check Tools list
print("\n--- 6. FERRAMENTAS IDENTIFICADAS ---")
tool_nodes = [n for n in nodes if 'tool' in n.get('type', '').lower()]
for t in tool_nodes:
    print(f"  Ferramenta: {t['name']} ({t['type']})")
    params = t.get('parameters', {})
    creds = t.get('credentials', {})
    print(f"    Credenciais: {creds if creds else 'NENHUMA (PENDENTE)'}")
    print(f"    Operação/Config: {list(params.keys())[:5]}")
