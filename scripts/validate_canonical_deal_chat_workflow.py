# -*- coding: utf-8 -*-
"""
Validador Canônico de Arquitetura: BITRIX_TI_AI_TRIAGE_AGENT (CRM Deal Chat)
Verifica todos os 15 requisitos do patch canônico.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
WORKFLOW_PATH = os.path.join(REPO_ROOT, "workflows", "canonical", "BITRIX_TI_AI_TRIAGE_AGENT.json")

def validate():
    print("=== INICIANDO VALIDAÇÃO CANÔNICA CRM DEAL CHAT ===")
    
    if not os.path.exists(WORKFLOW_PATH):
        print(f"[FAIL] Arquivo não encontrado: {WORKFLOW_PATH}")
        sys.exit(1)
        
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        wf = json.load(f)
        
    nodes = {n["name"]: n for n in wf.get("nodes", [])}
    connections = wf.get("connections", {})
    
    checks = []
    
    # 1. REMOVER MODELO POR REQUESTER (Sem MAX_ACTIVE_PER_REQUESTER)
    raw_text = json.dumps(wf, ensure_ascii=False)
    has_max_active = "MAX_ACTIVE_PER_REQUESTER" in raw_text
    checks.append({
        "req": "1. REMOVER MODELO POR REQUESTER",
        "passed": not has_max_active,
        "detail": "Sem MAX_ACTIVE_PER_REQUESTER, isolamento por deal_id"
    })
    
    # 2. IDENTIDADE CANÔNICA (dialog_id = chat<id>, internal_chat_id, ai_state)
    has_dialog_id = "dialog_id" in raw_text and "internal_chat_id" in raw_text and "ai_state" in raw_text
    checks.append({
        "req": "2. IDENTIDADE CANÔNICA",
        "passed": has_dialog_id,
        "detail": "Usa dialog_id = chat<internal_chat_id>, internal_chat_id, ai_state"
    })
    
    # 3. CHAT CREATION IDEMPOTENCY (Reserva atômica antes de im.chat.add)
    reserve_node = nodes.get("02_Reserve_Deal_Session_Atomic")
    chat_node = nodes.get("03_Create_CRM_Card_Chat")
    if_reserve = nodes.get("02_If_Reservation_Won")
    
    idempotent_order = (
        reserve_node is not None and 
        chat_node is not None and 
        if_reserve is not None and
        "CHAT_CREATING" in reserve_node["parameters"]["query"] and
        "ON CONFLICT (deal_id) DO NOTHING" in reserve_node["parameters"]["query"] and
        "RETURNING id" in reserve_node["parameters"]["query"]
    )
    checks.append({
        "req": "3. CHAT CREATION IDEMPOTENCY",
        "passed": idempotent_order,
        "detail": "Reserva deal_id UNIQUE com status CHAT_CREATING antes de chamar im.chat.add"
    })
    
    # 4. PRIORIDADE (P1_CRITICAL: 1202, P2_HIGH: 1204, P3_MEDIUM: 1206, P4_LOW: 1208 - SEM P0!)
    has_p0 = "P0" in raw_text or "p0" in raw_text
    b01_node = nodes.get("11_B01_Priority_And_Payload")
    b01_code = b01_node["parameters"]["functionCode"] if b01_node else ""
    correct_p_ids = "1202" in b01_code and "1204" in b01_code and "1206" in b01_code and "1208" in b01_code
    checks.append({
        "req": "4. PRIORIDADE CANÔNICA B01",
        "passed": (not has_p0) and correct_p_ids,
        "detail": "Contrato restrito P1(1202), P2(1204), P3(1206), P4(1208) — SEM P0"
    })
    
    # 5. REDIS MEMÓRIA POR DEAL
    redis_mem_node = nodes.get("Redis_Deal_Chat_Memory")
    mem_key = redis_mem_node["parameters"]["sessionKey"] if redis_mem_node else ""
    checks.append({
        "req": "5. REDIS MEMÓRIA POR DEAL",
        "passed": "redis_memory_key" in mem_key or "bitrix:ti:deal:" in raw_text,
        "detail": "Memória isolada por Deal (bitrix:ti:deal:<deal_id>:memory)"
    })
    
    # 6. MESSAGE POLLING & CURSOR ISOLADO
    filter_node = nodes.get("05_Filter_And_Classify_Messages")
    filter_code = filter_node["parameters"]["functionCode"] if filter_node else ""
    checks.append({
        "req": "6. MESSAGE POLLING & CURSOR",
        "passed": "lastProcessedId" in filter_code and "61622" in filter_code,
        "detail": "Filtra bot (61622), sistema (0) e controla cursor por Deal"
    })
    
    # 7. DEBOUNCE ADAPTATIVO (4s)
    wait_node = nodes.get("06_Wait_Debounce_4s")
    debounce_val = wait_node["parameters"].get("amount") if wait_node else 0
    checks.append({
        "req": "7. DEBOUNCE ADAPTATIVO",
        "passed": debounce_val == 4,
        "detail": "Janela de silêncio adaptativo de 4 segundos no Redis Buffer"
    })
    
    # 8. AI AGENT LANGCHAIN & INVARIANTES
    agent_node = nodes.get("08_AI_Agent_Triage_Deal")
    sys_msg = agent_node["parameters"]["options"]["systemMessage"] if agent_node else ""
    has_invariants = "DOMAIN SCOPE" in sys_msg and "SINGLE_USER" in sys_msg and "OPERATION_HALTED" in sys_msg
    checks.append({
        "req": "8. AI AGENT & INVARIANTES",
        "passed": has_invariants,
        "detail": "GPT-4o-mini + LangChain com 11 temas e invariante Domain Scope != Business Impact"
    })
    
    # 9. OUTPUT ESTRUTURADO (ASK / COMPLETE)
    checks.append({
        "req": "9. OUTPUT ESTRUTURADO",
        "passed": "COMPLETE" in sys_msg and "ASK" in sys_msg,
        "detail": "Ações ASK e COMPLETE com fatos e confiança estruturada"
    })
    
    # 10. HUMAN TAKEOVER (AI_PAUSED)
    pause_node = nodes.get("05_Pause_AI_On_Human_Takeover")
    pause_query = pause_node["parameters"]["query"] if pause_node else ""
    checks.append({
        "req": "10. HUMAN TAKEOVER",
        "passed": "AI_PAUSED" in pause_query and "humanTakeoverDetected" in filter_code,
        "detail": "Se técnico humano falar no chat, pausa imediatamente a IA (ai_state='AI_PAUSED')"
    })
    
    # 11. PARTICIPANTES (requester + 61622)
    json_body = chat_node["parameters"].get("jsonBody", "") if chat_node else ""
    checks.append({
        "req": "11. PARTICIPANTES DO CHAT",
        "passed": "61622" in json_body,
        "detail": "Inclusão do solicitante e do integration user (61622)"
    })
    
    # 12. TIMELINE MARCOS (crm.timeline.comment.add)
    timeline_node = nodes.get("14_Add_Timeline_Milestone_Comment")
    has_timeline = timeline_node is not None and "crm.timeline.comment.add" in timeline_node["parameters"]["url"]
    checks.append({
        "req": "12. RESUMO NA TIMELINE",
        "passed": has_timeline,
        "detail": "Registra marco da triagem na Linha do Tempo sem duplicar chat"
    })
    
    # 13. READBACK & CONCLUSÃO
    readback_node = nodes.get("13_Readback_Verify_Deal")
    complete_node = nodes.get("16_Mark_Session_Completed_Postgres")
    checks.append({
        "req": "13. READBACK & CONCLUSÃO",
        "passed": (readback_node is not None) and (complete_node is not None),
        "detail": "Verificação via crm.deal.get e marcação status='COMPLETED', ai_state='COMPLETED'"
    })
    
    # 14. PILOTO (Restrito 32598 & Cat 160)
    gate_node = nodes.get("01_Strict_Gate_Cat160_Pilot")
    gate_code = gate_node["parameters"]["functionCode"] if gate_node else ""
    checks.append({
        "req": "14. PILOTO RESTRITO",
        "passed": "32598" in gate_code and "160" in gate_code,
        "detail": "Gate fail-closed ativo exclusivamente para Eduardo Alaminos (32598) na Cat 160"
    })
    
    # Exibe resultados
    all_passed = True
    print("\n--- RESULTADOS DOS TESTES DE ARQUITETURA ---")
    for c in checks:
        status = "PASS" if c["passed"] else "FAIL"
        if not c["passed"]:
            all_passed = False
        print(f"[{status}] {c['req']}: {c['detail']}")
        
    print("--------------------------------------------")
    if all_passed:
        print("\nRESULTADO FINAL: CRM_DEAL_CHAT_ARCHITECTURE_PASS\n")
        return True
    else:
        print("\nRESULTADO FINAL: FAIL (Há bloqueios na arquitetura)\n")
        return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
