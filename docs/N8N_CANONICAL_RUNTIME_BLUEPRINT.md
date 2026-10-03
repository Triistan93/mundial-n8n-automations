# BITRIX TI — N8N CANONICAL RUNTIME BLUEPRINT
## Orquestração Oficial do Triage Bot V1.1 no n8n
**Mundial Concessionárias Honda — Central RPA**  
**Versão:** 1.1.0 — Canonical n8n Runtime  
**Status:** FEATURE_FREEZE (Preservação integral de TRIAGE_V11_PASS)

---

## 1. Decisão Arquitetural Oficial

```text
RUNTIME / ORCHESTRATION = n8n
```

Fica cancelado e descontinuado qualquer plano ou execução de:
* Python local service em background
* CMD / terminal manual runtime
* `Triage_Bot.exe` compilado
* Integração como processo do Painel Unificado
* Windows Service local

### Matriz de Responsabilidades do Ecossistema

| Componente | Papel Arquitetural | Tecnologias / Módulos |
|---|---|---|
| **n8n** | Orquestração da conversa, recepção de webhooks, roteamento e controle de fluxo | Workflow principal + 7 subworkflows modulares |
| **PostgreSQL** | Persistência de sessões, idempotência, auditoria de perguntas/respostas e roteamento seguro | `ticket_bot_sessions`, `ticket_bot_audit_log`, `ticket_bot_routing_audit` |
| **Bitrix24 CRM** | *System of Record* dos chamados, mensageria de chat 1:1 e linha do tempo | Category 160 (`crm.deal`), `im.message.add`, `crm.timeline.comment.add` |
| **Behavior Engine** | Autoridade única sobre regras de negócio, priorização e contratos de estágio | `B01` (Prioridade V1), `B02` (Título Canônico), `B04` (Contratos de Posse) |

---

## 2. Mapa Modular de Workflows (Main + Subworkflows)

O bot opera sob uma topologia modular desacoplada:

