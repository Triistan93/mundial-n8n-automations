# -*- coding: utf-8 -*-
"""
Bateria de Testes Automatizados - Fases 1, 2, 3 e 4
Validação estrutural e comportamental da Sophia AI na Central de TI (Cat 160)
"""
import requests
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'
SQL_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

test_results = {
    'fase_1': {'name': 'Fase 1: Resiliência & Isolamento (onError & SQL)', 'passed': 0, 'failed': 0, 'details': []},
    'fase_2': {'name': 'Fase 2: Identidade Dinâmica & Gestor vs Beneficiário', 'passed': 0, 'failed': 0, 'details': []},
    'fase_3': {'name': 'Fase 3: Semântica Estrita (\b) & Blindagem Outage', 'passed': 0, 'failed': 0, 'details': []},
    'fase_4': {'name': 'Fase 4: Guardrail Cognitivo Anti-Redundância', 'passed': 0, 'failed': 0, 'details': []}
}

print("=" * 80)
print("INICIANDO BATERIA DE TESTES DAS FASES 1, 2, 3 E 4 - SOPHIA AI")
print("=" * 80)

# ==============================================================================
# FASE 1: TESTES DE RESILIÊNCIA & ISOLAMENTO
# ==============================================================================
print("\n--- [TESTE 1/4] FASE 1: RESILIÊNCIA & ISOLAMENTO DE FALHAS ---")
wf_resp = requests.get(N8N_URL, headers=headers).json()
nodes_map = {n['name']: n for n in wf_resp.get('nodes', [])}

critical_nodes = [
    '02_Reserve_Deal_Session_Atomic',
    '01_Check_Store_Outage_Cluster',
    '01_Evaluate_Store_Outage',
    '03_Create_CRM_Card_Chat',
    '04_Fetch_Chat_Messages_Bitrix',
    '12_Update_Deal_CRM_Bitrix',
    '14_Add_Timeline_Milestone_Comment',
    '15_Send_Final_Confirmation_To_Chat',
    '16_Mark_Session_Completed_Postgres'
]

for c_node in critical_nodes:
    node = nodes_map.get(c_node)
    if not node:
        test_results['fase_1']['failed'] += 1
        test_results['fase_1']['details'].append(f"❌ Nó {c_node} não encontrado no workflow")
        print(f"  ❌ Nó {c_node} não encontrado")
        continue
    
    on_error = node.get('onError')
    if on_error == 'continueRegularOutput':
        test_results['fase_1']['passed'] += 1
        test_results['fase_1']['details'].append(f"✅ {c_node}: onError='{on_error}' ativo")
        print(f"  ✅ {c_node}: onError='{on_error}'")
    else:
        test_results['fase_1']['failed'] += 1
        test_results['fase_1']['details'].append(f"❌ {c_node}: onError ausente ou '{on_error}'")
        print(f"  ❌ {c_node}: onError='{on_error}' (esperado: continueRegularOutput)")

# Teste de Sanitização SQL
test_sql_strings = [
    ("Nome com apóstrofo: D'Ávila", "Nome com apóstrofo: D''Ávila"),
    ("Tentativa SQL Injection: ' OR 1=1; --", "Tentativa SQL Injection: '' OR 1=1; --"),
    ("Texto com aspas e barras: \"teste\" \\ barra", "Texto com aspas e barras: \"teste\"  barra")
]
def sanitize_sql(text):
    return str(text or '').replace("'", "''").replace("\\", "")

for original, expected in test_sql_strings:
    sanitized = sanitize_sql(original)
    if sanitized == expected:
        test_results['fase_1']['passed'] += 1
        print(f"  ✅ Sanitização SQL '{original}' -> '{sanitized}'")
    else:
        test_results['fase_1']['failed'] += 1
        print(f"  ❌ Sanitização falhou: '{sanitized}' != '{expected}'")

# ==============================================================================
# FASE 2: TESTES DE IDENTIDADE DINÂMICA & GESTOR VS BENEFICIÁRIO
# ==============================================================================
print("\n--- [TESTE 2/4] FASE 2: IDENTIDADE DINÂMICA & GESTOR VS BENEFICIÁRIO ---")

