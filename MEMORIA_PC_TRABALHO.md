# 🧠 MEMÓRIA OPERACIONAL & TÉCNICA DO PROJETO (PC DE TRABALHO)
**Central Mundial Honda — Cluster de Automação, RPA, CRM Bitrix24 & Agente de Triagem com IA**
*Data de Consolidação: Outubro de 2026 • Autor / Gestor: Eduardo Alaminos (`32598`)*

---

## 📌 1. Visão Geral do Ecossistema

Este documento é a **base mestra de memória técnica** contendo todas as chaves, endpoints, decisões arquiteturais, modelos de banco de dados, regras de negócio e histórico de incidentes/resoluções construídos para a **Mundial Concessionárias Honda**.

Ele serve para restauração completa de contexto, replicação em outros computadores de trabalho e continuidade operacional sem perda de nenhuma informação.

---

## 🔑 2. Credenciais, Chaves de API & Endpoints Operacionais

> [!IMPORTANT]
> Estas credenciais são as oficiais da infraestrutura ativa na nuvem e no Bitrix24 da Mundial Honda.

### 2.1. Instância n8n (Hostinger / Easypanel)
* **URL do Painel n8n:** `https://sophia-n8nsophia.timft8.easypanel.host`
* **n8n Public API Endpoint:** `https://sophia-n8nsophia.timft8.easypanel.host/api/v1`
* **n8n API Key:**
  ```text
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU
  ```
* **Workflows Principais Ativos:**
  * `c0F2GUMFm2BI94UG`: `BITRIX_TI_AI_TRIAGE_AGENT` (Robô de Triagem L1, RAG PGVector e Chat Bitrix)
  * `uRjdQlM8edLyKmQO`: `BITRIX_TI_PURCHASE_APPROVAL_HANDLER` (Webhook de Aprovação de Compras de TI)

### 2.2. Bitrix24 CRM da Mundial Honda
* **Domínio do Portal:** `https://b24-88dbfb.bitrix24.com.br`
* **Webhook de Integração REST API:**
  ```text
  https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/
  ```
* **ID do Usuário Bot do Webhook:** `61622` (`Dev Bot` / `botdesenvolvimento@mundialhonda.com.br`)

### 2.3. Webhooks Públicos Ativos (n8n)
* **Ação de Aprovação / Recusa de Compras:**
  * URL: `https://sophia-n8nsophia.timft8.easypanel.host/webhook/purchase-action`
  * Métodos: `GET`
  * Parâmetros esperados: `?deal_id=<ID>&action=<approve|reject>&user=<ID_USUARIO>`

### 2.4. Repositórios Oficiais no GitHub
1. **Cluster RPA / Scripts / Core:**
   * URL: `https://github.com/Triistan93/Mundial_RPA.git`
   * Diretório Local: `C:\Mundial_RPA`
2. **Workflows n8n / Canônicos / Deployers:**
   * URL: `https://github.com/Triistan93/mundial-n8n-automations.git`
   * Diretório Local: `C:\mundial-n8n-automations`

---

## 👥 3. Usuários e Aprovadores Chave

| Nome | ID Bitrix | Cargo / Função | E-mail | Papel no Sistema |
| :--- | :---: | :--- | :--- | :--- |
| **Eduardo Alaminos** | `32598` | Gestor de TI | TI Mundial | Criador dos testes, desenvolvedor e aprovador técnico de TI. |
| **Zélia Silva** | `71` | Diretoria / Controladoria | `controladoria@mundialmotos.com.br` | Aprovadora executiva final de solicitações de compras e equipamentos. |
| **Dev Bot** | `61622` | Usuário de Serviço / Webhook | `botdesenvolvimento@mundialhonda.com.br` | Identidade que posta no chat do Bitrix, cria salas e atualiza cards. |

---

## 🏢 4. Mapeamento da Categoria 160 (Central de Serviços TI)

### 4.1. Filosofia de Governança
* **Pipeline Única:** É expressamente proibido criar pipelines "filhas" para compras ou manutenções. Toda a vida do chamado de TI acontece dentro da **Categoria 160**, utilizando etapas especializadas.

### 4.2. Mapeamento de Etapas (Stages) da Categoria 160

