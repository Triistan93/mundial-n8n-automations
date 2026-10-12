import json

path = r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json'
with open(path, 'r', encoding='utf-8-sig') as f:
    wf = json.load(f)

nodes = {n['name']: n for n in wf.get('nodes', [])}
connections = wf.get('connections', {})

def inspect_nodes(target_names):
    for name in target_names:
        n = nodes.get(name)
        if not n:
            print(f'Node not found: {name}')
            continue
        print(f"=== {name} [{n.get('type')}] ===")
        p = n.get('parameters', {})
        for k in ['url', 'method', 'operation', 'key', 'propertyName', 'value', 'jsCode', 'conditions', 'values', 'sendBody', 'bodyParameters', 'jsonParameters', 'body']:
            if k in p:
                val = p[k]
                if isinstance(val, (dict, list)):
                    print(f"  {k}: {json.dumps(val, indent=2, ensure_ascii=False)}")
                else:
                    print(f"  {k}: {val}")
        print()

print("--- ANALYZING BRANCH 1: INGRESSO & PRIMEIRA EXECUCAO ---")
inspect_nodes([
    'Webhook',
    'JID',
    'Entrada',
    '[IF] Triagem: Receptivo vs Ativo',
    'RECEPTIVO',
    'Status da MSG é fromMe?1',
    'Inseri Chave Block1',
    'Buscar Chave Block2',
    'IF: Bot Bloqueado?',
    'Preparar Chave do Lock1',
    'Redis: GET Valor Atual do Lock1',
    'IF: Chave Legada?1',
    'Redis: INCR Lock Atomico',
    'Redis: Definir TTL do Lock',
    'IF: Primeira Execucao?',
    'Bitrix: Buscar Contato',
    'If1',
    'Bitrix: Buscar Deal Aberto',
    'IF: Deal Aberto Existe?',
    'Bitrix: Criar Deal (Contato Existente)1',
    'Bitrix: Criar Contato1',
    'Bitrix: Buscar Deal (Pos-Criacao Contato)',
    'If',
    'Bitrix: Criar Deal (Contato Novo)1',
    'Redis: Registrar Lock 12h'
])
