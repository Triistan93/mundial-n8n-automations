# 🚀 Mundial n8n Automations

Repositório central de fluxos, blueprints e automações **n8n** da **Central Mundial Concessionárias Honda (RPA, TI & RH)**.

Este repositório abriga os workflows homologados em produção, schemas de persistência, suítes de validação automatizada e documentações de engenharia de automação.

---

## 📁 Estrutura do Repositório

```text
mundial-n8n-automations/
├── database/
│   └── schema.sql                          # Schema PostgreSQL canônico (ticket_bot_sessions, auditoria)
├── workflows/
│   ├── canonical/
│   │   ├── BITRIX_TI_AI_TRIAGE_AGENT.json  # Workflow Canônico TI C160 (89 nós - Deal Chat + LangChain RAG)
│   │   └── AGENTE_RH_COM_CORRECOES.json    # Workflow Canônico RH C198 (95 nós - WhatsApp Evolution + Bitrix CRM)
│   ├── AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json # Espelho ativo em produção n8n
│   └── legacy_v11/                         # Workflows e sub-workflows legados
├── scripts/
│   ├── check_broken_refs.py                # Validador de referências e expressões quebradas no JSON do n8n
│   ├── test_vagas_matching.py              # Suíte de validação de mapeamento das 25 vagas oficiais da C198
│   ├── test_sprint3_scenarios.py           # Validador determinístico dos cenários de estado e pós-atendimento
│   ├── test_sprint2_flow.py                # Teste de integração do Handover Humano e alerta IM no Bitrix
│   ├── deploy_sprint1_rh.py                # Deployer automatizado Sprint 1 via n8n Public API
│   ├── deploy_sprint2_rh.py                # Deployer automatizado Sprint 2 via n8n Public API
│   ├── deploy_sprint3_rh.py                # Deployer automatizado Sprint 3 via n8n Public API
│   ├── generate_canonical_deal_chat_workflow.py # Gerador determinístico do JSON canônico de TI
│   └── validate_canonical_deal_chat_workflow.py # Validador de arquitetura de TI (14 invariantes)
├── docs/                                   # Blueprints operacionais e matrizes de homologação
├── DIARIO_DE_AJUSTES_E_MELHORIAS.md        # Diário oficial definitivo de todas as sprints e melhorias
├── MEMORIA_PC_TRABALHO.md                  # Base mestra de credenciais, IDs, etapas e regras de negócio
├── requirements.txt                        # Dependências Python para execução das suítes de teste
└── README.md
```

---

## 🤖 1. Agente de IA do RH: `AGENTE_RH_COM_CORRECOES` (95 Nós)

* **ID no n8n:** `8OvNSMmZFZWxiW9A`
* **Canal de Entrada:** WhatsApp Receptivo via **Evolution API** (`botrh1`).
* **CRM de Destino:** Bitrix24 — **Categoria 198** (*Recrutamento e seleção*).

```text
1 Mensagem no WhatsApp (Evolution API)
   ├── Higienização JID / LID / DDI 55
   ├── Buffer Anti-Digitação Rápida (Debounce 30s no Redis)
   ├── Cérebro IA (LangChain Agent + OpenAI GPT-4.1-mini + Pense Tool + Redis Chat Memory)
   ├── Triagem em 4 Trilhas Operacionais:
   │   ├── Trilha 1: Recrutamento e Vagas (Mapeamento em 25 funções oficiais)
   │   ├── Trilha 2: Saúde Ocupacional / Clínicas / Exames
   │   ├── Trilha 3: Departamento Pessoal / Colaboradores
   │   └── Trilha 4: B2B / Fornecedores / Outros
   ├── Esteira de Currículos: Upload no Google Drive + Link Público na Linha do Tempo
   ├── Handover Inteligente: Card em ASSUNTOS RH (C198:UC_0YLZXN) + Alerta no Bitrix Chat
   └── Pós-Atendimento Blindado: Reconhecimento de candidato, anti-loop e silêncio em etapas humanas
```

### 🌟 As Entregas das 3 Sprints Homologadas (Outubro/2026):

#### 🚀 Sprint 1: Estabilização de Pipeline, Mapeamento de 25 Vagas & Blindagem de Nome
1. **Correção de Referência Quebrada:** Nó `Bitrix: Criar Deal (Contato Existente)1` retificado para `$('Bitrix: Buscar Contato').item.json.result[0].ID` (eliminando erro silencioso de ID nulo).
2. **Mapeamento 100% Sincronizado das 25 Vagas:** Mapeamento determinístico de todas as funções do campo `UF_CRM_1775845859336` (adicionadas opções `1142` - Atendente SAC e `1144` - Dev Junior e todos os sinônimos práticos como *Almoxarife*, *Social Media*, *Dev Jr*).
3. **Fim do "Candidato: Novo Cadastro":** Regra Inviolável de Nome no prompt e fallback em código para o `pushName` do WhatsApp.