| Stage ID | Nome da Etapa | Função no Fluxo |
| :--- | :--- | :--- |
| `C160:NEW` | **Solicitação / Triagem** | Card recém-criado. O robô faz a triagem L1 conversacional. |
| `C160:PREPARATION` | **Em atendimento** | Chamado assumido pela equipe técnica humana de TI. |
| `C160:PREPAYMENT_INVOI` | **Aguardando Solicitante** | Chamado pausado aguardando retorno de testes ou dúvidas pelo usuário. |
| `C160:UC_Q3RSE9` | **Aguardando Fornecedor** | Pendência externa com operadora de internet, fornecedor ou fábrica. |
| `C160:UC_4Y908A` | **Em Manutenção / Bancada** | Equipamento físico em reparo na bancada da TI. |
| `C160:UC_JIOBG8` | **Aguardando autorização** | Solicitação de compra/upgrade classificada, aguardando clique da gestão. |
| `C160:UC_YUL75I` | **Em Cotação** | Compra autorizada em fase de coleta de preços pelo setor de compras. |
| `C160:UC_AR9ORZ` | **Autorizado** | Compra aprovada pelo gestor/diretoria via botão interativo. |
| `C160:UC_A18YO8` | **Negado** | Compra recusada pelo gestor/diretoria. |
| `C160:WON` | **Ticket Finalizado** | Chamado concluído com sucesso. Gatilho para checagem pós-atendimento. |
| `C160:LOSE` | **Finalizado por inatividade** | Fechado por falta de resposta do solicitante. |
| `C160:UC_Z6S2N5` | **Manutenção realizada** | Reparo físico concluído. |
| `C160:UC_RTCFS9` | **Material entregue** | Item de compra entregue ao colaborador. |

### 4.3. Campos Customizados Críticos (UFs) da Categoria 160

* **`UF_CRM_1763388156` (Categoria do Chamado):**
  * `876`: **Solicitação de Compra de TI** (Peças, hardware, upgrades).
* **`UF_CRM_TI_RESPONSIBLE` (Responsável TI):**
  * ID do Campo: `1796` | Tipo: `employee` (Usuário do Bitrix).
  * Criado na seção *"Triagem & Gestão Técnica (TI)"*.
  * Preenchido automaticamente pelo webhook quando o gestor clica em autorizar/negar.
* **`UF_CRM_TI_IMPACT` (Impacto Operacional - B01):**
  * `1180`: Empresa Inteira • `1182`: Loja Inteira • `1184`: Departamento Inteiro • `1186`: Múltiplos Usuários • `1188`: Usuário Individual • `1190`: Sem Impacto.
* **`UF_CRM_TI_URGENCY` (Urgência - B01):**
  * `1192`: Operação Parada • `1194`: Severamente Degradada • `1196`: Contorno Disponível • `1198`: Solicitação Planejada • `1200`: Dúvida / Informação.
* **`UF_CRM_TI_PRIORITY` (Prioridade Calculada Determinística):**
  * `1202`: P1 - Crítico • `1204`: P2 - Alto • `1206`: P3 - Médio • `1208`: P4 - Baixo / Resolvido L1.
* **`UF_CRM_1729774515200` (Descrição Original do Usuário):**
  * Campo preservado como array. O robô nunca sobrescreve o texto do usuário; apenas anexa o resumo da triagem.

---

## 🗄️ 5. Banco de Dados PostgreSQL & RAG Vetorial (PGVector)

* **Credencial n8n:** ID `J8q2YHlBbp4WxxV2` (`Postgres account`).
* **Instância:** PostgreSQL corporativo rodando no cluster Easypanel.

### 5.1. Tabela `kb_ti_conhecimento` (Base de Conhecimento Vetorial)
* Extensão: `CREATE EXTENSION IF NOT EXISTS vector;`
* Esquema:
  ```sql
  CREATE TABLE IF NOT EXISTS kb_ti_conhecimento (
      id SERIAL PRIMARY KEY,
      codigo VARCHAR(50) UNIQUE NOT NULL,
      titulo VARCHAR(255) NOT NULL,
      categoria VARCHAR(100) NOT NULL,
      tags TEXT[],
      sintomas TEXT NOT NULL,
      procedimento_l1 TEXT NOT NULL,
      solucao_definitiva TEXT NOT NULL,
      criterio_escalonamento TEXT,
      embedding vector(1536),
      criado_em TIMESTAMPTZ DEFAULT NOW(),
      atualizado_em TIMESTAMPTZ DEFAULT NOW()
  );
  ```
