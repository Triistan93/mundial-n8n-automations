# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

WORKFLOW_FILE = "c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_HOMOLOG.json"
N8N_WORKFLOW_ID = "5pFwAtQWvsuhyxO0"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU"
N8N_BASE_URL = "https://sophia-n8nsophia.timft8.easypanel.host/api/v1"

with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
    wf = json.load(f)

nodes = wf.get("nodes", [])
conns = wf.get("connections", {})

# 1. Remover versões antigas dos nós da Sprint 3 caso já existam
sprint3_node_names = [
    "Preparar Contexto de Follow-Up (Sprint 3)",
    "Redis: Gravar Token Follow-Up",
    "Esperar Inatividade do Lead (Sprint 3)",
    "Redis: Obter Token Atual",
    "Redis: Obter Status de Bloqueio",
    "Avaliar Disparo do Resgate (Sprint 3)",
    "IF: Executar Resgate de Follow-Up?",
    "Enviar MSG Resgate (WhatsApp)",
    "Inserir Resgate na Memoria IA",
    "Redis: Marcar Resgate Finalizado",
    "Sticky_09_FollowUp_Resgate"
]
nodes = [n for n in nodes if n["name"] not in sprint3_node_names]

# 2. Definição do Código de Preparação
js_preparar_contexto = """// =========================================================================
// SPRINT 3: PREPARAÇÃO DE CONTEXTO E TOKEN DE FOLLOW-UP
// =========================================================================
const receptivo = $('RECEPTIVO').first().json;
const instance = receptivo.instance || "outrasmidias";
const remoteJid = receptivo.remoteJid || "";
const pushName = receptivo.pushName || "tudo bem?";
const timestamp = Date.now();

// Gera um token único atômico para esta interação
const followup_token = `${instance}_${remoteJid}_${timestamp}`;

let lastBotMessage = "";
try {
    lastBotMessage = $('Formatar Output do Agente').first().json.message || "";
} catch (e) {}

return [{
    json: {
        instance: instance,
        remoteJid: remoteJid,
        pushName: pushName,
        followup_token: followup_token,
        last_bot_message: lastBotMessage,
        armed_at: new Date().toISOString()
    }
}];"""

js_avaliar_resgate = """// =========================================================================
// SPRINT 3: AVALIAÇÃO DE ELEGIBILIDADE PARA RESGATE DE INATIVIDADE
// =========================================================================
const FLAG_FOLLOWUP_ATIVO = true; // Master switch da Sprint 3

const prep = $('Preparar Contexto de Follow-Up (Sprint 3)').first().json;
const tokenOriginal = prep.followup_token || "";

let tokenAtual = "";
try {
    tokenAtual = $('Redis: Obter Token Atual').first().json.token_atual || "";
} catch (e) {}

let isBlocked = "";
try {
    isBlocked = $('Redis: Obter Status de Bloqueio').first().json.is_blocked || "";
} catch (e) {}

// 1. Verificação da Feature Flag
if (!FLAG_FOLLOWUP_ATIVO) {
    return [{ json: { deve_resgatar: false, motivo: "Feature flag de Follow-up desativada" } }];
}

// 2. Se o bot estiver bloqueado (atendente humano assumiu ou lead concluído)
if (isBlocked === "true") {
    return [{ json: { deve_resgatar: false, motivo: "Lead bloqueado por atendimento humano ou finalizado" } }];
}

// 3. Se o token atual for diferente do original (cliente respondeu e gerou nova interação)
if (tokenAtual !== tokenOriginal) {
    return [{ json: { deve_resgatar: false, motivo: `Cliente respondeu durante o período (atual: ${tokenAtual} vs original: ${tokenOriginal})` } }];
}

// CLIENTE PERMANECE SILENCIOSO E ELEGÍVEL PARA RESGATE!
const pushName = prep.pushName || "tudo bem?";
const primeiroNome = pushName.split(" ")[0].trim();
const remoteJid = prep.remoteJid;

// Mensagem empática de resgate da Sophia (Mundial Motos)
const mensagemResgate = `*Mundial Motos*: Oi ${primeiroNome}, tudo bem? Vi que estávamos conversando agora a pouco! Você conseguiu dar uma olhadinha na minha mensagem anterior? Se quiser, consigo tirar qualquer dúvida ou simular as opções para você aqui rapidinho! 😊🏍️`;

return [{
    json: {
        deve_resgatar: true,
        remoteJid: remoteJid,
        primeiroNome: primeiroNome,
        mensagem_resgate: mensagemResgate
    }
}];"""

# 3. Novos Nós
node_prep_ctx = {
    "parameters": {"jsCode": js_preparar_contexto},
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [3680, 700],
    "id": "sdr-sprint3-prep-ctx",
    "name": "Preparar Contexto de Follow-Up (Sprint 3)"
}

