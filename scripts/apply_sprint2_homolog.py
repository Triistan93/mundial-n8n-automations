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

# 1. Remover versões antigas dos nós da Sprint 2 caso já existam
nodes_to_remove = [
    "Preparar Notificação Chat Bitrix (Sprint 2)",
    "IF: Disparar Notificação IM?",
    "HTTP: Notificar Vendedor no Chat Bitrix"
]
nodes = [n for n in nodes if n["name"] not in nodes_to_remove]

# 2. Código da Preparação da Notificação (Feature Flag + BBCode)
js_preparar_notificacao = """// =========================================================================
// CHAVES DE CONTROLE & CONFIGURAÇÃO DA SPRINT 2 (FEATURE FLAGS)
// =========================================================================
const FLAG_NOTIFICAR_IM = true;               // Master switch da Sprint 2
const NOTIFICAR_SOMENTE_QUENTE = true;        // true = Apenas leads 🔥 QUENTES; false = Todos os leads
const NOTIFICAR_RESPONSAVEL = true;          // Notifica o vendedor responsável no chat 1:1
const CHATS_ADICIONAIS = [];                  // IDs de chats adicionais (ex: supervisão)

let dadosLead = {};
try {
    dadosLead = $('1. Preparar Dados Lead').first().json;
} catch (e) {}

let dealId = "";
try {
    const normalizar = $('Normalizar IDs Finais').first().json;
    if (normalizar && normalizar.dealId) dealId = String(normalizar.dealId);
} catch (e) {}

if (!dealId) {
    try {
        const fb = $('4b. Criar Card de Candidato1 (Fallback)').first().json;
        if (fb && fb.result) dealId = String(fb.result);
    } catch (e) {}
}

if (!dealId) {
    try {
        const a = $('Preparar Payload de Atualização1').first().json;
        if (a && a.deal_id) dealId = String(a.deal_id);
    } catch (e) {}
}

const temperatura = String(dadosLead.Temperatura || "").toUpperCase();
const badgeTemp = dadosLead.BadgeTemperatura || "";
const ehQuente = temperatura === "QUENTE" || badgeTemp.includes("QUENTE");

// Decisão de disparo baseada nas Feature Flags
if (!FLAG_NOTIFICAR_IM) {
    return [{ json: { deve_notificar: false, motivo: "Feature Flag FLAG_NOTIFICAR_IM desativada" } }];
}

if (NOTIFICAR_SOMENTE_QUENTE && !ehQuente) {
    return [{ json: { deve_notificar: false, motivo: `Lead com temperatura ${temperatura} não atingiu o critério QUENTE` } }];
}

const responsavelId = dadosLead.ResponsavelHomologacaoId || 32598; // Eduardo Alaminos em homologação
const dealUrl = dealId ? `https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${dealId}/` : "";

const destinatarios = [];
if (NOTIFICAR_RESPONSAVEL && responsavelId) {
    destinatarios.push(String(responsavelId));
}
for (const chat of CHATS_ADICIONAIS) {
    if (chat && !destinatarios.includes(String(chat))) {
        destinatarios.push(String(chat));
    }
}

if (!destinatarios.length) {
    return [{ json: { deve_notificar: false, motivo: "Nenhum destinatário configurado" } }];
}

// Montagem da mensagem rica com BBCode Bitrix24 e Alerta Visual/Sonoro
const mensagem = `🚨🔥 [b]ALERTA DE LEAD QUENTE NO WHATSAPP![/b] 🔥🚨\\n` +
    `[b]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/b]\\n` +
    `👤 [b]Lead:[/b] ${dadosLead.Nome || "Cliente Mundial Motos"}\\n` +
    `📱 [b]WhatsApp:[/b] ${dadosLead.Contato || "Não informado"}\\n` +
    `📍 [b]Cidade/Unidade:[/b] ${dadosLead.Cidade || "Não informado"}\\n` +
    `🏍️ [b]Modelo:[/b] ${dadosLead.Modelo || "Não informado"}\\n` +
    `💰 [b]Condição / Entrada:[/b] ${dadosLead.Entrada || "Não informado"}\\n` +
    `📊 [b]Feeling / Score:[/b] ${badgeTemp || "🔥 LEAD QUENTE"}\\n` +
    `💡 [b]Motivo do Score:[/b] ${dadosLead.JustificativaTemperatura || "Alta intenção de compra"}\\n` +
    `🎯 [b]Ação Imediata Recomendada:[/b] [u]${dadosLead.ProximaAcaoRecomendada || "Ligar imediatamente para o cliente"}[/u]\\n\\n` +
    (dealUrl ? `👉 [url=${dealUrl}][b]CLIQUE AQUI PARA ABRIR O CARD NO CRM (Deal #${dealId})[/b][/url]` : `Card #${dealId}`);

return destinatarios.map(destId => ({
    json: {
        deve_notificar: true,
        dialog_id: destId,
        mensagem: mensagem,
        dealId: dealId,
        leadNome: dadosLead.Nome,
        temperatura: temperatura
    }
}));"""

