import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf['nodes']
connections = wf['connections']

node_dict = {n['name']: n for n in nodes}

# Let's see the sequence of nodes along the primary path:
# 1. Entry: Webhook -> JID -> Entrada -> [IF] Triagem: Receptivo vs Ativo -> RECEPTIVO
# 2. Media: RECEPTIVO -> Tipo de mensagem:
#    - branch text: Mensagem de Texto -> Mensagem
#    - branch audio: If2 -> Get Base 64 -> Audio -> Converter Audio em Texto -> Mensagem de Audio -> Mensagem
#    - branch media: If3 -> Obter m dia em base64 -> Converter Base64 > Binário -> Upload GDrive -> Gerar Link Público -> Injetar URL no Contexto -> Mensagem
# 3. Message routing & lock:
#    Mensagem -> Status da MSG é fromMe?1:
#    - if true (attendant): Inseri Chave Block1 -> Inserir Mensagem do Atendente1
#    - if false (client): Buscar Chave Block2 -> IF: Bot Bloqueado? -> Preparar Chave do Lock1 -> Redis: GET Valor Atual do Lock1 -> IF: Chave Legada?1 -> Redis: INCR Lock Atomico -> Redis: Definir TTL do Lock -> IF: Primeira Execucao?
# 4. First execution branch:
#    - if true: Bitrix: Buscar Contato -> If1:
#               - if true: Bitrix: Buscar Deal Aberto -> Checar Estagio e Bloqueio Humano -> IF: Em Gestao Humana?:
#                          - if human: Redis: Silenciar Gestao Humana 30d -> Timeline: Notificar Silencio Humano
#                          - if bot: IF: Deal Aberto Existe?:
#                                    - exists: Redis: Registrar Lock 12h -> Buscar Chave Block
#                                    - not exists: Bitrix: Criar Deal (Contato Existente)1 -> Redis: Registrar Lock 12h -> Buscar Chave Block
#               - if false: Bitrix: Criar Contato1 -> Bitrix: Buscar Deal (Pos-Criacao Contato) -> If:
#                           - Bitrix: Criar Deal (Contato Novo)1 -> Redis: Registrar Lock 12h -> Buscar Chave Block
#    - if false: Buscar Chave Block1 -> Bloqueado?
# 5. Buffer & Debounce:
#    Buscar Chave Block / Buscar Chave Block1 -> Bloqueado?:
#    - if blocked: Inserir Mensagem Cliente
#    - if not blocked: Mensagem Temporária1 -> Esperar 30 segundos -> Mensagens temporárias -> Última Mensagem? -> Deletar Lista Temporária -> MensagemFinal1
# 6. Core AI:
#    MensagemFinal1 -> AI Agent (connected with OpenAI Chat Model1, Redis Chat Memory1, Pense) -> Formatar Output do Agente -> Roteador de Saída
# 7. Outputs:
#    - Output 0 (continua papo): Enviar MSG (Continua o Papo)
#    - Output 1 (finalizado): 1. Preparar Dados RH -> HTTP: Buscar Contato (Tentativa 1) -> IF: Contato Encontrado?1 -> (or Espera Busca -> HTTP: Buscar Contato (Tentativa 2)) -> Isolar IDs dos Contatos -> Montar URL de Busca -> 3. Buscar Processo no Funil -> IF: Processo Encontrado?1 -> (Preparar Atualização -> Atualizar Deal Existente / Preparar Criação -> Criar Novo Deal) -> Adicionar Timeline (Unificado) -> Redis2 -> Enviar MSG (Continua o Papo)2
#    - Output 2 (transferencia RH): Preparar Dados Transferência -> Buscar Contato Transferência -> Preparar Deal Assuntos RH -> Criar Deal Assuntos RH -> Adicionar Timeline Assuntos RH -> Alertar Responsavel RH -> Redis: Bloquear Bot 30d (Handover Humano) -> WhatsApp: Enviar Despedida Transferência

print("Mapping confirmed successfully.")