node_redis_gravar_token = {
    "parameters": {
        "operation": "set",
        "key": "={{ $('RECEPTIVO').first().json.instance }} {{ $('RECEPTIVO').first().json.remoteJid }} followup_token",
        "value": "={{ $json.followup_token }}",
        "expire": True,
        "ttl": 86400
    },
    "type": "n8n-nodes-base.redis",
    "typeVersion": 1,
    "position": [3900, 700],
    "id": "sdr-sprint3-redis-gravar",
    "name": "Redis: Gravar Token Follow-Up",
    "credentials": {"redis": {"id": "NlIbdmbaePYxgp6S", "name": "Redis Evolution"}}
}

node_esperar_inatividade = {
    "parameters": {
        "amount": 35,
        "unit": "seconds"
    },
    "type": "n8n-nodes-base.wait",
    "typeVersion": 1.1,
    "position": [4120, 700],
    "id": "sdr-sprint3-wait-inatividade",
    "name": "Esperar Inatividade do Lead (Sprint 3)"
}

node_redis_obter_token = {
    "parameters": {
        "operation": "get",
        "key": "={{ $('RECEPTIVO').first().json.instance }} {{ $('RECEPTIVO').first().json.remoteJid }} followup_token",
        "propertyName": "token_atual",
        "options": {}
    },
    "type": "n8n-nodes-base.redis",
    "typeVersion": 1,
    "position": [4340, 700],
    "id": "sdr-sprint3-redis-obter-token",
    "name": "Redis: Obter Token Atual",
    "credentials": {"redis": {"id": "NlIbdmbaePYxgp6S", "name": "Redis Evolution"}}
}

node_redis_obter_block = {
    "parameters": {
        "operation": "get",
        "key": "={{ $('RECEPTIVO').first().json.instance }} {{ $('RECEPTIVO').first().json.remoteJid }} block",
        "propertyName": "is_blocked",
        "options": {}
    },
    "type": "n8n-nodes-base.redis",
    "typeVersion": 1,
    "position": [4560, 700],
    "id": "sdr-sprint3-redis-obter-block",
    "name": "Redis: Obter Status de Bloqueio",
    "credentials": {"redis": {"id": "NlIbdmbaePYxgp6S", "name": "Redis Evolution"}}
}

node_avaliar_resgate = {
    "parameters": {"jsCode": js_avaliar_resgate},
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [4780, 700],
    "id": "sdr-sprint3-avaliar-resgate",
    "name": "Avaliar Disparo do Resgate (Sprint 3)"
}

node_if_resgate = {
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [
                {
                    "id": "cond-resgate-sdr",
                    "leftValue": "={{ $json.deve_resgatar }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "equals"}
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [5000, 700],
    "id": "sdr-sprint3-if-resgate",
    "name": "IF: Executar Resgate de Follow-Up?"
}

node_enviar_resgate = {
    "parameters": {
        "method": "POST",
        "url": "=https://sophia-evolution-api.timft8.easypanel.host/message/sendText/outrasmidias",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "apikey", "value": "7EuD96NSfnpNRvJZdAAGgnbcdX3rAA9aIsbR8prV7Z0wCyTwQVJdRaEMvj0dgD33KfYtWch6556VSX6JxBMWYC3QHo28CWux9iTqpH5umrnYON2r3DRLzmfyZvrbG2sn"}
            ]
        },
        "sendBody": True,
        "bodyParameters": {
            "parameters": [
                {"name": "number", "value": "={{ $json.remoteJid }}"},
                {"name": "text", "value": "={{ $json.mensagem_resgate }}"}
            ]
        },
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [5240, 600],
    "id": "sdr-sprint3-enviar-resgate",
    "name": "Enviar MSG Resgate (WhatsApp)",
    "onError": "continueRegularOutput"
}

node_inserir_memoria = {
    "parameters": {
        "mode": "insert",
        "messages": {
            "messageValues": [
                {
                    "type": "ai",
                    "message": "={{ $('Avaliar Disparo do Resgate (Sprint 3)').first().json.mensagem_resgate }}"
                }
            ]
        }
    },
    "type": "@n8n/n8n-nodes-langchain.memoryManager",
    "typeVersion": 1.1,
    "position": [5460, 600],
    "id": "sdr-sprint3-inserir-memoria",
    "name": "Inserir Resgate na Memoria IA"
}

node_redis_marcar_feito = {
    "parameters": {
        "operation": "set",
        "key": "={{ $('RECEPTIVO').first().json.instance }} {{ $('RECEPTIVO').first().json.remoteJid }} followup_token",
        "value": "resgate_concluido_step1",
        "expire": True,
        "ttl": 86400
    },
    "type": "n8n-nodes-base.redis",
    "typeVersion": 1,
    "position": [5680, 600],
    "id": "sdr-sprint3-marcar-feito",
    "name": "Redis: Marcar Resgate Finalizado",
    "credentials": {"redis": {"id": "NlIbdmbaePYxgp6S", "name": "Redis Evolution"}}
}

