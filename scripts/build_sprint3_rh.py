import json
import sys
import uuid

sys.stdout.reconfigure(encoding='utf-8')

input_path = r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json'
with open(input_path, 'r', encoding='utf-8-sig') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
connections = wf.get('connections', {})
node_dict = {n['name']: n for n in nodes}

# 1. Update Handover Redis node TTL to 30 days (2592000s)
node_redis_handover = node_dict.get('Redis: Bloquear Bot 24h') or node_dict.get('Redis: Bloquear Bot 30d (Handover Humano)')
if node_redis_handover:
    node_redis_handover['name'] = 'Redis: Bloquear Bot 30d (Handover Humano)'
    node_redis_handover['parameters']['ttl'] = 2592000
    print("✅ Updated Handover Redis block to 30 days (2592000s)")

# 2. Update AI Agent Prompt with PASSO 3: RETORNO DE CANDIDATO / PÓS-ATENDIMENTO
node_ai = node_dict.get('AI Agent')
if node_ai:
    current_prompt = node_ai['parameters']['options']['systemMessage']
    
    passo3_text = """

# PASSO 3: RETORNO DE CANDIDATO JÁ CADASTRADO / PÓS-ATENDIMENTO
Se o histórico da conversa indicar que o candidato JÁ CONCLUIU sua candidatura para uma vaga anteriormente:
1. RECONHECIMENTO: Acolha o candidato pelo primeiro nome (ex: "Olá, [Nome]! Que bom falar com você novamente.").
2. DÚVIDA OU STATUS DO PROCESSO: Se ele perguntar se há novidades, prazos ou resultados da vaga, tranquilize-o com empatia:
   - Explique que o currículo dele já está registrado com sucesso e em análise cuidadosa pela equipe de Recursos Humanos.
   - Informe que, assim que o setor avançar para a etapa de entrevistas, a equipe de RH entrará em contato diretamente por este WhatsApp.
   - Deseje um excelente dia e encerre cordialmente.
   - IMPORTANTE: NÃO gere o bloco de código JSON para dúvidas de status (apenas responda cordialmente em texto).
3. ENVIO DE NOVO DOCUMENTO OU DADO ADICIONAL: Se o candidato enviar um certificado, documento complementar ou informação extra:
   - Agradeça e confirme que o arquivo/informação foi recebido e anexado ao perfil dele.
   - NÃO gere o bloco de código JSON.
4. CANDIDATURA PARA NOVA VAGA ADICIONAL: Somente se o candidato disser expressamente que deseja se candidatar para OUTRA VAGA diferente da anterior:
   - Confirme a nova vaga da lista oficial e a cidade.
   - Aí sim gere o bloco de código JSON no encerramento para atualizar o cadastro no CRM."""

    # Insert PASSO 3 right after PASSO 2
    if "# PASSO 3: RETORNO DE CANDIDATO" not in current_prompt:
        if "# REGRAS DE CONVERSAÇÃO" in current_prompt:
            current_prompt = current_prompt.replace("# REGRAS DE CONVERSAÇÃO", passo3_text + "\n\n# REGRAS DE CONVERSAÇÃO")
        else:
            current_prompt += passo3_text
        node_ai['parameters']['options']['systemMessage'] = current_prompt
        print("✅ Added PASSO 3 (Pós-Atendimento e Anti-Loop) to AI Agent prompt")

