# -*- coding: utf-8 -*-
import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
connections = wf.get('connections', {})
nodes_by_name = {n['name']: n for n in nodes}

print("=================================================================")
print("     AUDITORIA COMPLETA: SDR - MUNDIAL MOTOS (UNIFICADO)        ")
print("=================================================================\n")
print(f"ID: {wf.get('id')}")
print(f"Nome: {wf.get('name')}")
print(f"Ativo: {wf.get('active')}")
print(f"Total de Nós: {len(nodes)}")

# Contagem de tipos
type_counts = Counter(n.get('type') for n in nodes)
print("\n--- DISTRIBUIÇÃO DE TIPOS DE NÓS ---")
for t, c in type_counts.most_common():
    print(f"  {t}: {c}")

# Triggers
triggers = [n for n in nodes if any(k in n.get('type', '').lower() for k in ['trigger', 'webhook', 'schedule', 'poll'])]
print(f"\n--- GATILHOS / ENTRADAS ({len(triggers)}) ---")
for tr in triggers:
    params = tr.get('parameters', {})
    print(f"  - {tr['name']} ({tr['type']}) | Path/Schedule: {params.get('path', params.get('rule', ''))} | Disabled: {tr.get('disabled', False)}")

# Credenciais
creds_used = {}
for n in nodes:
    if 'credentials' in n and n['credentials']:
        for k, v in n['credentials'].items():
            creds_used.setdefault(k, []).append((n['name'], v))
print(f"\n--- CREDENCIAIS REFERENCIADAS ({len(creds_used)}) ---")
for k, v in creds_used.items():
    print(f"  Tipo: {k} ({len(v)} nós)")
    for nname, cdata in v:
        print(f"    - Nó: {nname} -> Credential: {cdata}")

# Agentes de IA
agents = [n for n in nodes if 'agent' in n.get('type', '').lower()]
print(f"\n--- NÚCLEO COGNITIVO / AGENTES DE IA ({len(agents)}) ---")
for ag in agents:
    print(f"Nome: {ag['name']} ({ag['type']})")
    params = ag.get('parameters', {})
    prompt = params.get('options', {}).get('systemMessage', '')
    text_in = params.get('text', '')
    print(f"  Entrada de Texto: {text_in}")
    print(f"  Tamanho do System Prompt: {len(prompt)} caracteres")
    if prompt:
        print("  Primeiros 400 caracteres do Prompt:")
        print("  " + prompt[:400].replace('\n', '\n  ') + "...\n")

# Modelos LLM e Memória conectados
print("--- MODELOS LLM, MEMÓRIA E FERRAMENTAS ---")
for ag in agents:
    for src, bdict in connections.items():
        for btype, tglist in bdict.items():
            for tg in tglist:
                for t in tg:
                    if t.get('node') == ag['name']:
                        src_node = nodes_by_name.get(src, {})
                        print(f"  [{btype}] {src} ({src_node.get('type')})")

# Integridade de Conexões
node_names = set(nodes_by_name.keys())
missing_src = set()
missing_tgt = set()
for src, branches in connections.items():
    if src not in node_names:
        missing_src.add(src)
    for b_name, b_list in branches.items():
        for tg in b_list:
            for t in tg:
                t_name = t.get('node')
                if t_name not in node_names:
                    missing_tgt.add(t_name)

print("\n--- INTEGRIDADE DO GRAFO ---")
print(f"Fontes faltando: {missing_src if missing_src else 'Nenhuma (100% OK)'}")
print(f"Alvos faltando: {missing_tgt if missing_tgt else 'Nenhum (100% OK)'}")

# Sticky Notes
stickies = [n for n in nodes if n.get('type') == 'n8n-nodes-base.stickyNote']
print(f"\n--- STICKY NOTES ({len(stickies)}) ---")
for s in stickies:
    lines = [l for l in s.get('parameters', {}).get('content', '').split('\n') if l.strip()]
    header = lines[0] if lines else 'Vazio'
    print(f"  - {s['name']}: {header}")
