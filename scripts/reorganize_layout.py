import json
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load canonical workflow
canonical_path = 'workflows/canonical/AGENTE_RH_COM_CORRECOES.json'
backup_path = 'workflows/backup_before_layout_reorganize.json'

shutil.copyfile(canonical_path, backup_path)
print(f"Backup created at: {backup_path}")

with open(canonical_path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

# 2. Get positions
import test_layout_mapping
pos_dict = test_layout_mapping.get_node_positions()

# 3. Update positions of functional nodes
functional_count = 0
for node in wf['nodes']:
    if not node['type'].endswith('stickyNote'):
        name = node['name']
        if name in pos_dict:
            node['position'] = pos_dict[name]
            functional_count += 1
        else:
            print(f"ERROR: Node {name} not in pos_dict!")
            sys.exit(1)

print(f"Updated positions for {functional_count} functional nodes.")

# 4. Define 11 modern, elegant Bento Sticky Notes
# We map them cleanly:
sticky_notes_data = [
    {
        "name": "Sticky Note",
        "parameters": {
            "width": 1120,
            "height": 260,
            "color": 6,  # Azul
            "content": "### 📥 1. Ingestão & Saneamento WhatsApp\n\n- **Webhook Evolution API:** Recebimento de eventos e mensagens em tempo real.\n- **Normalização JID:** Trata identificadores de usuários e números.\n- **Triagem Anti-Spam:** Filtra mensagens de status/broadcast e grupos (`@g.us`)."
        },
        "position": [80, 100]
    },
    {
        "name": "Sticky Note1",
        "parameters": {
            "width": 1140,
            "height": 170,
            "color": 7,  # Teal
            "content": "### 🎙️ 2A. Transcrição de Áudio (Whisper)\n- Converte mensagens de voz da Evolution API em binário.\n- Executa transcrição assíncrona para texto via OpenAI Whisper."
        },
        "position": [1540, 200]
    },
    {
        "name": "Sticky Note2",
        "parameters": {
            "width": 1360,
            "height": 170,
            "color": 3,  # Coral / Laranja
            "content": "### 📄 2B. Processamento de Currículo & Google Drive\n- Converte PDF em binário e faz upload seguro na pasta corporativa do Drive.\n- Gera link público de visualização e injeta a URL no contexto do agente."
        },
        "position": [1540, 390]
    },
    {
        "name": "Sticky Note3",
        "parameters": {
            "width": 1980,
            "height": 520,
            "color": 5,  # Roxo
            "content": "### 🔒 3. Concorrência & Lock Atômico Redis\n\n- **Detecção fromMe:** Se o atendente humano enviou mensagem, silencia o bot imediatamente.\n- **Lock Atômico:** Impede race conditions e mensagens concorrentes fragmentadas.\n- **TTL Inteligente:** Garante persistência e liberação controlada."
        },
        "position": [80, 720]
    },
    {
        "name": "Sticky Note6",
        "parameters": {
            "width": 1820,
            "height": 520,
            "color": 2,  # Laranja
            "content": "### 🏢🛑 4. Detecção de Estágio CRM & Silêncio Humano (30d)\n\n- **Verificação Prévia:** Localiza contatos e deals abertos na Categoria 198.\n- **Blindagem de Gestão Humana:** Se o card estiver em etapas de gestão humana (`ASSUNTOS RH`, `Entrevista`, `Contratado`, etc.), o bot se cala por 30 dias no Redis e registra evento na Linha do Tempo."
        },
        "position": [2080, 600]
    },
    {
        "name": "Sticky Note7",
        "parameters": {
            "width": 1760,
            "height": 420,
            "color": 1,  # Amarelo
            "content": "### ⏱️ 5. Fila de Buffer & Debounce (30 Segundos)\n\n- Agrupa mensagens picadas do candidato no WhatsApp.\n- Aguarda 30 segundos de inatividade para consolidar tudo em um único lote.\n- Economiza 75% dos tokens e elimina respostas fragmentadas em duplicidade."
        },
        "position": [80, 1360]
    },
    {
        "name": "Sticky Note4",
        "parameters": {
            "width": 460,
            "height": 420,
            "color": 6,  # Azul escuro
            "content": "### 🧠🤖 6. Núcleo Cognitivo de IA\n\n- **OpenAI gpt-4.1-mini:** Diálogo e triagem com Regra Inviolável de Nome.\n- **Tool Pense:** Raciocínio chain-of-thought interno.\n- **Redis Chat Memory:** Histórico contextual.\n- **Pós-Atendimento:** Acolhe retornos sem duplicar cartões."
        },
        "position": [1900, 1360]
    },
    {
        "name": "Sticky Note5",
        "parameters": {
            "width": 460,
            "height": 420,
            "color": 7,  # Teal
            "content": "### 🔀 7. Formatação & Roteamento\n\n- Extrai JSON estruturado do modelo.\n- Direciona para as saídas:\n  - `0`: Chat Contínuo\n  - `1`: Bitrix C198 (Conclusão)\n  - `2`: Handover RH (Nina)"
        },
        "position": [2380, 1360]
    },
    {
        "name": "Sticky Note - Trilha 1",
        "parameters": {
            "width": 420,
            "height": 260,
            "color": 1,  # Amarelo
            "content": "### 💬 Trilha 1: Diálogo WhatsApp\n- Disparo de mensagem conversacional direta de volta para a Evolution API."
        },
        "position": [160, 1960]
    },
    {
        "name": "Sticky Note - Trilha 2",
        "parameters": {
            "width": 2720,
            "height": 440,
            "color": 7,  # Verde
            "content": "### 🏆 Trilha 2: Conclusão de Candidatura & Sincronização Bitrix24 (C198)\n\n- Mapeia 25 cargos oficiais no campo `UF_CRM_1775845859336`.\n- Atualiza ou cria deal no funil de Recrutamento com Nome Real e link do Drive.\n- Registra histórico pericial na Linha do Tempo e envia mensagem final no WhatsApp."
        },
        "position": [700, 1920]
    },
    {
        "name": "Sticky Note - Handover RH",
        "parameters": {
            "width": 1820,
            "height": 240,
            "color": 4,  # Magenta / Coral
            "content": "### 🚨 Trilha 3: Handover Inteligente para o RH (Alerta Nina Biermann - ID 4278)\n\n- Desvia Trilhas 2 (Saúde/ASO), 3 (DP/Colaborador) e 4 (B2B/Parcerias comerciais).\n- Cria Deal na etapa ASSUNTOS RH (`C198:UC_0YLZXN`) e anota histórico na Timeline.\n- Dispara notificação instantânea com link direto no chat privado da Nina Biermann (`4278`).\n- Bloqueia o bot por 30 dias para garantir o atendimento humano sem interferências."
        },
        "position": [700, 2480]
    }
]

# Remove old sticky notes from wf['nodes']
non_sticky_nodes = [n for n in wf['nodes'] if not n['type'].endswith('stickyNote')]

# Create new sticky note objects
new_sticky_nodes = []
for s in sticky_notes_data:
    new_sticky_nodes.append({
        "parameters": s["parameters"],
        "id": f"sticky_{s['name'].replace(' ', '_').replace(':', '')}",
        "name": s["name"],
        "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1,
        "position": s["position"]
    })

wf['nodes'] = non_sticky_nodes + new_sticky_nodes
print(f"Total nodes in updated workflow: {len(wf['nodes'])} (86 functional + {len(new_sticky_nodes)} stickies)")

# Save updated canonical file
with open(canonical_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

# Sync with instance backup file
shutil.copyfile(canonical_path, 'workflows/AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json')
print("Successfully saved and synced canonical workflow with new layout!")