# 3. Add Human Stage Safety Check Nodes
# 3.1. Checar Estagio e Bloqueio Humano (Code)
node_check_human = {
    "parameters": {
        "jsCode": """const item = $input.item.json;
const deals = item.result || [];
const total = item.total || 0;

let temDealAberto = total > 0 && deals.length > 0;
let deal = temDealAberto ? deals[0] : null;

// Etapas onde o atendimento é EXCLUSIVAMENTE humano:
const etapasHumanas = [
    'C198:UC_0YLZXN',        // ASSUNTOS RH
    'C198:PREPAYMENT_INVOI', // Entrevista RH
    'C198:UC_WFH3KE',        // Testes
    'C198:UC_8KNLBM',        // Entrevista Gerencial
    'C198:UC_ML059R',        // Avaliação
    'C198:EXECUTING',        // Documentação
    'C198:WON',              // Contratados
    'C198:LOSE',             // Desqualificado
    'C198:UC_YEOIKS'         // Duplicados
];

let emAtendimentoHumano = false;
let stageId = deal ? (deal.STAGE_ID || "") : "";
if (deal && etapasHumanas.includes(stageId)) {
    emAtendimentoHumano = true;
}

let instance = "botrh1";
let remoteJid = "";
try {
    instance = $('RECEPTIVO').first().json.instance || "botrh1";
    remoteJid = $('RECEPTIVO').first().json.remoteJid || "";
} catch(e) {}

return [{
    json: {
        ...item,
        tem_deal_aberto: temDealAberto,
        deal_id: deal ? deal.ID : null,
        stage_id: stageId,
        em_atendimento_humano: emAtendimentoHumano,
        instance: instance,
        remote_jid: remoteJid
    }
}];"""
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [7050, -3800],
    "id": str(uuid.uuid4()),
    "name": "Checar Estagio e Bloqueio Humano"
}

# 3.2. IF: Em Gestao Humana? (IF node)
node_if_human = {
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
                    "id": "cond-gestao-humana",
                    "leftValue": "={{ $json.em_atendimento_humano }}",
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
    "position": [7250, -3800],
    "id": str(uuid.uuid4()),
    "name": "IF: Em Gestao Humana?"
}

# 3.3. Redis: Silenciar Gestao Humana 30d (Redis)
node_redis_human = {
    "parameters": {
        "operation": "set",
        "key": "={{ $json.instance }} {{ $json.remote_jid }} block",
        "value": "true",
        "expire": True,
        "ttl": 2592000
    },
    "type": "n8n-nodes-base.redis",
    "typeVersion": 1,
    "position": [7480, -3950],
    "id": str(uuid.uuid4()),
    "name": "Redis: Silenciar Gestao Humana 30d",
    "credentials": {
        "redis": {
            "id": "NlIbdmbaePYxgp6S",
            "name": "Redis Evolution"
        }
    }
}

# 3.4. Timeline: Notificar Silencio Humano (HTTP)
node_timeline_silence = {
    "parameters": {
        "method": "POST",
        "url": "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.timeline.comment.add.json",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={\n  \"fields\": {\n    \"ENTITY_ID\": {{ $json.deal_id }},\n    \"ENTITY_TYPE\": \"deal\",\n    \"COMMENT\": \"<b>💬 MENSAGEM DO CONTATO (BOT EM SILÊNCIO):</b><br>O contato enviou mensagem no WhatsApp enquanto o card está sob gestão humana na etapa <b>{{ $json.stage_id }}</b>.<br><i>O robô permaneceu em silêncio absoluto para dar preferência ao atendimento humano da equipe de RH.</i>\"\n  }\n}",
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [7700, -3950],
    "id": str(uuid.uuid4()),
    "name": "Timeline: Notificar Silencio Humano"
}

# Add new nodes to list
nodes.extend([node_check_human, node_if_human, node_redis_human, node_timeline_silence])

# Update Connections:
# Bitrix: Buscar Deal Aberto -> Checar Estagio e Bloqueio Humano -> IF: Em Gestao Humana?
connections['Bitrix: Buscar Deal Aberto'] = {
    "main": [[{"node": "Checar Estagio e Bloqueio Humano", "type": "main", "index": 0}]]
}
connections['Checar Estagio e Bloqueio Humano'] = {
    "main": [[{"node": "IF: Em Gestao Humana?", "type": "main", "index": 0}]]
}

# IF: Em Gestao Humana?:
# Output 0 (True: em atendimento humano) -> Redis: Silenciar Gestao Humana 30d -> Timeline: Notificar Silencio Humano
connections['IF: Em Gestao Humana?'] = {
    "main": [
        [{"node": "Redis: Silenciar Gestao Humana 30d", "type": "main", "index": 0}],
        [{"node": "IF: Deal Aberto Existe?", "type": "main", "index": 0}]
    ]
}
connections['Redis: Silenciar Gestao Humana 30d'] = {
    "main": [[{"node": "Timeline: Notificar Silencio Humano", "type": "main", "index": 0}]]
}

# Update Handover Redis connections with new name
connections['Alertar Responsavel RH'] = {
    "main": [[{"node": "Redis: Bloquear Bot 30d (Handover Humano)", "type": "main", "index": 0}]]
}
connections['Redis: Bloquear Bot 30d (Handover Humano)'] = {
    "main": [[{"node": "WhatsApp: Enviar Despedida Transferência", "type": "main", "index": 0}]]
}

# Clean up any leftover connection from old node names
if 'Redis: Bloquear Bot 24h' in connections:
    del connections['Redis: Bloquear Bot 24h']
if 'Redis' in connections:
    del connections['Redis']

wf['nodes'] = nodes
wf['connections'] = connections

out_file = r'C:\mundial-n8n-automations\workflows\AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A_SPRINT3.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print(f"🎉 Created Sprint 3 workflow with {len(nodes)} nodes!")
