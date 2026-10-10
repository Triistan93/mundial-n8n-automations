import json
import sys
import shutil
import requests

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'

live_file = 'workflows/BITRIX_TI_AI_TRIAGE_AGENT_LIVE.json'
backup_file = 'workflows/backup_before_ticket_layout_reorganize.json'

shutil.copyfile(live_file, backup_file)
print(f"Backup created at: {backup_file}")

with open(live_file, 'r', encoding='utf-8') as f:
    wf = json.load(f)

import test_ticket_layout_mapping
pos_dict = test_ticket_layout_mapping.get_ticket_node_positions()

# 1. Update functional node positions
functional_count = 0
for node in wf['nodes']:
    if not node['type'].endswith('stickyNote'):
        name = node['name']
        if name in pos_dict:
            node['position'] = pos_dict[name]
            functional_count += 1
        else:
            print(f"ERROR: Missing position for {name}")
            sys.exit(1)

print(f"Updated positions for {functional_count} functional nodes.")

# 2. Define the 8 Bento Sticky Notes
stickies_data = [
    {
        "name": "Sticky_01_Intake_Idempotency",
        "parameters": {
            "width": 1540,
            "height": 380,
            "color": 6,  # Azul
            "content": "### 📥 01. Ingestão & Criação Idempotente de Sessão\n\n- **Polling & Webhook:** Monitoramento a cada 15s de novos deals na Categoria 160 (Central de TI).\n- **Gate C160:** Filtra apenas chamados válidos da categoria piloto.\n- **Reserva Atômica Postgres:** Impede processamento concorrente do mesmo ticket (`ticket_bot_sessions`)."
        },
        "position": [80, 80]
    },
    {
        "name": "Sticky_02_Inteligencia_Preventiva",
        "parameters": {
            "width": 1540,
            "height": 380,
            "color": 5,  # Roxo
            "content": "### 🚨🛡️ 02. Inteligência Preventiva (P1 & Anti-Duplicados)\n\n- **Detector de Queda Filial (P1 Cluster):** Detecta $\\ge 2$ tickets da mesma loja em 30min e eleva para Incidente Crítico P1 com banner.\n- **Detector de Duplicados:** Identifica tickets com mesmo chassi ou problema nas últimas 24h, unifica comentários e fecha em `C160:LOSE`."
        },
        "position": [1680, 80]
    },
    {
        "name": "Sticky_03_Card_Chat_Purchase",
        "parameters": {
            "width": 1540,
            "height": 320,
            "color": 7,  # Teal
            "content": "### 💬📋 03. Ativação de Chat no Card & Alçada de Compras\n\n- Cria o chat corporativo Bitrix associado diretamente ao card do chamado.\n- Injeta mensagem receptiva de acolhimento e registra sessão ativa.\n- Se categoria for Compra/Alçada: envia botões interativos de aprovação e move para `Aguardando Autorização`."
        },
        "position": [80, 580]
    },
    {
        "name": "Sticky_04_Polling_Takeover",
        "parameters": {
            "width": 1340,
            "height": 320,
            "color": 2,  # Laranja
            "content": "### ⏱️🛑 04. Monitoramento de Chat & Human Takeover\n\n- Realiza polling contínuo de novas mensagens digitadas pelo usuário no chat do card.\n- **Human Takeover:** Se um técnico humano assumir o chat, a IA pausa-se imediatamente para não interferir.\n- **Debounce:** Aguarda 4s de estabilização de mensagens."
        },
        "position": [1680, 580]
    },
    {
        "name": "Sticky_05_Vision_OCR",
        "parameters": {
            "width": 1340,
            "height": 280,
            "color": 3,  # Coral
            "content": "### 👁️🔍 05. Visão Computacional (GPT-4o Vision OCR)\n\n- Intercepta imagens e prints colados no chat do Bitrix (`im.v2.File.download`).\n- Realiza OCR inteligente de telas de erro do ERP MicroWork, portais Honda e Detran/RENAVE.\n- Injeta código de erro, chassi ou NF-e no prompt da IA."
        },
        "position": [80, 1100]
    },
    {
        "name": "Sticky_06_AI_LangChain_Triage",
        "parameters": {
            "width": 1700,
            "height": 560,
            "color": 6,  # Azul escuro
            "content": "### 🧠🤖 06. Núcleo Cognitivo de Triagem TI (LangChain)\n\n- **AI Agent + GPT-4o-mini:** Conduz o diálogo respeitando a Regra de Ouro (não inventar passos).\n- **Tool Diagnóstico TI:** Ferramenta autônoma para testar rede de filial, ERP MicroWork e robôs RPA.\n- **Tool Pense & Redis Memory:** Raciocínio chain-of-thought e histórico contextual.\n- **RAG PGVector:** Consulta a 14 POPs oficiais da TI da Mundial Honda."
        },
        "position": [1500, 1040]
    },
    {
        "name": "Sticky_07_B01_CRM_Timeline",
        "parameters": {
            "width": 2640,
            "height": 400,
            "color": 7,  # Verde
            "content": "### 🏆📋 07. Validador B01, Atualização CRM & Timeline\n\n- Valida prioridade B01 (Urgência x Impacto) e calcula SLA de atendimento.\n- Atualiza campos no Bitrix24 e registra histórico pericial na Linha do Tempo.\n- Se alçada de compra: despacha mensagem direta com botões para o aprovador responsável.\n- Envia confirmação calorosa de conclusão e finaliza sessão no Postgres."
        },
        "position": [80, 1720]
    },
    {
        "name": "Sticky_08_PostRes_CSAT",
        "parameters": {
            "width": 2960,
            "height": 480,
            "color": 5,  # Roxo
            "content": "### 🔄⭐ 08. Roteador Pós-Resolução (PostRes) & CSAT Pulse\n\n- **Reabertura:** Se o usuário relatar que o problema persiste, reabre o ticket e notifica na Timeline.\n- **Anti-Carona:** Se relatar novo problema não relacionado, orienta a abrir novo chamado.\n- **Pesquisa CSAT:** Captura avaliação de 1 a 5 estrelas, registra na tabela `ticket_csat_ratings` e na Timeline do CRM."
        },
        "position": [80, 2280]
    }
]

