import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Let's define the layout coordinates for all nodes in AGENTE_RH_COM_CORRECOES.json

def get_node_positions():
    pos = {}

    # =========================================================================
    # ZONA 1: INGESTÃO & SANEAMENTO WHATSAPP (X: 100 .. 1100, Y: 100 .. 320)
    # =========================================================================
    pos['Webhook'] = [140, 200]
    pos['JID'] = [360, 200]
    pos['Entrada'] = [580, 200]
    pos['[IF] Triagem: Receptivo vs Ativo'] = [800, 200]
    pos['RECEPTIVO'] = [1020, 200]

    # =========================================================================
    # ZONA 2: PROCESSAMENTO DE MÍDIA & CURRÍCULOS (X: 1300 .. 3100, Y: 60 .. 560)
    # =========================================================================
    pos['Tipo de mensagem'] = [1340, 260]

    # Linha Texto (Topo)
    pos['Mensagem de Texto'] = [1600, 120]

    # Linha Áudio (Meio)
    pos['If2'] = [1600, 260]
    pos['Get Base 64'] = [1820, 260]
    pos['Audio'] = [2040, 260]
    pos['Converter Audio em Texto'] = [2260, 260]
    pos['Mensagem de Audio'] = [2480, 260]

    # Linha Documento/Currículo (Fundo)
    pos['If3'] = [1600, 440]
    pos['Obter m dia em base64'] = [1820, 440]
    pos['Converter Base64 > Binário'] = [2040, 440]
    pos['Upload GDrive'] = [2260, 440]
    pos['Gerar Link Público'] = [2480, 440]
    pos['Injetar URL no Contexto'] = [2700, 440]

    # Convergência da Mensagem
    pos['Mensagem'] = [2980, 260]

    # =========================================================================
    # ZONA 3: CONCORRÊNCIA & LOCK ATÔMICO REDIS (X: 100 .. 1400, Y: 720 .. 1220)
    # =========================================================================
    pos['Status da MSG é fromMe?1'] = [140, 800]

    # Ramo Atendente Humano (fromMe = true)
    pos['Inseri Chave Block1'] = [140, 980]
    pos['Inserir Mensagem do Atendente1'] = [140, 1140]

    # Ramo Cliente (fromMe = false)
    pos['Buscar Chave Block2'] = [360, 800]
    pos['IF: Bot Bloqueado?'] = [580, 800]
    pos['Preparar Chave do Lock1'] = [800, 800]
    pos['Redis: GET Valor Atual do Lock1'] = [1020, 800]
    pos['IF: Chave Legada?1'] = [1240, 800]
    pos['Redis: DELETE Chave Legada'] = [1240, 980]
    pos['Redis: INCR Lock Atomico'] = [1460, 800]
    pos['Redis: Definir TTL do Lock'] = [1680, 800]
    pos['IF: Primeira Execucao?'] = [1900, 800]

    # =========================================================================
    # ZONA 4: VERIFICAÇÃO CRM & GESTÃO HUMANA (X: 1600 .. 3300, Y: 720 .. 1220)
    # =========================================================================
    pos['Bitrix: Buscar Contato'] = [2140, 800]
    pos['If1'] = [2360, 800]

    # Contato Existe
    pos['Bitrix: Buscar Deal Aberto'] = [2580, 740]
    pos['Checar Estagio e Bloqueio Humano'] = [2800, 740]
    pos['IF: Em Gestao Humana?'] = [3020, 740]

    # Sub-ramo Humano (Silêncio 30d)
    pos['Redis: Silenciar Gestao Humana 30d'] = [3260, 680]
    pos['Timeline: Notificar Silencio Humano'] = [3500, 680]

    # Sub-ramo Robô
    pos['IF: Deal Aberto Existe?'] = [3260, 800]
    pos['Bitrix: Criar Deal (Contato Existente)1'] = [3500, 840]
    pos['Redis: Registrar Lock 12h'] = [3740, 800]

    # Contato Não Existe
    pos['Bitrix: Criar Contato1'] = [2580, 980]
    pos['Bitrix: Buscar Deal (Pos-Criacao Contato)'] = [2800, 980]
    pos['If'] = [3020, 980]
    pos['Bitrix: Criar Deal (Contato Novo)1'] = [3260, 980]

    # =========================================================================
    # ZONA 5: BUFFER DEBOUNCE (30s) (X: 100 .. 1500, Y: 1380 .. 1720)
    # =========================================================================
    pos['Buscar Chave Block1'] = [140, 1480]
    pos['Buscar Chave Block'] = [140, 1620]
    pos['Bloqueado?'] = [360, 1540]
    pos['Inserir Mensagem Cliente'] = [360, 1720]

    pos['Mensagem Temporária1'] = [580, 1540]
    pos['Esperar 30 segundos'] = [800, 1540]
    pos['Mensagens temporárias'] = [1020, 1540]
    pos['Última Mensagem?'] = [1240, 1540]
    pos['Deletar Lista Temporária'] = [1460, 1540]
    pos['MensagemFinal1'] = [1680, 1540]

    # =========================================================================
    # ZONA 6: NÚCLEO COGNITIVO DE IA (LANGCHAIN) (X: 1900 .. 2800, Y: 1380 .. 1800)
    # =========================================================================
    pos['AI Agent'] = [2180, 1540]

    # Satélites à esquerda do Agent
    pos['OpenAI Chat Model1'] = [1960, 1420]
    pos['Pense'] = [1960, 1540]
    pos['Redis Chat Memory1'] = [1960, 1660]

    # Saídas cognitivas
    pos['Formatar Output do Agente'] = [2420, 1540]
    pos['Roteador de Saída'] = [2660, 1540]

    # =========================================================================
    # ZONA 7: AS 3 TRILHAS DE EXECUÇÃO & SAÍDA (Y: 1920 .. 2800)
    # =========================================================================
    # Trilha 1: Conversa Contínua no WhatsApp (X: 100 .. 600, Y: 1980)
    pos['Enviar MSG (Continua o Papo)'] = [260, 2060]

    # Trilha 2: Candidato Finalizado - Bitrix C198 (X: 750 .. 3900, Y: 1940 .. 2360)
    pos['1. Preparar Dados RH'] = [760, 2060]
    pos['HTTP: Buscar Contato (Tentativa 1)'] = [980, 2060]
    pos['IF: Contato Encontrado?1'] = [1200, 2060]

    # Ramo Busca Tentativa 2
    pos['Espera Busca'] = [1200, 2220]
    pos['HTTP: Buscar Contato (Tentativa 2)'] = [1420, 2220]

    pos['Isolar IDs dos Contatos'] = [1420, 2060]
    pos['Montar URL de Busca'] = [1640, 2060]
    pos['3. Buscar Processo no Funil'] = [1860, 2060]
    pos['IF: Processo Encontrado?1'] = [2080, 2060]

    # Atualização
    pos['Preparar Atualização'] = [2320, 2000]
    pos['Atualizar Deal Existente'] = [2540, 2000]

    # Criação
    pos['Preparar Criação'] = [2320, 2120]
    pos['Criar Novo Deal'] = [2540, 2120]

    # Convergência Trilha 2
    pos['Adicionar Timeline (Unificado)'] = [2780, 2060]
    pos['Redis2'] = [3000, 2060]
    pos['Enviar MSG (Continua o Papo)2'] = [3220, 2060]

    # Trilha 3: Handover Inteligente para RH (Nina Biermann) (X: 750 .. 2600, Y: 2480 .. 2720)
    pos['Preparar Dados Transferência'] = [760, 2560]
    pos['Buscar Contato Transferência'] = [980, 2560]
    pos['Preparar Deal Assuntos RH'] = [1200, 2560]
    pos['Criar Deal Assuntos RH'] = [1420, 2560]
    pos['Adicionar Timeline Assuntos RH'] = [1640, 2560]
    pos['Alertar Responsavel RH'] = [1860, 2560]
    pos['Redis: Bloquear Bot 30d (Handover Humano)'] = [2080, 2560]
    pos['WhatsApp: Enviar Despedida Transferência'] = [2300, 2560]

    return pos

pos_dict = get_node_positions()
print(f"Total mapped positions: {len(pos_dict)}")

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

functional_nodes = [n for n in wf['nodes'] if not n['type'].endswith('stickyNote')]
print(f"Total functional nodes in workflow: {len(functional_nodes)}")

missing = [n['name'] for n in functional_nodes if n['name'] not in pos_dict]
if missing:
    print(f"MISSING: {missing}")
else:
    print("ALL functional nodes mapped successfully!")
