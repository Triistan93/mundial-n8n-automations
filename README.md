# 🚀 Mundial n8n Automations

Repositório central de fluxos, blueprints e automações **n8n** da **Central Mundial Honda (RPA & TI)**.

Este repositório abriga os workflows homologados em produção, schemas de persistência, suítes de validação automatizada e documentações de engenharia de automação.

---

## 📁 Estrutura do Repositório

```text
mundial-n8n-automations/
├── database/
│   └── schema.sql                          # Schema PostgreSQL canônico (ticket_bot_sessions, auditoria)
├── workflows/
│   ├── canonical/
│   │   └── BITRIX_TI_AI_TRIAGE_AGENT.json  # Workflow Canônico Homologado (Deal Chat + LangChain AI)
│   └── legacy_v11/
│       ├── BITRIX_TI_TRIAGE_BOT_V11.json   # Versão V11 (Private Chat)
│       └── subworkflows/                   # Sub-workflows legados (WF_NEW_TICKET, WF_PROCESS_REPLY, etc.)
├── scripts/
│   ├── generate_canonical_deal_chat_workflow.py # Gerador determinístico do JSON canônico
│   ├── validate_canonical_deal_chat_workflow.py # Validador de arquitetura (14 invariantes)
│   ├── test_context_integrity_and_continuity.py # Suíte de concorrência e integridade multi-deal
│   └── test_crm_deal_chat_e2e_simulation.py     # Simulação E2E de regras B01 e Human Takeover
├── docs/
│   ├── N8N_CANONICAL_RUNTIME_BLUEPRINT.md  # Blueprint operacional de tempo de execução
│   └── N8N_SINGLE_WORKFLOW_VALIDATION.md   # Matriz de homologação do workflow unificado
├── requirements.txt                        # Dependências Python para execução das suítes de teste
└── README.md
```

---

## 🤖 Arquitetura Canônica: `BITRIX_TI_AI_TRIAGE_AGENT` (89 Nós)

O workflow principal implementa o modelo **CRM Deal Chat com RAG Vetorial e Auto-Remediação Ativa**:

```text
1 Chamado (Deal Categoria 160)
   ├── 1 Sessão no PostgreSQL (ticket_bot_sessions)
   ├── 1 Chat Nativo do Card (Bitrix24 im.chat.add com ENTITY_TYPE=CRM)
   ├── 1 Memória Redis Isolada (bitrix:ti:deal:<deal_id>:memory)
   ├── 1 Contexto RAG Vetorial (PGVector kb_ti_conhecimento com 14 POPs)
   ├── 1 Motor Multimodal Vision (GPT-4o OCR de Prints de Erro)
   ├── 1 Cluster de Diagnóstico Ativo (Tool_Diagnostico_TI -> BITRIX_TI_DIAGNOSTIC_TOOLS)
   └── 1 Contexto de IA (LangChain Agent + OpenAI GPT-4o-mini)
```

### 🌟 As 6 Funcionalidades Avançadas de Help Desk (Homologadas em Produção):
1. **📸 Feature 1: Visão Multimodal & OCR de Prints (GPT-4o Vision):**
   - Intercepta uploads de imagens e fotos coladas no chat do Bitrix24 (`im.dialog.messages.get`).
   - Download autenticado via `im.v2.File.download` e extração de códigos de erro, telas do MicroWork Cloud, Chassi (17 dígitos) e Chave de NF-e (44 dígitos).
2. **🚨 Feature 2: Detector de Quedas Gerais por Loja (Incident Clustering P1):**
   - Correlaciona chamados da mesma filial em janela deslizante de 30 minutos via tabela `store_outage_events`.
   - Se $\ge 2$ chamados prévios existirem sobre o mesmo tema, eleva para **P1 - Crítico**, injeta banner de outage e unifica a comunicação no chat.
3. **😡 Feature 3: Detector de Frustração & "Cliente em Loja":**
   - Detecta atendimento presencial em balcão ou cliente aguardando na mesa, elevando a urgência para `OPERATION_HALTED` (P2/P1) com banner visual vermelho.
