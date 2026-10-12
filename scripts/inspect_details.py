# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/JARVIS_KyGWXLxc08bemhEk.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}
conns = wf.get('connections', {})

print("==================================================")
print("1. AGENTE J.A.R.V.I.S E LLM CONECTADO")
print("==================================================")
jarvis = nodes.get('J.A.R.V.I.S')
if jarvis:
    print("Agent Type:", jarvis.get('type'))
    print("Agent Parameters:", json.dumps(jarvis.get('parameters', {}), indent=2, ensure_ascii=False))

print("\nIncoming to J.A.R.V.I.S:")
for src, bdict in conns.items():
    for btype, targets in bdict.items():
        for tg in targets:
            for t in tg:
                if t.get('node') == 'J.A.R.V.I.S':
                    src_node = nodes.get(src, {})
                    print(f"  [{btype}] {src} ({src_node.get('type')}) - Creds: {src_node.get('credentials')}")

print("\n==================================================")
print("2. CHAIN LLM (SETA PERSONALIDADE)")
print("==================================================")
chain = nodes.get('Seta Personalidade do J.A.R.V.I.S')
if chain:
    print("Chain Type:", chain.get('type'))
    # check what LLM is connected to it
    for src, bdict in conns.items():
        for btype, targets in bdict.items():
            for tg in targets:
                for t in tg:
                    if t.get('node') == 'Seta Personalidade do J.A.R.V.I.S':
                        print(f"  Connected to Chain: {src} ({btype})")

print("\n==================================================")
print("3. REDIS NODES & CONFIG")
print("==================================================")
redis_nodes = [n for n in wf.get('nodes', []) if 'redis' in n.get('type', '').lower() or 'redis' in n['name'].lower()]
for rn in redis_nodes:
    print(f"Node: {rn['name']} ({rn.get('type')})")
    print(f"  Credentials: {rn.get('credentials')}")
    print(f"  Parameters: {rn.get('parameters')}")

print("\n==================================================")
print("4. PINECONE & EMBEDDINGS (RAG)")
print("==================================================")
pinecone_nodes = [n for n in wf.get('nodes', []) if 'pinecone' in n.get('type', '').lower() or 'vector' in n.get('type', '').lower()]
for pn in pinecone_nodes:
    print(f"Node: {pn['name']} ({pn.get('type')})")
    print(f"  Credentials: {pn.get('credentials')}")
    print(f"  Parameters: {pn.get('parameters')}")

print("\n==================================================")
print("5. MCP SERVERS CONFIG")
print("==================================================")
mcp_nodes = [n for n in wf.get('nodes', []) if 'mcp' in n.get('type', '').lower() or 'mcp' in n['name'].lower()]
for mn in mcp_nodes:
    print(f"Node: {mn['name']} ({mn.get('type')})")
    print(f"  Credentials: {mn.get('credentials')}")
    print(f"  Parameters: {mn.get('parameters')}")

print("\n==================================================")
print("6. CONDICIONAL DE SAÍDA (ÁUDIO VS TEXTO)")
print("==================================================")
# Check what J.A.R.V.I.S outputs to:
if 'J.A.R.V.I.S' in conns:
    print("J.A.R.V.I.S outputs to:", conns['J.A.R.V.I.S'])

# Check 'Se o retorno for menos de 601 caracteres gera voz'
cond_voz = nodes.get('Se o retorno for menos de 601 caracteres gera voz')
if cond_voz:
    print("\nCondição Voz Parameters:", json.dumps(cond_voz.get('parameters', {}), indent=2, ensure_ascii=False))