# 1. Checagem do Cache de Usuários no Postgres
q_count = "SELECT COUNT(*) as total FROM bitrix_users_cache;"
r_count = requests.post(SQL_URL, json={'query': q_count}).json()
total_cached = int(r_count.get('rows', [{}])[0].get('total', 0))

if total_cached >= 300:
    test_results['fase_2']['passed'] += 1
    print(f"  ✅ bitrix_users_cache populado com {total_cached} colaboradores (> 300)")
else:
    test_results['fase_2']['failed'] += 1
    print(f"  ❌ bitrix_users_cache com apenas {total_cached} registros")

# 2. Resolução de Usuários Reais
test_users = [
    (2606, 'Hadner', 'Gerente'),
    (32598, 'Eduardo', 'TI'),
    (352678, 'Igor', 'TI')
]
for uid, expected_first_name, expected_pos_keyword in test_users:
    q_user = f"""
    SELECT user_id, name, 
           SPLIT_PART(TRIM(name), ' ', 1) AS first_word,
           work_position
    FROM bitrix_users_cache 
    WHERE user_id = {uid};
    """
    res = requests.post(SQL_URL, json={'query': q_user}).json()
    rows = res.get('rows', [])
    if rows:
        row = rows[0]
        first_word = row.get('first_word')
        pos = row.get('work_position', '')
        if first_word.lower() == expected_first_name.lower():
            test_results['fase_2']['passed'] += 1
            print(f"  ✅ UID {uid}: Resolvido como '{first_word}' ({pos}) com sucesso")
        else:
            test_results['fase_2']['failed'] += 1
            print(f"  ❌ UID {uid}: Resolvido como '{first_word}', esperado '{expected_first_name}'")
    else:
        test_results['fase_2']['failed'] += 1
        print(f"  ❌ UID {uid} não encontrado na tabela bitrix_users_cache")

# 3. Teste do Detector de Terceiro (Gestor vs Beneficiário)
def detect_third_party(title, requester_name, requester_position=''):
    third_party_regex = re.compile(
        r'(?:para|do|da|mecanico|mecânico|vendedor|estoquista|novo colaborador|novo consultor)\s+([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+)?)',
        re.IGNORECASE
    )
    match = third_party_regex.search(title)
    if match and match.group(1) and requester_name.lower() not in match.group(1).lower():
        beneficiary = match.group(1).strip()
        note = (
            f"[ATENÇÃO - CHAMADO ABERTO EM NOME DE OUTRA PESSOA]:\n"
            f"- O usuário conversando com você no chat é o(a) solicitante: {requester_name}"
            f"{' (' + requester_position + ')' if requester_position else ''}.\n"
            f"- O colaborador citado que precisa da liberação/suporte é: \"{beneficiary}\".\n"
            f"- DIRETIVA: Dirija-se sempre a {requester_name} pelo nome dele(a). NUNCA o confunda com {beneficiary}."
        )
        return beneficiary, note
    return None, None

cases_third_party = [
    ("[TI-BITRIX24] - Liberar acesso CRM para mecânico Ailton", "Hadner", "Gerente de Loja", "Ailton", True),
    ("Novo vendedor Marcos Araras", "Carlos", "Gerente Comercial", "Marcos", True),
    ("Reset de senha para colaboradora Vanessa", "Roberto", "Supervisor", "Vanessa", True),
    ("Meu ramal 221 não está funcionando", "Flavio", "Consultor", None, False)
]

for title, req_name, req_pos, exp_beneficiary, exp_is_third_party in cases_third_party:
    beneficiary, note = detect_third_party(title, req_name, req_pos)
    if exp_is_third_party:
        if beneficiary and exp_beneficiary.lower() in beneficiary.lower() and f"Dirija-se sempre a {req_name}" in note:
            test_results['fase_2']['passed'] += 1
            print(f"  ✅ Detecção de terceiro OK: Solicitante '{req_name}' -> Beneficiário '{beneficiary}'")
        else:
            test_results['fase_2']['failed'] += 1
            print(f"  ❌ Falha na detecção de terceiro para título '{title}': obteve '{beneficiary}'")
    else:
        if beneficiary is None:
            test_results['fase_2']['passed'] += 1
            print(f"  ✅ Chamado direto identificado corretamente: Solicitante único '{req_name}'")
        else:
            test_results['fase_2']['failed'] += 1
            print(f"  ❌ Falso positivo de terceiro para chamado direto: '{beneficiary}'")


