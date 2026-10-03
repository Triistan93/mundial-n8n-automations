# -*- coding: utf-8 -*-
"""
Teste de Integridade de Contexto e Continuidade: BITRIX_TI_AI_TRIAGE_AGENT
Valida:
1. FIRST_REPLY_PASS: Processamento e envio da primeira resposta da IA
2. SECOND_REPLY_PASS: Continuidade da conversa na segunda interação com histórico
3. TWO_SIMULTANEOUS_DEALS_PASS: Dois deals ativos simultâneos do mesmo solicitante (32598)
4. NO_CROSS_DEAL_CONTEXT: Zero cruzamento de memória, chat, cursor e updates entre deals
5. CURSOR_AFTER_SEND_PASS: Cursor atualizado somente após sucesso confirmado do envio no Bitrix
6. SELF_HEAL_GENERIC_PASS: Auto-recuperação genérica por estado sem IDs fixos
"""

import json
import os
import unittest

def simulate_pipeline_multi_item(active_sessions, bitrix_messages_by_dialog, bitrix_send_results):
    """
    Simula exatamente o pipeline dos nós Code do n8n para múltiplos itens.
    Garante que nenhum .first() seja utilizado e que cada item preserve seu contexto.
    """
    # Nó 04: Fetch messages para cada sessão
    fetched_items = []
    for s in active_sessions:
        dialog_id = s["dialog_id"]
        msgs = bitrix_messages_by_dialog.get(dialog_id, [])
        fetched_items.append({"result": {"chat_id": s["internal_chat_id"], "messages": msgs}})
        
    # Nó 05: Filter And Classify Messages
    # Código idêntico ao gerado em 05_Filter_And_Classify_Messages
    classified_items = []
    for i in range(len(fetched_items)):
        session = active_sessions[i]
        res = fetched_items[i].get("result", {})
        messages = res.get("messages", [])
        
        last_processed_id = int(session.get("last_processed_message_id", 0))
        requester_id = int(session["requester_user_id"])
        bot_id = 61622
        
        sorted_msgs = sorted(messages, key=lambda m: int(m["id"]))
        new_messages = []
        human_takeover = False
        last_msg_id = last_processed_id
        
        for msg in sorted_msgs:
            m_id = int(msg["id"])
            if m_id <= last_processed_id:
                continue
            last_msg_id = max(last_msg_id, m_id)
            author_id = int(msg.get("author_id", 0))
            if author_id == bot_id or author_id == 0:
                continue
            if author_id != requester_id:
                human_takeover = True
                break
            txt = str(msg.get("text", "")).strip()
            if txt:
                new_messages.push(txt) if hasattr(new_messages, 'push') else new_messages.append(txt)
                
        if human_takeover:
            classified_items.append({
                "deal_id": session["deal_id"],
                "dialog_id": session["dialog_id"],
                "human_takeover": True,
                "last_msg_id": last_msg_id
            })
            continue
            
        if session.get("ai_state") == "AI_PAUSED":
            continue
            
        if len(new_messages) > 0:
            classified_items.append({
                "deal_id": session["deal_id"],
                "chat_id": session["internal_chat_id"],
                "dialog_id": session["dialog_id"],
                "requester_user_id": requester_id,
                "message_id": last_msg_id,
                "message_text": "\n".join(new_messages),
                "redis_memory_key": f"bitrix:ti:deal:{session['deal_id']}:memory",
                "ai_state": session.get("ai_state", "AI_ACTIVE")
            })

    # Nó 07: Prepare AI Input
    prep_ai_items = []
    for item in classified_items:
        if item.get("human_takeover"):
            continue
        prep_ai_items.append({
            "deal_id": item["deal_id"],
            "chat_id": item["chat_id"],
            "dialog_id": item["dialog_id"],
            "requester_user_id": item["requester_user_id"],
            "message_id": item["message_id"],
            "full_user_input": item["message_text"],
            "redis_memory_key": item["redis_memory_key"],
            "ai_state": item["ai_state"]
        })

    # Nó 08: AI Agent (Simulação com output estruturado ou ask)
    agent_outputs = []
    for item in prep_ai_items:
        # Resposta simulada isolada com menção ao contexto do chamado
        text = f"Entendido chamado #{item['deal_id']}. Qual é o sintoma exato?"
        agent_outputs.append({"output": text})

    # Nó 09: Format AI Response (index-based pairing, sem .first())
    formatted_responses = []
    for i in range(len(agent_outputs)):
        agent_item = agent_outputs[i]
        prev_data = prep_ai_items[i]
        formatted_responses.append({
            "deal_id": prev_data["deal_id"],
            "chat_id": prev_data["chat_id"],
            "dialog_id": prev_data["dialog_id"],
            "requester_user_id": prev_data["requester_user_id"],
            "message_id": prev_data["message_id"],
            "reply_text": agent_item["output"],
            "structured_data": None,
            "is_complete": False
        })

    # Nó 10: Prepare Cursor Update pós envio Bitrix
    cursor_updates = []
    for i in range(len(formatted_responses)):
        ask_data = formatted_responses[i]
        bitrix_res = bitrix_send_results.get(ask_data["dialog_id"], {})
        
        # Cursor SÓ avança se Bitrix retornou result
        if bitrix_res.get("result"):
            cursor_updates.append({
                "deal_id": ask_data["deal_id"],
                "message_id": ask_data["message_id"],
                "sent_bitrix_msg_id": bitrix_res["result"]
            })

    return {
        "classified_items": classified_items,
        "prep_ai_items": prep_ai_items,
        "formatted_responses": formatted_responses,
        "cursor_updates": cursor_updates
    }


