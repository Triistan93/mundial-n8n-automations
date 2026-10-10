import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_ticket_node_positions():
    pos = {}

    # =========================================================================
    # ZONA 1: INGESTÃO DE TICKETS & IDEMPOTÊNCIA (X: 100 .. 1500, Y: 100 .. 420)
    # =========================================================================
    pos['00_Schedule_Trigger'] = [140, 180]
    pos['00_Webhook_Deal_Add'] = [140, 320]
    pos['01_Polling_Get_New_Deals'] = [360, 240]
    pos['01_Extract_Discovered_Deal_IDs'] = [580, 240]
    pos['01_Fetch_Deal_Bitrix_Verification'] = [800, 240]
    pos['01_Strict_Gate_Cat160_Pilot'] = [1020, 240]
    pos['02_Reserve_Deal_Session_Atomic'] = [1240, 240]
    pos['02_If_Reservation_Won'] = [1460, 240]

    # =========================================================================
    # ZONA 2: INTELIGÊNCIA PREVENTIVA (P1 CLUSTERING & ANTI-DUPLICADOS) (X: 1700 .. 3400, Y: 100 .. 500)
    # =========================================================================
    # Sub-bloco A: Outage Clustering P1
    pos['01_Check_Store_Outage_Cluster'] = [1740, 160]
    pos['01_Evaluate_Store_Outage'] = [1960, 160]

    # Sub-bloco B: Anti-Duplicados
    pos['01_Fetch_Requester_Open_Deals'] = [1740, 320]
    pos['01_Evaluate_Duplicate_Check'] = [1960, 320]
    pos['01_If_Is_Duplicate'] = [2180, 320]
    pos['Dup_01_Add_Comment_Original'] = [2400, 260]
    pos['Dup_02_Close_New_Deal'] = [2620, 260]
    pos['Dup_03_Add_Timeline_New_Deal'] = [2840, 260]
    pos['Dup_04_Notify_User'] = [3060, 260]

    # =========================================================================
    # ZONA 3: ATIVAÇÃO DE CHAT NO CARD & ALÇADAS DE COMPRA (X: 100 .. 1600, Y: 600 .. 980)
    # =========================================================================
    pos['03_Create_CRM_Card_Chat'] = [140, 700]
    pos['03_Prepare_Activation'] = [360, 700]
    pos['03_Activate_Session_With_Chat'] = [580, 700]
    pos['03_Filter_Purchase_Only'] = [800, 700]
    pos['03_Send_Buttons_Deal_Chat'] = [1020, 700]
    pos['03_Send_Buttons_Direct_Chat'] = [1240, 700]
    pos['03_Move_To_Aguardando_Autorizacao'] = [1460, 700]

    # =========================================================================
    # ZONA 4: MONITORAMENTO DE CHAT, TAKEOVER & DEBOUNCE (X: 1700 .. 3400, Y: 600 .. 980)
    # =========================================================================
    pos['04_Get_Active_Sessions_Postgres'] = [1740, 700]
    pos['04_Fetch_Chat_Messages_Bitrix'] = [1960, 700]
    pos['05_Filter_And_Classify_Messages'] = [2180, 700]
    pos['05_If_Human_Takeover'] = [2400, 700]
    pos['05_Pause_AI_On_Human_Takeover'] = [2400, 860]
    pos['06_Route_Session_Status'] = [2620, 700]
    pos['06_Wait_Debounce_4s'] = [2840, 700]

    # =========================================================================
    # ZONA 5: VISÃO COMPUTACIONAL (GPT-4O-MINI OCR) (X: 100 .. 1400, Y: 1100 .. 1500)
    # =========================================================================
    pos['06_If_Has_Image_To_Process'] = [140, 1220]
    pos['Vision_01_Get_Download_Url'] = [360, 1220]
    pos['Vision_02_Download_Image'] = [580, 1220]
    pos['Vision_03_Prepare_Vision_Payload'] = [800, 1220]
    pos['Vision_04_Call_OpenAI_Vision'] = [1020, 1220]
    pos['Vision_05_Merge_Vision_Context'] = [1240, 1220]

    # =========================================================================
    # ZONA 6: NÚCLEO COGNITIVO DE TRIAGEM TI (LANGCHAIN) (X: 1540 .. 2800, Y: 1100 .. 1600)
    # =========================================================================
    pos['07_Prepare_AI_Deal_Input'] = [1560, 1220]
    pos['08_AI_Agent_Triage_Deal'] = [1860, 1220]

    # Satélites LangChain à esquerda e abaixo do Agent
    pos['OpenAI_Chat_Model_Deal'] = [1640, 1380]
    pos['Redis_Deal_Chat_Memory'] = [1860, 1380]
    pos['Tool_Think_Deal'] = [2080, 1380]
    pos['Tool_Diagnostico_TI'] = [1640, 1500]
    pos['KB_TI_PGVector_Tool'] = [1860, 1500]
    pos['Embeddings_OpenAI_KB'] = [2080, 1500]

    # Saídas cognitivas
    pos['09_Format_AI_Response'] = [2160, 1220]
    pos['09_If_Triage_Complete'] = [2380, 1220]

    # Se precisa aprofundar (continuação do papo no card):
    pos['10_Send_AI_Question_To_Card_Chat'] = [2600, 1140]
    pos['10_Prepare_Cursor_Update'] = [2820, 1140]
    pos['10_Update_Cursor_On_Ask'] = [3040, 1140]

    # =========================================================================
    # ZONA 7: CONCLUSÃO B01, ATUALIZAÇÃO CRM & TIMELINE (X: 100 .. 2600, Y: 1720 .. 2200)
    # =========================================================================
    pos['11_B01_Priority_And_Payload'] = [140, 1840]
    pos['11_Fetch_Deal_For_Description'] = [360, 1840]
    pos['12_Prepare_Deal_Update_Payload'] = [580, 1840]
    pos['12_Update_Deal_CRM_Bitrix'] = [800, 1840]
    pos['12_Prepare_Readback_Context'] = [1020, 1840]
    pos['13_Readback_Verify_Deal'] = [1240, 1840]
    pos['14_Prepare_Timeline_And_Chat'] = [1460, 1840]
    pos['14_Add_Timeline_Milestone_Comment'] = [1680, 1840]
    pos['15_Prepare_Final_Chat'] = [1900, 1840]
    pos['15_Send_Final_Confirmation_To_Chat'] = [2120, 1840]
    pos['16_Prepare_Complete_Session'] = [2340, 1840]
    pos['16_Mark_Session_Completed_Postgres'] = [2560, 1840]

    # Alçada Direta de Compra para Aprovador
    pos['15_Filter_Purchase_For_Approver'] = [1900, 2020]
    pos['15_Send_Direct_Approval_To_Approver'] = [2120, 2020]

    # =========================================================================
    # ZONA 8: ROTEADOR PÓS-RESOLUÇÃO & CSAT PULSE (X: 100 .. 3300, Y: 2320 .. 2900)
    # =========================================================================
    pos['PostRes_01_Fetch_Deal'] = [140, 2460]
    pos['PostRes_02_Prepare_Prompt'] = [360, 2460]
    pos['PostRes_03_Classify_Intent'] = [580, 2460]
    pos['PostRes_04_Parse_Classification'] = [800, 2460]

    # Linha Reabertura
    pos['PostRes_05_If_Reopen'] = [1040, 2380]
    pos['PostRes_Reopen_Deal_CRM'] = [1260, 2380]
    pos['PostRes_Reopen_Timeline'] = [1480, 2380]
    pos['PostRes_Reopen_Send_Chat'] = [1700, 2380]
    pos['PostRes_Reopen_Update_Postgres'] = [1920, 2380]

    # Linha Anti-Carona & Agradecimento
    pos['PostRes_06_If_Carona'] = [1040, 2540]
    pos['PostRes_Carona_Timeline'] = [1260, 2540]
    pos['PostRes_Carona_Send_Chat'] = [1480, 2540]
    pos['PostRes_Carona_Update_Postgres'] = [1700, 2540]
    pos['PostRes_Thanks_Send_Chat'] = [1480, 2680]
    pos['PostRes_Thanks_Update_Postgres'] = [1700, 2680]

    # Linha CSAT (1 a 5 estrelas)
    pos['PostRes_07_If_CSAT'] = [2000, 2540]
    pos['PostRes_CSAT_Insert_Postgres'] = [2220, 2540]
    pos['PostRes_CSAT_Timeline_CRM'] = [2440, 2540]
    pos['PostRes_CSAT_Send_Chat'] = [2660, 2540]
    pos['PostRes_CSAT_Update_Postgres'] = [2880, 2540]

    return pos

if __name__ == '__main__':
    pos = get_ticket_node_positions()
    print(f"Total mapped positions: {len(pos)}")

    with open('workflows/BITRIX_TI_AI_TRIAGE_AGENT_LIVE.json', 'r', encoding='utf-8') as f:
        wf = json.load(f)

    functional_nodes = [n for n in wf['nodes'] if not n['type'].endswith('stickyNote')]
    print(f"Total functional nodes in workflow: {len(functional_nodes)}")

    missing = [n['name'] for n in functional_nodes if n['name'] not in pos]
    if missing:
        print(f"MISSING: {missing}")
    else:
        print("ALL functional nodes mapped successfully!")

    # Check for duplicate positions
    seen = {}
    for name, p in pos.items():
        k = tuple(p)
        if k in seen:
            print(f"Duplicate pos {p} for {name} and {seen[k]}")
        seen[k] = name
    print(f"Unique positions: {len(seen)} / {len(pos)}")