* **POPs Indexados (13 Procedimentos Oficiais):**
  1. `KB-001`: Impressoras Térmicas e Etiquetas (Zebra/Argox, bobina, travamento).
  2. `KB-002`: Impressoras Multifuncionais de Rede (Kyocera/Brother/HP, scanner SMB).
  3. `KB-003`: Queda de Internet e VPN Filiais (Roteador, balanceador, link redundante).
  4. `KB-004`: Computador Não Liga / Falha Elétrica (Cabo traseiro, filtro, chave seletora).
  5. `KB-005`: Telefonia IP e Ramais Bitrix24 (Microfone do Chrome, fone USB).
  6. `KB-006`: Reset de Senhas Windows AD e E-mail (Bloqueio de conta, segurança).
  7. `KB-007`: Lentidão Extrema e Diagnóstico de RAM/Disco (Uso 98%, inicialização).
  8. `KB-008`: Portais Honda (Garantia, Peças, Extranet, compatibilidade de navegador).
  9. `KB-009`: Plataforma FANDI Financiamento (Cálculo de parcelas, simulação).
  10. `KB-010`: E-mail Corporativo e Outlook (Caixa cheia, autenticação).
  11. `KB-011`: Bitrix24 CRM (Funis, leads perdidos, cache Ctrl+F5).
  12. `KB-012`: MicroWork Cloud DMS (Travamentos de tela, NF-e, gravação de pedidos).
  13. `KB-013`: RENAVE & ATPV-E (Intenção de venda, comunicação Detran/Serpro, chassi).

### 5.2. Tabela `ticket_bot_sessions` (Controle Atômico de Sessão)
* Controla em tempo real qual chamado tem bot ativo, qual o ID do chat Bitrix, se está aguardando humano ou concluído.
* Campos chave: `deal_id`, `requester_user_id`, `dialog_id`, `internal_chat_id`, `state`, `ai_state`, `status`.

---

## 🤖 6. Arquitetura dos Workflows n8n

### 6.1. Workflow Principal: `BITRIX_TI_AI_TRIAGE_AGENT` (`c0F2GUMFm2BI94UG`)
1. **`00_Schedule_Trigger`:** Dispara a cada 15 segundos.
2. **`01_Polling_Get_New_Deals`:** Busca novos deals em `C160:NEW`.
3. **`01_Strict_Gate_Cat160_Pilot`:** Filtro fail-closed permitindo apenas o usuário `32598` (Eduardo Alaminos) durante o piloto.
4. **`03_Create_CRM_Card_Chat`:** Cria o chat exclusivo no Bitrix via `im.chat.add`.
   * **Nova Saudação Humanizada:**
     > *"Oi, [Nome]! Tudo bem? Sou da equipe virtual de TI aqui da Mundial.*  
     > *Vi que você abriu este chamado sobre: **\"[Título do Card]\"**.*  
     > *Me conta com calma o que está acontecendo por aí? Se quiser mandar uma foto da tela ou do equipamento, fica à vontade! Vamos tentar resolver juntos."*
5. **`04_Fetch_Chat_Messages_Bitrix`:** Lê novas mensagens enviadas pelo usuário.
6. **`08_AI_Agent_Triage_Deal`:** Cérebro da IA (LangChain / OpenAI Chat Model) equipado com:
   * `KB_TI_PGVector_Tool`: Consulta semântica nos 13 POPs.
   * `Tool_Think_Deal`: Raciocínio estruturado.
7. **Regras Conversacionais da IA:**
   * **Proibição Total de Jargões Técnicos:** Nada de *driver, spooler, DHCP, DNS, gateway, boot*. Fala por pistas visuais: *"cabinho azul ou cinza com pontinha transparente atrás do PC"*, *"caixinha do computador que fica no chão"*, *"botãozinho redondo da tela"*.
   * **Diretiva da Zélia Silva (Controladoria):** Em compras, é **obrigatório** perguntar se há peça/equipamento no setor ou reserva para substituição temporária. Resposta registrada no Resumo Técnico.
   * **Acolhimento para Usuários Leigos:** Se o usuário disser *"não sei onde fica"* ou *"tenho medo de mexer"*, a IA não insiste, acalma o usuário e conclui a triagem com o técnico assumindo.
