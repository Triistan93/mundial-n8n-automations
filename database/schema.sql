-- ====================================================================
-- TABELA: ticket_bot_sessions
-- Motor de Persistência de Estado de Conversação (n8n Triage Bot MVP)
-- Modelo Canônico de Identidade e Roteamento (Hotfix P0)
-- Mundial Concessionárias Honda — Central RPA
-- ====================================================================

CREATE TABLE IF NOT EXISTS ticket_bot_sessions (
    id SERIAL PRIMARY KEY,
    deal_id INTEGER NOT NULL UNIQUE,
    requester_user_id INTEGER NOT NULL,
    requester_name VARCHAR(150),
    channel VARCHAR(50) NOT NULL DEFAULT 'BITRIX_PRIVATE_CHAT',
    private_dialog_id VARCHAR(50),
    dialog_id VARCHAR(50),
    internal_chat_id INTEGER,
    dialog_type VARCHAR(20) NOT NULL DEFAULT 'chat',
    state VARCHAR(50) NOT NULL DEFAULT 'INIT',
    ai_state VARCHAR(50) NOT NULL DEFAULT 'AI_ACTIVE',
    current_question VARCHAR(50),
    collected_data_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_processed_message_id VARCHAR(50),
    redis_memory_key VARCHAR(100),
    last_interaction_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'
);

-- Migrações incrementais seguras (Idempotentes)
ALTER TABLE ticket_bot_sessions ADD COLUMN IF NOT EXISTS dialog_id VARCHAR(50);
ALTER TABLE ticket_bot_sessions ADD COLUMN IF NOT EXISTS last_processed_message_id VARCHAR(50);
ALTER TABLE ticket_bot_sessions ADD COLUMN IF NOT EXISTS ai_state VARCHAR(50) NOT NULL DEFAULT 'AI_ACTIVE';
ALTER TABLE ticket_bot_sessions ADD COLUMN IF NOT EXISTS redis_memory_key VARCHAR(100);
ALTER TABLE ticket_bot_sessions ALTER COLUMN private_dialog_id DROP NOT NULL;

-- Índices operacionais para performance em polling e recuperação por Deal / Usuário
CREATE INDEX IF NOT EXISTS idx_bot_sessions_deal ON ticket_bot_sessions(deal_id);
CREATE INDEX IF NOT EXISTS idx_bot_sessions_status_state ON ticket_bot_sessions(status, state);
CREATE INDEX IF NOT EXISTS idx_bot_sessions_requester_user ON ticket_bot_sessions(requester_user_id);
CREATE INDEX IF NOT EXISTS idx_bot_sessions_dialog ON ticket_bot_sessions(dialog_id);
CREATE INDEX IF NOT EXISTS idx_bot_sessions_last_interaction ON ticket_bot_sessions(last_interaction_at);

-- ====================================================================
-- TABELA: ticket_bot_audit_log
-- Rastreabilidade Pericial de Perguntas, Respostas e Evidência (B06)
-- ====================================================================

CREATE TABLE IF NOT EXISTS ticket_bot_audit_log (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES ticket_bot_sessions(id) ON DELETE CASCADE,
    deal_id INTEGER NOT NULL,
    requester_user_id INTEGER NOT NULL,
    question_identifier VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    answer_raw TEXT,
    answer_normalized VARCHAR(100),
    field_updated VARCHAR(100),
    value_updated VARCHAR(100),
    message_id VARCHAR(100),
    channel VARCHAR(50) NOT NULL DEFAULT 'BITRIX_PRIVATE_CHAT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bot_audit_deal ON ticket_bot_audit_log(deal_id);
CREATE INDEX IF NOT EXISTS idx_bot_audit_requester ON ticket_bot_audit_log(requester_user_id);

-- ====================================================================
-- TABELA: ticket_bot_routing_audit
-- Auditoria Pré e Pós-Envio de Mensagens (Pre-Send & Post-Send Verification)
-- ====================================================================

CREATE TABLE IF NOT EXISTS ticket_bot_routing_audit (
    id SERIAL PRIMARY KEY,
    deal_id INTEGER NOT NULL,
    requester_user_id INTEGER NOT NULL,
    private_dialog_id VARCHAR(50) NOT NULL,
    internal_chat_id INTEGER,
    dialog_type VARCHAR(20) NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    block_reason TEXT,
    message_id VARCHAR(100),
    sent_at TIMESTAMPTZ,
    result VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_routing_audit_deal ON ticket_bot_routing_audit(deal_id);
CREATE INDEX IF NOT EXISTS idx_routing_audit_requester ON ticket_bot_routing_audit(requester_user_id);

-- ====================================================================
-- TABELA: store_outage_events
-- Incident Clustering & Alerta de Queda Geral por Loja (Sprint 2 - Feature 2)
-- ====================================================================

CREATE TABLE IF NOT EXISTS store_outage_events (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    category_theme VARCHAR(50) NOT NULL,
    deal_id BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_outage_store_time ON store_outage_events (store_name, category_theme, created_at);

-- ====================================================================
-- TABELA: ticket_csat_ratings
-- Pesquisa de Satisfação Pós-Atendimento - CSAT Pulse (Sprint 3 - Feature 5)
-- ====================================================================

CREATE TABLE IF NOT EXISTS ticket_csat_ratings (
    id SERIAL PRIMARY KEY,
    deal_id BIGINT NOT NULL,
    requester_user_id BIGINT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_csat_deal_user ON ticket_csat_ratings (deal_id, requester_user_id);
