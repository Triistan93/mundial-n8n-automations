# -*- coding: utf-8 -*-
"""
Script de Reingestão das Bases de Conhecimento Refinadas no pgvector (kb_ti_conhecimento)
Atualiza KB-011 (Bitrix, Telefonia & Grupos), KB-012 (MicroWork Cloud / ICMS / OS), KB-015 (WhatsApp / Espelhamento)
e insere KB-017 (Integração MyHonda) e KB-018 (Chamados Apenas com Nome de Pessoa).
"""
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

N8N_SQL_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
INGEST_WEBHOOK = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-ingest'

print("1. Removendo chunks legados das KBs 011, 012, 015, 017 e 018 no PostgreSQL...")
del_sql = "DELETE FROM kb_ti_conhecimento WHERE metadata->>'kb_id' IN ('KB-011', 'KB-012', 'KB-015', 'KB-017', 'KB-018');"
r_del = requests.post(N8N_SQL_URL, json={'query': del_sql})
print("Resultado da limpeza:", r_del.json())

docs = [
    {
        "kb_id": "KB-011",
        "title": "Bitrix24: Lentidão, Telefonia e Ramal, Exclusão de Grupos de Chat (L1) e Guardrails de Segurança",
        "systems": "Bitrix24 CRM, Telefonia Fale Fácil, App Desktop Bitrix, Chat e Grupos",
        "keywords": "bitrix, bitrix24, bitrix lento, tela branca, não toca telefone, telefone bitrix, não recebo ligação, ramal mudo, headset, microfone, app desktop, fone mutado, som windows, excluir grupo, apagar grupo, sobre o grupo, ações excluir grupo",
        "source": "KB-011-bitrix24-telefonia-e-grupos.md",
        "text": """# KB-011 - Bitrix24: Lentidão, Telefonia e Ramal, Exclusão de Grupos de Chat (L1) e Guardrails de Segurança
Sistemas: Bitrix24 CRM, Telefonia Integrada (Fale Fácil), Aplicativo Desktop Bitrix24, Grupos e Chat
Palavras-chave: bitrix, bitrix24, bitrix lento, tela branca, não toca telefone, telefone bitrix, não recebo ligação, ramal mudo, headset, microfone, app desktop, fone mutado, som windows, excluir grupo, apagar grupo, sobre o grupo, ações excluir grupo

## 1. Falha na Telefonia / Ramal Bitrix Não Toca ou Não Recebe Ligação
### Causas Técnicas Comuns:
- Colaborador desinstalou ou fechou o aplicativo desktop e está usando pelo navegador;
- Headset com botão mudo físico ativado no cabo ou som do Windows mudo;
- Falta de atualização do aplicativo Bitrix24;
- Colaborador ausente ou ramal deslogado na telefonia.

### Checklist Guiado de Atendimento L1 (Sophia AI):
1. **Ambiente de Uso (Obrigatório):**
   - Perguntar se o colaborador está utilizando o **Aplicativo Desktop do Bitrix24 instalado no computador** ou acessando pelo navegador.
   - Orientação: Na Rede Mundial, o uso do Aplicativo Desktop é o padrão obrigatório para estabilidade da telefonia. Se estiver no navegador, oriente a abrir o aplicativo instalado.
2. **Checagem de Áudio e Microfone:**
   - Conferir se o controle do cabo do headset não está com o botão de **MUTE físico** ativado (luz vermelha acesa no fio).
   - Verificar se o volume de som do Windows no canto inferior direito da barra de tarefas não está zerado ou em mudo.
3. **REGRA DE OURO & GUARDRAIL DE SEGURANÇA:**
   - A Sophia AI **NUNCA** deve instruir ou sugerir que o colaborador acerte ou tente verificar configurações de telefonia ou configurações de filas dentro do Bitrix24. Essas telas são de acesso e gestão exclusivos da equipe de TI.
   - Se o checklist físico estiver correto e persistir sem tocar, a Sophia conclui o chamado para a TI verificar em *Contact Center > Telefonia / Configurações de Fila*.

## 2. Dúvida de Uso do Bitrix: Excluir Grupos de Chat (Autoatendimento L1)
### Regra Operacional da Mundial:
- Usuários comuns de loja (caixas, consultores, faturistas) **possuem permissão para excluir grupos de chat/trabalho**, desde que eles próprios tenham criado o grupo e constem como proprietários/administradores dele.

### Passo a Passo Guiado de Auto-Resolução L1:
Ao receber pedidos do tipo "como apago um grupo no Bitrix", a Sophia responde imediatamente:
1. Abra o Grupo de Chat no Bitrix24;
2. No canto superior direito, clique em **'Sobre o grupo'**;
3. No menu suspenso **'Ações'**, clique em **'Excluir grupo'**;
4. Confirme a exclusão na janela de confirmação.

- Se o colaborador confirmar a realização com sucesso: Finalizar como **`RESOLVED_L1`**.

### GUARDRAIL ESTRITO DE SEGURANÇA DE DADOS (CRUCIAL):
- A Sophia AI **NUNCA** pode orientar, sugerir ou ensinar qualquer colaborador a excluir:
  * Cards de Negócio (Deals);
  * Contatos e Empresas do CRM;
  * Mensagens do histórico de WhatsApp ou Openlines.
- A exclusão permitida em autoatendimento limita-se estritamente a **Grupos de Chat** criados pelo próprio usuário.

## 3. Lentidão Geral ou Tela Branca
- Orientar o colaborador a pressionar `Ctrl + F5` para atualizar o cache, ou reiniciar o aplicativo Bitrix24."""
    },
    {
        "kb_id": "KB-012",
        "title": "MicroWork Cloud (ERP/DMS): Travamento, Erros de ICMS, Ordem de Serviço (OS) e Ajuste Fiscal Automatizado",
        "systems": "MicroWork Cloud ERP/DMS, Bot Fiscal da TI, Módulo Peças, Oficina, Vendas e Faturamento",
        "keywords": "microwork, microwork cloud, erp, dms, erro icms, erro de icms, tipo de movimento, ordem de serviço, os, nota fiscal travada, cfop, cst fiscal, bot fiscal, rejeição sefaz, faturamento travado, gabrielle, paula brenda",
        "source": "KB-012-microwork-cloud-erros-icms-os.md",
        "text": """# KB-012 - MicroWork Cloud (ERP/DMS): Travamento, Erros de ICMS, Ordem de Serviço (OS) e Ajuste Fiscal Automatizado
Sistemas: MicroWork Cloud ERP/DMS, Rotina Fiscal Automatizada da TI, Módulos Vendas, Peças, Oficina e Faturamento
Palavras-chave: microwork, microwork cloud, erp, dms, erro icms, erro de icms, tipo de movimento, ordem de serviço, os, nota fiscal travada, cfop, cst fiscal, bot fiscal, rejeição sefaz, faturamento travado, gabrielle, paula brenda

## Quando usar
Colaborador relata: "erro de ICMS ao gravar pedido/nota", "rejeição de ICMS na OS", "bloqueio de tipo de movimento no MicroWork", "não consigo faturar peças/motos".

## Resolução Técnica da TI
A equipe de TI não efetua essa liberação manualmente tela por tela: a TI possui um **robô/bot automatizado** dedicado a executar a correção fiscal e a liberação de movimentações no MicroWork Cloud DMS.

## Coleta Obrigatória pela Sophia AI para Alimentar a Automação da TI
Para que o suporte de TI e o robô fiscal atuem imediatamente sem necessidade de trocas adicionais de mensagens, a Sophia DEVE coletar:
1. **Link do Card de Negócio no Bitrix24 (se houver):** Link direto do card onde o pedido ou proposta está sendo tramitado;
2. **Número da Ordem de Serviço (OS) OU Número do Pedido / Nota Fiscal (NF):** O número exato do documento pendente no DMS;
3. **Chassi Completo da Motocicleta:** Chassi de 17 caracteres (iniciado por 9C2...), quando envolver veículos ou OS de oficina;
4. **Print ou Transcrição da Tela de Erro:** Captura legível com o código do erro do ICMS ou rejeição tributária (processado pelo OCR Vision).

Com esses 4 dados, o chamado é classificado na Categoria 160 e o bot fiscal da TI resolve a pendência com agilidade máxima."""
    },
    {
        "kb_id": "KB-015",
        "title": "WhatsApp Corporativo, Fale Fácil e Contact Center: Espelhamento Atrasado e Escopo de Conexão",
        "systems": "WhatsApp Corporativo, Bitrix24 Contact Center, Telefonia Fale Fácil, Meta API",
        "keywords": "whatsapp, wpp, fale facil, contact center, espelhamento atrasado, atraso de mensagem, mensagens não chegam, canal desconectado, qr code, conexão específica, todas as conexões, link de cliente de exemplo",
        "source": "KB-015-whatsapp-corporativo-fale-facil.md",
        "text": """# KB-015 - WhatsApp Corporativo, Fale Fácil e Contact Center: Espelhamento Atrasado e Escopo de Conexão
Sistemas: WhatsApp Corporativo, Bitrix24 Contact Center, Plataforma Fale Fácil, Meta WhatsApp Business API
Palavras-chave: whatsapp, wpp, fale facil, contact center, espelhamento atrasado, atraso de mensagem, mensagens não chegam, canal desconectado, qr code, conexão específica, todas as conexões, link de cliente de exemplo

## O que Caracteriza o "Espelhamento Atrasado":
- A mensagem enviada pelo cliente no WhatsApp não chega para o atendente no chat do Bitrix24; **OU**
- A mensagem enviada pelo atendente no Bitrix24 não chega no celular do cliente (delay ou falha na fila de envio da API).

## Causa Raiz Técnica:
Falha temporária na conexão da API de mensageria da Fale Fácil, lentidão momentânea no CRM ou necessidade de reinicialização de sessão. A TI normaliza reiniciando a conexão no painel de administração e, quando necessário, acionando o suporte da Fale Fácil ou Bitrix.

## Escopo do Bot & Coleta Obrigatória:
O colaborador NÃO possui acesso à plataforma Fale Fácil e não deve tentar mexer nela. A Sophia AI deve realizar a triagem investigando:
1. **Escopo da Falha (Pergunta Chave):**
   - Perguntar com clareza: *"O problema está ocorrendo em uma conexão ou número específico (e qual seria)? Ou está acontecendo em todas as conexões de WhatsApp da loja?"*
2. **Identificação da Linha:**
   - Número corporativo com DDD (ex: 19 9xxxx-xxxx ou fixo da loja).
3. **Evidência Obrigatória (Uma das duas):**
   - **Link de um card/cliente de exemplo no Bitrix24:** Para que a TI rastreie os logs de webhook e fila de mensageria; **OU**
   - **Print da tela de erro:** Foto/print capturado com erro de envio (analisado pelo OCR).
4. **Checagem Guiada no Smartphone Físico:**
   - Pedir para o colaborador olhar em *Configurações/Ajustes > Aparelhos Conectados* do WhatsApp físico e confirmar se consta como Conectado."""
    },
    {
        "kb_id": "KB-017",
        "title": "Integração MyHonda ➡️ Bitrix24: Falha na Recepção de Leads e Verificação de Servidor RPA",
        "systems": "Portal MyHonda Montadora, Bitrix24 CRM, Robô RPA de Integração de Leads, Servidor Mundial",
        "keywords": "myhonda, portal myhonda, lead sumiu, leads não entram, integração myhonda, robô parado, leads atrasados, captação honda, marketing, leads pararam",
        "source": "KB-017-integracao-myhonda-bitrix24.md",
        "text": """# KB-017 - Integração MyHonda ➡️ Bitrix24: Falha na Recepção de Leads e Verificação de Servidor RPA
Sistemas: Portal MyHonda da Montadora, Robô RPA de Captação, Bitrix24 CRM, Servidor de Automação
Palavras-chave: myhonda, portal myhonda, lead sumiu, leads não entram, integração myhonda, robô parado, leads atrasados, captação honda, marketing, leads pararam

## Quando usar
Colaborador do Marketing, Vendas ou Gestão relata: "os leads do MyHonda pararam de cair no Bitrix", "não estou recebendo novos clientes da Honda", "leads com atraso no funil".

## Causa Técnica:
A captação dos leads do portal da montadora MyHonda é realizada por um robô RPA autônomo executado no servidor corporativo. As causas mais frequentes de parada são:
- Servidor físico/virtual reiniciado ou temporariamente desligado;
- Queda da sessão/login no portal MyHonda (necessidade de renovação de credenciais);
- Travamento pontual no ciclo de execução do script de extração.

## Coleta Obrigatória pela Sophia AI:
Para que a TI identifique a parada e normalize o robô imediatamente, a Sophia deve extrair do solicitante:
1. **Data e Horário do Último Lead:** Quando foi a última vez que um lead do MyHonda entrou no Bitrix24 (ex: "hoje às 09:30" ou "desde ontem à tarde")?
2. **Origem da Constatação:** Onde o colaborador constatou a falta do lead?
   - Consultou diretamente o portal oficial MyHonda e viu leads pendentes lá que não estão no CRM?
   - Verificou em planilha de controle ou foi cobrado por um cliente específico?

Com esses dados, o chamado é encaminhado à TI para validação do status do robô no servidor e normalização da fila."""
    },
    {
        "kb_id": "KB-018",
        "title": "Triagem Acolhedora de Chamados Abertos Apenas com Nome de Pessoa",
        "systems": "Service Desk Sophia AI, Bitrix24 Helpdesk Categoria 160, Gestão de Identidades",
        "keywords": "nome de pessoa, chamado sem descrição, apenas nome, lucas, amanda, joão, admissão, demissão, desligamento, troca de senha, alteração de permissão, onboarding",
        "source": "KB-018-triagem-chamados-apenas-nome.md",
        "text": """# KB-018 - Triagem Acolhedora de Chamados Abertos Apenas com Nome de Pessoa
Sistemas: Service Desk Sophia AI, Bitrix24 Helpdesk Categoria 160
Palavras-chave: nome de pessoa, chamado sem descrição, apenas nome, lucas, amanda, joão, admissão, demissão, desligamento, troca de senha, alteração de permissão, onboarding

## Contexto Operacional
Na rotina corrida das concessionárias, supervisores ou consultores frequentemente abrem chamados rápidos digitando no título apenas o nome de um funcionário (ex: "Lucas Silva", "Paula Brenda", "Amanda Seminovas") e deixam o campo de descrição em branco.

## Conduta da Sophia AI
Em vez de rejeitar o chamado ou solicitar dados de forma genérica, o assistente adota uma postura empática, acolhedora e investigativa:
1. **Interpretação do Card:**
   - A Sophia lê o solicitante, a concessionária e o nome citado no título;
2. **Pergunta Clarificadora Estruturada:**
   - A Sophia responde no chat do chamado:
     > *"Olá! Notei que seu chamado cita [Nome Citado]. Para que eu possa agilizar seu atendimento: trata-se de criação de novos acessos para este colaborador, redefinição de senha esquecida, alteração de permissão/fila de atendimento ou desligamento/desativação de usuário?"*
3. **Encaminhamento Direcionado:**
   - Se for **Criação de novos acessos:** Direciona para o checklist de Onboarding (KB-016: cargo, fila telefonia, whatsapp e máquina);
   - Se for **Redefinição de senha:** Avalia fluxo L1 ou L2 (KB-005);
   - Se for **Desligamento / Desativação:** Coleta a data do desligamento e filial para bloqueio de contas."""
    }
]

print("\n2. Enviando documentos enriquecidos para o webhook de ingestão do n8n...")
payload = {"documents": docs}
r_ingest = requests.post(INGEST_WEBHOOK, json=payload)
print(f"Status da ingestão: {r_ingest.status_code} - {r_ingest.text}")

print("\n3. Aguardando 5 segundos para indexação vetorial...")
time.sleep(5)

print("\n4. Verificando artigos presentes em kb_ti_conhecimento após ingestão...")
r_check = requests.post(N8N_SQL_URL, json={'query': "SELECT DISTINCT metadata->>'kb_id' as kb_id, metadata->>'title' as title FROM kb_ti_conhecimento ORDER BY kb_id ASC;"})
rows = r_check.json().get('rows', [])
for r in rows:
    print(f"  [{r.get('kb_id')}] {r.get('title')}")

print("\nReingestão concluída com sucesso!")
