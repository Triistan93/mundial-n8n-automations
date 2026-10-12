import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json'
with open(path, 'r', encoding='utf-8-sig') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}

def inspect_nodes(target_names):
    for name in target_names:
        n = nodes.get(name)
        if not n:
            print(f'Node not found: {name}')
            continue
        print(f"=== {name} [{n.get('type')}] ===")
        p = n.get('parameters', {})
        for k in ['url', 'method', 'operation', 'key', 'propertyName', 'value', 'jsCode', 'conditions', 'rules', 'values', 'assignments', 'sendBody', 'bodyParameters', 'jsonParameters', 'body', 'text', 'options']:
            if k in p:
                val = p[k]
                if isinstance(val, (dict, list)):
                    print(f"  {k}: {json.dumps(val, indent=2, ensure_ascii=False)}")
                else:
                    print(f"  {k}: {val}")
        print()

print("--- ANALYZING END OF FLOW: ROTEADOR DE SAIDA & BITRIX SYNC ---")
inspect_nodes([
    'Preparar Atualização',
    'Preparar Criação',
    'Atualizar Deal Existente',
    'Criar Novo Deal',
    'Adicionar Timeline (Unificado)',
    'Redis2',
    'Enviar MSG (Continua o Papo)2'
])