4. **🔍 Feature 4: Detector Inteligente de Chamados Duplicados (Anti-Spam):**
   - Localiza chamados abertos nas últimas 24h para o mesmo usuário/chassi, anexa o contexto no card original e encerra a duplicata em `C160:LOSE`.
5. **⭐ Feature 5: Pesquisa de Satisfação Pós-Atendimento (CSAT Pulse no Chat):**
   - Coleta notas de 1 a 5 estrelas no chat de tickets concluídos (`COMPLETED`), persistindo na tabela `ticket_csat_ratings` e na Timeline do CRM.
6. **🤖 Feature 6: Gatilhos de Auto-Remediação Ativa (RPA / Self-Healing):**
   - Ferramenta LangChain `Tool_Diagnostico_TI` acionando o sub-workflow `BITRIX_TI_DIAGNOSTIC_TOOLS` (`PdpgXjbRMygjaL25`) para testes em tempo real de links de filiais, status do servidor MicroWork Cloud, validação de Chassi no Detran e status das filas de robôs RPA.

### Principais Invariantes Homologadas:
1. **Chat Nativo do Card:** A triagem ocorre diretamente na aba de chat dentro do próprio chamado no CRM Bitrix24, sem poluir o chat privado dos usuários.
2. **Reserva Atômica e Idempotência:** Criação da sessão com `status = 'CHAT_CREATING'` antes de chamar o Bitrix, prevenindo duplicação em concorrência.
3. **Isolamento de Contexto Multi-Deal (Zero `.first()`):** Todo o pipeline processa múltiplos deals concorrentes do mesmo solicitante mantendo `deal_id`, `dialog_id` e `message_id` indexados item a item.
4. **Motor Determinístico B01 de Prioridade:** A IA extrai fatos (`IMPACTO` e `URGÊNCIA`), mas a prioridade física é calculada por código estrito:
   - `P1_CRITICAL (1202)`
   - `P2_HIGH (1204)`
   - `P3_MEDIUM (1206)`
   - `P4_LOW (1208)`
5. **Avanço de Cursor Seguro:** O cursor `last_processed_message_id` só avança após confirmação de sucesso de envio no Bitrix24 (`bitrixRes.result`).
6. **Detecção de Human Takeover:** Se um técnico humano postar no chat do card, a IA é pausada automaticamente (`ai_state = 'AI_PAUSED'`).
7. **Roteador Pós-Resolução (`PostRes`):** Escuta ativa de 7 dias com tratamento de `REOPEN`, `CARONA`, `THANKS` e `CSAT_FEEDBACK`.

---


## 🛠️ Como Trabalhar de Outras Máquinas

### 1. Clonar o Repositório
```bash
git clone https://github.com/Triistan93/mundial-n8n-automations.git
cd mundial-n8n-automations
```

### 2. Configurar Ambiente Python
```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Executar as Suítes de Validação e Testes
```bash
# Validar arquitetura canônica (14 invariantes):
python scripts/validate_canonical_deal_chat_workflow.py

# Validar concorrência multi-deal, integridade de contexto e cursor:
python scripts/test_context_integrity_and_continuity.py

# Simulação E2E de regras e matriz B01:
python scripts/test_crm_deal_chat_e2e_simulation.py
```

### 4. Importar no n8n
1. Acesse o painel do n8n (`https://sophia-n8nsophia.timft8.easypanel.host/`).
2. Abra ou crie um novo workflow.
3. No menu superior direito (`...`), clique em **Import from File...**.
4. Selecione `workflows/canonical/BITRIX_TI_AI_TRIAGE_AGENT.json`.
5. Salve e ative o workflow (**Active: ON**).

---

## 🗄️ Banco de Dados PostgreSQL
O schema de persistência está disponível em `database/schema.sql`.

Para inicializar ou verificar a tabela:
```sql
\i database/schema.sql
```
Tabelas:
- `ticket_bot_sessions`: Sessões ativas, cursores de mensagens e estado da IA.
- `ticket_bot_audit_log`: Rastreabilidade de perguntas e respostas.
- `ticket_bot_routing_audit`: Auditoria de roteamento e envio de mensagens.

---

## 📄 Licença & Governança
Uso interno e confidencial — Central Mundial Concessionárias Honda.
Desenvolvido pela equipe de RPA e TI.
