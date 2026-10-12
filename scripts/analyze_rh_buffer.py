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
        for k in ['url', 'method', 'operation', 'key', 'propertyName', 'value', 'jsCode', 'conditions', 'values', 'sendBody', 'bodyParameters', 'jsonParameters', 'body', 'text', 'options']:
            if k in p:
                val = p[k]
                if isinstance(val, (dict, list)):
                    print(f"  {k}: {json.dumps(val, indent=2, ensure_ascii=False)}")
                else:
                    print(f"  {k}: {val}")
        print()

print("--- ANALYZING MESSAGE ROUTING & BUFFERING ---")
inspect_nodes([
    'Tipo de mensagem',
    'Mensagem de Texto',
    'If2',
    'Get Base 64',
    'Audio',
    'Converter Audio em Texto',
    'Mensagem de Audio',
    'If3',
    'Obter m dia em base64',
    'Converter Base64 > Binário',
    'Upload GDrive',
    'Gerar Link Público',
    'Injetar URL no Contexto',
    'Mensagem',
    'Buscar Chave Block',
    'Bloqueado?',
    'Mensagem Temporária1',
    'Esperar 30 segundos',
    'Mensagens temporárias',
    'Última Mensagem?',
    'Deletar Lista Temporária',
    'MensagemFinal1',
    'Inserir Mensagem Cliente',
    'Redis Chat Memory1',
    'AI Agent',
    'Formatar Output do Agente',
    'Roteador de Saída',
    'Enviar MSG (Continua o Papo)',
    '1. Preparar Dados RH'
])