non_stickies = [n for n in wf['nodes'] if not n['type'].endswith('stickyNote')]
new_stickies = []
for s in stickies_data:
    new_stickies.append({
        "parameters": s["parameters"],
        "id": f"sticky_{s['name']}",
        "name": s["name"],
        "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1,
        "position": s["position"]
    })

wf['nodes'] = non_stickies + new_stickies
print(f"Total nodes: {len(wf['nodes'])} ({functional_count} functional + {len(new_stickies)} stickies)")

# Validation: Check connections
node_names = {n['name'] for n in wf['nodes']}
missing_sources = set()
missing_targets = set()
for src, branches in wf['connections'].items():
    if src not in node_names:
        missing_sources.add(src)
    for branch_name, branch_list in branches.items():
        for target_group in branch_list:
            for target in target_group:
                t_name = target.get('node')
                if t_name not in node_names:
                    missing_targets.add(t_name)

if missing_sources or missing_targets:
    print(f"ERROR: Missing connections: sources={missing_sources}, targets={missing_targets}")
    sys.exit(1)

print("Validation PASSED! All connections strictly valid.")

# Save local files
with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

with open('workflows/canonical/BITRIX_TI_AI_TRIAGE_AGENT.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print("Saved to local workflow files.")

# Deploy to n8n
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}
r = requests.put(N8N_URL, json=payload, headers=headers)

if r.status_code == 200:
    print(f"Successfully deployed to n8n! Workflow ID: c0F2GUMFm2BI94UG | Status: {r.status_code}")
    r_get = requests.get(N8N_URL, headers=headers)
    active = r_get.json().get('active')
    print(f"Workflow active status: {active}")
    if not active:
        r_act = requests.post(f"{N8N_URL}/activate", headers=headers)
        print(f"Activation status: {r_act.status_code}")
else:
    print(f"Deployment FAILED: {r.status_code} - {r.text}")
    sys.exit(1)
