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

## 🤖 Arquitetura Canônica: `BITRIX_TI_AI_TRIAGE_AGENT`

O workflow principal implementa o modelo **CRM Deal Chat**:

```text
1 Chamado (Deal Categoria 160)
   ├── 1 Sessão no PostgreSQL (ticket_bot_sessions)
   ├── 1 Chat Nativo do Card (Bitrix24 im.chat.add com ENTITY_TYPE=CRM)
   ├── 1 Memória Redis Isolada (bitrix:ti:deal:<deal_id>:memory)
   └── 1 Contexto de IA (LangChain Agent + OpenAI GPT-4o-mini)
```

### Principais Invariantes Homologadas:
1. **Chat Nativo do Card:** A triagem ocorre diretamente na aba de chat dentro do próprio chamado no CRM Bitrix24, sem poluir o chat privado dos usuários.
2. **Reserva Atômica e Idempotência:** Criação da sessão com `status = 'CHAT_CREATING'` antes de chamar o Bitrix, prevenindo duplicação em concorrência.
3. **Isolamento de Contexto Multi-Deal (Zero `.first()`):** Todo o pipeline processa múltiplos deals concorrentes do mesmo solicitante mantendo `deal_id`, `dialog_id` e `message_id` indexados item a item.
4. **Motor Determinístico B01 de Prioridade:** A IA extrai fatos (`IMPACTO` e `URGÊNCIA`), mas a prioridade física é calculada por código estrito:
   - `P1_CRITICAL (1202)`
   - `P2_HIGH (1204)`
   - `P3_MEDIUM (1206)`
   - `P4_LOW (1208)`
   - *Nota: P0 foi eliminado por conformidade de segurança.*
5. **Avanço de Cursor Seguro:** O cursor `last_processed_message_id` só avança após confirmação de sucesso de envio no Bitrix24 (`bitrixRes.result`). Em caso de falha de rede/API, o cursor é preservado para retry.
6. **Detecção de Human Takeover:** Se um técnico humano postar no chat do card, a IA é pausada automaticamente (`ai_state = 'AI_PAUSED'`).
7. **Self-Healing Genérico:** Sessões travadas em `CHAT_CREATING` são promovidas genericamente por estado quando o chat já existe.

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