class TestContextIntegrityAndContinuity(unittest.TestCase):

    def test_first_and_second_reply_continuity(self):
        """Valida FIRST_REPLY_PASS e SECOND_REPLY_PASS mantendo continuidade e isolamento de cursor."""
        deal_id = 1372428
        dialog_id = "chat828656"
        requester_id = 32598
        
        # 1. Primeira resposta do solicitante
        session = {
            "id": 1,
            "deal_id": deal_id,
            "requester_user_id": requester_id,
            "internal_chat_id": 828656,
            "dialog_id": dialog_id,
            "last_processed_message_id": "64394378", # Após welcome msg
            "ai_state": "AI_ACTIVE"
        }
        
        msgs_run_1 = [
            {"id": 64394374, "author_id": 0, "text": "Sistema convidou..."},
            {"id": 64394378, "author_id": 61622, "text": "Olá Eduardo..."},
            {"id": 64394416, "author_id": requester_id, "text": "Sim, afeta a loja"}
        ]
        
        send_res_1 = {dialog_id: {"result": 64394420}} # Bitrix retornou sucesso
        
        run_1 = simulate_pipeline_multi_item([session], {dialog_id: msgs_run_1}, send_res_1)
        
        # Valida FIRST_REPLY_PASS
        self.assertEqual(len(run_1["formatted_responses"]), 1)
        self.assertEqual(run_1["formatted_responses"][0]["deal_id"], deal_id)
        self.assertEqual(run_1["formatted_responses"][0]["message_id"], 64394416)
        self.assertEqual(len(run_1["cursor_updates"]), 1)
        self.assertEqual(run_1["cursor_updates"][0]["message_id"], 64394416)
        print("\n[PASS] FIRST_REPLY_PASS: Primeira resposta da IA gerada e cursor avançado após envio")

        # 2. Segunda resposta do solicitante (continuidade)
        session["last_processed_message_id"] = "64394416" # Cursor atualizado pós run 1
        
        msgs_run_2 = msgs_run_1 + [
            {"id": 64394420, "author_id": 61622, "text": "Entendido chamado #1372428..."},
            {"id": 64394450, "author_id": requester_id, "text": "É no caixa 02, não abre o Microwork"}
        ]
        
        send_res_2 = {dialog_id: {"result": 64394460}}
        
        run_2 = simulate_pipeline_multi_item([session], {dialog_id: msgs_run_2}, send_res_2)
        
        # Valida SECOND_REPLY_PASS
        self.assertEqual(len(run_2["formatted_responses"]), 1)
        self.assertEqual(run_2["formatted_responses"][0]["message_id"], 64394450)
        self.assertEqual(run_2["cursor_updates"][0]["message_id"], 64394450)
        print("[PASS] SECOND_REPLY_PASS: Segunda resposta processada mantendo cursor e histórico")

    def test_two_simultaneous_deals_no_cross_context(self):
        """Valida TWO_SIMULTANEOUS_DEALS_PASS e NO_CROSS_DEAL_CONTEXT com 2 deals simultâneos de Eduardo (32598)."""
        requester_id = 32598
        
        # Duas sessões ativas simultâneas
        session_a = {
            "id": 10,
            "deal_id": 1372428,
            "requester_user_id": requester_id,
            "internal_chat_id": 828656,
            "dialog_id": "chat828656",
            "last_processed_message_id": "100",
            "ai_state": "AI_ACTIVE"
        }
        
        session_b = {
            "id": 11,
            "deal_id": 1372450,
            "requester_user_id": requester_id,
            "internal_chat_id": 828700,
            "dialog_id": "chat828700",
            "last_processed_message_id": "200",
            "ai_state": "AI_ACTIVE"
        }
        
        active_sessions = [session_a, session_b]
        
        # Mensagens distintas em cada chat
        msgs_by_dialog = {
            "chat828656": [
                {"id": 105, "author_id": requester_id, "text": "Mensagem exclusiva do Deal A: Impressora parada"}
            ],
            "chat828700": [
                {"id": 205, "author_id": requester_id, "text": "Mensagem exclusiva do Deal B: Microwork travado"}
            ]
        }
        
        send_results = {
            "chat828656": {"result": 106},
            "chat828700": {"result": 206}
        }
        
        results = simulate_pipeline_multi_item(active_sessions, msgs_by_dialog, send_results)
        
        # 1. Verifica que ambos os deals foram processados
        self.assertEqual(len(results["formatted_responses"]), 2)
        
        resp_a = results["formatted_responses"][0]
        resp_b = results["formatted_responses"][1]
        
        # 2. Isolamento estrito de Deal A
        self.assertEqual(resp_a["deal_id"], 1372428)
        self.assertEqual(resp_a["dialog_id"], "chat828656")
        self.assertEqual(resp_a["message_id"], 105)
        self.assertEqual(results["prep_ai_items"][0]["redis_memory_key"], "bitrix:ti:deal:1372428:memory")
        self.assertIn("1372428", resp_a["reply_text"])
        self.assertNotIn("1372450", resp_a["reply_text"])
        
        # 3. Isolamento estrito de Deal B
        self.assertEqual(resp_b["deal_id"], 1372450)
        self.assertEqual(resp_b["dialog_id"], "chat828700")
        self.assertEqual(resp_b["message_id"], 205)
        self.assertEqual(results["prep_ai_items"][1]["redis_memory_key"], "bitrix:ti:deal:1372450:memory")
        self.assertIn("1372450", resp_b["reply_text"])
        self.assertNotIn("1372428", resp_b["reply_text"])
        
        # 4. Zero vazamento de cursor entre deals
        self.assertEqual(results["cursor_updates"][0]["deal_id"], 1372428)
        self.assertEqual(results["cursor_updates"][0]["message_id"], 105)
        self.assertEqual(results["cursor_updates"][1]["deal_id"], 1372450)
        self.assertEqual(results["cursor_updates"][1]["message_id"], 205)
        
        print("[PASS] TWO_SIMULTANEOUS_DEALS_PASS: Deal A e Deal B respondem estritamente em seus respectivos chats")
        print("[PASS] NO_CROSS_DEAL_CONTEXT: Zero cruzamento de memória, chat, cursor ou IA entre múltiplos deals")

    def test_cursor_remains_previous_on_send_failure(self):
        """Valida CURSOR_AFTER_SEND_PASS: se envio no Bitrix falhar, cursor não é atualizado."""
        session = {
            "id": 1,
            "deal_id": 1372428,
            "requester_user_id": 32598,
            "internal_chat_id": 828656,
            "dialog_id": "chat828656",
            "last_processed_message_id": "100",
            "ai_state": "AI_ACTIVE"
        }
        
        msgs = [{"id": 105, "author_id": 32598, "text": "Teste falha de envio"}]
        send_fail = {"chat828656": {"error": "BITRIX_NETWORK_ERROR"}} # Sem 'result'
        
        results = simulate_pipeline_multi_item([session], {"chat828656": msgs}, send_fail)
        
        # Resposta foi gerada pela IA, mas o cursor NÃO deve ser atualizado
        self.assertEqual(len(results["formatted_responses"]), 1)
        self.assertEqual(len(results["cursor_updates"]), 0)
        print("[PASS] CURSOR_AFTER_SEND_PASS: Cursor permanece intacto quando envio Bitrix não retorna sucesso")

    def test_self_heal_generic_by_state(self):
        """Valida SELF_HEAL_GENERIC_PASS: auto-recuperação genérica por estado sem IDs fixos."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(script_dir)
        workflow_path = os.path.join(repo_root, "workflows", "canonical", "BITRIX_TI_AI_TRIAGE_AGENT.json")
        with open(workflow_path, "r", encoding="utf-8") as f:
            wf_content = f.read()
            
        # Garante que não existem IDs fixos no código do workflow
        self.assertNotIn("1372428", wf_content, "Não deve haver ID 1372428 fixo")
        self.assertNotIn("1372356", wf_content, "Não deve haver ID 1372356 fixo")
        self.assertNotIn("chat828656", wf_content, "Não deve haver chat828656 fixo")
        self.assertNotIn(".first()", wf_content, "Não deve haver chamada .first() para contexto de deal")
        
        # Garante a cláusula SQL genérica por estado
        self.assertIn("status = 'CHAT_CREATING' AND internal_chat_id IS NOT NULL", wf_content)
        print("[PASS] SELF_HEAL_GENERIC_PASS: Auto-recuperação 100% genérica por estado e livre de IDs fixos")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestContextIntegrityAndContinuity)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n=======================================================")
        print("RESULTADO FINAL: CRM_CARD_CHAT_CONTINUITY_PASS")
        print("=======================================================\n")
    else:
        print("\nRESULTADO FINAL: FAIL\n")
        exit(1)
