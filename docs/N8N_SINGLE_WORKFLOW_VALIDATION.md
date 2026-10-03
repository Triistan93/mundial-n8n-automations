# BITRIX TI — N8N SINGLE WORKFLOW VALIDATION REPORT
## Consolidação Oficial do Triage Bot V1.1 em Fluxo Único
**Mundial Concessionárias Honda — Central RPA**  
**Versão:** 1.1.0 — Single Workflow Consolidated  
**Data:** 21 de Setembro de 2026

---

### 1. Resumo da Consolidação

A arquitetura do Triage Bot V1.1 foi consolidada em **1 ÚNICO WORKFLOW N8N** (`BITRIX_TI_TRIAGE_BOT_V11`), eliminando subworkflows separados nesta fase e organizando visualmente todas as etapas operacionais por meio de **Sticky Notes** temáticos e blocos sequenciais com nomenclatura canônica.

* **Arquivo de Entrega:** [`BITRIX_TI_TRIAGE_BOT_V11.json`](file:///C:/Mundial_RPA/infra/n8n/BITRIX_TI_TRIAGE_BOT_V11.json)
* **Nós Totais:** 31 (24 nós operacionais + 7 Sticky Notes coloridos)
* **Conexões:** 20 links direcionados
* **Ciclo de Execução:** Curto, autônomo e idempotente via trigger cíclico (15 segundos) ou webhook.

---

### 2. Mapa Visual dos Blocos (Sticky Notes)

```text
[00 — CONFIG / PRE-FLIGHT] ────► [01 — DISCOVERY / POLLING]
  - 00_Load_Config                 - 01_Get_New_Tickets
  - 00_Kill_Switch                 - 01_Get_New_Messages
          │                                │
          ▼                                ▼
[02 — NEW TICKET & QUEUE]        [03 — INCOMING REPLY & IDEMPOTÊNCIA]
  - 02_Validate_Deal               - 03_Validate_Message (Self-Message Guard)
  - 02_Check_Active_Session        - 04_Load_Session
  - 02_Create_Session (Queueing)   - 03_Normalize_Answer (Duplicate Guard)
          │                                │
          ▼                                ▼
[04, 05, 06 — THEME & QUESTION]  [07, 08 — CRM & BEHAVIOR ENGINE]
  - 05_Detect_Theme                - 04_Advance_State
  - 05_Extract_Known_Data          - 08_Update_CRM (Impact/Urgency)
  - 06_Get_Next_Question           - 08_Call_Behavior_Engine (B01, B02, B04)
  - 06_Send_Question               - 08_Read_Back
                                   - 07_Write_Timeline
                                   - 08_Send_Final_Message
                                           │
                                           ▼
                                 [09, 10 — TIMEOUT, AUDIT & ERRORS]
                                   - 09_Check_Timeouts (T+4h, T+24h)
                                   - 10_Audit_Event (ticket_bot_audit_log)
                                   - 10_Handle_Error (Fail-Closed)
```

---

### 3. Matriz de Hard Acceptance

| Critério de Homologação | Requisito Técnico | Status |
|---|---|:---:|
| **ONE_WORKFLOW** | Concentração total em 1 único arquivo `.json` sem subworkflows | **PASS** |
| **FEATURE_FREEZE** | Preservação integral do catálogo, perguntas e invariantes homologadas | **PASS** |
| **PRIVATE_ROUTING** | Envio restrito ao `DIALOG_ID = str(requester_user_id)` no chat privado | **PASS** |
| **ALLOWLIST** | Restrito a `BOT_ALLOWED_REQUESTERS = [32598]` (Eduardo Alaminos) | **PASS** |
| **SESSION_STATE** | Persistência externa em PostgreSQL (`ticket_bot_sessions`) | **PASS** |
| **THEME_DETECTION** | Ordem: `CATEGORY > SUBCATEGORY > TEXT FALLBACK > GENERICO` | **PASS** |
| **KNOWN_DATA_SKIP** | Suprime perguntas de escopo quando já extraídas com alta confiança | **PASS** |
| **DYNAMIC_QUESTIONS** | Apresenta botões estruturados conforme o tema do catálogo | **PASS** |
| **OPTIONAL_COMMENT** | Fluxo de comentário opcional sem alterar prioridade ou impact/urgency | **PASS** |
| **B01/B02/B04** | Behavior Engine executa prioridade SLA, título canônico e posse TI | **PASS** |
| **DUPLICATE_GUARD** | Descarte silencioso (`NOOP`) de mensagens com `last_processed_message_id` | **PASS** |
| **SELF_MESSAGE_GUARD** | Ignora mensagens emitidas pelo usuário do bot (`author_id == INTEGRATION_USER_ID`) | **PASS** |
| **QUEUE** | Máximo de 1 sessão `ACTIVE` por solicitante; excedentes ficam `QUEUED` | **PASS** |
| **TIMEOUT** | Alerta amigável em T+4h; encerramento de sessão em T+24h mantendo o ticket aberto | **PASS** |
| **FAIL_CLOSED** | Falhas de banco ou API Bitrix abortam sem envio de mensagens incorretas | **PASS** |

---

### 4. Conclusão Operacional

O fluxo único [`BITRIX_TI_TRIAGE_BOT_V11.json`](file:///C:/Mundial_RPA/infra/n8n/BITRIX_TI_TRIAGE_BOT_V11.json) está totalmente apto para importação direta no n8n.
