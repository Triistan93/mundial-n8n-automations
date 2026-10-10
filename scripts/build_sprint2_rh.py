import json
import sys
import uuid

sys.stdout.reconfigure(encoding='utf-8')

input_path = r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json'
with open(input_path, 'r', encoding='utf-8-sig') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
connections = wf.get('connections', {})

# Build node index
node_dict = {n['name']: n for n in nodes}

# 1. Preparar Dados Transferência (Code)
node_prep = {
    "parameters": {
        "jsCode": """const item = $input.item.json;

// 1. Definição do Responsável do RH
// Modo Teste: 32598 (Eduardo Alaminos)
// Modo Produção: 4278 (Nina Biermann - RH)
const RESPONSAVEL_RH_ID = 32598;

// 2. Extração segura dos dados
const extracted = item.extracted_data || {};
const candidato = extracted.candidato || {};

let nomeCandidato = (candidato.nome || "").trim();
if (!nomeCandidato) {
    try {
        nomeCandidato = ($('RECEPTIVO').first().json.pushName || "").trim();
    } catch(e) {}
}
if (!nomeCandidato) {
    nomeCandidato = "Solicitante WhatsApp";
}

let telefone = item.telefone || "";
if (!telefone) {
    try {
        telefone = ($('RECEPTIVO').first().json.remoteJid || "").replace(/\\D/g, "");
    } catch(e) {}
}

let remoteJid = "";
let instance = "botrh1";
try {
    remoteJid = $('RECEPTIVO').first().json.remoteJid || "";
    instance = $('RECEPTIVO').first().json.instance || "botrh1";
} catch(e) {}

const tipoAtendimento = extracted.tipo_atendimento || "geral";
const mapaTipos = {
    "saude_ocupacional": "🏥 Saúde Ocupacional / Clínica / Exames",
    "departamento_pessoal": "👥 Departamento Pessoal / Colaborador",
    "b2b_outros": "🏢 B2B / Fornecedor / Outros"
};
const tipoRotulo = mapaTipos[tipoAtendimento] || "📋 Assuntos Gerais RH";

const resumoAssunto = (extracted.resumo_assunto || "Solicitação de atendimento humano via WhatsApp").trim();
const mensagemDespedida = (item.message || "Agradecemos o contato. Encaminhamos sua solicitação para a equipe responsável.").trim();

return [{
    json: {
        nome_candidato: nomeCandidato,
        telefone: telefone,
        remote_jid: remoteJid,
        instance: instance,
        tipo_atendimento: tipoAtendimento,
        tipo_rotulo: tipoRotulo,
        resumo_assunto: resumoAssunto,
        assigned_user_id: RESPONSAVEL_RH_ID,
        mensagem_despedida: mensagemDespedida
    }
}];"""
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [10560, -3888],
    "id": str(uuid.uuid4()),
    "name": "Preparar Dados Transferência"
}

# 2. Buscar Contato Transferência (HTTP)
node_busca_contato = {
    "parameters": {
        "method": "POST",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.duplicate.findbycomm.json",
        "sendQuery": True,
        "queryParameters": {
            "parameters": [
                {"name": "entity_type", "value": "=CONTACT"},
                {"name": "type", "value": "PHONE"},
                {"name": "values[0]", "value": "={{ $json.telefone }}"}
            ]
        },
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [10784, -3888],
    "id": str(uuid.uuid4()),
    "name": "Buscar Contato Transferência",
    "onError": "continueRegularOutput"
}

# 3. Preparar Deal Assuntos RH (Code)
node_prep_deal = {
    "parameters": {
        "jsCode": """const prev = $('Preparar Dados Transferência').first().json;
let contactId = null;

try {
    const res = $json.result;
    if (res && res.CONTACT && Array.isArray(res.CONTACT) && res.CONTACT.length > 0) {
        contactId = res.CONTACT[0];
    }
} catch(e) {}

const dealPayload = {
    fields: {
        TITLE: `[RH - ${prev.tipo_rotulo}] ${prev.nome_candidato}`,
        CATEGORY_ID: 198,
        STAGE_ID: "C198:UC_0YLZXN",
        ASSIGNED_BY_ID: prev.assigned_user_id,
        COMMENTS: `<b>Demanda recebida via WhatsApp (Bot RH):</b><br><b>Tipo:</b> ${prev.tipo_rotulo}<br><b>Solicitante:</b> ${prev.nome_candidato}<br><b>Telefone:</b> ${prev.telefone}<br><b>Resumo:</b> ${prev.resumo_assunto}`
    }
};

if (contactId) {
    dealPayload.fields.CONTACT_ID = contactId;
}

return [{
    json: {
        ...prev,
        contact_id: contactId,
        deal_payload: dealPayload
    }
}];"""
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [11008, -3888],
    "id": str(uuid.uuid4()),
    "name": "Preparar Deal Assuntos RH"
}

# 4. Criar Deal Assuntos RH (HTTP)
node_criar_deal = {
    "parameters": {
        "method": "POST",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.deal.add.json",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ $json.deal_payload }}",
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [11232, -3888],
    "id": str(uuid.uuid4()),
    "name": "Criar Deal Assuntos RH"
}

# 5. Adicionar Timeline Assuntos RH (HTTP)
node_timeline = {
    "parameters": {
        "method": "POST",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.timeline.comment.add.json",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={\n  \"fields\": {\n    \"ENTITY_ID\": {{ $json.result }},\n    \"ENTITY_TYPE\": \"deal\",\n    \"COMMENT\": \"<b>⚠️ TRANSFERÊNCIA HUMANA / ATENDIMENTO RH:</b><br><b>Tipo:</b> {{ $('Preparar Dados Transferência').first().json.tipo_rotulo }}<br><b>Solicitante:</b> {{ $('Preparar Dados Transferência').first().json.nome_candidato }}<br><b>Telefone:</b> {{ $('Preparar Dados Transferência').first().json.telefone }}<br><b>Resumo:</b> {{ $('Preparar Dados Transferência').first().json.resumo_assunto }}<br><i>O robô foi pausado para permitir o atendimento humano no WhatsApp.</i>\"\n  }\n}",
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [11456, -3888],
    "id": str(uuid.uuid4()),
    "name": "Adicionar Timeline Assuntos RH"
}

# 6. Alertar Responsavel RH (HTTP)
node_alerta = {
    "parameters": {
        "method": "POST",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/im.message.add.json",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={\n  \"DIALOG_ID\": {{ $('Preparar Dados Transferência').first().json.assigned_user_id }},\n  \"MESSAGE\": \"🔔 [ALERTA RH] Novo Atendimento no WhatsApp aguardando equipe!\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n📌 Tipo: {{ $('Preparar Dados Transferência').first().json.tipo_rotulo }}\\n👤 Solicitante: {{ $('Preparar Dados Transferência').first().json.nome_candidato }}\\n📱 WhatsApp: {{ $('Preparar Dados Transferência').first().json.telefone }}\\n📝 Resumo: {{ $('Preparar Dados Transferência').first().json.resumo_assunto }}\\n🔗 Abrir Card no Bitrix: https://b24-88dbfb.bitrix24.com.br/crm/deal/details/{{ $('Criar Deal Assuntos RH').first().json.result }}/\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\"\n}",
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [11680, -3888],
    "id": str(uuid.uuid4()),
    "name": "Alertar Responsavel RH"
}

# 7. Redis: Bloquear Bot 24h
node_redis_block = {
    "parameters": {
        "operation": "set",
        "key": "={{ $('Preparar Dados Transferência').first().json.instance }} {{ $('Preparar Dados Transferência').first().json.remote_jid }} block",
        "value": "true",
        "expire": True,
        "ttl": 86400
    },
    "type": "n8n-nodes-base.redis",
    "typeVersion": 1,
    "position": [11904, -3888],
    "id": str(uuid.uuid4()),
    "name": "Redis: Bloquear Bot 24h",
    "credentials": {
        "redis": {
            "id": "NlIbdmbaePYxgp6S",
            "name": "Redis Evolution"
        }
    }
}

# 8. WhatsApp: Enviar Despedida Transferência (HTTP)
node_send_zap = {
    "parameters": {
        "method": "POST",
        "url": "=https://sophia-evolution-api.timft8.easypanel.host/message/sendText/botrh1",
        "sendBody": True,
        "bodyParameters": {
            "parameters": [
                {
                    "name": "number",
                    "value": "={{ $('Preparar Dados Transferência').first().json.remote_jid }}"
                },
                {
                    "name": "text",
                    "value": "={{ '*Mundial Motos RH*: ' + $('Preparar Dados Transferência').first().json.mensagem_despedida }}"
                }
            ]
        },
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [12128, -3888],
    "id": str(uuid.uuid4()),
    "name": "WhatsApp: Enviar Despedida Transferência"
}

# 9. Sticky Note
node_note = {
    "parameters": {
        "content": "## HANDOVER HUMANO (TRILHAS 2, 3 E 4)\nCria card na etapa ASSUNTOS RH (Categoria 198), anota histórico na Timeline, alerta o responsável no Bitrix (32598 teste / 4278 prod), bloqueia o bot e envia mensagem de encerramento ao usuário.",
        "height": 180,
        "width": 1780,
        "color": 4
    },
    "type": "n8n-nodes-base.stickyNote",
    "typeVersion": 1,
    "position": [10560, -4120],
    "id": str(uuid.uuid4()),
    "name": "Sticky Note - Handover RH"
}

# Remove old unused 'Redis' node
nodes = [n for n in nodes if n.get('name') != 'Redis']

# Add new nodes
new_nodes = [
    node_prep,
    node_busca_contato,
    node_prep_deal,
    node_criar_deal,
    node_timeline,
    node_alerta,
    node_redis_block,
    node_send_zap,
    node_note
]
nodes.extend(new_nodes)

# Update Connections:
# In Roteador de Saída:
# Output 1 was connected to Redis and Enviar MSG.
# Now Output 1 connects to 'Preparar Dados Transferência'.
if 'Roteador de Saída' in connections:
    conns_saida = connections['Roteador de Saída'].get('main', [])
    if len(conns_saida) > 1:
        # Output index 1 is Transferência
        conns_saida[1] = [{"node": "Preparar Dados Transferência", "type": "main", "index": 0}]

# Pipeline connections:
connections['Preparar Dados Transferência'] = {
    "main": [[{"node": "Buscar Contato Transferência", "type": "main", "index": 0}]]
}
connections['Buscar Contato Transferência'] = {
    "main": [[{"node": "Preparar Deal Assuntos RH", "type": "main", "index": 0}]]
}
connections['Preparar Deal Assuntos RH'] = {
    "main": [[{"node": "Criar Deal Assuntos RH", "type": "main", "index": 0}]]
}
connections['Criar Deal Assuntos RH'] = {
    "main": [[{"node": "Adicionar Timeline Assuntos RH", "type": "main", "index": 0}]]
}
connections['Adicionar Timeline Assuntos RH'] = {
    "main": [[{"node": "Alertar Responsavel RH", "type": "main", "index": 0}]]
}
connections['Alertar Responsavel RH'] = {
    "main": [[{"node": "Redis: Bloquear Bot 24h", "type": "main", "index": 0}]]
}
connections['Redis: Bloquear Bot 24h'] = {
    "main": [[{"node": "WhatsApp: Enviar Despedida Transferência", "type": "main", "index": 0}]]
}

# Clean up any leftover connection to 'Redis'
if 'Redis' in connections:
    del connections['Redis']

wf['nodes'] = nodes
wf['connections'] = connections

out_file = r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A_SPRINT2.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print(f"🎉 Created Sprint 2 workflow with {len(nodes)} nodes!")
