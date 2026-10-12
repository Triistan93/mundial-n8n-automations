# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/mundial-n8n-automations/workflows/JARVIS_KyGWXLxc08bemhEk.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

conns = wf.get('connections', {})
nodes = {n['name']: n for n in wf.get('nodes', [])}

print("=== 1. DEBOUNCE / BUFFER CHAIN ===")
def trace(node, depth=0, visited=None):
    if visited is None: visited = set()
    if node in visited or depth > 15: return
    visited.add(node)
    if node in conns:
        for btype, blist in conns[node].items():
            for tg in blist:
                for t in tg:
                    tname = t.get('node')
                    print(f"{'  ' * depth} -> [{btype}] {tname}")
                    trace(tname, depth + 1, visited)

trace('Seta Memória da Conversa')

print("\n=== 2. NODES INVOLVED IN DEBOUNCE & MEMORY ===")
for name in ['Seta Memória da Conversa', 'Gera Timeout no Redis', 'Remove metadados e dados que não fazem sentido enviar para o agente']:
    if name in nodes:
        print(f"\nNode: {name} ({nodes[name].get('type')})")
        print("Parameters:", json.dumps(nodes[name].get('parameters', {}), indent=2, ensure_ascii=False))

print("\n=== 3. PREPARAR DADOS ===")
if 'Preparar Dados' in nodes:
    print(json.dumps(nodes['Preparar Dados'].get('parameters', {}), indent=2, ensure_ascii=False))

print("\n=== 4. CHECA SE É MEU NÚMERO ===")
if 'Checa se é meu número' in nodes:
    print(json.dumps(nodes['Checa se é meu número'].get('parameters', {}), indent=2, ensure_ascii=False))

print("\n=== 5. SAÍDA PARA WHATSAPP / ELEVENLABS ===")
for nname in ['Seta Personalidade do J.A.R.V.I.S', 'Seta Voz via ElevenLabs', 'Envia Audio para o WhatsApp', 'Enviar Mensagem para o WhatsApp']:
    if nname in nodes:
        print(f"\nNode: {nname} ({nodes[nname].get('type')})")
        print("Parameters:", json.dumps(nodes[nname].get('parameters', {}), indent=2, ensure_ascii=False))