# 3. Definição dos Novos Nós
node_preparar = {
    "parameters": {
        "jsCode": js_preparar_notificacao
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [3040, 2380],
    "id": "sdr-sprint2-preparar-notificacao",
    "name": "Preparar Notificação Chat Bitrix (Sprint 2)"
}

node_if = {
    "parameters": {
        "conditions": {
            "options": {
                "caseSensitive": True,
                "leftValue": "",
                "typeValidation": "strict",
                "version": 2
            },
            "conditions": [
                {
                    "id": "cond-notificar-im-sdr",
                    "leftValue": "={{ $json.deve_notificar }}",
                    "rightValue": True,
                    "operator": {
                        "type": "boolean",
                        "operation": "equals"
                    }
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [3260, 2380],
    "id": "sdr-sprint2-if-notificar",
    "name": "IF: Disparar Notificação IM?"
}

node_http = {
    "parameters": {
        "method": "POST",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/im.message.add.json",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n  DIALOG_ID: $json.dialog_id,\n  MESSAGE: $json.mensagem,\n  SYSTEM: \"N\",\n  URL_PREVIEW: \"N\"\n}) }}",
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [3480, 2380],
    "id": "sdr-sprint2-http-notificar",
    "name": "HTTP: Notificar Vendedor no Chat Bitrix",
    "onError": "continueRegularOutput"
}

nodes.append(node_preparar)
nodes.append(node_if)
nodes.append(node_http)

# 4. Atualizar Sticky Note 8 para incluir a Sprint 2
for n in nodes:
    if n["name"] == "Sticky_08_Transicao_Handover":
        n["parameters"]["content"] = """### 🚀 08. Transição de Etapa, Handover OpenLines & Despedida WhatsApp (Sprint 2)

- **Normalizador de Etapa:** Mapeia `status_triagem` para a etapa de destino na Categoria 18:
  * Vendas/Humana ➔ `C18:UC_CGWMZF` (*ATENDIMENTO VENDEDOR*)
  * Pós-Vendas ➔ `C18:UC_G95T35` (*Pós Vendas*)
  * Administrativo ➔ `C18:UC_FKQTE0` (*Seguro/Documento*)
- **Mover Card de Etapa:** Atualiza o `STAGE_ID` do Deal no CRM.
- **Trava de Silêncio 24h:** Bloqueia o bot no Redis para não interferir na conversa do vendedor.
- **Despedida WhatsApp:** Envia mensagem cordial de encerramento da triagem para o cliente.
- **🚨 Alertas no Chat Bitrix (Sprint 2):** Dispara notificação instantânea com alerta sonoro via `im.message.add` para o vendedor responsável no momento exato em que um Lead Quente (🔥) for qualificado."""
        n["parameters"]["height"] = 720

# 5. Conexões Lógicas
# Bloquear Bot 24h deve conectar em:
# 1) Enviar MSG Final (já conectava)
# 2) Preparar Notificação Chat Bitrix (Sprint 2)
conns["Bloquear Bot 24h"] = {
    "main": [
        [
            {"node": "Enviar MSG Final", "type": "main", "index": 0},
            {"node": "Preparar Notificação Chat Bitrix (Sprint 2)", "type": "main", "index": 0}
        ]
    ]
}

conns["Preparar Notificação Chat Bitrix (Sprint 2)"] = {
    "main": [
        [
            {"node": "IF: Disparar Notificação IM?", "type": "main", "index": 0}
        ]
    ]
}

conns["IF: Disparar Notificação IM?"] = {
    "main": [
        [
            {"node": "HTTP: Notificar Vendedor no Chat Bitrix", "type": "main", "index": 0}
        ],
        []
    ]
}

conns["HTTP: Notificar Vendedor no Chat Bitrix"] = {
    "main": [[]]
}

wf["nodes"] = nodes
wf["connections"] = conns

# Salvar arquivo local
with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print(f"Workflow local atualizado: {len(nodes)} nós.")

# 6. Deploy para o n8n
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
    print("✅ Sprint 2 aplicada com sucesso no workflow de homologação [5pFwAtQWvsuhyxO0]!")
else:
    print("❌ Erro no deploy:", r.text[:400])