#### 🚀 Sprint 2: Handover Inteligente para o RH (Trilhas 2, 3 e 4)
1. **Acolhimento de Demandas Fora de Vagas:** Quando o contato trata de exames admissionais, dúvidas de holerite ou fornecedores, o robô não abandona o usuário.
2. **Criação de Card em `ASSUNTOS RH` (`C198:UC_0YLZXN`):** Criação automática com vínculo do contato e histórico na Timeline.
3. **Notificação Instantânea no Chat Privado Bitrix:** Disparo via `im.message.add` para o responsável com link direto (`details/${deal_id}/`). Parametrizado inicialmente para **Eduardo Alaminos (`32598`)** para homologação, com chave de virada rápida para **Nina Biermann (`4278`)**.

#### 🚀 Sprint 3: Pós-Atendimento Inteligente & Blindagem Anti-Interferência Humana
1. **Cancelamento de OCR/Vision:** Descartada leitura multimodal pesada de imagens, poupando tokens e mantendo o fluxo ágil.
2. **Bloqueio Estendido de 30 Dias no Handover:** O nó `Redis: Bloquear Bot 30d (Handover Humano)` silencia o bot por 30 dias após transferência para humano.
3. **Motor de Detecção de Etapa Humana no CRM:** Se o card no Bitrix estiver em qualquer etapa de gestão humana ativa (*ASSUNTOS RH, Entrevista RH, Testes, Avaliação, Contratados*), o bot detecta o status, reativa a trava no Redis por 30 dias, anota na Timeline e **permanece 100% mudo**, sem interferir com o recrutador.
4. **Pós-Atendimento Acolhedor no `AI Agent` (`PASSO 3`):** Se um candidato já cadastrado enviar mensagens de status ("alguma novidade?"), a IA reconhece o candidato pelo primeiro nome, tranquiliza com prazos e **não gera JSON**, garantindo **zero cards duplicados no CRM**.

---

## 🤖 2. Central de Serviços TI: `BITRIX_TI_AI_TRIAGE_AGENT` (89 Nós)

* **ID no n8n:** `c0F2GUMFm2BI94UG`
* **Canal de Entrada:** Chat Nativo do Card CRM Bitrix24 (`im.chat.add`).
* **CRM de Destino:** Bitrix24 — **Categoria 160** (*Central de Serviços TI*).

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

### 🌟 As 6 Funcionalidades Avançadas de Help Desk:
1. **📸 Feature 1: Visão Multimodal & OCR de Prints (GPT-4o Vision):** Download autenticado via `im.v2.File.download` e extração de erros, MicroWork Cloud, Chassi (17 dígitos) e NF-e (44 dígitos).
2. **🚨 Feature 2: Detector de Quedas Gerais por Loja (Incident Clustering P1):** Correlaciona chamados da mesma filial em janela de 30 min (`store_outage_events`). Se $\ge 2$, força **P1 - Crítico**.
3. **😡 Feature 3: Detector de Frustração & "Cliente em Loja":** Detecta cliente aguardando na mesa ou entrega parada, elevando para `OPERATION_HALTED` (P2/P1) com banner vermelho.
4. **🔍 Feature 4: Detector Inteligente de Chamados Duplicados:** Unifica chamados abertos nas últimas 24h para o mesmo chassi/problema e encerra a duplicata em `C160:LOSE`.
5. **⭐ Feature 5: Pesquisa de Satisfação Pós-Atendimento (CSAT Pulse no Chat):** Coleta notas de 1 a 5 estrelas em chamados concluídos, gravando em `ticket_csat_ratings` e na Timeline.
6. **🤖 Feature 6: Gatilhos de Auto-Remediação Ativa (RPA / Self-Healing):** Ferramenta LangChain `Tool_Diagnostico_TI` acionando testes de links de filiais, servidor MicroWork, Detran/RENAVE e filas de robôs RPA.

---

## 🛠️ Como Executar as Suítes de Testes

```bash
# Ativar ambiente virtual Python:
.venv\Scripts\activate

# Validar ausência de referências quebradas nos workflows:
python scripts/check_broken_refs.py

# Validar mapeamento determinístico das 25 vagas de RH:
python scripts/test_vagas_matching.py

# Validar cenários de estado e pós-atendimento da Sprint 3:
python scripts/test_sprint3_scenarios.py

# Validar arquitetura canônica de TI (14 invariantes):
python scripts/validate_canonical_deal_chat_workflow.py
```

---

## 📄 Governança & Controle de Versão
- **Diário de Bordo Oficial:** Consulte [`DIARIO_DE_AJUSTES_E_MELHORIAS.md`](file:///c:/MundialRPA/DIARIO_DE_AJUSTES_E_MELHORIAS.md) para detalhes completos de cada sprint, commits e histórico forense.
- **Uso interno e confidencial:** Central Mundial Concessionárias Honda.