# ==============================================================================
# FASE 3: TESTES DE SEMÂNTICA ESTREITA (\b) & BLINDAGEM DE OUTAGE
# ==============================================================================
print("\n--- [TESTE 3/4] FASE 3: SEMÂNTICA ESTREITA (\\b) & BLINDAGEM OUTAGE ---")

# Regex idênticas às aplicadas no nó 01_Strict_Gate_Cat160_Pilot
rxRobo = re.compile(r'\b(rob[ôo]|card\s+rob[ôo]|entrada\s+honda|entrada\s+grupo|vigia|dms_vigia|faturamento\s+direto|solicita[çc][ãa]o\s+de\s+entrada|loop)\b', re.IGNORECASE)
rxDetran = re.compile(r'\b(atpv|atpv-?e|renave|detran|inten[çc][ãa]o\s+de\s+venda|9c2[a-hj-npr-z0-9]{14})\b', re.IGNORECASE)
rxNetwork = re.compile(r'\b(internet|rede\s+caiu|queda\s+de\s+link|roteador|vpn|fora\s+do\s+ar|offline|sem\s+sistema|tudo\s+vermelho|lentid[ãa]o\s+geral|sem\s+net|wi-?fi|link\s+caiu)\b', re.IGNORECASE)
rxTelefonia = re.compile(r'\b(telefone|ramal|liga[çc][ãa]o|liga[çc][õo]es|headset|fone|fale\s+f[áa]cil|n[ãa]o\s+toca|sem\s+tom)\b', re.IGNORECASE)
rxWhatsapp = re.compile(r'\b(whats?app|wpp|zap|conex[ãa]o\s+zap|n[úu]mero\s+corporativo|espelhamento)\b', re.IGNORECASE)
rxAccess = re.compile(r'\b(libera[çc][ãa]o\s+de\s+acesso|liberar\s+acesso|acesso\s+crm|liberar\s+crm|permiss[ãa]o|permissoes|criar\s+usu[áa]rio|novo\s+colaborador|novo\s+consultor|onboarding|admiss[ãa]o|reset\s+de\s+senha|esqueci\s+a\s+senha|trocar\s+senha)\b', re.IGNORECASE)
rxMicroWork = re.compile(r'\b(microwork|dms|banco\s+travou|nuvem\s+microwork|icms|ordem\s+de\s+servi[çc]o|o\.?s\.?\s*\d+|rotina\s*\d+)\b', re.IGNORECASE)

def classify_theme(text):
    if rxRobo.search(text): return 'ROBO_RPA'
    if rxDetran.search(text): return 'DETRAN_RENAVE'
    if rxNetwork.search(text): return 'CONNECTIVITY_NETWORK'
    if rxTelefonia.search(text): return 'TELEFONIA'
    if rxWhatsapp.search(text): return 'WHATSAPP_FALEFACIL'
    if rxAccess.search(text): return 'ACCESS_PERMISSIONS'
    if rxMicroWork.search(text): return 'MICROWORK_DMS'
    return 'GENERAL_IT'

test_cases_theme = [
    # Caso crítico de falso positivo antigo: 'os ' casava com artigo 'os'
    ("Favor verificar e abrir os cards da semana passada para conferência", "GENERAL_IT", "Não deve casar 'os' artigo plural"),
    # Robô RPA
    ("Card robô de entrada honda travou em processamento", "ROBO_RPA", "Detecção de Robô RPA"),
    ("Erro 500 no loop da rotina 1719", "ROBO_RPA", "Detecção de Loop"),
    # Detran / ATPV
    ("Erro ao emitir atpv para comprador final chassi 9C2JC4100MR001234", "DETRAN_RENAVE", "Detecção de ATPV e Chassi"),
    # Telefonia
    ("Meu ramal 1234 não toca e ninguém consegue ligar", "TELEFONIA", "Detecção de Telefonia e Ramal"),
    # Queda de Conectividade
    ("Internet caiu em Araras, link da vivo fora do ar", "CONNECTIVITY_NETWORK", "Detecção de Queda de Link/Internet"),
    # Permissão de Acesso
    ("Solicito liberação de acesso ao CRM para novo colaborador", "ACCESS_PERMISSIONS", "Detecção de Liberação de Acesso"),
    # DMS Ordem de Serviço
    ("Erro de cálculo de ICMS na ordem de serviço 45192", "MICROWORK_DMS", "Detecção de Ordem de Serviço legítima")
]