8. **Conclusão da Triagem (`15_Prepare_Final_Chat`):**
   * Se for Compra: move para `C160:UC_JIOBG8` (*Aguardando autorização*).
   * **Chat do Chamado (Solicitante):** Recebe **apenas** a mensagem informativa sem nenhum botão.
   * **Chat Privado do Gestor (`32598` / `71`):** Recebe exclusivamente a notificação com os 3 botões interativos:
     * `[ ✅ Autorizar Compra ]`
     * `[ 💬 Falar no Chamado ]` (Abre direto o card no Bitrix24)
     * `[ ❌ Negar ]`

### 6.2. Workflow de Aprovação: `BITRIX_TI_PURCHASE_APPROVAL_HANDLER` (`uRjdQlM8edLyKmQO`)
1. **`Webhook_Purchase_Action`:** Recebe o clique do botão com `responseMode: "responseNode"`.
2. **`Bitrix_Update_Deal_Stage`:**
   * Se autorizar: move para `C160:UC_AR9ORZ` (*Autorizado*) e grava `UF_CRM_TI_RESPONSIBLE = user_id`.
   * Se negar: move para `C160:UC_A18YO8` (*Negado*) e grava `UF_CRM_TI_RESPONSIBLE = user_id`.
3. **`Bitrix_Add_Timeline_Comment`:** Grava histórico na timeline do CRM com auditoria de quem clicou.
4. **`Bitrix_Notify_Eduardo_Chat`:** Confirma a ação no chat do gestor.
5. **`Respond_To_Webhook`:** Renderiza HTML moderno, visual corporativo claro com **contador regressivo de 3 segundos** e auto-redirecionamento direto para a tela do chamado no Bitrix24 (`https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${deal_id}/`).

---

## 🛠️ 7. Histórico Forense de Incidentes & Correções Definitivas

| Incidente | Causa Raiz | Correção Aplicada |
| :--- | :--- | :--- |
| **Botões ausentes no Card #1398518** | Botões só eram disparados na criação bruta e não na conclusão da IA (`15_Send_Final_Confirmation_To_Chat`). | Conectada a emissão de teclado interativo na rota de encerramento de compra do n8n. |
| **Tela Preta (`{"success":true}`)** | Webhook n8n retornava JSON cru (`lastNode`) em vez de resposta web formatada. | Adicionado nó `Respond to Webhook` com HTML responsivo, branding visual e auto-redirecionamento de 3s. |
| **Vulnerabilidade de Autoaprovação** | Teclado interativo era enviado dentro do chat público do chamado (visível ao funcionário que pediu a compra). | Isolamento total: chat do card sem botões; botões enviados **exclusivamente** no privado 1:1 do gestor/diretoria. |
| **Retrabalho da Zélia (Diretoria)** | Zélia sempre precisava perguntar se tinha peça no setor antes de aprovar. | IA agora pergunta preventivamente na triagem e grava a resposta pronta no Resumo do CRM. |
| **Saudação Robótica e "Tecniquês"** | Saudação padrão formal de cartório assustava colaboradores leigos de concessionária. | Reformulada mensagem inicial por primeiro nome, contextualizada pelo título e modo DIY com linguagem cotidiana visual. |

---

## 📋 8. Próximo Passo Planejado: Protocolo Pós-Atendimento & Filtro Anti-Carona

* **Objetivo:** Monitorar o fechamento de tickets (`C160:WON`).
* **Regra de Negócio dos 3 Cenários:**
  1. *Usuário agradece ou confirma ("Tudo certo", "Valeu"):* Robô agradece com carinho e encerra definitivamente.
  2. *Mesmo problema persiste ("Ainda tá travando", "Voltou a apagar"):* Robô reabre o chamado para *Em atendimento* (`C160:PREPARATION`), registra na timeline e avisa o técnico.
  3. *Problema NOVO / Diferente ("Aproveitando, a impressora parou"):* Robô **barra educadamente**, explica que o chamado anterior já foi concluído e orienta o usuário a abrir um novo ticket no Bitrix24 para garantir prioridade e organização.

---

*Arquivo compilado e mantido sob controle de versão oficial — Central de Tecnologia Mundial Honda.*