node_sticky9 = {
    "parameters": {
        "content": """### ⏱️ 09. Follow-Up Inteligente de Resgate (Sprint 3 - Anti-Abandono)

- **Arma Token Atômico:** Registra um token único de interação no Redis (`followup_token`).
- **Espera Não-Bloqueante:** Aguarda a inatividade do cliente (35s em testes / 2h em produção).
- **Validação Anti-Spam:**
  * Se o cliente responder ➔ O token no Redis muda e o resgate é cancelado silenciosamente.
  * Se um vendedor assumir ➔ `isBlocked` impede qualquer envio.
- **Disparo Empático:** Envia mensagem carinhosa e personalizada de reengajamento no WhatsApp.
- **Sincronia de Memória:** Registra a fala no Redis Chat Memory para manter o contexto 100% perfeito caso o cliente responda mais tarde.""",
        "height": 560,
        "width": 2260,
        "color": 6
    },
    "type": "n8n-nodes-base.stickyNote",
    "typeVersion": 1,
    "position": [3620, 480],
    "id": "sdr-sprint3-sticky-note",
    "name": "Sticky_09_FollowUp_Resgate"
}

nodes.extend([
    node_prep_ctx,
    node_redis_gravar_token,
    node_esperar_inatividade,
    node_redis_obter_token,
    node_redis_obter_block,
    node_avaliar_resgate,
    node_if_resgate,
    node_enviar_resgate,
    node_inserir_memoria,
    node_redis_marcar_feito,
    node_sticky9
])

# 4. Conexões Lógicas
# Enviar MSG (Continua o Papo) -> Preparar Contexto de Follow-Up (Sprint 3)
conns["Enviar MSG (Continua o Papo)"] = {
    "main": [
        [{"node": "Preparar Contexto de Follow-Up (Sprint 3)", "type": "main", "index": 0}]
    ]
}

conns["Preparar Contexto de Follow-Up (Sprint 3)"] = {
    "main": [
        [{"node": "Redis: Gravar Token Follow-Up", "type": "main", "index": 0}]
    ]
}

conns["Redis: Gravar Token Follow-Up"] = {
    "main": [
        [{"node": "Esperar Inatividade do Lead (Sprint 3)", "type": "main", "index": 0}]
    ]
}

conns["Esperar Inatividade do Lead (Sprint 3)"] = {
    "main": [
        [{"node": "Redis: Obter Token Atual", "type": "main", "index": 0}]
    ]
}

conns["Redis: Obter Token Atual"] = {
    "main": [
        [{"node": "Redis: Obter Status de Bloqueio", "type": "main", "index": 0}]
    ]
}

conns["Redis: Obter Status de Bloqueio"] = {
    "main": [
        [{"node": "Avaliar Disparo do Resgate (Sprint 3)", "type": "main", "index": 0}]
    ]
}

conns["Avaliar Disparo do Resgate (Sprint 3)"] = {
    "main": [
        [{"node": "IF: Executar Resgate de Follow-Up?", "type": "main", "index": 0}]
    ]
}

conns["IF: Executar Resgate de Follow-Up?"] = {
    "main": [
        [{"node": "Enviar MSG Resgate (WhatsApp)", "type": "main", "index": 0}],
        []
    ]
}

conns["Enviar MSG Resgate (WhatsApp)"] = {
    "main": [
        [{"node": "Inserir Resgate na Memoria IA", "type": "main", "index": 0}]
    ]
}

conns["Inserir Resgate na Memoria IA"] = {
    "main": [
        [{"node": "Redis: Marcar Resgate Finalizado", "type": "main", "index": 0}]
    ]
}

conns["Redis: Marcar Resgate Finalizado"] = {
    "main": [[]]
}

# Conectar ai_memory do Redis Chat Memory1 para o novo Inserir Resgate na Memoria IA
if "Redis Chat Memory1" in conns:
    ai_mem_conns = conns["Redis Chat Memory1"].get("ai_memory", [[]])
    if len(ai_mem_conns) > 0:
        existing_targets = ai_mem_conns[0]
        if not any(t.get("node") == "Inserir Resgate na Memoria IA" for t in existing_targets):
            existing_targets.append({"node": "Inserir Resgate na Memoria IA", "type": "ai_memory", "index": 0})
        conns["Redis Chat Memory1"]["ai_memory"] = [existing_targets]

wf["nodes"] = nodes
wf["connections"] = conns

# Salvar arquivo local
with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print(f"Workflow local atualizado: {len(nodes)} nós.")

# 5. Deploy no n8n
headers = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "name": wf.get("name", "[HOMOLOG] SDR - Mundial Motos (Unificado)"),
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

r = requests.put(f"{N8N_BASE_URL}/workflows/{N8N_WORKFLOW_ID}", headers=headers, json=payload)
print(f"Deploy no n8n: HTTP {r.status_code}")
if r.status_code == 200:
    print("✅ Sprint 3 aplicada com sucesso no workflow de homologação [5pFwAtQWvsuhyxO0]!")
else:
    print("❌ Erro no deploy:", r.text[:400])