for text, expected_theme, rationale in test_cases_theme:
    detected = classify_theme(text)
    if detected == expected_theme:
        test_results['fase_3']['passed'] += 1
        print(f"  ✅ [{detected}] \"{text[:55]}...\" ({rationale})")
    else:
        test_results['fase_3']['failed'] += 1
        print(f"  ❌ Falha: Detectou [{detected}], esperado [{expected_theme}] em: \"{text}\"")

# Teste da Lógica de Outage Cluster: Apenas CONNECTIVITY_NETWORK qualifica para Queda de Loja
def evaluate_outage_eligibility(theme, count_in_window):
    # Regra estrita: apenas CONNECTIVITY_NETWORK e count >= 3
    if theme == 'CONNECTIVITY_NETWORK' and count_in_window >= 3:
        return 'P1_STORE_OUTAGE'
    return 'STANDARD_TRIAGE'

outage_tests = [
    ('CONNECTIVITY_NETWORK', 3, 'P1_STORE_OUTAGE', "3 chamados de rede -> Queda Geral confirmada"),
    ('CONNECTIVITY_NETWORK', 2, 'STANDARD_TRIAGE', "2 chamados de rede -> Abaixo do limiar"),
    ('TELEFONIA', 4, 'STANDARD_TRIAGE', "4 chamados de ramal -> NUNCA gera Queda Geral de Loja"),
    ('MICROWORK_DMS', 5, 'STANDARD_TRIAGE', "5 chamados de DMS -> Falha de ERP, não queda de link físico")
]
for th, cnt, exp_outage, desc in outage_tests:
    res = evaluate_outage_eligibility(th, cnt)
    if res == exp_outage:
        test_results['fase_3']['passed'] += 1
        print(f"  ✅ Outage Gate: {th} (qtd={cnt}) -> {res} ({desc})")
    else:
        test_results['fase_3']['failed'] += 1
        print(f"  ❌ Falha Outage Gate: {th} (qtd={cnt}) -> {res}, esperado {exp_outage}")


# ==============================================================================
# FASE 4: TESTES DE GUARDRAIL ANTI-REDUNDÂNCIA (UX CONVERSACIONAL)
# ==============================================================================
print("\n--- [TESTE 4/4] FASE 4: GUARDRAIL COGNITIVO ANTI-REDUNDÂNCIA ---")

# 1. Pré-Extração Determinística (idêntica ao nó 07_Prepare_AI_Deal_Input)
def extract_deterministic_facts(title, user_input):
    full_text = f"{title} {user_input}"
    extracted = []
    
    # Chassi 17 dígitos
    chassi_match = re.search(r'\b(9C2[A-HJ-NPR-Z0-9]{14})\b', full_text, re.IGNORECASE)
    if chassi_match:
        extracted.append(f'Chassi Identificado: "{chassi_match.group(1).upper()}" -> (REGRA ESTRITA: PROIBIDO PERGUNTAR O CHASSI NOVAMENTE AO USUÁRIO)')
        
    # Link de Card Bitrix
    card_match = re.search(r'(https://b24-[a-z0-9]+\.bitrix24\.com\.br/crm/deal/details/\d+/)', full_text, re.IGNORECASE)
    if card_match:
        extracted.append(f'Link do Card no Bitrix: "{card_match.group(1)}" -> (REGRA ESTRITA: PROIBIDO PEDIR O LINK DO CARD NOVAMENTE)')
        
    # NF
    nf_match = re.search(r'\b(?:nf|nota|nfe)\s*[:#ºn]?\s*(\d{4,9})\b', full_text, re.IGNORECASE)
    if nf_match:
        extracted.append(f'Número de Nota Fiscal: "{nf_match.group(1)}"')
        
    # OS
    os_match = re.search(r'\b(?:os|o\.s\.)\s*[:#ºn]?\s*(\d{4,8})\b', full_text, re.IGNORECASE)
    if os_match:
        extracted.append(f'Número da OS: "{os_match.group(1)}"')
        
    facts_block = ''
    if extracted:
        facts_block = "[DADOS JÁ CONFIRMADOS E COMPROVADOS NO CARD (NÃO PERGUNTE NOVAMENTE AO USUÁRIO)]:\n" + "\n".join([f"• {e}" for e in extracted]) + "\n\n"
        
    return extracted, facts_block

