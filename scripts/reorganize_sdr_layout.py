# -*- coding: utf-8 -*-
import json
import sys
import shutil
import requests

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/HTbHT6SLugyAn3NO'

live_file = 'c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado_HTbHT6SLugyAn3NO.json'
backup_file = 'c:/mundial-n8n-automations/workflows/backup_before_sdr_layout_reorganize.json'

shutil.copyfile(live_file, backup_file)
print(f"Backup seguro criado em: {backup_file}")

with open(live_file, 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Import position mapping
sys.path.append('c:/mundial-n8n-automations/scripts')
import test_sdr_layout_mapping
pos_dict = test_sdr_layout_mapping.get_sdr_node_positions()

# 1. Update functional node positions
functional_count = 0
for node in wf['nodes']:
    if not node['type'].endswith('stickyNote'):
        name = node['name']
        if name in pos_dict:
            node['position'] = pos_dict[name]
            functional_count += 1
        else:
            print(f"ERRO: Posição ausente para nó '{name}'!")
            sys.exit(1)

print(f"Posições atualizadas para {functional_count} nós funcionais.")

# 2. Define the 8 Bento Grid Sticky Notes
stickies_data = [
    {
        "name": "Sticky_01_Ingestao_Saneamento",
        "parameters": {
            "width": 1220,
            "height": 420,
            "color": 6,  # Azul
            "content": "### 📥 01. Ingestão & Saneamento WhatsApp\n\n- **Webhook Evolution API:** Recebimento do webhook de eventos (`testesdr`).\n- **Normalização JID:** Trata identificadores de remetente e destinatário.\n- **Triagem Anti-Spam:** Filtra mensagens de status/broadcast e grupos (`@g.us`).\n- **Roteamento de Tipo:** Separa fluxos de texto vs áudio."
        },
        "position": [80, 80]
    },
    {
        "name": "Sticky_02_Transcricao_Audio",
        "parameters": {
            "width": 1160,
            "height": 420,
            "color": 7,  # Teal
            "content": "### 🎙️ 02. Transcrição de Áudio (Groq Whisper)\n\n- **Baixa Mídia:** Obtém o áudio em base64 da Evolution API (`Get Base 64`).\n- **Conversão Binária:** Prepara arquivo para envio assíncrono.\n- **Groq Whisper:** Transcrição de voz ultrarrápida com alta precisão em PT-BR.\n- **Convergência:** Unifica áudios transcritos e mensagens de texto puro."
        },
        "position": [1360, 80]
    },
    {
        "name": "Sticky_03_Buffer_Debounce",
        "parameters": {
            "width": 1160,
            "height": 420,
            "color": 1,  # Amarelo
            "content": "### ⏱️ 03. Fila de Buffer & Debounce (15 Segundos)\n\n- **Agrupamento Redis:** Enfileira mensagens consecutivas enviadas pelo lead.\n- **Janela de Silêncio (15s):** Aguarda o cliente terminar de formular o pensamento.\n- **Anti-Duplicação:** Apenas a última execução assume o lote consolidado.\n- **Economia de Tokens:** Reduz em até 70% o consumo da LLM."
        },
        "position": [2580, 80]
    },
    {
        "name": "Sticky_04_Concorrencia_Lock",
        "parameters": {
            "width": 1840,
            "height": 640,
            "color": 5,  # Roxo
            "content": "### 🔒🛑 04. Concorrência, Lock Atômico & Human Takeover\n\n- **Detecção fromMe:** Se o vendedor humano falar no WhatsApp, o bot silencia imediatamente.\n- **Lock Atômico Redis:** `INCR` + `EXPIRE` com TTL controlado para evitar race conditions.\n- **Expurgo de Chaves Legadas:** Limpeza atômica de chaves obsoletas.\n- **Memória do Atendente:** Registra falas do vendedor no histórico da IA (`memoryManager`)."
        },
        "position": [80, 560]
    },
    {
        "name": "Sticky_05_Nucleo_Cognitivo_IA",
        "parameters": {
            "width": 1760,
            "height": 640,
            "color": 6,  # Azul Escuro
            "content": "### 🧠🤖 05. Núcleo Cognitivo de IA (LangChain ReAct)\n\n- **AI Agent + OpenAI:** Agente comercial com persona humana e empática da Mundial Motos.\n- **Tool Think:** Motor de raciocínio chain-of-thought para qualificação de leads.\n- **Redis Chat Memory:** Histórico contextual contínuo por conversa (`remoteJid`).\n- **Formatar Output:** Extrai JSON de qualificação e despacha texto limpo ao WhatsApp.\n- **Roteador de Saída:** Desvia para Vendas, Pós-Vendas, ADM, Outros ou Continuação do Papo."
        },
        "position": [1980, 560]
    },
    {
        "name": "Sticky_06_Resolucao_Contatos",
        "parameters": {
            "width": 3660,
            "height": 500,
            "color": 4,  # Azul Claro
            "content": "### 📇🔎 06. Resolução, Saneamento & Deduplicação de Contatos Bitrix24\n\n- **Normalização com 9º Dígito:** Trata variações de telefone (com/sem DDI 55, com/sem 9º dígito).\n- **Busca Dupla em Cascata:** Procura primeiro por duplicados (`findbycomm`) e depois por lista (`contact.list`).\n- **Criação de Contato:** Cadastra novo contato caso o cliente seja novo na base.\n- **Consulta Open Lines:** Identifica se já existe sessão de chat aberta no CRM.\n- **Deduplicação Nativa:** Executa `crm.entity.mergeBatch` para unificar cadastros duplicados do mesmo cliente."
        },
        "position": [80, 1260]
    },
    {
        "name": "Sticky_07_Gestao_Cards_Funil",
        "parameters": {
            "width": 1840,
            "height": 680,
            "color": 7,  # Verde
            "content": "### 🏢📋 07. Gestão de Cards no Funil (Categoria 18) & Linha do Tempo\n\n- **Busca Global de Deals Abertos:** Localiza se o cliente possui card ativo (`STAGE_SEMANTIC_ID='P'`).\n- **Ramo Atualização:** Atualiza o card existente mantendo o histórico de negociação.\n- **Ramo Criação (Fallback):** Cria novo card na Categoria 18 (*Vendas Outras mídias*) vinculando o contato.\n- **Campos Personalizados (UF_CRM):** Preenche Cidade, Modelo, Entrada, Parcela Ideal e Resumo Estruturado.\n- **Auditoria na Linha do Tempo:** Registra comentário detalhado em HTML na Timeline do Bitrix24."
        },
        "position": [80, 1820]
    },
    {
        "name": "Sticky_08_Transicao_Handover",
        "parameters": {
            "width": 1760,
            "height": 680,
            "color": 3,  # Coral / Laranja
            "content": "### 🚀 08. Transição de Etapa, Handover OpenLines & Despedida WhatsApp\n\n- **Normalizador de Etapa:** Mapeia `status_triagem` para a etapa de destino na Categoria 18:\n  * Vendas/Humana ➔ `C18:UC_CGWMZF` (*ATENDIMENTO VENDEDOR*)\n  * Pós-Vendas ➔ `C18:UC_G95T35` (*Pós Vendas*)\n  * Administrativo ➔ `C18:UC_FKQTE0` (*Seguro/Documento*)\n- **Mover Card de Etapa:** Atualiza o `STAGE_ID` do Deal no CRM.\n- **Transferência OpenLines:** Transfere o chat para a fila/operador humano (`5316`).\n- **Trava de Silêncio 24h:** Bloqueia o bot no Redis para não interferir na conversa do vendedor.\n- **Despedida WhatsApp:** Envia mensagem cordial de encerramento da triagem para o cliente."
        },
        "position": [1980, 1820]
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
print(f"Total de nós no fluxo: {len(wf['nodes'])} ({functional_count} funcionais + {len(new_stickies)} stickies)")

# 3. Connection integrity check
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
    print(f"ERRO: Conexões corrompidas! sources={missing_sources}, targets={missing_targets}")
    sys.exit(1)

print("Validação APROVADA: 100% das conexões lógicas estão perfeitamente intactas.")

# 4. Save local files
out_file = 'c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado.json'
canonical_file = 'c:/mundial-n8n-automations/workflows/canonical/SDR_Mundial_Motos_Unificado.json'

with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

with open(canonical_file, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print(f"Workflow salvo localmente em:\n  - {out_file}\n  - {canonical_file}")

# 5. Deploy to n8n API
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}

headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}
r = requests.put(N8N_URL, json=payload, headers=headers)

if r.status_code == 200:
    print(f"\nDEPLOY COM SUCESSO NO N8N! Workflow ID: HTbHT6SLugyAn3NO | Status HTTP: {r.status_code}")
    r_get = requests.get(N8N_URL, headers=headers)
    active = r_get.json().get('active')
    print(f"Status Ativo do Workflow: {active}")
    if not active:
        r_act = requests.post(f"{N8N_URL}/activate", headers=headers)
        print(f"Reativação executada: {r_act.status_code}")
else:
    print(f"\nFALHA NO DEPLOY: {r.status_code} - {r.text}")
    sys.exit(1)
