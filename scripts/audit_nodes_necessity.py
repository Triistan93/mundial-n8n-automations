import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('workflows/canonical/AGENTE_RH_COM_CORRECOES.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf['nodes']
connections = wf['connections']

# Let's map out groups of nodes and evaluate their necessity
"""
Architecture Groups:
1. Canvas Documentation: 9 Sticky Notes
2. Webhook & Ingestion: Webhook, JID, Entrada, [IF] Triagem: Receptivo vs Ativo, RECEPTIVO (5 nodes)
3. Media & Audio Processing: Tipo de mensagem, Mensagem de Texto, If2, Get Base 64, Audio, Converter Audio em Texto, Mensagem de Audio, If3, Obter m dia em base64, Converter Base64 > Binário, Upload GDrive, Gerar Link Público, Injetar URL no Contexto, Mensagem (14 nodes)
4. Anti-Race & Concurrency (Debounce + Redis Lock):
   Status da MSG é fromMe?1, Inseri Chave Block1, Inserir Mensagem do Atendente1, Buscar Chave Block2, IF: Bot Bloqueado?, Preparar Chave do Lock1, Redis: GET Valor Atual do Lock1, IF: Chave Legada?1, Redis: DELETE Chave Legada, Redis: INCR Lock Atomico, Redis: Definir TTL do Lock, IF: Primeira Execucao? (12 nodes)
5. Early Bitrix Verification / Human Takeover Silence:
   Bitrix: Buscar Contato, If1, Bitrix: Buscar Deal Aberto, Checar Estagio e Bloqueio Humano, IF: Em Gestao Humana?, Redis: Silenciar Gestao Humana 30d, Timeline: Notificar Silencio Humano, IF: Deal Aberto Existe?, Bitrix: Criar Deal (Contato Existente)1, Bitrix: Criar Contato1, Bitrix: Buscar Deal (Pos-Criacao Contato), If, Bitrix: Criar Deal (Contato Novo)1, Redis: Registrar Lock 12h (14 nodes)
6. 30s Buffer Queue & De-duplication:
   Buscar Chave Block, Buscar Chave Block1, Bloqueado?, Inserir Mensagem Cliente, Mensagem Temporária1, Esperar 30 segundos, Mensagens temporárias, Última Mensagem?, Deletar Lista Temporária, MensagemFinal1 (10 nodes)
7. Core AI Engine:
   AI Agent, OpenAI Chat Model1, Redis Chat Memory1, Pense, Formatar Output do Agente, Roteador de Saída (6 nodes)
8. Branch 1 - Continuar Papo:
   Enviar MSG (Continua o Papo) (1 node)
9. Branch 2 - Candidato Finalizado (Atualização/Criação no Bitrix):
   1. Preparar Dados RH, HTTP: Buscar Contato (Tentativa 1), IF: Contato Encontrado?1, Espera Busca, HTTP: Buscar Contato (Tentativa 2), Isolar IDs dos Contatos, Montar URL de Busca, 3. Buscar Processo no Funil, IF: Processo Encontrado?1, Preparar Atualização, Preparar Criação, Atualizar Deal Existente, Criar Novo Deal, Adicionar Timeline (Unificado), Redis2, Enviar MSG (Continua o Papo)2 (16 nodes)
10. Branch 3 - Handover para RH (Assuntos Gerais, Saúde, DP, B2B):
   Preparar Dados Transferência, Buscar Contato Transferência, Preparar Deal Assuntos RH, Criar Deal Assuntos RH, Adicionar Timeline Assuntos RH, Alertar Responsavel RH, Redis: Bloquear Bot 30d (Handover Humano), WhatsApp: Enviar Despedida Transferência (8 nodes)
Total = 9 + 5 + 14 + 12 + 14 + 10 + 6 + 1 + 16 + 8 = 95 nodes!
"""

print(f"Total verified: {len(nodes)} nodes.")