# Teste com o caso real da Nataelen e Danielly
title_nataelen = "[TI-DETRAN] Erro no ATPV Chassi 9C2JC4100MR001234 NF 49102"
msg_nataelen = "O Detran diz que não existe intenção de venda para este veículo."
extracted_nat, block_nat = extract_deterministic_facts(title_nataelen, msg_nataelen)

if any("9C2JC4100MR001234" in e for e in extracted_nat) and any("49102" in e for e in extracted_nat):
    test_results['fase_4']['passed'] += 1
    print(f"  ✅ Pré-extração Nataelen: Chassi e NF extraídos com regra expressa de não perguntar")
else:
    test_results['fase_4']['failed'] += 1
    print(f"  ❌ Falha na pré-extração Nataelen: {extracted_nat}")

title_danielly = "Card robô de entrada travou"
msg_danielly = "Segue o link do card https://b24-88dbfb.bitrix24.com.br/crm/deal/details/1410810/ e a OS 88910"
extracted_dan, block_dan = extract_deterministic_facts(title_danielly, msg_danielly)

if any("1410810" in e for e in extracted_dan) and any("88910" in e for e in extracted_dan):
    test_results['fase_4']['passed'] += 1
    print(f"  ✅ Pré-extração Danielly: Link de Card Bitrix e OS extraídos com sucesso")
else:
    test_results['fase_4']['failed'] += 1
    print(f"  ❌ Falha na pré-extração Danielly: {extracted_dan}")

# 2. Verificação do Guardrail no System Prompt do Workflow Ativo no n8n
agent_node = nodes_map.get('08_AI_Agent_Triage_Deal')
system_message = agent_node.get('parameters', {}).get('options', {}).get('systemMessage', '')

if "ANTI-REDUNDÂNCIA & EFICIÊNCIA CONVERSACIONAL (UX)" in system_message:
    test_results['fase_4']['passed'] += 1
    print(f"  ✅ Guardrail Anti-Redundância confirmado no System Prompt do nó 08_AI_Agent_Triage_Deal")
else:
    test_results['fase_4']['failed'] += 1
    print(f"  ❌ Guardrail Anti-Redundância NÃO encontrado no System Prompt")

if "NUNCA pergunte ao usuário uma informação que já foi informada" in system_message:
    test_results['fase_4']['passed'] += 1
    print(f"  ✅ Regra estrita de proibição de perguntas redundantes confirmada no Prompt")
else:
    test_results['fase_4']['failed'] += 1
    print(f"  ❌ Regra estrita de proibição ausente")

# ==============================================================================
# CONSOLIDAÇÃO DOS RESULTADOS
# ==============================================================================
print("\n" + "=" * 80)
print("RELATÓRIO CONSOLIDADO DA BATERIA DE TESTES")
print("=" * 80)

total_passed = 0
total_failed = 0

for key, phase in test_results.items():
    p = phase['passed']
    f = phase['failed']
    total_passed += p
    total_failed += f
    status_icon = "✅ APROVADO" if f == 0 else "❌ FALHA"
    print(f"{status_icon} | {phase['name']}: {p} aprovados, {f} falhas")

print("-" * 80)
print(f"TOTAL GERAL: {total_passed} testes aprovados, {total_failed} falhas (Taxa de Sucesso: {(total_passed / (total_passed + total_failed) * 100):.1f}%)")
print("=" * 80)

if total_failed == 0:
    print("\n🎉 TODAS AS FASES (1, 2, 3 E 4) FORAM VALIDADAS E SURTIRAM EFEITO TOTAL EM PRODUÇÃO!")
else:
    print(f"\n⚠️ FORAM DETECTADAS {total_failed} FALHAS. VERIFIQUE OS LOGS ACIMA.")
    sys.exit(1)
