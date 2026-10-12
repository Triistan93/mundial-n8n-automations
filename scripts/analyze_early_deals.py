import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json'
with open(path, 'r', encoding='utf-8-sig') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}

def inspect_exact_node(name):
    n = nodes.get(name)
    if not n:
        print(f"Not found: {name}")
        return
    print(f"=== {name} ===")
    print(json.dumps(n, indent=2, ensure_ascii=False))

inspect_exact_node("Bitrix: Buscar Deal Aberto")
inspect_exact_node("Bitrix: Criar Deal (Contato Existente)1")
inspect_exact_node("Bitrix: Criar Deal (Contato Novo)1")
