# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_sdr_node_positions():
    pos = {}
    
    # =========================================================================
    # ZONA 1: 📥 01. Ingestão & Saneamento WhatsApp (X: 80, Y: 80)
    # Sticky: width=1220, height=420
    # =========================================================================
    pos['Webhook'] = [140, 180]
    pos['JID'] = [360, 180]
    pos['Entrada'] = [580, 180]
    pos['[IF] Triagem: Receptivo vs Ativo'] = [800, 180]
    pos['RECEPTIVO'] = [1020, 180]
    pos['Tipo de mensagem'] = [1020, 360]

    # =========================================================================
    # ZONA 2: 🎙️ 02. Transcrição de Áudio (Groq Whisper) (X: 1360, Y: 80)
    # Sticky: width=1160, height=420
    # =========================================================================
    pos['IF: É fromMe?'] = [1420, 180]
    pos['Get Base 64'] = [1640, 180]
    pos['Audio'] = [1860, 180]
    pos['Converter Audio em Texto'] = [2080, 180]
    pos['Mensagem de Audio'] = [2300, 180]
    pos['Mensagem de Texto'] = [1420, 360]
    pos['Mensagem'] = [1860, 360]

    # =========================================================================
    # ZONA 4: ⏱️ 04. Fila de Buffer & Debounce (15s) (X: 2580, Y: 80)
    # Sticky: width=1160, height=420
    # =========================================================================
    pos['Mensagem Temporária1'] = [2640, 180]
    pos['Esperar 15 segundos'] = [2860, 180]
    pos['Mensagens temporárias'] = [3080, 180]
    pos['Última Mensagem?'] = [3300, 180]
    pos['Deletar Lista Temporária'] = [3500, 180]
    pos['MensagemFinal1'] = [3500, 360]

    # =========================================================================
    # ZONA 3: 🔒 03. Concorrência, Lock Atômico & Human Takeover (X: 80, Y: 560)
    # Sticky: width=1840, height=640
    # =========================================================================
    # Linha 1: Detecção fromMe e Bloqueio
    pos['Status da MSG é fromMe?1'] = [140, 660]
    pos['Inserir Mensagem do Atendente1'] = [380, 660]
    pos['Inseri Chave Block1'] = [620, 660]
    pos['Buscar Chave Block2'] = [860, 660]
    pos['IF: Bot Bloqueado?'] = [1100, 660]

    # Linha 2: Lock Atômico e Tratamento Legado
    pos['Preparar Chave do Lock1'] = [140, 840]
    pos['Redis: GET Valor Atual do Lock1'] = [380, 840]
    pos['IF: Chave Legada?'] = [620, 840]
    pos['Redis: DELETE Chave Legada'] = [860, 840]
    pos['Redis: INCR Lock Atomico'] = [1100, 840]
    pos['Redis: Definir TTL do Lock'] = [1340, 840]
    pos['IF: Primeira Execucao?'] = [1580, 840]

    # Linha 3: Verificação Final e Memória
    pos['Buscar Chave Block1'] = [140, 1020]
    pos['Bloqueado?'] = [380, 1020]
    pos['Bitrix: Buscar Contato'] = [620, 1020]
    pos['Inserir Mensagem Cliente'] = [860, 1020]

    # =========================================================================
    # ZONA 5: 🧠🤖 05. Núcleo Cognitivo de IA (LangChain ReAct) (X: 1980, Y: 560)
    # Sticky: width=1760, height=640
    # =========================================================================
    # Satélites da IA (à esquerda e abaixo)
    pos['Redis Chat Memory1'] = [2040, 700]
    pos['OpenAI Chat Model1'] = [2040, 920]
    pos['Think'] = [2260, 920]
    
    # Agente central
    pos['AI Agent'] = [2380, 700]
    
    # Saída e Roteamento
    pos['Formatar Output do Agente'] = [2720, 700]
    pos['Roteador de Saída'] = [3040, 700]
    pos['Enviar MSG (Continua o Papo)'] = [3400, 700]
    pos['Redis'] = [3400, 920]

    # =========================================================================
    # ZONA 6: 📇🔎 06. Resolução, Saneamento & Deduplicação de Contatos Bitrix24 (X: 80, Y: 1260)
    # Sticky: width=3660, height=500
    # =========================================================================
    # Linha 1: Preparação e Buscas
    pos['1. Preparar Dados Lead'] = [140, 1360]
    pos['HTTP: Buscar Contato (Tentativa 1)'] = [420, 1360]
    pos['IF: Contato Encontrado?1'] = [700, 1360]
    pos['Espera Busca'] = [960, 1360]
    pos['HTTP: Buscar Contato (Tentativa 2)'] = [1220, 1360]
    pos['IF: Contato existe na 2ª busca?'] = [1480, 1360]
    pos['Criar Contato Bitrix'] = [1740, 1360]
    pos['Normalizar contato'] = [2000, 1360]

    # Linha 2: Deduplicação e Open Lines
    pos['Desmembrar IDs para Consulta'] = [700, 1560]
    pos['HTTP: Consultar Open Lines'] = [960, 1560]
    pos['Garantir Contato com Chat na Linha'] = [1260, 1560]
    pos['IF: Há Duplicados?'] = [1600, 1560]
    pos['HTTP: Mesclar Contatos Nativos (crm.entity.mergeBatch)'] = [1900, 1560]
    pos['HTTP: Atualizar Telefone Contato Salvo'] = [2240, 1560]

    # =========================================================================
    # ZONA 7: 🏢📋 07. Gestão de Cards no Funil (C18) & Linha do Tempo (X: 80, Y: 1820)
    # Sticky: width=1840, height=680
    # =========================================================================
    pos['Montar URL de Busca'] = [140, 1920]
    pos['3. Buscar Processo no Funil'] = [380, 1920]
    pos['IF: Processo Encontrado?1'] = [640, 1920]
    
    # Ramo A: Atualização de Card Existente
    pos['Preparar Payload de Atualização1'] = [940, 1920]
    pos['4a. Atualizar Card Existente1'] = [1220, 1920]
    pos['5a. Adicionar Nova Info no Timeline1'] = [1500, 1920]
    
    # Ramo B: Criação de Novo Card (Fallback)
    pos['Preparar Payload de Criação (Fallback)'] = [940, 2160]
    pos['4b. Criar Card de Candidato1 (Fallback)'] = [1220, 2160]
    pos['Vincular Contato ao Deal'] = [1500, 2160]
    pos['5b. Adicionar Log no Timeline (Novo Card)'] = [1500, 2340]

    # =========================================================================
    # ZONA 8: 🚀 08. Transição de Etapa, Handover OpenLines & Despedida (X: 1980, Y: 1820)
    # Sticky: width=1760, height=680
    # =========================================================================
    pos['Normalizar IDs Finais'] = [2040, 1920]
    pos['IF: Há etapa de destino?'] = [2280, 1920]
    pos['Mover Card de Etapa'] = [2520, 1920]
    pos['Rotear POS CRM'] = [2780, 1920]
    
    # Handover Open Lines & Bloqueio
    pos['Buscar Chat do Contato'] = [3040, 1920]
    pos['Extrair CHAT_ID'] = [3260, 1920]
    pos['IF: Há chat para transferir?'] = [3480, 1920]
    pos['Transferir Chat Pós-Venda'] = [3480, 2100]
    pos['Bloquear Bot 24h'] = [3040, 2180]
    pos['Enviar MSG Final'] = [3300, 2180]

    return pos

if __name__ == '__main__':
    with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json', 'r', encoding='utf-8') as f:
        wf = json.load(f)
    
    functional_names = [n['name'] for n in wf['nodes'] if not n['type'].endswith('stickyNote')]
    pos = get_sdr_node_positions()
    
    missing = [name for name in functional_names if name not in pos]
    extra = [name for name in pos if name not in functional_names]
    
    print(f"Total functional nodes in workflow: {len(functional_names)}")
    print(f"Total positions defined: {len(pos)}")
    print(f"Missing positions: {missing}")
    print(f"Extra positions: {extra}")
    
    if not missing and not extra:
        print("\nPERFEITO! Todos os 77 nós funcionais possuem coordenadas exatas definidas.")
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        print(f"Nova largura total: {max(xs) - min(xs)} px (X: {min(xs)} a {max(xs)})")
        print(f"Nova altura total: {max(ys) - min(ys)} px (Y: {min(ys)} a {max(ys)})")
        print(f"Nova proporção de tela: {(max(xs) - min(xs)) / (max(ys) - min(ys)):.2f} : 1")
