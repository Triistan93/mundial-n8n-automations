# -*- coding: utf-8 -*-
"""
Script de Reingestão Vetorial no pgvector (kb_ti_conhecimento)
Atualiza KB-001 (ATPV-e com aprendizado de Saída Final DMS),
KB-019 (Robô Entrada Honda com aprendizado de Erro 500 e Loop de 15 min),
e insere KB-020 (Permissão e Módulos Bitrix24).
"""
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

N8N_SQL_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
INGEST_WEBHOOK = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-ingest'

print("1. Removendo chunks anteriores de KB-001, KB-019 e KB-020 no PostgreSQL...")
del_sql = "DELETE FROM kb_ti_conhecimento WHERE metadata->>'kb_id' IN ('KB-001', 'KB-019', 'KB-020');"
r_del = requests.post(N8N_SQL_URL, json={'query': del_sql})
print("Resultado da limpeza:", r_del.json())

docs = [
    {
        "kb_id": "KB-001",
        "title": "Emissão de ATPV-e, RENAVE e Detran: Venda Final vs Transferência e Reprocessamento de Saída no DMS",
        "systems": "MicroWork Cloud DMS, Portal RENAVE, Detran, Intenção de Venda, ATPV-e",
        "keywords": "atpv, atpv-e, renave, detran, intencao de venda, intenção de venda, chassi, 9c2, transferência interna, venda final, saída comprador final, serviço de nota fiscal indisponivel, reprocessar movimento saida",
        "source": "KB-001-atpv-renave-detran.md",
        "text": """# KB-001 - Emissão de ATPV-e, RENAVE e Intenção de Venda no MicroWork Cloud
Sistemas: MicroWork Cloud (DMS Cloud), Portal RENAVE, Detran-SP
Palavras-chave: atpv, atpv-e, renave, detran, intencao de venda, intenção de venda, chassi, 9c2, transferência interna, venda final, saída comprador final, serviço de nota fiscal indisponivel, reprocessar movimento saida

## 1. Regra de Triagem L1 (Sophia AI)
- **Transferência entre Lojas Internas:** A equipe de TI NÃO emite ATPV para transferências entre concessionárias internas da rede Mundial. O colaborador deve ser orientado a seguir a rotina de transferência de estoque.
- **Venda para Cliente Final:** Exige a emissão da ATPV-e pela TI.

## 2. Dados Obrigatórios para a Triagem
- **Chassi Completo de 17 caracteres:** Iniciando obrigatoriamente por 9C2...
- **Print da Tela de Erro:** Captura legível do MicroWork com a mensagem de erro.

## 3. Procedimento Técnico da TI no MicroWork Cloud
Rotina: [Renave - MicroWork CLOUD DMS](https://microworkcloud.com.br/cloud/#/veiculo/estoque/renave)
Passo a passo:
1. Filtrar pelo Chassi informado;
2. Em Período, selecionar a opção 'PERÍODO';
3. Desmarcar o filtro 'NOVO';
4. Selecionar a Filial correspondente;
5. Clicar em Busca e transmitir a intenção de venda.

## 4. Causa Raiz e Solução para "Não existe intenção de venda disponível" (Incidente Real #1410592 - Nataelen)
- **Sintoma:** Ao tentar baixar a ATPV no Renave, o sistema exibe: 'Não existe intenção de venda disponível para veículo com chassi 9C2...' ou 'Status: UnprocessableEntity'.
- **Causa Raiz Técnica:** No DMS Cloud, o movimento de saída para o comprador final travou com o erro 'Serviço de nota fiscal indisponivel', impedindo a geração automática da intenção de venda no módulo de estoque.
- **Solução Técnica da TI:**
  1. Acessar o movimento de saída do veículo para o comprador final no MicroWork Cloud;
  2. Reprocessar o movimento de saída final para normalizar o serviço de nota fiscal;
  3. Retornar à rotina do Renave e gerar/transmitir a ATPV normalmente."""
    },
    {
        "kb_id": "KB-019",
        "title": "Robôs de Automação RPA: Entrada Honda, Entrada Grupo, Vigia, Loop de Processamento e Tratamento de Erro 500",
        "systems": "Automações RPA, Servidor de Produção, MicroWork Cloud Rotina 1719, Mission Control, Bitrix24 Funil 122",
        "keywords": "robo, robô, rpa, card robo, card robô, entrada honda, entrada grupo, faturamento direto, vigia, dms_vigia, loop processamento, solicitacao de entrada, erro 500 microwork, cookies corrompidos, rotina 1719, mission control",
        "source": "KB-019-robos-rpa-automacoes-e-loops.md",
        "text": """# KB-019 - Robôs de Automação RPA: Entrada de Notas e Tratamento de Loops
Sistemas: Servidor de Automação RPA, MicroWork Cloud (Rotina 1719), Bitrix24 (Funil 122 de Compras/Entrada), Mission Control
Palavras-chave: robo, robô, rpa, card robo, card robô, entrada honda, entrada grupo, faturamento direto, vigia, dms_vigia, loop processamento, solicitacao de entrada, erro 500 microwork, cookies corrompidos, rotina 1719, mission control

## 1. Diretriz Estrita de Triagem L1 (Sophia AI)
- Processos de robôs rodam em servidor de backend autônomo. A Sophia AI NUNCA deve orientar o usuário a fechar navegador, reiniciar computador ou limpar cookies da máquina local!
- O papel do bot é:
  1. Pedir o link do card de negócio no Bitrix24 onde o robô está atuando;
  2. Perguntar se o colaborador já conferiu se todos os dados do card estão corretos (número da nota, chassi, fornecedor, valores);
  3. Concluir imediatamente a triagem com alta urgência e encaminhar para a equipe técnica de TI atuar no servidor.

## 2. Causa Raiz e Solução para Loop "Em Processamento" / "Solicitação de Entrada" (Incidente Real #1410810 - Danielly)
- **Sintoma:** Colaboradora relata: 'Dei entrada em uma nota às 09:00 e até agora o robô não sai de processamento e solicitação de entrada, fica nesse loop e não finaliza'.
- **Causa Raiz Técnica Diagnosticada pela TI:**
  1. **Acúmulo de Cookies Corrompidos / Erro 500 no MicroWork:** A sessão do ERP no navegador do robô acumulou cookies corrompidos de autenticação OpenID, fazendo com que o MicroWork retornasse tela com 'Erro 500 - Interno do servidor' ao tentar acessar a Rotina 1719.
  2. **Loop de 15 Minutos:** A automação do Bitrix24 devolve para a fila inicial (C122:NEW) qualquer card que fique mais de 15 minutos em 'Em processamento'. Como a blacklist em memória do robô também expirava em 15 minutos, a cada 15 min exatos o robô re-capturava o card, caía no Erro 500 e o ciclo se repetia infinitamente.
- **Correções Aplicadas no Robô (apps/dms_entrada_honda/Lancamento_Entrada_Honda.py):**
  1. Função is_erro_500_page com auto-recuperação ativa (purga de cookies e re-login do zero);
  2. Mecanismo Anti-Loop em 2 Níveis (Tentativa 1 devolve para fila com aviso; Tentativa 2 bloqueia em Erro Desconhecido com alerta vermelho);
  3. Reciclagem automática da instância do WebDriver.
- **Atuação Operacional da TI:**
  1. Reiniciar o robô via Mission Control;
  2. Liberar os cards represados na etapa inicial para processamento sequencial."""
    },
    {
        "kb_id": "KB-020",
        "title": "Permissões de Perfil e Acesso a Módulos no Bitrix24: CRM, Cards de Folga e Tickets",
        "systems": "Bitrix24 CRM, Permissões de Perfil, Gestão de Acessos",
        "keywords": "permissao bitrix, acesso crm, liberar crm, crm mecanico, folga, card de folga, tickets, menu crm nao aparece, perfil bitrix, hadner, ailton",
        "source": "KB-020-bitrix-permissoes-crm-e-folgas.md",
        "text": """# KB-020 - Permissões de Perfil e Acesso a Módulos no Bitrix24
Sistemas: Bitrix24 CRM, Configurações de Permissões de Usuário, Acessos a Módulos
Palavras-chave: permissao bitrix, acesso crm, liberar crm, crm mecanico, folga, card de folga, tickets, menu crm nao aparece, perfil bitrix, hadner, ailton

## 1. Contexto e Identificação do Solicitante
- Quando gerentes de loja (ex: Hadner) solicitam liberação de CRM ou permissão para colaboradores da loja (ex: Mecânico Ailton acessar folgas e tickets):
- O solicitante no chat é o GESTOR. A Sophia AI deve sempre acolher o gestor pelo nome e identificar claramente que o acesso é para o colaborador beneficiário.

## 2. Diagnóstico Rápido
- Se o gestor confirmar que o colaborador testou no aplicativo e no navegador e o menu CRM não aparece, trata-se de ausência de permissão de acesso ao módulo CRM no perfil do usuário no Bitrix24.
- A Sophia conclui a triagem imediatamente como P4 (Baixo) e encaminha para a TI sem fazer perguntas irrelevantes de telefonia, chips ou compras de equipamentos.

## 3. Resolução da Equipe de TI
- Acessar Bitrix24 > CRM > Configurações > Permissões de Acesso;
- Atribuir o perfil de visualização adequado para o departamento/cargo do colaborador para que os cartões de folga e tickets fiquem visíveis no menu lateral."""
    }
]

print("2. Enviando KBs refinadas via webhook kb-ti-ingest...")
payload = {"documents": docs}
resp = requests.post(INGEST_WEBHOOK, json=payload)
print(f"Status: {resp.status_code} - Resposta: {resp.text}")

print("\n3. Aguardando 5 segundos para indexação vetorial...")
time.sleep(5)


print("\n3. Verificando quantidade total de chunks no PostgreSQL...")
check_sql = "SELECT metadata->>'kb_id' AS kb, COUNT(*) AS chunks FROM kb_ti_conhecimento GROUP BY metadata->>'kb_id' ORDER BY kb;"
r_check = requests.post(N8N_SQL_URL, json={'query': check_sql}).json()
print("Resumo de Chunks no banco:")
for row in r_check.get('rows', []):
    print(f"  {row.get('kb')}: {row.get('chunks')} chunks")

print("\nIngestão vetorial concluída com sucesso!")