```text
                    ┌──────────────────────────────────────────────┐
                    │      BITRIX_TI_TRIAGE_BOT_V11 (Main)         │
                    │  - Webhook Receiver & Router                 │
                    │  - Kill Switch (BOT_ENABLED)                 │
                    │  - Production Canary Guard (Category 160)    │
                    │  - Central Error Trigger & Monitoring        │
                    └──────────────┬───────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │ (Novo Ticket)           │ (Mensagem Recebida)     │ (Cron / Interval)
         ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  WF_NEW_TICKET   │      │ WF_PROCESS_REPLY │      │    WF_TIMEOUT    │
└────────┬─────────┘      └────────┬─────────┘      └──────────────────┘
         │                         │
         │                         ▼
         │                ┌──────────────────┐
         │                │WF_ASK_NEXT_QUEST.│
         │                └────────┬─────────┘
         │                         │ (Triage Finalizada)
         │                         ▼
         │                ┌──────────────────┐
         │                │WF_COMPLETE_TRIAGE│
         │                └────────┬─────────┘
         │                         │
         ├─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│WF_BEHAVIOR_ENGINE│      │WF_WRITE_TIMELINE │      │WF_CENTRAL_ERROR  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

---

## 3. Especificação dos Subworkflows

### 3.1 `WF_NEW_TICKET`
* **Trigger:** Chamado pelo Main ao receber evento de criação de Deal ou polling de novo ticket na Category 160 com `STAGE_ID = C160:NEW`.
* **Guardas Canônicas:**
  1. `BOT_ENABLED == true` (Kill switch)
  2. `CATEGORY_ID == 160`
  3. `requester_user_id IN BOT_ALLOWED_REQUESTERS` (atualmente `[32598]`)
* **Lógica Executada:**
  1. Extração determinística (`DeterministicKnowledgeExtractor`): avalia título, categoria, subcategoria e descrição.
  2. Identifica tema canônico (`ThemeDetector`) priorizando categorias explícitas.
  3. Aplica regra `KNOWN DATA > ASK AGAIN`: suprime perguntas redundantes se escopo e continuidade já constarem na abertura.
  4. Valida sessão ativa no PostgreSQL: se o solicitante já possui chamado ativo, enfileira o novo (`status = QUEUED`).
  5. Cria registro em `ticket_bot_sessions` (`state = ASKING_<Q_ID>`).
  6. Dispara primeira pergunta com botões interativos (`im.message.add`).

### 3.2 `WF_PROCESS_REPLY`
* **Trigger:** Chamado pelo Main ao receber evento de mensagem no chat privado do bot (`im.message.add` do usuário).
* **Idempotência e Segurança:**
  * Ignora mensagens enviadas pelo próprio robô (`author_id == BOT_ID`).
  * Despreza mensagens de usuários fora da allowlist (`NOOP`).
  * Despreza mensagens já processadas (`last_processed_message_id`).
  * Localiza a sessão ativa do usuário no PostgreSQL.
* **Processamento:**
  1. Validação da resposta contra as opções do catálogo (`triage_question_catalog.json`).
  2. Se inválida:
     * Tentativa 1: Envia orientação amigável e repete a pergunta com botões.
     * Tentativa 2: Executa `HANDOFF_TO_TI` (pausa robô, notifica usuário e passa para analista humano sem loop).
  3. Se válida:
     * Registra auditoria em `ticket_bot_audit_log`.
     * Grava metadados de impacto: `impact_value`, `impact_source = "BOT_STRUCTURED_ANSWER"`, `impact_evidence`.
     * Preserva invariant `DOMAIN_SCOPE != BUSINESS_IMPACT` (quantidades de veículos/câmeras/máquinas não viram impacto humano).
     * Determina próximo passo: próxima pergunta temática, comentário opcional ou conclusão.

### 3.3 `WF_ASK_NEXT_QUESTION`
* **Função:** Formatação e envio da próxima interação do catálogo.
* **Comportamento:**
  1. Monta o texto amigável e os botões interativos rápidos.
  2. Atualiza estado da sessão no PostgreSQL (`current_question`, `state`, `last_interaction_at`).
  3. Registra auditoria pré-envio em `ticket_bot_routing_audit` confirmando `dialog_type == 'private'` e `dialog_id == requester_user_id`.
  4. Envia mensagem via REST API Bitrix.

### 3.4 `WF_COMPLETE_TRIAGE`
* **Função:** Finalização formal da triagem e entrega para a esteira técnica.
* **Passos Estritos:**
  1. Atualiza **somente** `UF_CRM_TI_IMPACT` e `UF_CRM_TI_URGENCY` no Bitrix CRM.
  2. Se o chamado não possui `UF_CRM_TI_SHORT_SUBJECT`, preenche com o título ou síntese determinística.
  3. Invoca o subworkflow `WF_BEHAVIOR_ENGINE`.
  4. Executa **Read-Back Rigoroso**: lê os campos do Deal direto da API Bitrix24 e confere se `IMPACT`, `URGENCY`, `PRIORITY` e `TITLE` estão conformes.
  5. Invoca `WF_WRITE_TIMELINE` para gravar resumo estruturado na linha do tempo.
  6. Envia mensagem de agradecimento ao colaborador.
  7. Atualiza sessão no PostgreSQL para `COMPLETED`.
  8. Desbloqueia próximo ticket enfileirado do solicitante se houver.

### 3.5 `WF_TIMEOUT`
* **Trigger:** Execução agendada a cada 15 minutos via Cron Node no n8n.
* **Regras Temporais:**
  * **T + 4 horas sem resposta:** Envia lembrete amigável único no chat privado.
  * **T + 24 horas sem resposta:** Atualiza a sessão para `TIMED_OUT`.
  * **Salvaguarda Crítica:** O chamado no CRM **permanece aberto**. O bot **não chama B06** e não cancela/encerra o ticket. A equipe de TI assume o chamado normalmente.

### 3.6 `WF_WRITE_TIMELINE`
* **Função:** Registro de histórico visual na timeline do Bitrix CRM (`crm.timeline.comment.add`).
* **Conteúdo:**
  * Síntese dos fatos declarados pelo usuário (Cabo, Wi-Fi, escopo, continuidade).
  * Comentário adicional do colaborador (se fornecido).
  * **Isolamento de Falha:** Falha de escrita de timeline (ex: instabilidade temporária) não bloqueia o ticket nem reverte a prioridade; o log de auditoria no PostgreSQL permanece íntegro.

### 3.7 `WF_BEHAVIOR_ENGINE`
* **Função:** Execução das regras canônicas homologadas da esteira de TI:
  * **`B01` (Priority Authority):** Calcula a prioridade SLA (`P1_CRITICAL` a `P4_LOW`) via matriz cruzada Impacto x Urgência. O bot nunca arbitra prioridade.
  * **`B02` (Title Canonical):** Aplica titulação padronizada `[Loja] Assunto Curto`.
  * **`B04` (State Guards):** Garante que novos chamados estejam com `NEXT_OWNER = TI` e `WAIT_REASON = NONE`.

---

## 4. Salvaguardas Fail-Closed e Tolerância a Falhas

1. **PostgreSQL Indisponível:**
   * Caso o nó Postgres falhe na inicialização ou verificação de sessão, o workflow aborta imediatamente com status `FAIL_CLOSED`.
   * **Nenhuma mensagem é enviada ao usuário** e **nenhum campo do CRM é alterado**.

2. **Dúvida de Correlação / Resposta Ambígua:**
   * Se a mensagem do usuário não corresponder a nenhuma opção e exceder o limite de 1 tentativa, aciona `HANDOFF_TO_TI`.

3. **Kill Switch Global:**
   * Variável central `BOT_ENABLED`:
     ```json
     {
       "BOT_ENABLED": true,
       "BOT_ALLOWED_REQUESTERS": [32598]
     }
     ```
   * Se `BOT_ENABLED == false`, os triggers de novos chamados e de mensagens encerram em `NOOP` silencioso.

---

## 5. Fluxo do Comentário Opcional (Preservado)

A pergunta final de comentário opcional segue o padrão canônico congelado:
1. **Pergunta:** *"Gostaria de deixar algum comentário?"*
2. **Opções:**
   * `Sim, quero comentar`
   * `Não, pode finalizar`
3. Se `Sim, quero comentar`:
   * Mensagem: *"Pode escrever agora. Seja breve e envie tudo em uma única mensagem."*
   * Texto recebido é enviado para `ticket_bot_audit_log` e `crm.timeline.comment.add`.
   * **Regra Absoluta:** O texto livre do comentário **não altera** `IMPACT`, `URGENCY` nem `PRIORITY`.
